@echo off
echo Building Chat Client and Server...
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to PATH
    pause
    exit /b 1
)

echo Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing/Upgrading PyInstaller...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo Error: Failed to install PyInstaller
    echo Try running as administrator or check your internet connection
    pause
    exit /b 1
)

echo.
echo Building Client...
python -m PyInstaller --onefile --windowed --name=ChatClient --clean --noconfirm client.py
if errorlevel 1 (
    echo Error: Failed to build client
    pause
    exit /b 1
)

echo.
echo Building Server...
python -m PyInstaller --onefile --console --name=ChatServer --clean --noconfirm server.py
if errorlevel 1 (
    echo Error: Failed to build server
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Client: dist\ChatClient.exe
echo Server: dist\ChatServer.exe
echo.
echo You can now distribute these files to users.
echo Remember to test both programs before distribution.
echo.
pause
