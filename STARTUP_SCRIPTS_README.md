# 🚀 STARTUP SCRIPTS - CROSS PLATFORM

This project includes automated startup scripts for all major operating systems to make installation and launching seamless.

## 📋 AVAILABLE SCRIPTS

1. **`start_windows.bat`** - For Windows systems
2. **`start_linux.sh`** - For Linux systems
3. **`start_macos.sh`** - For macOS systems

## 🎯 USAGE INSTRUCTIONS

### 🪟 Windows Users
```cmd
Double-click on start_windows.bat
```
or run in Command Prompt:
```cmd
start_windows.bat
```

### 🐧 Linux Users
```bash
chmod +x start_linux.sh
./start_linux.sh
```

### 🍎 macOS Users
```bash
chmod +x start_macos.sh
./start_macos.sh
```

## 🧠 WHAT THESE SCRIPTS DO

### ✅ PRE-REQUISITE CHECKS
- 🔍 Verifies Python 3.8+ installation
- 🔍 Confirms pip is available
- 🔍 Ensures required files exist (`requirements.txt` and `mental_health_ml_system.py`)

### 🛠️ AUTOMATIC SETUP
- 🌐 Creates virtual environment (isolated Python environment)
- 🎯 Upgrades pip to latest version
- 📦 Installs all required dependencies from `requirements.txt`
- 🔧 Verifies critical packages (Gradio, scikit-learn, pandas, numpy)
- 🧪 Performs final system validation

### 🚀 APPLICATION LAUNCH
- 🎯 Starts the Mental Health Prediction System
- 🌐 Makes application available at `http://127.0.0.1:7860`
- 📊 Shows real-time startup information
- 🛑 Provides clean shutdown instructions

## 🎨 FEATURES

### 🎯 Cross-Platform Compatibility
- Works on Windows 10/11, Linux (Ubuntu, CentOS, Fedora), and macOS
- Handles OS-specific differences automatically
- Provides appropriate error messages for each platform

### 🛡️ Robust Error Handling
- Comprehensive validation at each step
- Clear error messages with troubleshooting suggestions
- Graceful fallbacks when components fail
- Detailed logging of all operations

### 🎨 Enhanced User Experience
- Color-coded status messages (where supported)
- Progress indicators and status updates
- Friendly error messages with solutions
- Automatic retry mechanisms for common failures

### 🔧 Smart Dependency Management
- Virtual environment isolation
- Automatic package verification
- Selective reinstallation of failed components
- Comprehensive final system check

## 📋 REQUIREMENTS

### Minimum System Requirements
- **Python**: 3.8 or higher
- **RAM**: 512MB minimum (1GB recommended)
- **Storage**: 100MB free space
- **Internet**: Required for initial package installation

### Platform-Specific Notes

**Windows:**
- Python should be added to PATH during installation
- May require administrator privileges for some operations

**Linux:**
- May need to install python3-venv package:
  ```bash
  sudo apt install python3-venv  # Ubuntu/Debian
  sudo yum install python3-venv  # CentOS/RHEL
  ```

**macOS:**
- Recommended to install Python via Homebrew
- Xcode command line tools may be required

## 🆘 TROUBLESHOOTING

### Common Issues and Solutions

**1. Python Not Found**
- **Windows**: Reinstall Python and check "Add to PATH" option
- **Linux**: `sudo apt install python3 python3-pip`
- **macOS**: Install via Homebrew: `brew install python`

**2. Permission Denied (Linux/macOS)**
```bash
chmod +x start_linux.sh  # or start_macos.sh
```

**3. Port Already in Use**
- Change port in `mental_health_ml_system.py` or wait for port 7860 to be free

**4. Package Installation Failures**
- Check internet connection
- Try running script again (automatic retry included)
- Manually install packages: `pip install -r requirements.txt`

**5. Virtual Environment Issues**
- Script will continue without virtual environment if creation fails
- All packages will be installed globally as fallback

## 🎯 SUCCESS INDICATORS

When the script runs successfully, you'll see:
- ✅ Green checkmarks for completed steps
- 🚀 Launch message with URL
- Application running at `http://127.0.0.1:7860`
- No error messages in the console

## 🛑 STOPPING THE APPLICATION

- **Windows/Linux/macOS**: Press `Ctrl+C` in the terminal/console
- The script will handle graceful shutdown automatically

---

*These startup scripts ensure anyone can run your Mental Health Prediction System regardless of their operating system or technical expertise!*