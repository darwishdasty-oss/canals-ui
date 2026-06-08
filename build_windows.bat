@echo off
REM ============================================================
REM  Hydraulic Design Studio - Windows build script
REM ============================================================
REM  Produces a single HydraulicStudio.exe via PyInstaller.
REM  Run this on a Windows 10/11 machine with Python 3.11+ installed.
REM ============================================================

echo.
echo ============================================================
echo  Hydraulic Design Studio - Windows build
echo ============================================================
echo.

REM ---- 1. Locate Python ----
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    set PY=py -3
) else (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        set PY=python
    ) else (
        echo [ERROR] Python 3.11+ is required but was not found in PATH.
        echo         Download from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo [1/4] Using: %PY%
%PY% --version
echo.

REM ---- 2. Create / refresh a virtual environment ----
if not exist "venv" (
    echo [2/4] Creating virtual environment in .\venv ...
    %PY% -m venv venv
) else (
    echo [2/4] Reusing existing virtual environment
)
call venv\Scripts\activate.bat
echo.

REM ---- 3. Install dependencies ----
echo [3/4] Installing dependencies ...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
python -m pip install pywebview pyinstaller --quiet
echo       done.
echo.

REM ---- 4. Build the .exe ----
echo [4/4] Building HydraulicStudio.exe (this can take 3-5 minutes) ...
pyinstaller hydraulic.spec --noconfirm --clean
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller build failed.  See the output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  BUILD COMPLETE
echo ============================================================
echo.
echo  Output:  dist\HydraulicStudio.exe
echo.
echo  To run:  double-click  dist\HydraulicStudio.exe
echo.
echo  First run on a new machine may install the WebView2
echo  runtime if it isn't already present (Windows 10 1803+
echo  ships it; older versions auto-download from Microsoft).
echo ============================================================
echo.
pause
