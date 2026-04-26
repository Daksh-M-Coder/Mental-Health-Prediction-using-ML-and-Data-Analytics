"""
database.py — MongoDB + Redis integration for MindBridge AI (local-only)

MongoDB (port 27017):
  - Stores every completed session/assessment as a document
  - Collections: sessions, crisis_logs

Redis (port 6379):
  - Caches LLM responses by (model, prompt_hash) → saves API round-trips
  - Default TTL: 1 hour for interview responses

Both are OPTIONAL — if MongoDB or Redis is not running, the app
falls back gracefully to in-memory / no-cache mode. Nothing breaks.
"""

import os
import json
import time
import hashlib
import logging
from datetime import datetime
from typing import Optional, Any, Dict

logger = logging.getLogger("mindbridge.db")

# ── MongoDB ────────────────────────────────────────────────────────────────────

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "mindbridge")

_mongo_client = None
_mongo_db     = None
_mongo_ok     = False

def _init_mongo():
    global _mongo_client, _mongo_db, _mongo_ok
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

        _mongo_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=2000,   # fail fast if not running
            connectTimeoutMS=2000,
        )
        # Ping to confirm connection
        _mongo_client.admin.command("ping")
        _mongo_db = _mongo_client[MONGO_DB]

        # Create useful indexes
        _mongo_db.sessions.create_index("timestamp")
        _mongo_db.sessions.create_index("source")
        _mongo_db.sessions.create_index("risk")
        _mongo_db.crisis_logs.create_index("timestamp")

        _mongo_ok = True
        logger.info(f"✅ MongoDB connected → {MONGO_URI} / {MONGO_DB}")
    except Exception as e:
        _mongo_ok = False
        logger.warning(f"⚠️  MongoDB not available ({e}). Sessions won't be persisted to DB.")

def get_db():
    """Return the mongo database handle, or None if not connected."""
    return _mongo_db if _mongo_ok else None


def save_session(session: Dict[str, Any]) -> Optional[str]:
    """
    Persist a completed session document to MongoDB.
    Returns the inserted _id as string, or None on failure.
    session should include: source, risk, confidence, crisis, userName,
                            snippet, timestamp, empathy_map, features, etc.
    """
    if not _mongo_ok:
        return None
    try:
        doc = {
            **session,
            "saved_at": datetime.utcnow().isoformat(),
        }
        # pymongo won't serialize custom objects — sanitise
        result = _mongo_db.sessions.insert_one(_sanitise(doc))
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"MongoDB save_session error: {e}")
        return None


def get_sessions(limit: int = 100, skip: int = 0) -> list:
    """Return recent sessions newest-first."""
    if not _mongo_ok:
        return []
    try:
        cursor = (
            _mongo_db.sessions
            .find({}, {"_id": 0})           # exclude ObjectId from JSON
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )
        return list(cursor)
    except Exception as e:
        logger.error(f"MongoDB get_sessions error: {e}")
        return []


def get_session_stats() -> Dict[str, Any]:
    """Aggregate risk counts + crisis count from DB."""
    if not _mongo_ok:
        return {}
    try:
        pipeline = [
            {"$group": {
                "_id": "$risk",
                "count": {"$sum": 1},
                "crisis_count": {"$sum": {"$cond": ["$crisis", 1, 0]}},
            }}
        ]
        result = list(_mongo_db.sessions.aggregate(pipeline))
        stats = {"total": _mongo_db.sessions.count_documents({})}
        for r in result:
            stats[str(r["_id"]).lower()] = r["count"]
        stats["crisis"] = sum(r["crisis_count"] for r in result)
        return stats
    except Exception as e:
        logger.error(f"MongoDB stats error: {e}")
        return {}


def save_crisis_log(user_name: Optional[str], turn: int, snippet: str):
    """Log a crisis detection event separately for review."""
    if not _mongo_ok:
        return
    try:
        _mongo_db.crisis_logs.insert_one({
            "timestamp": datetime.utcnow().isoformat(),
            "user_name": user_name,
            "turn": turn,
            "snippet": snippet[:200],
        })
    except Exception as e:
        logger.error(f"MongoDB crisis_log error: {e}")


# ── Redis ──────────────────────────────────────────────────────────────────────

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB   = int(os.getenv("REDIS_DB",   "0"))
REDIS_TTL  = int(os.getenv("REDIS_TTL",  "3600"))  # 1-hour cache

_redis_client = None
_redis_ok     = False

def _init_redis():
    global _redis_client, _redis_ok
    try:
        import redis
        _redis_client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
            socket_connect_timeout=1, socket_timeout=1, decode_responses=True,
        )
        _redis_client.ping()
        _redis_ok = True
        logger.info(f"✅ Redis connected → {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        _redis_ok = False
        logger.warning(f"⚠️  Redis not available ({e}). LLM responses won't be cached.")


def _cache_key(model: str, prompt_hash: str) -> str:
    return f"mb:llm:{model}:{prompt_hash}"


def cache_get(model: str, messages: list) -> Optional[str]:
    """Try to get a cached LLM response. Returns raw text or None."""
    if not _redis_ok:
        return None
    try:
        h = hashlib.sha256(json.dumps(messages, sort_keys=True).encode()).hexdigest()[:16]
        key = _cache_key(model, h)
        val = _redis_client.get(key)
        if val:
            logger.debug(f"Redis HIT: {key}")
        return val
    except Exception as e:
        logger.debug(f"Redis get error: {e}")
        return None


def cache_set(model: str, messages: list, response: str, ttl: int = REDIS_TTL):
    """Store an LLM response in Redis with TTL."""
    if not _redis_ok:
        return
    try:
        h = hashlib.sha256(json.dumps(messages, sort_keys=True).encode()).hexdigest()[:16]
        key = _cache_key(model, h)
        _redis_client.setex(key, ttl, response)
        logger.debug(f"Redis SET: {key} (ttl={ttl}s)")
    except Exception as e:
        logger.debug(f"Redis set error: {e}")


def cache_flush():
    """Flush all MindBridge LLM cache keys (not the whole Redis DB)."""
    if not _redis_ok:
        return 0
    try:
        keys = _redis_client.keys("mb:llm:*")
        if keys:
            _redis_client.delete(*keys)
        return len(keys)
    except Exception as e:
        logger.debug(f"Redis flush error: {e}")
        return 0


def redis_status() -> Dict[str, Any]:
    """Return Redis connection info for /health endpoint."""
    if not _redis_ok:
        return {"available": False}
    try:
        info = _redis_client.info("server")
        keys = len(_redis_client.keys("mb:llm:*"))
        return {
            "available": True,
            "version": info.get("redis_version", "unknown"),
            "cached_responses": keys,
            "host": f"{REDIS_HOST}:{REDIS_PORT}",
        }
    except Exception:
        return {"available": False}


def mongo_status() -> Dict[str, Any]:
    """Return MongoDB connection info for /health endpoint."""
    if not _mongo_ok:
        return {"available": False}
    try:
        stats = get_session_stats()
        return {
            "available": True,
            "uri": MONGO_URI.split("@")[-1],   # strip credentials if any
            "db": MONGO_DB,
            "total_sessions": stats.get("total", 0),
            "crisis_sessions": stats.get("crisis", 0),
        }
    except Exception:
        return {"available": False}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _sanitise(obj):
    """Recursively make an object JSON-serialisable for MongoDB."""
    if isinstance(obj, dict):
        return {k: _sanitise(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitise(x) for x in obj]
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    return str(obj)


def delete_session_by_id(session_id: str) -> bool:
    """Delete a single session document by its session_id field (not _id)."""
    if not _mongo_ok:
        return False
    try:
        result = _mongo_db.sessions.delete_one({"id": session_id})
        if result.deleted_count == 0:
            # Try matching by string _id fallback
            from bson import ObjectId
            try:
                result = _mongo_db.sessions.delete_one({"_id": ObjectId(session_id)})
            except Exception:
                pass
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"MongoDB delete_session_by_id error: {e}")
        return False


def update_session(session_id: str, updates: Dict[str, Any]) -> bool:
    """Update fields on a session (e.g. snippet/name rename)."""
    if not _mongo_ok:
        return False
    try:
        result = _mongo_db.sessions.update_one(
            {"id": session_id},
            {"$set": updates}
        )
        return result.matched_count > 0
    except Exception as e:
        logger.error(f"MongoDB update_session error: {e}")
        return False


def save_conversation(session_id: str, messages: list, empathy_map: dict = None, meta: dict = None) -> bool:
    """
    Persist the full conversation message history for a session.
    Stored in a separate 'conversations' collection keyed by session_id.
    """
    if not _mongo_ok:
        return False
    try:
        doc = {
            "session_id": session_id,
            "messages": _sanitise(messages),
            "empathy_map": _sanitise(empathy_map or {}),
            "saved_at": datetime.utcnow().isoformat(),
        }
        if meta:
            doc.update(_sanitise(meta))
        # Upsert — if session already saved (e.g. re-run), overwrite
        _mongo_db.conversations.replace_one(
            {"session_id": session_id},
            doc,
            upsert=True,
        )
        return True
    except Exception as e:
        logger.error(f"MongoDB save_conversation error: {e}")
        return False


def get_conversation(session_id: str) -> dict:
    """Retrieve stored conversation messages + empathy map for a session."""
    if not _mongo_ok:
        return {}
    try:
        doc = _mongo_db.conversations.find_one(
            {"session_id": session_id},
            {"_id": 0}
        )
        return doc or {}
    except Exception as e:
        logger.error(f"MongoDB get_conversation error: {e}")
        return {}


# ── Auto-init on import ────────────────────────────────────────────────────────

_init_mongo()
_init_redis()

# Create index for conversations collection after init
try:
    if _mongo_ok:
        _mongo_db.conversations.create_index("session_id", unique=True)
except Exception:
    pass
