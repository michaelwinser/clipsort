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

:: Find the subcommand (first non-flag argument)
set SUBCOMMAND=
for %%a in (%*) do (
    set "ARG=%%a"
    if not "!ARG:~0,1!"=="-" (
        if not defined SUBCOMMAND set "SUBCOMMAND=%%a"
    )
)

:: Route by subcommand
if "!SUBCOMMAND!"=="organize" goto :MOUNT_DIRS
if "!SUBCOMMAND!"=="detect" goto :MOUNT_DIRS
if "!SUBCOMMAND!"=="split" goto :MOUNT_SPLIT
if "!SUBCOMMAND!"=="qr-generate" goto :QR_GENERATE
goto :PASSTHROUGH

:MOUNT_DIRS
:: organize/detect take: SUBCOMMAND [OPTIONS] INPUT_DIR OUTPUT_DIR
set INPUT_DIR=
set OUTPUT_DIR=
set POSITIONAL_COUNT=0
set FOUND_SUB=0
set SKIP_NEXT=0
set "PASSTHROUGH_ARGS="

for %%a in (%*) do (
    if !SKIP_NEXT!==1 (
        set SKIP_NEXT=0
        set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
    ) else if !FOUND_SUB!==0 (
        set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
        if "%%a"=="!SUBCOMMAND!" set FOUND_SUB=1
    ) else (
        set "ARG=%%a"
        if "!ARG:~0,1!"=="-" (
            set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
            if "%%a"=="--report-file" set SKIP_NEXT=1
            if "%%a"=="--scan-seconds" set SKIP_NEXT=1
            if "%%a"=="--sample-rate" set SKIP_NEXT=1
            if "%%a"=="--mode" set SKIP_NEXT=1
            if "%%a"=="--slate-buffer" set SKIP_NEXT=1
        ) else (
            set /a POSITIONAL_COUNT+=1
            if !POSITIONAL_COUNT!==1 (
                set "INPUT_DIR=%%a"
            ) else if !POSITIONAL_COUNT!==2 (
                set "OUTPUT_DIR=%%a"
            ) else (
                set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
            )
        )
    )
)

if not defined INPUT_DIR goto :PASSTHROUGH
if not defined OUTPUT_DIR goto :PASSTHROUGH

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

docker run --rm -v "!ABS_INPUT!:/input:ro" -v "!ABS_OUTPUT!:/output" %IMAGE_NAME% !PASSTHROUGH_ARGS! /input /output
goto :EOF

:MOUNT_SPLIT
:: split takes: SUBCOMMAND [OPTIONS] INPUT_FILE OUTPUT_DIR
set INPUT_FILE=
set OUTPUT_DIR=
set POSITIONAL_COUNT=0
set FOUND_SUB=0
set SKIP_NEXT=0
set "PASSTHROUGH_ARGS="

for %%a in (%*) do (
    if !SKIP_NEXT!==1 (
        set SKIP_NEXT=0
        set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
    ) else if !FOUND_SUB!==0 (
        set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
        if "%%a"=="!SUBCOMMAND!" set FOUND_SUB=1
    ) else (
        set "ARG=%%a"
        if "!ARG:~0,1!"=="-" (
            set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
            if "%%a"=="--mode" set SKIP_NEXT=1
            if "%%a"=="--sample-rate" set SKIP_NEXT=1
            if "%%a"=="--slate-buffer" set SKIP_NEXT=1
            if "%%a"=="--clap-threshold" set SKIP_NEXT=1
        ) else (
            set /a POSITIONAL_COUNT+=1
            if !POSITIONAL_COUNT!==1 (
                set "INPUT_FILE=%%a"
            ) else if !POSITIONAL_COUNT!==2 (
                set "OUTPUT_DIR=%%a"
            ) else (
                set "PASSTHROUGH_ARGS=!PASSTHROUGH_ARGS! %%a"
            )
        )
    )
)

if not defined INPUT_FILE goto :PASSTHROUGH
if not defined OUTPUT_DIR goto :PASSTHROUGH

:: Resolve input file parent directory and filename
for %%F in ("%INPUT_FILE%") do (
    set "ABS_INPUT_DIR=%%~dpF"
    set "INPUT_BASENAME=%%~nxF"
)

if not exist "%INPUT_FILE%" (
    echo Error: Input file '%INPUT_FILE%' does not exist. >&2
    exit /b 1
)

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
pushd "%OUTPUT_DIR%"
set "ABS_OUTPUT=%CD%"
popd

docker run --rm -v "!ABS_INPUT_DIR!:/input:ro" -v "!ABS_OUTPUT!:/output" %IMAGE_NAME% !PASSTHROUGH_ARGS! /input/!INPUT_BASENAME! /output
goto :EOF

:QR_GENERATE
:: No positional dir args — mount pwd as /work so output files land on host
docker run --rm -v "%CD%:/work" -w /work %IMAGE_NAME% %*
goto :EOF

:PASSTHROUGH
:: --help, --version, unknown commands
docker run --rm %IMAGE_NAME% %*
goto :EOF
