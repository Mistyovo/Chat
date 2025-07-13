#!/bin/bash
echo "Building Chat Client and Server..."
echo

# Check Python installation
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python 3.7+ and add it to PATH"
    exit 1
fi

# Use python3 if available, otherwise use python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Check pip installation
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "Error: pip is not available"
    echo "Please install pip for your Python installation"
    exit 1
fi

echo "Installing/Upgrading PyInstaller..."
$PYTHON_CMD -m pip install --upgrade pyinstaller
if [ $? -ne 0 ]; then
    echo "Error: Failed to install PyInstaller"
    echo "Try running with sudo or check your internet connection"
    exit 1
fi

echo
echo "Building Client..."
$PYTHON_CMD -m PyInstaller --onefile --windowed --name=ChatClient --clean --noconfirm client.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to build client"
    exit 1
fi

echo
echo "Building Server..."
$PYTHON_CMD -m PyInstaller --onefile --console --name=ChatServer --clean --noconfirm server.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to build server"
    exit 1
fi

echo
echo "Build completed successfully!"
echo "Client: dist/ChatClient"
echo "Server: dist/ChatServer"
echo
echo "You can now distribute these files to users."
echo "Remember to test both programs before distribution."
