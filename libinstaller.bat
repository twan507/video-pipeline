@echo off
chcp 65001 >nul
echo ============================================
echo   UV Package Manager - VBSE Video Pipeline
echo ============================================

:: Lay duong dan thu muc goc (chinh la thu muc chua file .bat nay)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
set "ROOT_DIR=%CD%"

:: Duong dan den Python embedded
set "PYTHON_EXE=%ROOT_DIR%\python\python.exe"

echo.
echo [INFO] Kiem tra Python...
echo   - Python: %PYTHON_EXE%

:: Kiem tra Python co ton tai khong
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Khong tim thay Python tai: %PYTHON_EXE%
    echo Vui long chay 'pyinstaller.bat' truoc.
    pause
    exit /b 1
)

:: Hien thi version Python
"%PYTHON_EXE%" --version
echo.

:: Kiem tra pip co san khong
echo [INFO] Kiem tra pip...
"%PYTHON_EXE%" -m pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] pip chua duoc cai dat
    echo [INFO] Dang cai dat pip...
    "%PYTHON_EXE%" -m ensurepip --upgrade
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Khong the cai dat pip
        pause
        exit /b 1
    )
)

:: Kiem tra UV da co san chua
echo.
echo [INFO] Kiem tra UV...
"%PYTHON_EXE%" -m uv --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] UV chua duoc cai dat!
    echo.
    echo Vui long chay 'pyinstaller.bat' truoc de cai dat Python + UV.
    echo Hoac cai thu cong: %PYTHON_EXE% -m pip install uv
    pause
    exit /b 1
)

:: Hien thi UV version
echo [OK] UV da san sang:
"%PYTHON_EXE%" -m uv --version

:: Kiem tra pyproject.toml
echo.
echo [INFO] Kiem tra pyproject.toml...
echo [DEBUG] ROOT_DIR: %ROOT_DIR%
if not exist "%ROOT_DIR%\pyproject.toml" (
    echo [ERROR] Khong tim thay file pyproject.toml tai: %ROOT_DIR%\pyproject.toml
    pause
    exit /b 1
)
echo [OK] Tim thay pyproject.toml

:: Cai dat dependencies tu pyproject.toml
echo.
echo ============================================
echo [INFO] Dang cai dat dependencies tu pyproject.toml...
echo [INFO] Cai dat truc tiep vao: %PYTHON_EXE%
echo ============================================

:: Chuyen ve thu muc goc de chay uv pip install
cd /d "%ROOT_DIR%"
"%PYTHON_EXE%" -m uv pip install --python "%PYTHON_EXE%" --system -e .

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Cai dat that bai voi ma loi: %ERRORLEVEL%
    pause
    exit /b 1
)

:: Don dep folder egg-info (duoc tao boi editable install)
echo.
echo [INFO] Don dep metadata folder...
if exist "%ROOT_DIR%\vbse_video.egg-info" (
    rmdir /s /q "%ROOT_DIR%\vbse_video.egg-info"
    echo [OK] Da xoa: vbse_video.egg-info
)

echo.
echo ============================================
echo   HOAN TAT! Da cai dat thanh cong.
echo ============================================
echo.
pause
