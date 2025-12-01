@echo off
REM Windows build script for Christmas Tree application
REM Usage: Run this script in Windows Command Prompt

setlocal enabledelayedexpansion

:menu
cls
echo ========================================
echo Christmas Tree Build Script
echo ========================================
echo.
echo Please select build type:
echo 1. Build executable (main.py)
echo 2. Build screensaver (screensaver.py)
echo 3. Clean all builds
echo 0. Exit
echo.
set /p choice="Enter your choice (0/1/2/3): "

if "%choice%"=="0" (
    echo Exiting...
    exit /b 0
) else if "%choice%"=="1" (
    set BUILD_SCREENSAVER=0
    set BUILD_TYPE=Executable
    goto build
) else if "%choice%"=="2" (
    set BUILD_SCREENSAVER=1
    set BUILD_TYPE=Screensaver
    goto build
) else if "%choice%"=="3" (
    goto clean_all
) else (
    echo.
    echo Invalid choice. Please select 0, 1, 2, or 3.
    timeout /t 2 >nul
    goto menu
)

:build
echo.
echo Selected: %BUILD_TYPE%
echo.

REM Check virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo.
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\activate.bat
    echo Finally run: pip install -r requirements.txt
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto menu
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo Step 1/3: Preparing build...
REM Only clean on first build to preserve previous builds
if "%FIRST_BUILD%"=="" (
    echo Cleaning old build cache...
    if exist "build" rmdir /s /q build
    set FIRST_BUILD=done
) else (
    echo Skipping cache cleanup to preserve previous builds...
)

echo Step 2/3: Building with PyInstaller...
pyinstaller build.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto menu
)

REM Step 3 depends on build type
if "%BUILD_SCREENSAVER%"=="1" (
    goto build_screensaver
) else (
    goto build_executable
)

:build_executable
echo Step 3/3: Verifying executable...
cd dist\Christmas_Tree
if exist "Christmas_Tree.exe" (
    echo.
    echo ========================================
    echo Build SUCCESS!
    echo ========================================
    echo.
    echo Executable location:
    echo %CD%\Christmas_Tree.exe
    echo.
    echo You can now run the application by double-clicking Christmas_Tree.exe
    echo.
) else (
    echo ERROR: Executable not found
    cd ..\..
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto menu
)
cd ..\..
goto complete

:build_screensaver
echo Step 3/3: Creating .scr file...
cd dist\Christmas_Tree_Screensaver
if exist "Christmas_Tree_Screensaver.exe" (
    move Christmas_Tree_Screensaver.exe Christmas_Tree.scr >nul
    echo Created Christmas_Tree.scr
) else (
    echo ERROR: Executable not found
    cd ..\..
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto menu
)

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
    echo 1. Copy the entire folder to a permanent location
    echo 2. Right-click Desktop - Personalize - Screen Saver
    echo 3. Browse and select Christmas_Tree.scr
    echo.
    echo IMPORTANT: Keep the entire folder intact!
    echo.
) else (
    echo ERROR: Failed to create .scr file
    cd ..\..
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto menu
)
cd ..\..
goto complete

:complete
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:clean_all
echo.
echo Cleaning all build files...
if exist "dist" (
    rmdir /s /q dist
    echo - Deleted dist folder
)
if exist "build" (
    rmdir /s /q build
    echo - Deleted build folder
)
set FIRST_BUILD=
echo.
echo Clean completed!
echo.
echo Press any key to return to menu...
pause >nul
goto menu
