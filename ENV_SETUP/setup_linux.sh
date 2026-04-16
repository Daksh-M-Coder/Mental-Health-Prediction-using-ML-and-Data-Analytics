#!/usr/bin/env bash
# ============================================================
# ENV_SETUP/setup_linux.sh
# Mental Health Risk Prediction System - Linux Setup Script
# Live logging: all output visible AND tee'd to log file
# Usage: chmod +x setup_linux.sh && ./setup_linux.sh
# ============================================================

set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="setup_log_${TIMESTAMP}.txt"
VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
PYTHON_CMD="python3"

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
log "  Mental Health Risk Prediction System - Linux Setup"
log "  Started: $(date)"
log "  Log file: ${LOG_FILE} (in project root)"
log "============================================================"

# ── STEP 1: Check Python ────────────────────────────────────
header "STEP 1/5 - Checking Python installation"
if command -v $PYTHON_CMD &>/dev/null; then
    PY_VER=$($PYTHON_CMD --version 2>&1)
    success "Found: ${PY_VER}"
else
    err "python3 not found. Install it with:"
    err "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    err "  Fedora:        sudo dnf install python3"
    exit 1
fi

# Check python3-venv is available
if ! $PYTHON_CMD -c "import venv" &>/dev/null; then
    err "python3-venv module missing. Install it:"
    err "  Ubuntu/Debian: sudo apt install python3-venv"
    exit 1
fi
success "python3-venv module found."

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
