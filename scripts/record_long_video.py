"""录制省赛版演示视频：5-8 分钟、1080x1920、含 ≥2.5 分钟 AI 协同过程复现。

结构（对应 docs/demo-video-script.md）：
  1. 片头                    ~10s
  2. 第一幕 痛点背景          ~36s（3 张静态卡）
  3. 第二幕 拍照识药          ~75s（云端真机）
  4. 第三幕 相互作用检查      ~60s（云端真机）
  5. 第四幕 服药提醒          ~60s（云端真机）
  6. 第五幕 用药问答          ~60s（云端真机）
  7. 第六幕 AI 协同复现       ~155s（10 张编辑器风卡，打字机动效，全部真实材料）
  8. 第七幕 技术架构          ~40s（2 张卡）
  9. 片尾                    ~15s

用法：
  python scripts/record_long_video.py --base <云端地址> --out <输出.mp4>
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

MEDBOX = Path(tempfile.gettempdir()) / "test_medbox.png"
SLIDES_DIR = Path(tempfile.gettempdir()) / "zyt_long_slides"

# ---------------- 公共 CSS/JS ----------------

COMMON_HEAD = """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:540px; height:960px; overflow:hidden;
    font-family:"Microsoft YaHei","PingFang SC",sans-serif; }
  .reveal { opacity:0; transform:translateY(14px); transition:all .6s ease; }
  .reveal.show { opacity:1; transform:none; }
  .chip { display:inline-block; padding:6px 18px; border-radius:20px;
    font-size:17px; letter-spacing:2px; }
</style>
<script>
function play() {
  document.querySelectorAll('.reveal').forEach(el => {
    setTimeout(() => el.classList.add('show'), parseInt(el.dataset.after || '0'));
  });
  document.querySelectorAll('[data-type]').forEach(el => {
    const text = el.dataset.type;
    const speed = parseInt(el.dataset.speed || '26');
    setTimeout(() => {
      let j = 0;
      el.classList.add('typing');
      const t = setInterval(() => {
        el.textContent = text.slice(0, ++j);
        if (j >= text.length) { clearInterval(t); el.classList.remove('typing'); }
      }, speed);
    }, parseInt(el.dataset.after || '0'));
  });
}
</script>
</head><body onload="play()">
"""

CARD_CSS = """
  body { background:linear-gradient(160deg,#eaf3ff 0%,#f7fbff 55%,#e9fff6 100%);
    display:flex; flex-direction:column; }
  .topbar { padding:34px 44px 0; }
  .tagline { margin-top:26px; padding:0 44px; }
  .content { flex:1; display:flex; flex-direction:column;
    justify-content:center; padding:0 44px; }
  h1 { font-size:44px; color:#0d3b66; line-height:1.35; }
  h2 { font-size:30px; color:#12507e; line-height:1.5; }
  .big { font-size:88px; font-weight:800; color:#0b6ec9; line-height:1.1; }
  .mid { font-size:26px; color:#39566e; margin-top:16px; line-height:1.6; }
  .foot { padding:0 44px 40px; font-size:15px; color:#7d93a8; letter-spacing:1px; }
"""

DARK_CSS = """
  body { background:#161b22; color:#e6edf3; display:flex; flex-direction:column; }
  .head { padding:26px 36px 14px; border-bottom:1px solid #2d333b; }
  .step { color:#58a6ff; font-size:16px; letter-spacing:2px; margin-bottom:8px; }
  .title { font-size:24px; font-weight:700; color:#f0f6fc; }
  .chat { padding:20px 30px; flex:1; overflow:hidden; }
  .bubble { max-width:88%; padding:14px 18px; border-radius:14px;
    font-size:16.5px; line-height:1.65; margin-bottom:16px; white-space:pre-wrap;
    word-break:break-all; }
  .user { background:#1f3a5f; margin-left:auto; border:1px solid #2b527c; }
  .ai { background:#21262d; border:1px solid #30363d; }
  .who { font-size:13px; color:#8b949e; margin-bottom:6px; }
  .code { background:#0d1117; border:1px solid #30363d; border-radius:10px;
    padding:16px 18px; font-family:Consolas,"Courier New",monospace;
    font-size:14.5px; line-height:1.62; color:#c9d1d9; white-space:pre-wrap;
    word-break:break-all; margin:6px 0 16px; }
  .cm { color:#8b949e; } .kw { color:#ff7b72; } .st { color:#a5d6ff; }
  .fn { color:#d2a8ff; } .ok { color:#7ee787; } .warn { color:#ffa657; }
  .typing { border-right:2px solid #58a6ff; }
  .foot { padding:14px 36px 26px; font-size:14px; color:#8b949e;
    border-top:1px solid #2d333b; }
"""

# ---------------- 静态卡 ----------------

def card(body: str, css: str = CARD_CSS, foot: str = "智药通 · 传智杯 Vibe Coding 挑战赛") -> str:
    return COMMON_HEAD + "<style>" + css + "</style>" + body + \
        f'<div class="foot reveal" data-after="500">{foot}</div></body></html>'


def slide_title() -> str:
    return card("""
<div class="topbar reveal" data-after="200">
  <span class="chip" style="background:#0b6ec9;color:#fff">传智杯 Vibe Coding 挑战赛 · 参赛作品</span>
</div>
<div class="content">
  <div class="reveal" data-after="600" style="font-size:64px;font-weight:800;color:#0d3b66;letter-spacing:6px">智药通</div>
  <div class="reveal" data-after="1400" style="font-size:26px;color:#12507e;margin-top:14px">AI 老年人用药安全助手</div>
  <div class="reveal" data-after="2400" style="font-size:18px;color:#7d93a8;margin-top:34px;line-height:2">
    拍照识药 · 相互作用检查 · 用药问答 · 服药提醒<br>从 0 到 1，全程与 AI 协同开发
  </div>
</div>
""", foot="演示视频 · 全程约 7 分半")


def slide_pain(num: str, big: str, mid: str, sub: str) -> str:
    return card(f"""
<div class="topbar reveal" data-after="200">
  <span class="chip" style="background:#e8590c;color:#fff">为什么做这个项目 · {num}</span>
</div>
<div class="content">
  <div class="big reveal" data-after="600">{big}</div>
  <div class="mid reveal" data-after="1600">{mid}</div>
  <div class="reveal" data-after="2800" style="font-size:20px;color:#12507e;margin-top:30px">{sub}</div>
</div>
""", foot="第一幕 · 项目背景与痛点")


def ai_slide(step: str, title: str, body: str, foot: str) -> str:
    return card(f"""
<div class="head reveal" data-after="150">
  <div class="step">{step}</div>
  <div class="title">{title}</div>
</div>
{body}
""", css=DARK_CSS, foot=foot)


# ---------------- Playwright 交互 ----------------

def ensure_medbox() -> Path:
    if MEDBOX.exists():
        return MEDBOX
    from PIL import Image, ImageDraw, ImageFont
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


def build_slides() -> dict[str, str]:
    """生成全部静态页 HTML，返回 名称->路径。"""
    if SLIDES_DIR.exists():
        shutil.rmtree(SLIDES_DIR, ignore_errors=True)
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)

    pages: dict[str, str] = {}

    def put(name: str, html: str) -> str:
        f = SLIDES_DIR / f"{name}.html"
        f.write_text(html, encoding="utf-8")
        pages[name] = str(f)
        return str(f)

    # -- 片头 / 痛点 --
    put("title", slide_title())
    put("pain1", slide_pain("1 / 3", "2.6 亿", "中国 60 岁以上老年人，患慢病比例超过 70%",
                             "他们几乎每天都在和药打交道"))
    put("pain2", slide_pain("2 / 3", "30000 字+", "一个药盒说明书的平均字数，字号却只有 6 号",
                            "老人平均同时服用 3-5 种药"))
    put("pain3", slide_pain("3 / 3", "“饭前还是饭后？”", "看不清 · 读不懂 · 记不住 · 容易吃错",
                            "「智药通」要解决的问题"))

    # -- AI 协同（内容全部来自真实开发记录 docs/ai-prompts/ 与 git 历史）--
    prompt1 = ("用 FastAPI 写一个拍照识药接口：接收药盒图片（base64），"
               "调用 DashScope 的视觉模型识别，返回严格 JSON，"
               "字段固定为 name/brand/specification/manufacturer/dosage/precautions/confidence，"
               "不要输出任何多余文本。")
    code1 = (
        '<div class="code reveal" data-after="9000"><span class="cm"># AI 生成 · backend/app/services/qwen_vl.py（节选，真实代码）</span>\n'
        '<span class="kw">async def</span> <span class="fn">recognize_medicine</span>(image_b64: <span class="st">str</span>) -> <span class="st">dict</span>:\n'
        '    client = AsyncOpenAI(\n'
        '        api_key=settings.dashscope_api_key,\n'
        '        base_url=<span class="st">"https://dashscope.aliyuncs.com/compatible-mode/v1"</span>,\n'
        '    )\n'
        '    resp = <span class="kw">await</span> client.chat.completions.create(\n'
        '        model=<span class="st">"qwen3-vl-plus"</span>,\n'
        '        messages=[{<span class="st">"role"</span>: <span class="st">"user"</span>,\n'
        '            <span class="st">"content"</span>: [\n'
        '                {<span class="st">"type"</span>: <span class="st">"image_url"</span>,\n'
        '                 <span class="st">"image_url"</span>: {<span class="st">"url"</span>: <span class="st">f"data:image/png;base64,{image_b64}"</span>}},\n'
        '                {<span class="st">"type"</span>: <span class="st">"text"</span>, <span class="st">"text"</span>: RECOGNIZE_PROMPT},\n'
        '            ]}],\n'
        '    )\n'
        '    <span class="kw">return</span> <span class="fn">_safe_json_parse</span>(resp.choices[0].message.content)</div>'
    )
    put("ai1", ai_slide("第六幕 · 链条一（1/3）", "拍照识药服务的诞生 —— 我只写意图，AI 写实现", f"""
<div class="chat">
  <div class="who reveal" data-after="400">我的 Prompt（docs/ai-prompts/vl-recognition.md 快照）</div>
  <div class="bubble user" data-type="{prompt1}" data-speed="20" data-after="800"></div>
  <div class="who reveal" data-after="8600">AI 生成的核心实现（约 9 秒完成）</div>
  {code1}
</div>
""", "全程真实记录 · 对话快照已随仓库开源"))

    json_resp = ('<div class="code reveal" data-after="2500"><span class="ok">POST /api/medicine/recognize → 200 OK</span>\n'
                 '{\n'
                 '  <span class="st">"name"</span>: <span class="st">"布洛芬缓释胶囊"</span>,\n'
                 '  <span class="st">"specification"</span>: <span class="st">"0.3g×20粒"</span>,\n'
                 '  <span class="st">"manufacturer"</span>: <span class="st">"中美天津史克"</span>,\n'
                 '  <span class="st">"dosage"</span>: <span class="st">"口服，一次1粒，一日2次"</span>,\n'
                 '  <span class="st">"confidence"</span>: <span class="st">0.97</span>\n'
                 '}</div>')
    put("ai2", ai_slide("第六幕 · 链条一（2/3）", "Swagger 实测 —— 生成的接口直接能跑", f"""
<div class="chat">
  <div class="who reveal" data-after="400">AI 生成的接口经 Swagger /api/docs 实测</div>
  {json_resp}
  <div class="bubble ai reveal" data-after="6500">我负责<strong>验收</strong>：字段名、字段类型、置信度是否符合契约 —— 这就是「意图控制」：我定义边界（严格 JSON + 固定字段），AI 在边界内自由实现。</div>
</div>
""", "对话快照：docs/ai-prompts/vl-recognition.md"))

    prompt_bug = ("调用返回的文本是 ```json {…} ``` 这样带代码围栏的，"
                  "我直接 json.loads 就抛 JSONDecodeError，"
                  "3 张照片 2 张解析失败，怎么修？")
    put("ai3", ai_slide("第六幕 · 链条二（1/3）", "第一次联调就翻车 —— 我把 Bug 现场端给 AI", f"""
<div class="chat">
  <div class="who reveal" data-after="400">终端报错（真实现场）</div>
  <div class="code reveal" data-after="900"><span class="warn">json.decoder.JSONDecodeError:</span> Expecting value: line 1 column 1 (char 0)</div>
  <div class="who reveal" data-after="3500">我把报错原样贴给 AI，并描述现场</div>
  <div class="bubble user" data-type="{prompt_bug}" data-speed="20" data-after="5000"></div>
</div>
""", "报错现场 · 我的描述 · 全部真实"))

    put("ai4", ai_slide("第六幕 · 链条二（2/3）", "AI 给出两层修复 —— 我追问边界情况", """
<div class="chat">
  <div class="who reveal" data-after="400">AI 的修复建议</div>
  <div class="bubble ai reveal" data-after="900">① 提示词加硬约束：要求模型「直接输出 JSON，禁止任何代码围栏和解释文字」
② 服务端再加一层容错：新增 _safe_json_parse，容忍围栏和前后杂物</div>
  <div class="who reveal" data-after="5000">我的追问（引导 AI 考虑边界）</div>
  <div class="bubble user" data-type="兜底返回 None 会让前端白屏。改成解析失败时返回一个结构完全相同的降级对象，让页面还能展示「无法识别，请重拍」。" data-speed="20" data-after="6500"></div>
</div>
""", "关键点：AI 修 Bug，我负责发现 Bug、描述现场、追问边界"))

    parse_code = (
        '<div class="code reveal" data-after="1200"><span class="cm"># 真实代码 · backend/app/services/qwen_vl.py:196</span>\n'
        '<span class="kw">def</span> <span class="fn">_safe_json_parse</span>(text: <span class="st">str</span>) -> <span class="st">dict</span>:\n'
        '    <span class="st">"""尝试从模型输出里抠出 JSON（容忍 ```json 包裹、前后杂物）"""</span>\n'
        '    text = text.strip()\n'
        '    <span class="cm"># 去掉代码块围栏</span>\n'
        '    <span class="kw">if</span> text.startswith(<span class="st">"```"</span>):\n'
        '        lines = text.splitlines()\n'
        '        text = <span class="st">"\\n"</span>.join(\n'
        '            line <span class="kw">for</span> line <span class="kw">in</span> lines <span class="kw">if not</span> line.strip().startswith(<span class="st">"```"</span>)\n'
        '        )\n'
        '    <span class="cm"># 直接解析 → 失败则用正则抠 {} → 再失败返回结构化降级对象</span></div>'
    )
    put("ai5", ai_slide("第六幕 · 链条二（3/3）", "这个函数现在守护着所有大模型返回的解析", f"""
<div class="chat">
  {parse_code}
  <div class="bubble ai reveal" data-after="9500">修复后实测：<strong>3 张照片全部解析成功</strong>。这层容错后来被复用到识药、相互作用、问答三个模块。</div>
</div>
""", "git 提交 a3d395e 可追溯"))

    put("ai6", ai_slide("第六幕 · 链条三（1/4）", "更顽固的 Bug：云端相互作用接口 500", f"""
<div class="chat">
  <div class="who reveal" data-after="400">云端日志（部署后才暴露，本地从未复现）</div>
  <div class="code reveal" data-after="900"><span class="warn">RuntimeError:</span> ChromaDB not installed. Run: pip install chromadb
<span class="warn">INFO:</span> 500 Internal Server Error · POST /api/interaction/check</div>
  <div class="who reveal" data-after="3500">我的提问（截图存档于对话记录）</div>
  <div class="bubble user" data-type="云端没装 chromadb，check_interactions 抛 RuntimeError 导致 500。但代码里明明写了 except FileNotFoundError，为什么没兜住？怎样设计才不会漏？" data-speed="20" data-after="5000"></div>
</div>
""", "真实事故 · 提交 1c31852 修复"))

    diff_code = (
        '<div class="code reveal" data-after="1200"><span class="cm"># git show 1c31852 · backend/app/services/rag.py（真实 diff）</span>\n'
        '<span class="warn">-    except FileNotFoundError as e:</span>\n'
        '<span class="warn">-        # 向量库未构建，用 DeepSeek 内置知识兜底</span>\n'
        '<span class="ok">+    if not getattr(settings, "rag_enabled", True):</span>\n'
        '<span class="ok">+        return await deepseek.analyze_interactions(medicines)</span>\n'
        '<span class="ok">+    except Exception as e:</span>\n'
        '<span class="ok">+        # 依赖未安装(RuntimeError)/库未构建(FileNotFoundError)……\n'
        '+        # 任何一种都必须回落 LLM，绝不能把异常抛给上层导致 500</span>\n'
        '<span class="ok">+        return await deepseek.analyze_interactions(medicines)</span></div>'
    )
    put("ai7", ai_slide("第六幕 · 链条三（2/4）", "AI 定位根因：异常类型不只有一种 —— 兜底要兜「所有」", f"""
<div class="chat">
  <div class="who reveal" data-after="400">AI 的分析 + 修复 diff</div>
  {diff_code}
</div>
""", "同时新增 settings.rag_enabled 配置开关，云端未装向量库时直接短路"))

    put("ai8", ai_slide("第六幕 · 链条三（3/4）", "修复后云端实测 —— 降级不失效", """
<div class="chat">
  <div class="who reveal" data-after="400">POST /api/interaction/check（云端真机）</div>
  <div class="bubble ai reveal" data-after="900" style="border-left:5px solid #ffa657">
    <strong style="color:#ffa657">【较严重】阿司匹林肠溶片 + 布洛芬缓释胶囊</strong><br><br>
    布洛芬竞争性抑制 COX-1，削弱阿司匹林抗血小板作用，并增加胃出血风险。<br><br>
    建议：两药错开服用，或改用对乙酰氨基酚代替布洛芬。
  </div>
  <div class="bubble ai reveal" data-after="6000">这就是「<strong>降级不失效</strong>」设计：向量库在就检索增强，不在就用大模型内置知识 —— 功能永远可用。</div>
</div>
""", "这一幕完整对应视频第三幕的功能效果"))

    put("ai9", ai_slide("第六幕 · 链条三（4/4）", "语音 500 之谜：依赖版本锁死 + 兜底设计", f"""
<div class="chat">
  <div class="who reveal" data-after="400">又一起：Edge-TTS 被微软 403 → 接口 500</div>
  <div class="code reveal" data-after="900"><span class="warn">requirements.txt</span>   edge-tts==6.1.18   <span class="cm"># 签名算法过期，必 403</span>
<span class="ok">修复后</span>              edge-tts&gt;=7.3.1,&lt;8  <span class="cm"># 实测 200 OK，21456 字节音频</span></div>
  <div class="bubble ai reveal" data-after="5500">我的设计原则（引导 AI 实现）：<strong>TTS 不可用绝不能报错吓到老人</strong> —— 后端返回 204，前端静默降级到浏览器内置语音。现在即使语音服务再挂，界面也干干净净。</div>
</div>
""", "git 提交 a41d3c3 · 前端仍有浏览器语音兜底"))

    log_code = (
        '<div class="code reveal" data-after="1200"><span class="cm">$ git log --oneline（55 次细粒度提交，节选）</span>\n'
        '<span class="st">a3d395e</span> feat(backend): add 4 core APIs for stage 2\n'
        '<span class="st">40d744d</span> feat(backend): add RAG vector store + AI integration docs\n'
        '<span class="st">1c31852</span> fix: 修复相互作用 500、提醒失效、详细说明丢失等缺陷\n'
        '<span class="st">04f33da</span> fix(qa): 问答气泡渲染 Markdown；TTS 静默降级\n'
        '<span class="st">a41d3c3</span> fix(tts): 升级 edge-tts 7.3.1 修复微软 403\n'
        '<span class="st">089b3e1</span> docs(intro): 作品介绍配图更换为线上真机截图\n'
        '<span class="st">d20209b</span> chore: 后端版本号对齐 v0.4.0</div>'
    )
    put("ai10", ai_slide("第六幕 · 小结", "AI 协同工作流：我负责意图与验收，AI 负责实现与修复", f"""
<div class="chat">
  {log_code}
  <div class="bubble ai reveal" data-after="9000">3 条完整 Prompt 链快照已随仓库开源：<strong>docs/ai-prompts/</strong>（vl-recognition / rag-interaction / voice-qa），评委可一键复现。</div>
</div>
""", "过程可复现 · 演进链路完整 · Git + Prompt 双留痕"))

    # -- 架构卡 --
    put("arch1", card("""
<div class="topbar reveal" data-after="200">
  <span class="chip" style="background:#0b6ec9;color:#fff">第七幕 · 技术架构（1/2）</span>
</div>
<div class="content" style="gap:18px">
  <div class="reveal" data-after="500" style="background:#fff;border-radius:16px;padding:22px 26px;box-shadow:0 2px 10px rgba(13,71,161,.08)">
    <div style="font-size:21px;font-weight:700;color:#0d3b66">前端 · 移动端优先</div>
    <div style="font-size:17px;color:#39566e;margin-top:8px;line-height:1.7">Vue3 + Vite + Vant4 + Pinia<br>PWA 离线缓存（可添加到主屏幕）</div>
  </div>
  <div class="reveal" data-after="1600" style="background:#fff;border-radius:16px;padding:22px 26px;box-shadow:0 2px 10px rgba(13,71,161,.08)">
    <div style="font-size:21px;font-weight:700;color:#0d3b66">后端 · 异步服务</div>
    <div style="font-size:17px;color:#39566e;margin-top:8px;line-height:1.7">FastAPI + Pydantic 校验 + Swagger 自动文档<br>单端口托管 SPA，部署一份即全站</div>
  </div>
  <div class="reveal" data-after="2700" style="background:#fff;border-radius:16px;padding:22px 26px;box-shadow:0 2px 10px rgba(13,71,161,.08)">
    <div style="font-size:21px;font-weight:700;color:#0d3b66">AI 能力层</div>
    <div style="font-size:17px;color:#39566e;margin-top:8px;line-height:1.7">Qwen3-VL 拍照识药 · DeepSeek 问答与相互作用<br>Edge-TTS 语音 · ChromaDB RAG（自动降级）</div>
  </div>
</div>
""", foot="全部 Key 走服务端转发，不落前端"))
    put("arch2", card("""
<div class="topbar reveal" data-after="200">
  <span class="chip" style="background:#0b6ec9;color:#fff">第七幕 · 技术架构（2/2）</span>
</div>
<div class="content" style="gap:18px">
  <div class="reveal" data-after="500" style="background:#fff;border-radius:16px;padding:24px 28px;box-shadow:0 2px 10px rgba(13,71,161,.08)">
    <div style="font-size:21px;font-weight:700;color:#0d3b66">真实上线 · 不是本地演示</div>
    <div style="font-size:17px;color:#39566e;margin-top:10px;line-height:1.8">腾讯云 CloudBase 云托管（国内）<br>Git 推送 → 自动构建部署 · 电脑关机也能用<br>演示视频全程使用公网地址真机录制</div>
  </div>
  <div class="reveal" data-after="1800" style="background:#fff;border-radius:16px;padding:24px 28px;box-shadow:0 2px 10px rgba(13,71,161,.08)">
    <div style="font-size:21px;font-weight:700;color:#0d3b66">可复现性保障</div>
    <div style="font-size:17px;color:#39566e;margin-top:10px;line-height:1.8">README 十分钟极速复现指南<br>.env.example 环境变量模板 + 一键启动脚本<br>无 Key 自动进入演示模式，全流程可体验</div>
  </div>
</div>
""", foot="工程质量 · 模块清晰 · 无 Key 泄漏（安检脚本随包）"))

    put("outro", card("""
<div class="topbar reveal" data-after="200">
  <span class="chip" style="background:#0b6ec9;color:#fff">谢谢观看</span>
</div>
<div class="content" style="align-items:center;text-align:center">
  <div class="reveal" data-after="400" style="font-size:56px;font-weight:800;color:#0d3b66;letter-spacing:5px">智药通</div>
  <div class="reveal" data-after="1200" style="font-size:22px;color:#12507e;margin-top:12px">让每一位老人看得懂药、吃得对药</div>
  <div class="reveal" data-after="2400" style="margin-top:40px;background:#fff;border-radius:16px;padding:20px 26px;font-size:14.5px;color:#39566e;line-height:2;text-align:left;word-break:break-all">
    在线体验：<br>zhiyaotong-330314-11-1509077553.sh.run.tcloudbase.com<br>GitHub：wuhu2331936/zyt（Public）<br>AI Prompt 快照：docs/ai-prompts/
  </div>
</div>
""", foot="传智杯 Vibe Coding 挑战赛 · 个人赛参赛作品"))

    return pages


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT, help="站点地址")
    ap.add_argument("--out", default=str(DESKTOP / "zhiyaotong-demo-8min.mp4"))
    args = ap.parse_args()

    box = ensure_medbox()
    pages = build_slides()

    tmp_vid = Path(tempfile.gettempdir()) / "zyt_video_long"
    if tmp_vid.exists():
        shutil.rmtree(tmp_vid, ignore_errors=True)
    tmp_vid.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    def goto_file(page, path: str, hold_ms: int) -> None:
        page.goto(Path(path).as_uri(), wait_until="load", timeout=30000)
        page.wait_for_timeout(hold_ms)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(
            viewport={"width": 540, "height": 960},
            device_scale_factor=2,
            record_video_dir=str(tmp_vid),
            record_video_size={"width": 540, "height": 960},
        )
        page = ctx.new_page()

        def wait(ms: int) -> None:
            page.wait_for_timeout(ms)

        def safe_click(loc, timeout=20000) -> None:
            loc.first.wait_for(state="visible", timeout=timeout)
            loc.first.evaluate("el => el.scrollIntoView({block: 'center'})")
            wait(500)
            loc.first.click(timeout=timeout)

        def open_site() -> None:
            page.goto(args.base, wait_until="domcontentloaded", timeout=90000)
            try:
                btn = page.get_by_text("确定访问").first
                btn.wait_for(state="visible", timeout=6000)
                btn.click(timeout=6000)
                print("已通过 CloudBase 拦截页")
            except Exception:
                pass
            page.wait_for_load_state("networkidle", timeout=60000)

        def tab(name: str) -> None:
            page.locator(".van-tabbar-item", has_text=name).first.click()
            wait(2200)

        def seed_second_med() -> None:
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

        # ============ 1. 片头 ============
        print("[1/9] 片头")
        goto_file(page, pages["title"], 10000)

        # ============ 2. 痛点 ============
        print("[2/9] 痛点")
        goto_file(page, pages["pain1"], 12000)
        goto_file(page, pages["pain2"], 12000)
        goto_file(page, pages["pain3"], 12000)

        # ============ 3. 识药（云端真机） ============
        print("[3/9] 拍照识药")
        open_site()
        wait(3000)
        page.mouse.wheel(0, 420)
        wait(1500)
        safe_click(page.get_by_text("拍照识药"))
        wait(1500)
        try:
            page.set_input_files("input[type=file]", str(box))
        except Exception as e:
            print("上传控件定位失败:", e)
        add_btn = page.get_by_text("添加到我的用药清单").first
        try:
            add_btn.wait_for(state="visible", timeout=90000)
            print("    识别完成")
        except Exception:
            print("    识别未完成:", page.locator("body").inner_text()[:150].replace("\n", " | "))
        wait(4000)
        page.mouse.wheel(0, 520)
        wait(2200)
        page.mouse.wheel(0, 520)
        wait(2200)
        try:
            safe_click(page.get_by_text("添加到我的用药清单"))
            wait(4000)
            print("    入箱完成")
            for _ in range(3):
                page.mouse.wheel(0, 520)
                wait(1400)
        except Exception as e:
            print("    入箱失败:", e)

        # ============ 4. 相互作用 ============
        print("[4/9] 相互作用")
        open_site()
        seed_second_med()
        try:
            btn = page.locator(".interaction-btn button").first
            btn.wait_for(state="visible", timeout=20000)
            safe_click(page.locator(".interaction-btn button"))
            for _ in range(60):
                wait(1000)
                if page.locator(".van-dialog").count():
                    break
            wait(8000)
            page.mouse.wheel(0, 300)
            wait(2000)
            safe_click(page.get_by_text("知道了"))
            wait(1500)
        except Exception as e:
            print("    相互作用失败:", e)

        # ============ 5. 提醒 ============
        print("[5/9] 提醒")
        try:
            tab("提醒")
            safe_click(page.locator(".van-nav-bar__right"))
            wait(1800)
            page.locator("input, textarea").first.fill("苯磺酸氨氯地平片")
            wait(900)
            for t in ["确定", "保存", "确认"]:
                if page.get_by_text(t).count():
                    safe_click(page.get_by_text(t))
                    break
            wait(2500)
            # 标记已服 → 撤销，展示交互
            try:
                safe_click(page.get_by_text("吃了"))
                wait(2200)
                safe_click(page.get_by_text("撤销"))
                wait(2200)
            except Exception:
                pass
        except Exception as e:
            print("    提醒失败:", e)

        # ============ 6. 问答 ============
        print("[6/9] 用药问答")
        try:
            tab("问答")
            page.locator("input, textarea").first.fill("我在吃阿司匹林，关节疼能吃布洛芬吗？")
            wait(900)
            safe_click(page.get_by_text("发送"))
            for _ in range(60):
                wait(1000)
                if page.locator(".bubble").count() >= 2:
                    break
            wait(4000)
            page.mouse.wheel(0, 300)
            wait(1500)
        except Exception as e:
            print("    问答失败:", e)

        # ============ 7. AI 协同（≥150s） ============
        print("[7/9] AI 协同复现（约 2 分半）")
        ai_slides = ["ai1", "ai2", "ai3", "ai4", "ai5", "ai6", "ai7", "ai8", "ai9", "ai10"]
        for i, s in enumerate(ai_slides, 1):
            print(f"    AI {i}/10: {s}")
            goto_file(page, pages[s], 15500)

        # ============ 8. 架构 ============
        print("[8/9] 架构")
        goto_file(page, pages["arch1"], 20000)
        goto_file(page, pages["arch2"], 20000)

        # ============ 9. 片尾 ============
        print("[9/9] 片尾")
        goto_file(page, pages["outro"], 15000)

        ctx.close()
        browser.close()

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
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-vf", "scale=1080:1920:flags=lanczos",
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
