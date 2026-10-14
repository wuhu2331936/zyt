"""生成 PWA 图标的辅助脚本。

使用前先 pip install Pillow:
    pip install Pillow

然后:
    python scripts/generate_pwa_icons.py

会自动从 icon.svg 生成 192x192、512x512、maskable 三个尺寸的 PNG。
比赛提交时务必把这 3 个 PNG 一起提交到 public/pwa-icons/。
"""

import os
import sys
from pathlib import Path

PUBLIC_DIR = Path(__file__).parent.parent / "public" / "pwa-icons"
SVG_PATH = PUBLIC_DIR / "icon.svg"

try:
    from PIL import Image
except ImportError:
    print("请先安装 Pillow: pip install Pillow")
    sys.exit(1)


def generate():
    if not SVG_PATH.exists():
        print(f"找不到源 SVG: {SVG_PATH}")
        sys.exit(1)

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    # 通过 cairosvg 把 SVG 转 PNG；如果没装就降级提示
    try:
        import cairosvg

        svg_bytes = SVG_PATH.read_bytes()
        sizes = {
            "pwa-192x192.png": 192,
            "pwa-512x512.png": 512,
            "pwa-maskable-512x512.png": 512,  # 需要在 safelist 里加 safe-zone
        }
        for name, size in sizes.items():
            out = PUBLIC_DIR / name
            cairosvg.svg2png(
                bytestring=svg_bytes,
                output_width=size,
                output_height=size,
                write_to=str(out),
            )
            print(f"  生成 {name} ({size}x{size})")
        print(f"\n完成！PNG 已存到 {PUBLIC_DIR}")
    except ImportError:
        # 降级方案：用 Pillow 直接画简化版（没有 SVG 也能生成纯色渐变图）
        import math

        for name, size, maskable in [
            ("pwa-192x192.png", 192, False),
            ("pwa-512x512.png", 512, False),
            ("pwa-maskable-512x512.png", 512, True),
        ]:
            img = Image.new("RGBA", (size, size), (25, 137, 250, 255))
            # 用渐变填充
            for y in range(size):
                t = y / size
                r = int(25 + (5 - 25) * t)
                g = int(137 + (112 - 137) * t)
                b = int(250 + (224 - 250) * t)
                for x in range(size):
                    img.putpixel((x, y), (r, g, b, 255))

            # 画一个白色药丸圆角矩形
            margin = int(size * 0.22)
            pw, ph = size - 2 * margin, int(size * 0.25)
            px = (size - pw) // 2
            py = (size - ph) // 2
            # 圆角矩形（用 mask）
            from PIL import ImageDraw

            draw = ImageDraw.Draw(img)
            radius = ph // 2
            # 左半圆白色
            draw.rounded_rectangle(
                [px, py, px + pw, py + ph],
                radius=radius,
                fill=(255, 255, 255, 255),
            )
            # 右半黄色
            draw.rounded_rectangle(
                [px + pw // 2, py, px + pw, py + ph],
                radius=radius,
                fill=(255, 210, 29, 255),
            )
            # 中线
            draw.rectangle(
                [px + pw // 2 - 2, py, px + pw // 2 + 2, py + ph],
                fill=(255, 255, 255, 255),
            )

            out = PUBLIC_DIR / name
            img.save(out, "PNG")
            print(f"  生成 {name}（Pillow 降级版 {size}x{size}）")

        print(f"\n完成！PNG 已存到 {PUBLIC_DIR}")
        print("提示：安装 cairosvg 后可获得更精致的 SVG 渲染版本：pip install cairosvg")


if __name__ == "__main__":
    generate()
