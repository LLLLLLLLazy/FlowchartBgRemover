# 流程图去白底工具 (Flowchart Background Remover)

一个用于批量去除图片（尤其是流程图、白底黑字或带颜色线框图）白色背景的工具，提供直观的图形用户界面（GUI），同时也支持命令行（CLI）调用。

## 功能特性

- **三种去背景模式**：
  - `去白边(dehalo)`（推荐）：去除白底，并清理边缘白边，尤其适合线条和文字边缘。
  - `仅纯白(strict)`：仅删除绝对为纯白色的像素。
  - `近白色(near)`：删除近白像素，支持自定义检测阈值（0~255）。
- **批量处理**：支持单独选择图片，也支持选择整个文件夹批量自动化处理。
- **高分屏适配**：GUI 界面已适配 Windows 高 DPI 设置，显示更清晰。

## 运行与使用

### GUI 模式 (推荐普通用户使用)

您可以直接运行 Python 脚本启动图形界面：
```bash
python qubeijing.py
```
*(如果您已经打包成了 `FlowchartBgRemover.exe`，直接双击运行即可)*

### CLI 命令行模式

适合需要将本项目嵌入自动化脚本或批处理中的开发者：

```bash
# 基本用法
python qubeijing.py --mode dehalo --input "D:\input\a.png" --output-dir "D:\output"
```

你可以通过 `--help` 查看所有的参数配置：
```bash
python qubeijing.py --help
```

## 构建为可执行文件 (Windows)

如果需要将该程序打包给没有 Python 环境的 Windows 用户使用：

1. 确保系统安装了 Python 3.10+ 并已加入 PATH 环境变量。
2. 双击运行（或在终端执行）目录下的 `build_windows.bat`。
3. 执行成功后，在 `dist` 目录下将会生成单文件版的 `FlowchartBgRemover.exe`。

面向 Windows 极客与最终用户的详细帮助还可以查看：[README_windows.md](README_windows.md)
