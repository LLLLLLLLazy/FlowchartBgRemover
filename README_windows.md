# 流程图去白底工具（Windows）

## 给最终用户（不会命令行）
1. 双击 `FlowchartBgRemover.exe`
2. 在界面里选择“单张图片”或“整个文件夹”
3. 选择输出文件夹
4. 直接点击“开始处理”

推荐模式：`dehalo`（可去掉文字和线条边缘白边）

## 给打包的人（生成 exe）

前置条件：
- Windows 10/11
- 已安装 Python 3.10+（安装时勾选 Add Python to PATH）

打包步骤：
1. 打开命令提示符，进入项目目录
2. 运行：

```bat
build_windows.bat
```

打包产物：
- `dist\\FlowchartBgRemover.exe`

## 命令行模式（可选）

```bat
python qubeijing.py --mode dehalo --input "D:\\input\\a.png" --output-dir "D:\\output"
```

模式说明：
- `dehalo`：推荐，去白底并清理白边
- `strict`：只删除纯白像素
- `near`：删除近白像素（可配合 `--threshold`）
