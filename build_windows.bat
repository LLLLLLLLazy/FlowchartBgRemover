@echo off
setlocal

REM Windows 一键打包脚本（使用虚拟环境纯净打包，有效减小体积）
REM 输出 exe: dist\FlowchartBgRemover.exe

REM 1. 创建并激活独立的虚拟环境，避免全局包的污染
python -m venv build_env
call build_env\Scripts\activate.bat

python -m pip install -U pip
python -m pip install -U pillow pyinstaller

REM 2. 打包并显式排除常见的大型无用库
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name FlowchartBgRemover ^
  --exclude-module numpy ^
  --exclude-module pandas ^
  --exclude-module matplotlib ^
  --exclude-module scipy ^
  --exclude-module PyQt5 ^
  --exclude-module PySide2 ^
  --exclude-module PyQt6 ^
  --exclude-module PySide6 ^
  qubeijing.py

REM 退出虚拟环境
call deactivate

echo.
echo 打包完成，exe 在 dist\FlowchartBgRemover.exe
pause
