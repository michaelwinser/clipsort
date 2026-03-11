@echo off
setlocal enabledelayedexpansion

set IMAGE_NAME=clipsort

:: Check that the Docker image exists
docker image inspect %IMAGE_NAME% >nul 2>&1
if errorlevel 1 (
    echo Error: Docker image '%IMAGE_NAME%' not found. >&2
    echo Build it first by running: build.bat >&2
    exit /b 1
)

:: Parse arguments to find the subcommand and positional paths
:: Usage: clipsort.bat organize [OPTIONS] INPUT_DIR OUTPUT_DIR
set SUBCOMMAND=
set INPUT_DIR=
set OUTPUT_DIR=
set POSITIONAL_COUNT=0
set FOUND_SUB=0
set "PASSTHROUGH="
set SKIP_NEXT=0

for %%a in (%*) do (
    if !SKIP_NEXT!==1 (
        set SKIP_NEXT=0
        set "PASSTHROUGH=!PASSTHROUGH! %%a"
    ) else if !FOUND_SUB!==0 (
        :: Looking for subcommand
        set "SUBCOMMAND=%%a"
        set "PASSTHROUGH=!PASSTHROUGH! %%a"
        set FOUND_SUB=1
    ) else (
        :: After subcommand: check if flag or positional
        set "ARG=%%a"
        if "!ARG:~0,1!"=="-" (
            set "PASSTHROUGH=!PASSTHROUGH! %%a"
            if "%%a"=="--report-file" set SKIP_NEXT=1
        ) else (
            set /a POSITIONAL_COUNT+=1
            if !POSITIONAL_COUNT!==1 (
                set "INPUT_DIR=%%a"
            ) else if !POSITIONAL_COUNT!==2 (
                set "OUTPUT_DIR=%%a"
            ) else (
                set "PASSTHROUGH=!PASSTHROUGH! %%a"
            )
        )
    )
)

:: If we have input/output dirs, resolve and mount them
if defined INPUT_DIR if defined OUTPUT_DIR (
    :: Resolve to absolute paths
    pushd "%INPUT_DIR%" 2>nul
    if errorlevel 1 (
        echo Error: Input directory '%INPUT_DIR%' does not exist. >&2
        exit /b 1
    )
    set "ABS_INPUT=%CD%"
    popd

    if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
    pushd "%OUTPUT_DIR%"
    set "ABS_OUTPUT=%CD%"
    popd

    docker run --rm -v "!ABS_INPUT!:/input:ro" -v "!ABS_OUTPUT!:/output" %IMAGE_NAME% !PASSTHROUGH! /input /output
) else (
    :: No path translation needed (e.g. --help, --version)
    docker run --rm %IMAGE_NAME% %*
)
