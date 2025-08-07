@echo off
setlocal enabledelayedexpansion

REM Wakili Quick Docker Deployment Script for Windows

if "%1"=="" goto help

if "%1"=="prod" goto production
if "%1"=="dev" goto development
if "%1"=="stop" goto stop
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="cleanup" goto cleanup
if "%1"=="help" goto help

goto help

:production
echo [INFO] Deploying production services...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo [SUCCESS] Production services deployed successfully!
echo [INFO] Backend: http://localhost:8000
echo [INFO] Frontend: http://localhost:3000
echo [INFO] API Docs: http://localhost:8000/docs
goto end

:development
echo [INFO] Deploying development services...
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
echo [SUCCESS] Development services deployed successfully!
echo [INFO] Backend: http://localhost:8000 (with hot reload)
echo [INFO] Frontend: http://localhost:3000 (with hot reload)
echo [INFO] API Docs: http://localhost:8000/docs
goto end

:stop
echo [INFO] Stopping services...
docker-compose down
docker-compose -f docker-compose.dev.yml down
echo [SUCCESS] All services stopped
goto end

:logs
if "%2"=="dev" (
    docker-compose -f docker-compose.dev.yml logs -f
) else (
    docker-compose logs -f
)
goto end

:status
echo [INFO] Service Status:
echo.
echo Production Services:
docker-compose ps
echo.
echo Development Services:
docker-compose -f docker-compose.dev.yml ps
goto end

:cleanup
echo [INFO] Cleaning up Docker resources...
docker-compose down
docker-compose -f docker-compose.dev.yml down
docker system prune -f
docker volume prune -f
echo [SUCCESS] Cleanup completed
goto end

:help
echo Wakili Quick Docker Deployment Script
echo.
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   prod          Deploy production services
echo   dev           Deploy development services
echo   stop          Stop all services
echo   logs [dev]    View logs (add 'dev' for development services)
echo   status        Show service status
echo   cleanup       Clean up Docker resources
echo   help          Show this help message
echo.
echo Examples:
echo   %0 prod       # Deploy production
echo   %0 dev        # Deploy development
echo   %0 logs dev   # View development logs
goto end

:end
endlocal