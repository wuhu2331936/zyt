"""给自动录制的演示片段加上片头/片尾，输出成品 mp4

用法：
  python scripts/make_final_video.py                 # 默认读桌面 zhiyaotong-demo.mp4
  python scripts/make_final_video.py --in 输入.mp4 --out 输出.mp4
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"
if not DESKTOP.exists():
    DESKTOP = Path(os.path.expanduser("~")) / "Desktop"

W, H = 390, 844
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑 Bold
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    cands = FONT_CANDIDATES if bold else FONT_CANDIDATES[1:]
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def gradient(bg_top: tuple[int, int, int], bg_bottom: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (W, H), bg_top)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(bg_top[i] + (bg_bottom[i] - bg_top[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return img


def center_text(d: ImageDraw.ImageDraw, y: int, text: str, f: ImageFont.FreeTypeFont, fill):
    bbox = d.textbbox((0, 0), text, font=f)
    w = bbox[2] - bbox[0]
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def make_intro() -> Path:
    img = gradient((59, 141, 255), (34, 193, 164))
    d = ImageDraw.Draw(img)
    # 药丸图标
    d.ellipse([W / 2 - 55, 250, W / 2 + 55, 360], fill=(255, 255, 255))
    center_text(d, 420, "智 药 通", font(52), (255, 255, 255))
    center_text(d, 500, "AI 老年人用药安全助手", font(22, False), (235, 250, 255))
    center_text(d, 560, "拍照识药 · 用药问答 · 相互作用 · 服药提醒", font(15, False), (220, 245, 255))
    center_text(d, 740, "功能演示", font(18, False), (255, 255, 255))
    p = Path(os.environ.get("TEMP", ".")) / "zyt_intro.png"
    img.save(p)
    return p


def make_outro(url: str) -> Path:
    img = gradient((34, 193, 164), (59, 141, 255))
    d = ImageDraw.Draw(img)
    center_text(d, 300, "感谢观看", font(40), (255, 255, 255))
    center_text(d, 380, "让 AI 陪伴每一位老人健康生活", font(18, False), (235, 250, 255))
    center_text(d, 470, "在线体验地址", font(16, False), (220, 245, 255))
    # 网址可能过长，按字符宽度折行
    f = font(14, False)
    max_chars = 22
    lines = [url[i : i + max_chars] for i in range(0, len(url), max_chars)]
    y = 505
    for ln in lines:
        center_text(d, y, ln, f, (255, 255, 255))
        y += 24
    center_text(d, 640, "GitHub: github.com/wuhu2331936/zyt", font(14, False), (235, 250, 255))
    center_text(d, 700, "Vue3 + FastAPI + 通义千问VL + DeepSeek", font(13, False), (220, 245, 255))
    p = Path(os.environ.get("TEMP", ".")) / "zyt_outro.png"
    img.save(p)
    return p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=str(DESKTOP / "zhiyaotong-demo.mp4"))
    ap.add_argument("--out", default=str(DESKTOP / "zhiyaotong-demo-final.mp4"))
    ap.add_argument("--url", default="zhiyaotong-330314-11-1509077553.sh.run.tcloudbase.com")
    args = ap.parse_args()

    from moviepy import ImageClip, VideoFileClip, concatenate_videoclips

    src = Path(args.src)
    if not src.exists():
        print("找不到源视频:", src)
        return

    intro = make_intro()
    outro = make_outro(args.url)

    clip = VideoFileClip(str(src))
    c_intro = ImageClip(str(intro)).with_duration(3.5)
    c_outro = ImageClip(str(outro)).with_duration(4)
    final = concatenate_videoclips([c_intro, clip, c_outro], method="compose")
    out = Path(args.out)
    final.write_videofile(
        str(out), fps=25, codec="libx264", audio=False,
        preset="medium", logger=None,
    )
    print("成品:", out, f"{out.stat().st_size/1024/1024:.2f} MB", f"{final.duration:.1f} 秒")


if __name__ == "__main__":
    main()
