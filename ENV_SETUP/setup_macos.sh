#!/usr/bin/env bash
# ============================================================
# ENV_SETUP/setup_macos.sh
# Mental Health Risk Prediction System - macOS Setup Script
# Live logging: all output visible AND tee'd to log file
# Usage: chmod +x setup_macos.sh && ./setup_macos.sh
# ============================================================

set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="setup_log_${TIMESTAMP}.txt"
VENV_DIR="venv"
REQUIREMENTS="requirements.txt"

# ── Colour helpers ──────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()     { echo -e "$1" | tee -a "../${LOG_FILE}"; }
header()  { log "\n${CYAN}${BOLD}[----] $1${RESET}"; }
success() { log "${GREEN}[ OK ] $1${RESET}"; }
warn()    { log "${YELLOW}[WARN] $1${RESET}"; }
err()     { log "${RED}[FAIL] $1${RESET}"; }

# ── Start ───────────────────────────────────────────────────
log "============================================================"
log "  Mental Health Risk Prediction System - macOS Setup"
log "  Started: $(date)"
log "  Log file: ${LOG_FILE} (in project root)"
log "============================================================"

# ── STEP 1: Check Python ────────────────────────────────────
header "STEP 1/5 - Checking Python installation"

# macOS ships python3 via Xcode CLT or Homebrew
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    success "Found: ${PY_VER}"
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PY_VER=$(python --version 2>&1)
    # Make sure it's Python 3
    if python -c "import sys; sys.exit(0 if sys.version_info.major==3 else 1)" 2>/dev/null; then
        success "Found (as 'python'): ${PY_VER}"
        PYTHON_CMD="python"
    else
        err "Only Python 2 found. Install Python 3 via Homebrew:"
        err "  brew install python"
        exit 1
    fi
else
    err "Python not found. Install it via:"
    err "  Homebrew: brew install python"
    err "  Official: https://python.org"
    exit 1
fi

# Check for Homebrew (helpful for macOS)
if command -v brew &>/dev/null; then
    success "Homebrew found: $(brew --version | head -1)"
else
    warn "Homebrew not found (optional). If you hit SSL/cert issues: https://brew.sh"
fi

# ── STEP 2: Create Virtual Environment ──────────────────────
header "STEP 2/5 - Creating virtual environment"
if [ -d "../${VENV_DIR}" ]; then
    warn "Virtual environment '${VENV_DIR}/' already exists — skipping creation."
    warn "Delete it manually if you want a clean reinstall: rm -rf ../${VENV_DIR}"
else
    log "Running: $PYTHON_CMD -m venv ../${VENV_DIR}"
    $PYTHON_CMD -m venv "../${VENV_DIR}" 2>&1 | tee -a "../${LOG_FILE}"
    success "Virtual environment created at '${VENV_DIR}/'"
fi

# ── STEP 3: Activate ────────────────────────────────────────
header "STEP 3/5 - Activating virtual environment"
source "../${VENV_DIR}/bin/activate"
success "Virtual environment activated. Python: $(which python)"

# ── STEP 4: Upgrade pip ─────────────────────────────────────
header "STEP 4/5 - Upgrading pip (all output shown live)"
log "Running: pip install --upgrade pip"
pip install --upgrade pip 2>&1 | tee -a "../${LOG_FILE}"
success "pip upgraded to $(pip --version)"

# ── STEP 5: Install Requirements ────────────────────────────
header "STEP 5/5 - Installing requirements (all output shown live)"
if [ -f "../${REQUIREMENTS}" ]; then
    log "Found ${REQUIREMENTS} — installing all packages..."
    log "Running: pip install -r ../${REQUIREMENTS}"
    echo ""
    pip install -r "../${REQUIREMENTS}" 2>&1 | tee -a "../${LOG_FILE}"
    success "All packages installed."
else
    warn "${REQUIREMENTS} not found in project root. Skipping."
    warn "Add a requirements.txt then re-run this script."
fi

# ── Done ────────────────────────────────────────────────────
log ""
log "============================================================"
log "  Setup Complete - $(date)"
log "  Full log saved to: ${LOG_FILE}"
log "============================================================"
log ""
log "To activate venv in future sessions:"
log "  source ${VENV_DIR}/bin/activate"
log ""
log "To start the app:"
log "  python mental_health_ml_system.py"
