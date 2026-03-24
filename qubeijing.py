#!/usr/bin/env python3
"""
批量去除图片白色背景（输出透明 PNG）。

使用方式：
1) 直接双击 / 运行（无命令行参数）: 启动图形界面（推荐给普通用户）
2) 命令行模式: 传入参数进行批处理

示例：
  python3 qubeijing.py
  python3 qubeijing.py --mode strict --input 流程图.png --output-dir out
  python3 qubeijing.py --mode near --threshold 248 --input . --output-dir out
"""

from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path
from typing import Iterable

from PIL import Image

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def iter_images(path: Path) -> Iterable[Path]:
    if path.is_file():
        if path.suffix.lower() in SUPPORTED_EXTS:
            yield path
        return

    for p in sorted(path.iterdir()):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            yield p


def is_white(pixel: tuple[int, int, int, int], threshold: int, strict: bool) -> bool:
    r, g, b, a = pixel
    if a == 0:
        return False
    if strict:
        return r == 255 and g == 255 and b == 255
    return r >= threshold and g >= threshold and b >= threshold


def remove_all_white(img: Image.Image, threshold: int, strict: bool) -> Image.Image:
    rgba = img.convert("RGBA")
    pixels = list(rgba.getdata())
    out_pixels = []
    for r, g, b, a in pixels:
        if is_white((r, g, b, a), threshold, strict):
            out_pixels.append((r, g, b, 0))
        else:
            out_pixels.append((r, g, b, a))

    out = Image.new("RGBA", rgba.size)
    out.putdata(out_pixels)
    return out


def clamp_u8(x: int) -> int:
    if x < 0:
        return 0
    if x > 255:
        return 255
    return x


def remove_white_with_dehalo(img: Image.Image) -> Image.Image:
    """
    将白色背景转换为透明，并去除抗锯齿导致的白边。
    公式近似于 Color to Alpha(white)。
    """
    rgba = img.convert("RGBA")
    pixels = list(rgba.getdata())
    out_pixels = []

    for r, g, b, src_a in pixels:
        if src_a == 0:
            out_pixels.append((r, g, b, 0))
            continue

        calc_a = 255 - min(r, g, b)
        if calc_a <= 0:
            out_pixels.append((0, 0, 0, 0))
            continue

        base = 255 - calc_a
        nr = clamp_u8(((r - base) * 255) // calc_a)
        ng = clamp_u8(((g - base) * 255) // calc_a)
        nb = clamp_u8(((b - base) * 255) // calc_a)
        na = (calc_a * src_a) // 255
        out_pixels.append((nr, ng, nb, na))

    out = Image.new("RGBA", rgba.size)
    out.putdata(out_pixels)
    return out


def build_output_path(src: Path, output_dir: Path, suffix: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{src.stem}{suffix}.png"


def process_image(src_path: Path, output_dir: Path, mode: str, threshold: int, suffix: str) -> Path:
    with Image.open(src_path) as img:
        if mode == "dehalo":
            out = remove_white_with_dehalo(img)
        elif mode == "strict":
            out = remove_all_white(img, threshold, strict=True)
        else:
            out = remove_all_white(img, threshold, strict=False)

        out_path = build_output_path(src_path, output_dir, suffix)
        out.save(out_path, format="PNG")
        return out_path


def run_cli(args: argparse.Namespace) -> int:
    if not (0 <= args.threshold <= 255):
        print("--threshold 必须在 0~255 之间")
        return 2

    images = list(iter_images(args.input))
    if not images:
        print("未找到可处理的图片文件")
        return 1

    ok = 0
    for img_path in images:
        try:
            out_path = process_image(img_path, args.output_dir, args.mode, args.threshold, args.suffix)
            ok += 1
            print(f"[OK] {img_path.name} -> {out_path}")
        except Exception as e:
            print(f"[FAIL] {img_path}: {e}")

    print(f"完成：成功 {ok} 张 / 共 {len(images)} 张")
    return 0 if ok > 0 else 1


def run_gui() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    # 尝试开启 Windows 高分屏适配，解决模糊问题
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    class App:
        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.root.title("流程图去白底工具")
            self.root.geometry("720x520")
            self.root.minsize(680, 480)

            self.input_kind = tk.StringVar(value="file")
            self.input_path = tk.StringVar()
            self.output_dir = tk.StringVar()
            self.mode = tk.StringVar(value="去白边(dehalo)")
            self.threshold = tk.IntVar(value=245)
            self.suffix = tk.StringVar(value="_nobg")
            self.running = False

            self._build_ui()

        def _build_ui(self) -> None:
            outer = ttk.Frame(self.root, padding=12)
            outer.pack(fill="both", expand=True)

            title = ttk.Label(outer, text="流程图去白底", font=("Microsoft YaHei UI", 14, "bold"))
            title.pack(anchor="w")

            subtitle = ttk.Label(outer, text="1. 选择图片/文件夹  2. 选择输出目录  3. 点击开始处理")
            subtitle.pack(anchor="w", pady=(2, 10))

            input_box = ttk.LabelFrame(outer, text="输入")
            input_box.pack(fill="x", pady=4)

            row1 = ttk.Frame(input_box, padding=8)
            row1.pack(fill="x")
            ttk.Radiobutton(row1, text="单张图片", value="file", variable=self.input_kind).pack(side="left")
            ttk.Radiobutton(row1, text="整个文件夹", value="dir", variable=self.input_kind).pack(side="left", padx=(12, 0))

            row2 = ttk.Frame(input_box, padding=(8, 0, 8, 8))
            row2.pack(fill="x")
            ttk.Entry(row2, textvariable=self.input_path).pack(side="left", fill="x", expand=True)
            ttk.Button(row2, text="选择...", command=self.pick_input).pack(side="left", padx=(8, 0))

            output_box = ttk.LabelFrame(outer, text="输出")
            output_box.pack(fill="x", pady=4)

            row3 = ttk.Frame(output_box, padding=8)
            row3.pack(fill="x")
            ttk.Entry(row3, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
            ttk.Button(row3, text="选择...", command=self.pick_output).pack(side="left", padx=(8, 0))

            setting_box = ttk.LabelFrame(outer, text="处理参数")
            setting_box.pack(fill="x", pady=4)

            row4 = ttk.Frame(setting_box, padding=8)
            row4.pack(fill="x")
            ttk.Label(row4, text="模式").pack(side="left")
            mode_combo = ttk.Combobox(
                row4,
                textvariable=self.mode,
                values=["去白边(dehalo)", "仅纯白(strict)", "近白色(near)"],
                state="readonly",
                width=16,
            )
            mode_combo.pack(side="left", padx=(6, 18))
            mode_combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh_threshold_state())

            ttk.Label(row4, text="阈值(near模式)").pack(side="left")
            self.threshold_spin = ttk.Spinbox(row4, from_=0, to=255, textvariable=self.threshold, width=6)
            self.threshold_spin.pack(side="left", padx=(6, 18))

            ttk.Label(row4, text="输出后缀").pack(side="left")
            ttk.Entry(row4, textvariable=self.suffix, width=16).pack(side="left", padx=(6, 0))

            row5 = ttk.Frame(outer)
            row5.pack(fill="x", pady=(8, 4))
            self.start_btn = ttk.Button(row5, text="开始处理", command=self.start)
            self.start_btn.pack(side="left")

            help_text = (
                "模式说明: dehalo=去白边(推荐), strict=仅删纯白, near=删除近白。"
            )
            ttk.Label(row5, text=help_text).pack(side="left", padx=(12, 0))

            log_box = ttk.LabelFrame(outer, text="处理日志")
            log_box.pack(fill="both", expand=True, pady=(6, 0))
            self.log = tk.Text(log_box, height=12)
            self.log.pack(fill="both", expand=True, padx=8, pady=8)
            self.log.configure(state="disabled")

            self.refresh_threshold_state()

        def refresh_threshold_state(self) -> None:
            state = "normal" if "near" in self.mode.get() else "disabled"
            self.threshold_spin.configure(state=state)

        def add_log(self, text: str) -> None:
            self.log.configure(state="normal")
            self.log.insert("end", text + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
            self.root.update_idletasks()

        def pick_input(self) -> None:
            if self.input_kind.get() == "file":
                path = filedialog.askopenfilename(
                    title="选择图片",
                    filetypes=[
                        ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"),
                        ("所有文件", "*.*"),
                    ],
                )
            else:
                path = filedialog.askdirectory(title="选择图片文件夹")
            if path:
                self.input_path.set(path)

        def pick_output(self) -> None:
            path = filedialog.askdirectory(title="选择输出文件夹")
            if path:
                self.output_dir.set(path)

        def validate(self) -> tuple[Path, Path] | None:
            in_path = self.input_path.get().strip()
            out_path = self.output_dir.get().strip()
            if not in_path:
                messagebox.showerror("提示", "请先选择输入图片或文件夹")
                return None
            if not out_path:
                messagebox.showerror("提示", "请先选择输出文件夹")
                return None

            src = Path(in_path)
            dst = Path(out_path)
            if not src.exists():
                messagebox.showerror("提示", "输入路径不存在")
                return None

            if "near" in self.mode.get():
                t = self.threshold.get()
                if t < 0 or t > 255:
                    messagebox.showerror("提示", "阈值必须在 0~255")
                    return None
            return src, dst

        def start(self) -> None:
            if self.running:
                return
            validated = self.validate()
            if not validated:
                return

            src, dst = validated
            self.running = True
            self.start_btn.configure(state="disabled")
            self.add_log("开始处理...")

            thread = threading.Thread(target=self._worker, args=(src, dst), daemon=True)
            thread.start()

        def _worker(self, src: Path, dst: Path) -> None:
            try:
                images = list(iter_images(src))
                if not images:
                    self._finish("未找到可处理的图片文件")
                    return

                ok = 0
                for p in images:
                    try:
                        mode_str = "dehalo"
                        selected = self.mode.get()
                        if "strict" in selected:
                            mode_str = "strict"
                        elif "near" in selected:
                            mode_str = "near"

                        out = process_image(
                            p,
                            dst,
                            mode_str,
                            int(self.threshold.get()),
                            self.suffix.get().strip() or "_nobg",
                        )
                        ok += 1
                        self._log_safe(f"[OK] {p.name} -> {out}")
                    except Exception as e:
                        self._log_safe(f"[FAIL] {p}: {e}")

                self._finish(f"完成：成功 {ok} 张 / 共 {len(images)} 张")
            except Exception as e:
                self._finish(f"处理失败: {e}")

        def _log_safe(self, text: str) -> None:
            self.root.after(0, lambda: self.add_log(text))

        def _finish(self, text: str) -> None:
            def done() -> None:
                self.add_log(text)
                self.running = False
                self.start_btn.configure(state="normal")
                messagebox.showinfo("完成", text)

            self.root.after(0, done)

    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量去除图片白色背景")
    parser.add_argument("--input", type=Path, default=Path("."), help="输入文件或目录（默认当前目录）")
    parser.add_argument("--output-dir", type=Path, default=Path("transparent_out"), help="输出目录")
    parser.add_argument("--mode", choices=["dehalo", "strict", "near"], default="dehalo", help="去白模式")
    parser.add_argument("--threshold", type=int, default=245, help="近白阈值 0-255（仅 mode=near 生效）")
    parser.add_argument("--suffix", default="_nobg", help="输出文件名后缀")
    parser.add_argument("--gui", action="store_true", help="强制启动图形界面")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])

    # 无参数时默认启动图形界面，方便非技术用户双击使用
    if len(sys.argv) == 1 or args.gui:
        return run_gui()

    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
