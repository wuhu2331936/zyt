"""自动录制智药通演示视频（手机尺寸竖屏）

用本机 Edge（无需下载 Chromium 内核）驱动页面，按脚本走完核心功能并录屏。
产物：桌面 zhiyaotong-demo.mp4

用法：
  1) 先启动后端（默认 http://127.0.0.1:8010，可用 --base 指定，例如云端地址）
  2) python scripts/record_demo_video.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE_DEFAULT = "http://127.0.0.1:8010"
DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"
if not DESKTOP.exists():
    DESKTOP = Path(os.path.expanduser("~")) / "Desktop"

# 测试用药盒图（若不存在则自动生成一张）
MEDBOX = Path(tempfile.gettempdir()) / "test_medbox.png"


def ensure_medbox() -> Path:
    if MEDBOX.exists():
        return MEDBOX
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("缺少 Pillow，无法生成药盒测试图")
        sys.exit(1)
    font = None
    for p in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
        if os.path.exists(p):
            font = p
            break
    img = Image.new("RGB", (900, 600), "white")
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(font, 64)
    f2 = ImageFont.truetype(font, 34)
    d.rectangle([20, 20, 880, 580], outline=(30, 90, 200), width=6)
    d.text((60, 90), "布洛芬缓释胶囊", font=f1, fill=(20, 20, 20))
    d.text((60, 200), "规格: 0.3g x 20粒", font=f2, fill=(60, 60, 60))
    d.text((60, 270), "适应症: 用于缓解轻至中度疼痛", font=f2, fill=(60, 60, 60))
    d.text((60, 340), "用法用量: 口服, 一次1粒, 一日2次", font=f2, fill=(60, 60, 60))
    d.text((60, 410), "生产企业: 中美天津史克制药有限公司", font=f2, fill=(60, 60, 60))
    d.text((60, 490), "禁忌: 活动性消化道溃疡患者禁用", font=f2, fill=(180, 30, 30))
    img.save(MEDBOX)
    return MEDBOX


def dismiss_interstitial(page) -> bool:
    """CloudBase 测试域名会先展示「页面访问提示」拦截页，需点「确定访问」进入。"""
    try:
        btn = page.get_by_text("确定访问").first
        btn.wait_for(state="visible", timeout=6000)
        btn.click(timeout=6000)
        print("已通过 CloudBase 拦截页")
        page.wait_for_load_state("domcontentloaded")
        return True
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT, help="站点地址")
    ap.add_argument("--out", default=str(DESKTOP / "zhiyaotong-demo.mp4"))
    args = ap.parse_args()

    box = ensure_medbox()
    tmp_vid = Path(tempfile.gettempdir()) / "zyt_video"
    if tmp_vid.exists():
        shutil.rmtree(tmp_vid, ignore_errors=True)
    tmp_vid.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            record_video_dir=str(tmp_vid),
            record_video_size={"width": 390, "height": 844},
        )
        page = ctx.new_page()
        page.goto(args.base, wait_until="domcontentloaded", timeout=90000)
        dismiss_interstitial(page)
        page.wait_for_load_state("networkidle", timeout=60000)

        # 预置一种常用药：保证后面「相互作用检查」按钮（≥2 种药才出现）一定可用
        page.evaluate(
            """() => {
              const key='zhiyaotong:medicines';
              const list=JSON.parse(localStorage.getItem(key)||'[]');
              if(!list.find(m=>m.name&&m.name.includes('阿司匹林'))){
                list.unshift({id:'demo_asp',name:'阿司匹林肠溶片',spec:'100mg*30片',source:'manual'});
                localStorage.setItem(key, JSON.stringify(list));
              }
            }"""
        )
        page.reload(wait_until="domcontentloaded")

        def wait(ms: int) -> None:
            page.wait_for_timeout(ms)

        # ---- 1. 首页 ----
        wait(2500)
        page.mouse.wheel(0, 420)
        wait(1800)

        def safe_click(loc, timeout=20000):
            """滚到视口中央再点击：避免被 fixed TabBar/NavBar 遮挡导致点击穿透"""
            loc.first.wait_for(state="visible", timeout=timeout)
            loc.first.evaluate("el => el.scrollIntoView({block: 'center'})")
            wait(600)
            loc.first.click(timeout=timeout)

        def tab(name: str) -> None:
            page.locator(".van-tabbar-item", has_text=name).first.click()
            wait(2200)

        # ---- 2. 拍照识药 ----
        safe_click(page.get_by_text("拍照识药"))
        wait(1500)
        try:
            page.set_input_files("input[type=file]", str(box))
        except Exception as e:
            print("上传控件定位失败:", e)
        # 识别 + 知识补全约 10-20 秒：等入箱按钮出现
        add_btn = page.get_by_text("添加到我的用药清单").first
        try:
            add_btn.wait_for(state="visible", timeout=90000)
            print("识别完成，入箱按钮已出现")
        except Exception:
            print("识别未完成，页面文本:", page.locator("body").inner_text()[:200].replace("\n", " | "))
        wait(3000)
        page.mouse.wheel(0, 500)
        wait(2000)

        # 加入药箱 → 详情页
        try:
            add_btn.scroll_into_view_if_needed()
            safe_click(page.get_by_text('添加到我的用药清单'))
            wait(4000)
            print("入箱后药品数:", page.evaluate("JSON.parse(localStorage.getItem('zhiyaotong:medicines')||'[]').length"))
            # 详情页下滑看完整说明
            for _ in range(4):
                page.mouse.wheel(0, 500)
                wait(1200)
        except Exception as e:
            print("加入药箱失败:", e)

        # ---- 3. 相互作用（先确保清单里有第二种药）----
        page.goto(args.base, wait_until="domcontentloaded", timeout=60000)
        dismiss_interstitial(page)
        page.evaluate(
            """() => {
              const key='zhiyaotong:medicines';
              const list=JSON.parse(localStorage.getItem(key)||'[]');
              if(!list.find(m=>m.name&&m.name.includes('阿司匹林'))){
                list.push({id:'demo_asp',name:'阿司匹林肠溶片',spec:'100mg*30片',source:'manual'});
                localStorage.setItem(key, JSON.stringify(list));
              }
            }"""
        )
        page.reload(wait_until="domcontentloaded")
        wait(2500)
        try:
            print("药品数:", page.evaluate("JSON.parse(localStorage.getItem('zhiyaotong:medicines')||'[]').length"))
            btn = page.locator(".interaction-btn button").first
            btn.wait_for(state="visible", timeout=20000)
            btn.scroll_into_view_if_needed()
            wait(800)
            safe_click(page.locator('.interaction-btn button'))
            for _ in range(60):
                wait(1000)
                if page.locator(".van-dialog").count():
                    break
            wait(6000)
            safe_click(page.get_by_text('知道了'))
            wait(1200)
        except Exception as e:
            print("相互作用演示失败:", e)

        # ---- 4. 语音问答 ----
        try:
            tab("问答")
            page.locator("input, textarea").first.fill("我在吃阿司匹林，关节疼能吃布洛芬吗？")
            wait(800)
            safe_click(page.get_by_text('发送'))
            for _ in range(60):
                wait(1000)
                if page.locator(".bubble").count() >= 2:
                    break
            wait(4000)
        except Exception as e:
            print("问答演示失败:", e)

        # ---- 5. 提醒：新增一条并展示 ----
        try:
            tab("提醒")
            safe_click(page.locator(".van-nav-bar__right"))
            wait(1800)
            page.locator("input, textarea").first.fill("苯磺酸氨氯地平片")
            wait(800)
            for t in ["确定", "保存", "确认"]:
                if page.get_by_text(t).count():
                    safe_click(page.get_by_text(t))
                    break
            wait(3000)
        except Exception as e:
            print("提醒演示失败:", e)

        ctx.close()
        browser.close()

    # 找到录制产物并转成 mp4
    vids = [f for f in tmp_vid.iterdir() if f.suffix == ".webm"]
    if not vids:
        print("未生成录屏文件")
        return
    src = max(vids, key=lambda f: f.stat().st_size)
    print("录屏:", src, f"{src.stat().st_size/1024/1024:.1f} MB")

    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = Path(args.out)
    cmd = [
        ffmpeg, "-y", "-i", str(src),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-vf", "scale=390:844",
        "-movflags", "+faststart",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("转码失败:", r.stderr[-500:])
        return
    print("视频已生成:", out, f"{out.stat().st_size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
