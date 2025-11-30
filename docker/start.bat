@echo off
REM QueryMind Docker Setup for Windows

echo 🚀 Starting QueryMind with Docker...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Build and start services
echo 📦 Building and starting services...
docker-compose up -d --build

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check service status
echo 📊 Service Status:
docker-compose ps

REM Show access information
echo.
echo ✅ QueryMind is ready!
echo 🌐 Frontend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🐘 Demo DB: localhost:5432 (querymind/querymind123)
echo.
echo To stop: docker-compose down
echo To view logs: docker-compose logs -f
pause