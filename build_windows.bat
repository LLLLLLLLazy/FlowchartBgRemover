@echo off
setlocal

REM Windows 一键打包脚本（需已安装 Python 3.10+）
REM 输出 exe: dist\FlowchartBgRemover.exe

python -m pip install -U pip
python -m pip install -U pillow pyinstaller

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name FlowchartBgRemover ^
  qubeijing.py

echo.
echo 打包完成，exe 在 dist\FlowchartBgRemover.exe
pause
