# 🎯 COMPLETE PROJECT SETUP GUIDE

## 📋 CROSS-PLATFORM STARTUP SCRIPTS

This repository includes automated startup scripts for all operating systems:

### 🪟 WINDOWS
**File**: `start_windows.bat`
**Usage**: Double-click the file or run `start_windows.bat` in Command Prompt

### 🐧 LINUX
**File**: `start_linux.sh`
**Usage**: 
```bash
chmod +x start_linux.sh
./start_linux.sh
```

### 🍎 MACOS
**File**: `start_macos.sh`
**Usage**:
```bash
chmod +x start_macos.sh
./start_macos.sh
```

## 🚀 WHAT THE SCRIPTS DO AUTOMATICALLY

1. **🔍 System Validation**: Checks Python, pip, and required files
2. **🔧 Environment Setup**: Creates virtual environment
3. **📦 Dependency Installation**: Installs all required packages
4. **🧪 System Verification**: Confirms all components work
5. **🚀 Application Launch**: Starts the web server at `http://127.0.0.1:7860`

## 🎯 QUICK START

### For Any Operating System:
1. **Download/Clone** the repository
2. **Navigate** to the project folder
3. **Run** the appropriate startup script for your OS
4. **Access** the application at `http://127.0.0.1:7860`

## 📊 SYSTEM REQUIREMENTS

- **Python**: 3.8 or higher
- **RAM**: 512MB minimum
- **Storage**: 100MB free space
- **Internet**: Required for initial setup

## 🆘 TROUBLESHOOTING

### If scripts don't work:
1. **Check Python installation**: `python --version` or `python3 --version`
2. **Verify current directory**: Ensure you're in the project folder
3. **Check file permissions**: Scripts need execute permissions (Linux/macOS)
4. **Manual installation**: Run `pip install -r requirements.txt` then `python mental_health_ml_system.py`

### Common Solutions:
- **Python not found**: Install from python.org or via package manager
- **Permission denied**: Use `chmod +x script_name.sh` on Linux/macOS
- **Port in use**: Application will show error with alternative port
- **Package errors**: Run script again or install manually

## 🎨 USER EXPERIENCE FEATURES

- **Color-coded feedback** (Windows: colored text, Linux/macOS: ANSI colors)
- **Progress indicators** at each step
- **Clear error messages** with solutions
- **Automatic retries** for common failures
- **Graceful degradation** when components fail

## 🛡️ ROBUST ERROR HANDLING

The scripts include comprehensive error handling:
- File existence verification
- Python version checking
- Package installation validation
- Virtual environment management
- Fallback mechanisms for failures

---

*These scripts make your Mental Health Prediction System accessible to users regardless of their technical background or operating system!*