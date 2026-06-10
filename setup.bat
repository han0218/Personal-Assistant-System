@echo off
chcp 65001 >nul

echo 安装依赖...
<YOUR_PYTHON_PATH>\python.exe -m pip install mem0ai fastembed

echo.
echo 检查 DEEPSEEK_API_KEY...
if "%DEEPSEEK_API_KEY%"=="" (
    echo 请先在 Windows 系统环境变量里设置 DEEPSEEK_API_KEY
) else (
    echo DEEPSEEK_API_KEY 已设置
)

pause
