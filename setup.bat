@echo off
chcp 65001 >nul
setlocal

set "PAS_ROOT=%~dp0"
set "REQ_FILE=%PAS_ROOT%requirements.txt"

if not "%PAS_PYTHON%"=="" (
    set "PYTHON_EXE=%PAS_PYTHON%"
) else (
    py -3.11 -c "import sys" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_EXE=py -3.11"
    ) else (
        python -c "import sys" >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON_EXE=python"
        ) else (
            echo 未找到 Python 3.11。请安装 Python 3.11 x64，或设置 PAS_PYTHON 为 python.exe 的完整路径。
            exit /b 1
        )
    )
)

echo 使用 Python: %PYTHON_EXE%
%PYTHON_EXE% --version
if errorlevel 1 exit /b 1

echo.
echo 安装依赖...
%PYTHON_EXE% -m pip install -r "%REQ_FILE%"
if errorlevel 1 exit /b 1

echo.
echo 检查 DEEPSEEK_API_KEY...
if "%DEEPSEEK_API_KEY%"=="" (
    echo 请先设置环境变量 DEEPSEEK_API_KEY，然后重新打开终端再运行本脚本。
    exit /b 1
)

echo DEEPSEEK_API_KEY 已设置。
echo 安装检查完成。可继续运行：%PYTHON_EXE% test_mem0.py
exit /b 0