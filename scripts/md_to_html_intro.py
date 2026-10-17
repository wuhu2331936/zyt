# -*- coding: utf-8 -*-
"""把 docs/作品介绍文档.md 转成带打印样式的 HTML（复用技术文档的 CSS），供 Edge 打印 PDF"""
import markdown
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
md_path = ROOT / "docs" / "作品介绍文档.md"
html_path = ROOT / "docs" / "作品介绍文档.html"

text = md_path.read_text(encoding="utf-8")
body = markdown.markdown(text, extensions=["tables", "fenced_code"])

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
       font-size: 11pt; line-height: 1.75; color: #1a1a2e; margin: 0; }
h1 { font-size: 20pt; color: #0d47a1; border-bottom: 3px solid #1976d2;
     padding-bottom: 8px; margin-top: 24px; }
h1:first-of-type { margin-top: 0; text-align: center; border-bottom: none;
     font-size: 24pt; padding: 60px 0 10px; }
h2 { font-size: 15pt; color: #1565c0; margin-top: 28px;
     border-left: 5px solid #1976d2; padding-left: 10px;
     page-break-after: avoid; }
h3 { font-size: 12.5pt; color: #283593; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 12px 0;
        font-size: 9.5pt; page-break-inside: avoid; }
th { background: #e3f2fd; color: #0d47a1; padding: 7px 9px;
     border: 1px solid #bbdefb; text-align: left; }
td { padding: 6px 9px; border: 1px solid #e3f2fd; }
tr:nth-child(even) td { background: #fafcff; }
code { font-family: Consolas, monospace; background: #eef2f7;
       padding: 1px 4px; border-radius: 3px; font-size: 9.5pt; }
blockquote { border-left: 4px solid #90caf9; background: #f3f8fe;
             margin: 12px 0; padding: 8px 14px; color: #455a64; }
ul, ol { padding-left: 24px; }
figure { margin: 14px 0; text-align: center; page-break-inside: avoid; }
figure img { display: block; margin: 0 auto; max-width: 62%; max-height: 170mm;
      width: auto; height: auto;
      border: 1px solid #cfd8e3; border-radius: 8px;
      box-shadow: 0 2px 8px rgba(13, 71, 161, 0.10); }
figcaption { font-size: 10pt; color: #455a64; margin-top: 5px; }
"""

html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>智药通 作品介绍文档</title><style>{CSS}</style></head>
<body>{body}</body></html>"""

html_path.write_text(html, encoding="utf-8")
print("HTML written:", html_path)
