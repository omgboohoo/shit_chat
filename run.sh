#!/bin/bash

# ShitChat Linux Launcher Script
# Equivalent to run.bat for Windows

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}ShitChat Linux Launcher${NC}"
echo "================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if python3-venv is available
if ! python3 -m venv --help &> /dev/null; then
    echo -e "${RED}Error: python3-venv package is not installed${NC}"
    echo "On Debian/Ubuntu systems, you need to install the python3-venv package:"
    echo -e "${YELLOW}sudo apt install python3.12-venv${NC}"
    echo ""
    echo "Or for other Python versions:"
    echo -e "${YELLOW}sudo apt install python3-venv${NC}"
    echo ""
    echo "After installing, run this script again."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_PATH" ] || [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating it now...${NC}"
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Please ensure Python 3 is installed and accessible.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Install requirements (excluding llama-cpp-python for now)
echo -e "${YELLOW}Installing requirements...${NC}"
pip install --upgrade pip
pip install colorama requests tqdm

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install requirements. Please check your internet connection and try again.${NC}"
    exit 1
fi

# Check if Linux CUDA wheel exists in llama.cpp folder and install it
if ls "$SCRIPT_DIR/llama.cpp/llama_cpp_python-"*"linux_x86_64.whl" 1> /dev/null 2>&1; then
    echo -e "${GREEN}Found Linux CUDA wheel in llama.cpp folder, installing...${NC}"
    LINUX_WHEEL=$(ls "$SCRIPT_DIR/llama.cpp/llama_cpp_python-"*"linux_x86_64.whl" | head -1)
    
    # Install the wheel directly from llama.cpp folder
    pip install "$LINUX_WHEEL" --force-reinstall
else
    # Check if wheel exists in main directory
    if ls "$SCRIPT_DIR/llama_cpp_python-"*"linux_x86_64.whl" 1> /dev/null 2>&1; then
        echo -e "${GREEN}Found Linux CUDA wheel in main directory, installing...${NC}"
        MAIN_WHEEL=$(ls "$SCRIPT_DIR/llama_cpp_python-"*"linux_x86_64.whl" | head -1)
        pip install "$MAIN_WHEEL" --force-reinstall
    else
        echo -e "${YELLOW}No Linux CUDA wheel found in llama.cpp folder or main directory.${NC}"
        echo -e "${YELLOW}Options:${NC}"
        echo -e "${YELLOW}1. Build with CUDA: ./llama.cpp/build_linux.sh${NC}"
        echo -e "${YELLOW}2. Install from PyPI (no CUDA): pip install llama-cpp-python${NC}"
        echo ""
        read -p "Install from PyPI without CUDA? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Installing llama-cpp-python from PyPI (no CUDA)...${NC}"
            pip install llama-cpp-python
        else
            echo -e "${RED}Please build the Linux wheel first or install from PyPI.${NC}"
            exit 1
        fi
    fi
fi

# Run the application
echo -e "${GREEN}Starting ShitChat...${NC}"
echo "================================"
python3 "$SCRIPT_DIR/app.py"

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo -e "${RED}Application exited with an error. Press Enter to close...${NC}"
    read -r
fi
