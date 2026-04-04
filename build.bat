@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Background Remover Studio - Build

echo.
echo  Background Remover Studio - Build
echo  -----------------------------------
echo.

:: Find Python
call :find_python
if not defined PY_EXE (
    echo Python not found. Install Python 3.10+ from https://www.python.org
    echo.
    pause
    exit /b 1
)
echo Python: %PY_EXE%

:: Check version
"%PY_EXE%" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 (
    echo Python 3.10 or newer required.
    pause
    exit /b 1
)

:: Install PyInstaller
echo Installing PyInstaller...
"%PY_EXE%" -m pip install --quiet --upgrade pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    pause
    exit /b 1
)

:: Install requirements
echo Installing requirements...
"%PY_EXE%" -m pip install --quiet -r requirements.txt

:: Clean
if exist "build\BackgroundRemoverStudio" rmdir /s /q "build\BackgroundRemoverStudio" >nul 2>nul
if exist "dist\BackgroundRemoverStudio"  rmdir /s /q "dist\BackgroundRemoverStudio"  >nul 2>nul

:: Build main app
echo.
echo Building app (this takes a few minutes)...
echo.
"%PY_EXE%" -m PyInstaller main.spec --noconfirm --clean
set BUILD_EXIT=%ERRORLEVEL%

if %BUILD_EXIT% neq 0 (
    echo.
    echo Build failed ^(code %BUILD_EXIT%^).
    echo Common causes: missing package, antivirus blocking dist\, onnxruntime still running.
    echo.
    pause
    exit /b %BUILD_EXIT%
)

if not exist "dist\BackgroundRemoverStudio\BackgroundRemoverStudio.exe" (
    echo EXE not found after build.
    pause
    exit /b 1
)

:: Build start.exe
echo Building start.exe...
"%PY_EXE%" -m PyInstaller launcher.spec --noconfirm --clean
if exist "dist\start.exe" (
    copy /y "dist\start.exe" "start.exe" >nul 2>nul
    echo start.exe ready.
)

:: Copy docs into bundle
copy /y "README.md" "dist\BackgroundRemoverStudio\" >nul 2>nul
copy /y "LICENSE"   "dist\BackgroundRemoverStudio\" >nul 2>nul

:: Try Inno Setup
echo.
echo Looking for Inno Setup...
set "ISCC="
for /f "delims=" %%I in ('where ISCC 2^>nul') do if not defined ISCC set "ISCC=%%I"
if not defined ISCC (
    for /f "delims=" %%I in ('dir /b /s "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" 2^>nul') do if not defined ISCC set "ISCC=%%I"
)
if not defined ISCC (
    for /f "delims=" %%I in ('dir /b /s "%ProgramFiles%\Inno Setup 6\ISCC.exe" 2^>nul') do if not defined ISCC set "ISCC=%%I"
)

if defined ISCC (
    echo Compiling installer...
    "%ISCC%" "installer\setup.iss"
    if errorlevel 1 (
        echo Inno Setup failed. Falling back to portable zip.
        goto :portable_fallback
    )
    for /f "delims=" %%F in ('dir /b "BackgroundRemoverStudio_Setup.exe" 2^>nul') do (
        echo Installer ready: %%F
    )
    goto :done
)

echo Inno Setup not found. Download from https://jrsoftware.org/isdl.php
echo Falling back to portable zip.

:portable_fallback
echo Creating portable zip...
set "ZIP_NAME=BackgroundRemoverStudio-portable.zip"
if exist "%ZIP_NAME%" del /f /q "%ZIP_NAME%" >nul 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Compress-Archive -Path 'dist\BackgroundRemoverStudio\*' -DestinationPath '%ZIP_NAME%' -Force"
if exist "%ZIP_NAME%" (
    echo Portable zip ready: %ZIP_NAME%
) else (
    echo Could not create zip. Build is in dist\BackgroundRemoverStudio\
)

:done
echo.
echo  Done. AI model (~170 MB) downloads on first run.
echo.
pause
exit /b 0

:find_python
set "PY_EXE="
for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
    if not defined PY_EXE call :try_python "%%I"
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('where python 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('dir /b /s "%LocalAppData%\Programs\Python\Python3*\python.exe" 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('dir /b /s "%ProgramFiles%\Python3*\python.exe" 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
exit /b 0

:try_python
if defined PY_EXE exit /b 0
set "PY_CANDIDATE=%~1"
if not exist "%PY_CANDIDATE%" exit /b 0
"%PY_CANDIDATE%" -c "import sys" >nul 2>nul
if errorlevel 1 exit /b 0
set "PY_EXE=%PY_CANDIDATE%"
exit /b 0
