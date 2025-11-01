@echo off
REM =========================================
REM 🚀 Starting Wikipedia Stream Pipeline
REM =========================================

REM Get the directory of this batch file and remove trailing backslash if present
set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo PROJECT_DIR is [%PROJECT_DIR%]

REM Step 1: Start backend services with Docker Compose
echo 🐳 Starting Kafka, Zookeeper, and Redis containers...
cd /d "%PROJECT_DIR%"
docker-compose up -d
timeout /t 10 >nul

REM Step 2: Check for required Python files and venv
if not exist "%PROJECT_DIR%\venv\Scripts\activate" (
    echo ERROR: venv not found in %PROJECT_DIR%\venv
    pause
    exit /b
)
if not exist "%PROJECT_DIR%\producer.py" (
    echo ERROR: producer.py not found in %PROJECT_DIR%
    pause
    exit /b
)
if not exist "%PROJECT_DIR%\processor.py" (
    echo ERROR: processor.py not found in %PROJECT_DIR%
    pause
    exit /b
)
if not exist "%PROJECT_DIR%\dashboard.py" (
    echo ERROR: dashboard.py not found in %PROJECT_DIR%
    pause
    exit /b
)

REM Step 3: Start Wikipedia Producer (streams edits to Kafka)
echo 📝 Starting Wikipedia Producer...
start cmd /k "cd /d "%PROJECT_DIR%" && call venv\Scripts\activate && python producer.py"
timeout /t 5 >nul

REM Step 4: Start Spark Processor (reads Kafka, writes to Redis)
echo 🔥 Starting Spark Processor...
start cmd /k "cd /d "%PROJECT_DIR%" && call venv\Scripts\activate && python processor.py"
timeout /t 5 >nul

REM Step 5: Start Dashboard (reads Redis, shows live chart)
echo 📊 Starting Dashboard...
start cmd /k "cd /d "%PROJECT_DIR%" && call venv\Scripts\activate && python dashboard.py"

REM Step 6: Open dashboard in browser
echo 🌐 Opening dashboard in browser...
start http://127.0.0.1:8050/

pause