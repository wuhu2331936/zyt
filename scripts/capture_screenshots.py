# -*- coding: utf-8 -*-
"""抓取智药通线上真机界面截图，供《作品介绍文档》第五章使用。

与 scripts/record_demo_video.py 走同一套流程（首页 → 拍照识药 → 识别结果 →
入箱 → 相互作用 → 语音问答 → 用药提醒），保证文档配图与演示视频完全一致。

用法:
    python scripts/capture_screenshots.py --base https://<云端地址> --out docs/screenshots
"""
import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_DEFAULT = "https://zhiyaotong-330314-11-1509077553.sh.run.tcloudbase.com"
MEDBOX = Path(tempfile.gettempdir()) / "test_medbox.png"


def ensure_medbox() -> Path:
    """生成/复用一张药盒测试图"""
    if MEDBOX.exists():
        return MEDBOX
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("缺少 Pillow，无法生成药盒测试图")
        sys.exit(1)
    font = None
    for p in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
        if Path(p).exists():
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
        btn.wait_for(state="visible", timeout=4000)
        btn.click(timeout=4000)
        print("  已通过 CloudBase 拦截页")
        page.wait_for_load_state("domcontentloaded")
        return True
    except Exception:
        return False


def seed_data(page) -> None:
    """预置演示数据：让药箱≥2种药（相互作用按钮才出现）、提醒有内容。"""
    page.evaluate(
        """() => {
          const meds = JSON.parse(localStorage.getItem('zhiyaotong:medicines')||'[]');
          if(!meds.find(m=>m.name&&m.name.includes('阿司匹林'))){
            meds.unshift({id:'demo_asp',name:'阿司匹林肠溶片',spec:'100mg*30片',source:'manual'});
            localStorage.setItem('zhiyaotong:medicines', JSON.stringify(meds));
          }
          const rems = JSON.parse(localStorage.getItem('zhiyaotong:reminders')||'[]');
          if(rems.length===0){
            const now=Date.now();
            rems.push(
              {id:'rem_demo1',medicineName:'苯磺酸氨氯地平片',time:'08:00',repeat:'daily',
               voice:'zh-CN-XiaoxiaoNeural',enabled:true,takenDate:null,createdAt:now},
              {id:'rem_demo2',medicineName:'阿托伐他汀钙片',time:'20:00',repeat:'daily',
               voice:'zh-CN-XiaoxiaoNeural',enabled:true,takenDate:null,createdAt:now}
            );
            localStorage.setItem('zhiyaotong:reminders', JSON.stringify(rems));
          }
        }"""
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT, help="站点地址")
    ap.add_argument("--out", default=str(ROOT / "docs" / "screenshots"), help="截图输出目录")
    args = ap.parse_args()

    box = ensure_medbox()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    shots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        def wait(ms: int) -> None:
            page.wait_for_timeout(ms)

        def shot(name: str) -> None:
            path = out / f"{name}.png"
            page.screenshot(path=str(path))
            shots.append(path.name)
            print("  截图 ->", path.name)

        def safe_click(loc, timeout=20000):
            loc.first.wait_for(state="visible", timeout=timeout)
            loc.first.evaluate("el => el.scrollIntoView({block: 'center'})")
            wait(600)
            loc.first.click(timeout=timeout)

        def tab(name: str) -> None:
            page.locator(".van-tabbar-item", has_text=name).first.click()
            wait(2200)

        def visit() -> None:
            page.goto(args.base, wait_until="domcontentloaded", timeout=90000)
            dismiss_interstitial(page)
            page.wait_for_load_state("networkidle", timeout=60000)

        # ---- 0. 首次进入：预置演示数据 ----
        print("[0] 打开首页并预置数据")
        visit()
        seed_data(page)
        page.reload(wait_until="domcontentloaded")
        wait(2500)

        # ---- 1. 首页 ----
        print("[1] 首页")
        wait(2000)
        page.mouse.wheel(0, 420)
        wait(1800)
        shot("home")

        # ---- 2. 拍照识药 - 上传页 ----
        print("[2] 拍照识药上传页")
        safe_click(page.get_by_text("拍照识药"))
        wait(1800)
        shot("scan-upload")

        # ---- 3. 识别结果（VL 读盒 + 说明书级补全）----
        print("[3] 识别结果页（等待 AI 识别与知识补全）")
        try:
            page.set_input_files("input[type=file]", str(box))
        except Exception as e:
            print("  上传失败:", e)
        add_btn = page.get_by_text("添加到我的用药清单").first
        try:
            add_btn.wait_for(state="visible", timeout=90000)
            print("  识别完成")
        except Exception:
            print("  识别未完成，页面文本:", page.locator("body").inner_text()[:150].replace("\n", " | "))
        wait(3000)
        page.mouse.wheel(0, 500)
        wait(2000)
        shot("scan-result")

        # ---- 4. 加入药箱 ----
        print("[4] 加入用药清单")
        try:
            add_btn.scroll_into_view_if_needed()
            safe_click(page.get_by_text("添加到我的用药清单"))
            wait(4000)
            n = page.evaluate("JSON.parse(localStorage.getItem('zhiyaotong:medicines')||'[]').length")
            print("  药箱药品数:", n)
        except Exception as e:
            print("  加入失败:", e)

        # ---- 5. 相互作用检查 ----
        print("[5] 相互作用检查")
        visit()
        wait(2500)
        try:
            btn = page.locator(".interaction-btn button").first
            btn.wait_for(state="visible", timeout=20000)
            btn.scroll_into_view_if_needed()
            wait(800)
            safe_click(page.locator(".interaction-btn button"))
            for _ in range(60):
                wait(1000)
                if page.locator(".van-dialog").count():
                    break
            wait(5000)
            shot("interaction")
            safe_click(page.get_by_text("知道了"))
            wait(1200)
        except Exception as e:
            print("  相互作用演示失败:", e)

        # ---- 6. 语音问答 ----
        print("[6] 语音问答")
        try:
            tab("问答")
            page.locator("input, textarea").first.fill("我在吃阿司匹林，关节疼能吃布洛芬吗？")
            wait(800)
            safe_click(page.get_by_text("发送"))
            for _ in range(60):
                wait(1000)
                if page.locator(".bubble").count() >= 2:
                    break
            wait(5000)
            page.mouse.wheel(0, 600)
            wait(1500)
            shot("voice-qa")
        except Exception as e:
            print("  问答演示失败:", e)

        # ---- 7. 用药提醒 ----
        print("[7] 用药提醒")
        try:
            tab("提醒")
            wait(1500)
            shot("reminder")
        except Exception as e:
            print("  提醒演示失败:", e)

        ctx.close()
        browser.close()

    print("\n完成，共", len(shots), "张:", ", ".join(shots))


if __name__ == "__main__":
    main()
