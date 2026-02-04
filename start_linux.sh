#!/bin/bash

# Mental Health Prediction System - Linux Startup Script
# Automatically installs dependencies and launches the application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================"
echo -e "🧠 MENTAL HEALTH RISK PREDICTION SYSTEM"
echo -e "======================================================${NC}"
echo "Starting Linux Setup and Launch Process..."
echo

# Function to print colored status messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
echo -e "${BLUE}🔍 Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Python $PYTHON_VERSION found"

# Check if pip is available
echo -e "${BLUE}🔍 Checking pip installation...${NC}"
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip not found. Please install pip."
    echo "Try: sudo apt install python3-pip (Ubuntu/Debian)"
    exit 1
fi
print_status "pip is available"

# Check if requirements.txt exists
echo -e "${BLUE}🔍 Checking requirements file...${NC}"
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in current directory."
    echo "Please ensure you're in the correct project folder."
    exit 1
fi
print_status "requirements.txt found"

# Check if main application file exists
echo -e "${BLUE}🔍 Checking main application file...${NC}"
if [ ! -f "mental_health_ml_system.py" ]; then
    print_error "mental_health_ml_system.py not found in current directory."
    echo "Please ensure you're in the correct project folder."
    exit 1
fi
print_status "Main application file found"

# Create virtual environment
echo -e "${BLUE}🔧 Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment."
        print_warning "Continuing without virtual environment..."
    else
        print_status "Virtual environment created"
        source venv/bin/activate
        if [ $? -ne 0 ]; then
            print_warning "Could not activate virtual environment, continuing..."
        else
            print_status "Virtual environment activated"
        fi
    fi
else
    print_status "Virtual environment already exists"
    source venv/bin/activate 2>/dev/null
fi

# Upgrade pip
echo -e "${BLUE}🔧 Upgrading pip...${NC}"
python3 -m pip install --upgrade pip --quiet
if [ $? -ne 0 ]; then
    print_warning "Failed to upgrade pip, continuing..."
else
    print_status "pip upgraded successfully"
fi

# Install required packages
echo -e "${BLUE}🔧 Installing Python dependencies...${NC}"
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    print_error "Failed to install required packages."
    echo "Please check your internet connection and try again."
    exit 1
fi
print_status "All dependencies installed successfully"

# Check for Gradio installation specifically
echo -e "${BLUE}🔍 Verifying Gradio installation...${NC}"
python3 -c "import gradio" &> /dev/null
if [ $? -ne 0 ]; then
    print_warning "Gradio not properly installed, attempting reinstallation..."
    pip install gradio --quiet
    if [ $? -ne 0 ]; then
        print_error "Failed to install Gradio."
        exit 1
    fi
fi
print_status "Gradio verified"

# Check for scikit-learn installation
echo -e "${BLUE}🔍 Verifying scikit-learn installation...${NC}"
python3 -c "import sklearn" &> /dev/null
if [ $? -ne 0 ]; then
    print_warning "scikit-learn not properly installed, attempting reinstallation..."
    pip install scikit-learn --quiet
    if [ $? -ne 0 ]; then
        print_error "Failed to install scikit-learn."
        exit 1
    fi
fi
print_status "scikit-learn verified"

# Final system check
echo -e "${BLUE}🔍 Performing final system check...${NC}"
python3 -c "import pandas, numpy, colorama" &> /dev/null
if [ $? -ne 0 ]; then
    print_warning "Some dependencies may be missing, attempting to install all..."
    pip install pandas numpy colorama --quiet
fi
print_status "System check completed"

# Launch the application
echo -e "${BLUE}======================================================"
echo -e "🚀 LAUNCHING MENTAL HEALTH PREDICTION SYSTEM"
echo -e "======================================================${NC}"
echo
echo "The application will be available at: http://127.0.0.1:7860"
echo "Press Ctrl+C to stop the application"
echo
echo "Starting server..."
echo

# Run the main application
python3 mental_health_ml_system.py

# Handle application exit
if [ $? -ne 0 ]; then
    echo
    print_error "Application encountered an error."
    echo "Please check the console output above for details."
    echo
    echo "Common solutions:"
    echo "1. Ensure all dependencies are installed"
    echo "2. Check if port 7860 is available"
    echo "3. Verify the mental_health_ml_system.py file exists"
    echo
else
    echo
    print_status "Application closed successfully."
fi

echo
echo "Press Enter to exit..."
read