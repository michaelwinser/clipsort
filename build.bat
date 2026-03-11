@echo off
setlocal

set IMAGE_NAME=clipsort

echo Building %IMAGE_NAME% Docker image...
docker build -t %IMAGE_NAME% .
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)
echo Done. Run clipsort.bat --help to get started.
