@echo off
setlocal EnableDelayedExpansion

REM ================= CAU HINH DU AN =================
REM Su dung ban 3.12.10 (Ban 3.12 moi nhat co ho tro Embeddable Package)
set "PYTHON_VER=3.12.10"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VER%/python-%PYTHON_VER%-embed-amd64.zip"
set "ZIP_NAME=python-%PYTHON_VER%-embed-amd64.zip"

REM Lay thu muc goc (chinh la thu muc chua file .bat nay)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
set "ROOT_DIR=%CD%"
set "DIR_NAME=%ROOT_DIR%\python"

REM ================= BAT DAU XU LY =================
echo [1/6] Dang kiem tra moi truong...
echo [INFO] Thu muc goc: %ROOT_DIR%
echo [INFO] Python se duoc cai vao: %DIR_NAME%

if exist "%DIR_NAME%" (
    echo [WARNING] Thu muc '%DIR_NAME%' da ton tai.
    echo Vui long xoa no hoac doi ten truoc khi chay lai de tranh loi.
    pause
    exit /b
)

REM --------------------------------------------------
echo [2/6] Dang tai Python %PYTHON_VER% Embeddable...
cd /d "%ROOT_DIR%"
if not exist "%ZIP_NAME%" (
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%ZIP_NAME%'"
) else (
    echo [i] Da tim thay file zip, bo qua buoc tai.
)

REM --------------------------------------------------
echo [3/6] Dang giai nen vao '%DIR_NAME%'...
powershell -Command "Expand-Archive -Path '%ZIP_NAME%' -DestinationPath '%DIR_NAME%' -Force"

REM --------------------------------------------------
echo [4/6] DANG PATCH FILE ._pth (Mo khoa import site)...
REM Buoc nay dung PowerShell de tim file .pth va xoa dau # de kich hoat tinh nang cai thu vien sau nay
powershell -Command "$p = Get-ChildItem '%DIR_NAME%\python*._pth' | Select-Object -First 1; $c = Get-Content $p.FullName; $c -replace '#import site', 'import site' | Set-Content $p.FullName"

REM --------------------------------------------------
echo [5/6] Dang cai dat PIP (Cong cu quan ly goi)...
set "GET_PIP=get-pip.py"
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%GET_PIP%'"

REM Chay get-pip bang chinh python vua tai
"%DIR_NAME%\python.exe" "%GET_PIP%" --no-warn-script-location

REM Xoa file rac get-pip.py
del "%GET_PIP%"

REM --------------------------------------------------
echo [6/6] Dang cai dat UV (Package manager sieu nhanh)...
echo [INFO] UV se thay the pip lam cong cu quan ly goi chinh...
"%DIR_NAME%\python.exe" -m pip install uv --no-warn-script-location

REM Kiem tra UV da cai thanh cong chua
"%DIR_NAME%\python.exe" -m uv --version
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Cai dat UV that bai. Ban co the cai thu cong sau.
) else (
    echo [OK] UV da duoc cai dat thanh cong!
)

REM Xoa file zip da tai de don dep
if exist "%ZIP_NAME%" (
    echo [i] Dang don dep file zip...
    del "%ZIP_NAME%"
)

REM --------------------------------------------------
echo.
echo ========================================================
echo   CAI DAT HOAN TAT!
echo   Python %PYTHON_VER% da san sang tai: %DIR_NAME%
echo   Package Manager: UV (uv-pip)
echo   Buoc tiep: chay libinstaller.bat
echo ========================================================
echo.
pause
