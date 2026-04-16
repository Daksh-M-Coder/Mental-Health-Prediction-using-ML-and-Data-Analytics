# ENV_SETUP — Environment Setup Instructions

Get the project running in 2 minutes on any OS.

---

## Windows

1. Open **File Explorer** → navigate to the `ENV_SETUP\` folder
2. Double-click **`setup_windows.bat`**
3. Watch the live output — every step is shown in the terminal
4. A timestamped log file (`setup_log_YYYYMMDD_HHMMSS.txt`) is saved in the **project root**

That's it. Once complete, activate manually in future:

```
venv\Scripts\activate.bat
python mental_health_ml_system.py
```

---

## Linux

```bash
cd ENV_SETUP
chmod +x setup_linux.sh
./setup_linux.sh
```

All `pip install` output is shown **live** and simultaneously saved to `setup_log_*.txt` in the project root.

Activate manually in future:

```bash
source venv/bin/activate
python mental_health_ml_system.py
```

---

## macOS

```bash
cd ENV_SETUP
chmod +x setup_macos.sh
./setup_macos.sh
```

The script auto-detects `python3` vs `python` and optionally checks for Homebrew. All output is tee'd live.

Activate manually in future:

```bash
source venv/bin/activate
python mental_health_ml_system.py
```

---

## What the scripts do

| Step | Action                                                     |
| ---- | ---------------------------------------------------------- |
| 1    | Check Python 3 is installed and print version              |
| 2    | Create `venv/` virtual environment (skip if exists)        |
| 3    | Activate the environment                                   |
| 4    | Upgrade pip (all output visible live)                      |
| 5    | Install `requirements.txt` (all output visible live)       |
| ✓    | Save full log to `setup_log_TIMESTAMP.txt` in project root |

---

## Log Files

Every run creates a timestamped log file in the **project root** (not inside ENV_SETUP). Useful for debugging if something fails. Example filename:

```
setup_log_20260310_225500.txt
```
