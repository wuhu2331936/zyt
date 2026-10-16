# -*- coding: utf-8 -*-
"""把 dist/index.html 里的外链 CSS 内嵌进 <style>，生成 dist/index_inline.html。
用于规避个别环境下单独拉取 CSS 失败导致页面无样式的问题。"""
import re
from pathlib import Path

dist = Path(__file__).resolve().parents[1] / "dist"
html_path = dist / "index.html"
html = html_path.read_text(encoding="utf-8")

css_blocks = []
def repl(m):
    href = m.group(1)
    css_file = dist / href.lstrip("/").replace("/", "/")
    if css_file.is_file():
        css_blocks.append(css_file.read_text(encoding="utf-8"))
        return ""
    return m.group(0)

html = re.sub(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>', repl, html)
inline = "\n".join(f"<style>\n{c}\n</style>" for c in css_blocks)
html = html.replace("</head>", inline + "\n</head>")
out = dist / "index_inline.html"
out.write_text(html, encoding="utf-8")
print(f"inline css blocks={len(css_blocks)} size={out.stat().st_size}")
