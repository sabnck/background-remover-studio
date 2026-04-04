@echo off
setlocal EnableExtensions

:: Developer launcher — runs the setup assistant from source (no build required).
:: For end users: use the installer from GitHub Releases instead.

cd /d "%~dp0.."

call :find_python
if not defined PY_EXE (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName PresentationFramework; if([System.Windows.MessageBox]::Show('Background Remover Studio precisa do Python para abrir o assistente de instalacao.\n\nO instalador oficial do Python sera transferido e executado.\n\nContinuar?','Background Remover Studio',[System.Windows.MessageBoxButton]::YesNo,[System.Windows.MessageBoxImage]::Question) -eq 'Yes'){ exit 0 } else { exit 1 }"
    if errorlevel 1 exit /b 1
    call :install_python
    call :find_python
)

if not defined PY_EXE (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Background Remover Studio nao conseguiu localizar o Python.`nInstale o Python 3 manualmente e tente novamente.','Background Remover Studio',[System.Windows.MessageBoxButton]::OK,[System.Windows.MessageBoxImage]::Error) | Out-Null"
    exit /b 1
)

call :find_pythonw

:open_assistant
if defined PYW_EXE (
    start "" "%PYW_EXE%" "%~dp0..\src\setup_assistant.pyw"
) else (
    start "" "%PY_EXE%" "%~dp0..\src\setup_assistant.pyw"
)
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
    for /f "delims=" %%I in ('dir /b /s "%LocalAppData%\Programs\Python\Python*\python.exe" 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('dir /b /s "%ProgramFiles%\Python*\python.exe" 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
exit /b 0

:find_pythonw
set "PYW_EXE="
if defined PY_EXE (
    set "PYW_EXE=%PY_EXE:python.exe=pythonw.exe%"
    if exist "%PYW_EXE%" exit /b 0
)
set "PYW_EXE="
for /f "delims=" %%I in ('where pythonw 2^>nul') do (
    if not defined PYW_EXE set "PYW_EXE=%%I"
)
if not defined PYW_EXE (
    for /f "delims=" %%I in ('dir /b /s "%LocalAppData%\Programs\Python\Python*\pythonw.exe" 2^>nul') do (
        if not defined PYW_EXE set "PYW_EXE=%%I"
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

:install_python
set "PY_SETUP=%TEMP%\background_remover_python_setup.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe' -OutFile '%PY_SETUP%'" >nul 2>nul
if errorlevel 1 (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Nao foi possivel baixar o instalador do Python.`nVerifique a sua ligacao a internet e tente novamente.','Background Remover Studio',[System.Windows.MessageBoxButton]::OK,[System.Windows.MessageBoxImage]::Error) | Out-Null"
    exit /b 1
)
"%PY_SETUP%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1 InstallLauncherAllUsers=0 AssociateFiles=0
del "%PY_SETUP%" >nul 2>nul
timeout /t 3 >nul
exit /b 0
