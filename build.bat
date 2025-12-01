@echo off
REM Windows screensaver build script
REM Usage: Run this script in Windows Command Prompt

setlocal enabledelayedexpansion

echo ========================================
echo Christmas Tree Screensaver Build Script
echo ========================================
echo.

REM Check virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\activate.bat
    echo Finally run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Set screensaver build flag
set BUILD_SCREENSAVER=1

echo Step 1/4: Cleaning old files...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo Step 2/4: Building with PyInstaller...
pyinstaller build.spec --clean

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Step 3/4: Creating .scr file...
cd dist\Christmas_Tree
if exist "Christmas_Tree.exe" (
    copy Christmas_Tree.exe Christmas_Tree.scr >nul
    echo Created Christmas_Tree.scr
) else (
    echo ERROR: Executable not found
    cd ..\..
    pause
    exit /b 1
)

echo Step 4/4: Verifying files...
if exist "Christmas_Tree.scr" (
    echo.
    echo ========================================
    echo Build SUCCESS!
    echo ========================================
    echo.
    echo Screensaver location:
    echo %CD%\Christmas_Tree.scr
    echo.
    echo Installation:
    echo 1. Right-click Christmas_Tree.scr
    echo 2. Select "Install"
    echo OR:
    echo 1. Copy Christmas_Tree.scr to C:\Windows\System32\
    echo 2. Right-click Desktop - Personalize - Screen Saver
    echo 3. Select "Christmas_Tree"
    echo.
    echo IMPORTANT: Keep the entire folder intact!
    echo.
) else (
    echo ERROR: Failed to create .scr file
    cd ..\..
    pause
    exit /b 1
)

cd ..\..
pause
