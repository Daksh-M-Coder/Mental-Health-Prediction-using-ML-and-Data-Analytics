"use client";
import { useState, useRef, useEffect, useCallback } from "react";

/**
 * SessionMenu.jsx — 3-dot dropdown menu for session cards.
 * Actions: Rename (inline), Delete, Share (JSON export)
 */

export default function SessionMenu({ session, onDelete, onRename, appTheme }) {
  const [open, setOpen]       = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [newName, setNewName]   = useState(session.snippet || "");
  const menuRef  = useRef(null);
  const inputRef = useRef(null);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
        setRenaming(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  // Focus input when rename mode opens
  useEffect(() => {
    if (renaming) inputRef.current?.focus();
  }, [renaming]);

  const handleDelete = useCallback((e) => {
    e.stopPropagation();
    setOpen(false);
    onDelete?.(session.id);
  }, [session.id, onDelete]);

  const handleRenameStart = useCallback((e) => {
    e.stopPropagation();
    setNewName(session.snippet || "");
    setRenaming(true);
  }, [session.snippet]);

  const handleRenameSubmit = useCallback((e) => {
    e?.stopPropagation?.();
    const trimmed = newName.trim();
    if (trimmed && trimmed !== session.snippet) {
      onRename?.(session.id, trimmed);
    }
    setRenaming(false);
    setOpen(false);
  }, [newName, session.id, session.snippet, onRename]);

  const handleShare = useCallback((e) => {
    e.stopPropagation();
    setOpen(false);
    // Build a clean export object
    const exportData = {
      id:         session.id,
      timestamp:  new Date(session.timestamp).toISOString(),
      source:     session.source,
      snippet:    session.snippet,
      userName:   session.userName || null,
      risk:       session.risk,
      confidence: session.confidence,
      crisis:     session.crisis,
      features:   session.features   || null,
      prediction: session.prediction || null,
      empathy_map: session.empathy_map || null,
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `mindbridge_session_${session.id}.json`;
    a.click();
  }, [session]);

  return (
    <div
      className="session-menu-wrap"
      ref={menuRef}
      onClick={e => e.stopPropagation()}
    >
      {/* 3-dot trigger */}
      <button
        className="session-menu-trigger"
        onClick={e => { e.stopPropagation(); setOpen(v => !v); }}
        aria-label="Session options"
        title="More options"
        data-app-theme={appTheme}
      >
        ⋯
      </button>

      {/* Dropdown */}
      {open && !renaming && (
        <div className="session-menu-dropdown" data-app-theme={appTheme}>
          <button className="session-menu-item" onClick={handleRenameStart}>
            <span>✏️</span> Rename
          </button>
          <button className="session-menu-item" onClick={handleShare}>
            <span>📤</span> Export JSON
          </button>
          <div className="session-menu-divider" />
          <button className="session-menu-item danger" onClick={handleDelete}>
            <span>🗑️</span> Delete
          </button>
        </div>
      )}

      {/* Inline rename input */}
      {renaming && (
        <div
          className="session-rename-wrap"
          onClick={e => e.stopPropagation()}
        >
          <input
            ref={inputRef}
            className="session-rename-input"
            value={newName}
            onChange={e => setNewName(e.target.value)}
            onKeyDown={e => {
              if (e.key === "Enter") handleRenameSubmit(e);
              if (e.key === "Escape") { setRenaming(false); setOpen(false); }
            }}
            placeholder="New name..."
            maxLength={80}
          />
          <button className="session-rename-ok" onClick={handleRenameSubmit} title="Save">✓</button>
          <button
            className="session-rename-cancel"
            onClick={e => { e.stopPropagation(); setRenaming(false); setOpen(false); }}
            title="Cancel"
          >✕</button>
        </div>
      )}
    </div>
  );
}
