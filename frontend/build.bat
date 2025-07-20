@echo off
REM NutFlix Frontend Build Script for Windows
echo 🥜 Building NutFlix React Frontend...

REM Navigate to frontend directory
cd /d "%~dp0"

REM Check if Node.js is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js/npm not found. Please install Node.js first:
    echo    https://nodejs.org/
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
call npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

REM Build for production
echo 🔨 Building React app...
call npm run build

if %errorlevel% neq 0 (
    echo ❌ Build failed
    exit /b 1
)

echo ✅ Build complete!
echo.
echo 🚀 Your React app is ready!
echo    Start Flask backend: python web_service.py
echo    Access dashboard: http://localhost:5050
echo.
echo 🔧 For development:
echo    Start dev server: npm run dev
echo    Access dev mode: http://localhost:3000

pause
