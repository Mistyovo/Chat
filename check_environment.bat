@echo off
echo Checking build environment...
echo.

echo Testing Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    goto :error
)

echo Testing pip...
pip --version
if errorlevel 1 (
    echo ERROR: pip not found
    goto :error
)

echo Testing PyInstaller installation...
python -c "import PyInstaller; print('PyInstaller version:', PyInstaller.__version__)" 2>nul
if errorlevel 1 (
    echo PyInstaller not installed, installing now...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        goto :error
    )
) else (
    echo PyInstaller is already installed
)

echo.
echo Environment check completed successfully!
echo You can now run build_all.bat to build the programs.
goto :end

:error
echo.
echo Environment check failed!
echo Please fix the issues above before building.

:end
pause
