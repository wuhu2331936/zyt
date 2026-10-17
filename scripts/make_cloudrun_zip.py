#!/usr/bin/env python3
"""打包 CloudBase 云托管部署包：只含云端构建必需文件，排除 venv / .env / node_modules。"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(
    os.path.expanduser("~"), "OneDrive", "Desktop", "zhiyaotong-cloudrun.zip"
)

INCLUDE_DIRS = ["backend/app", "frontend/dist"]
INCLUDE_FILES = [
    "Dockerfile",
    ".dockerignore",
    "backend/requirements-cloud.txt",
    "backend/pytest.ini",
]
SKIP_DIR_NAMES = {"__pycache__", "venv", ".venv", "chroma", "node_modules", ".git"}
SKIP_FILE_NAMES = {".env", ".env.local"}

count = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for rel in INCLUDE_FILES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            z.write(p, rel)
            count += 1
        else:
            print("MISSING", rel)
    for rel in INCLUDE_DIRS:
        base = os.path.join(ROOT, rel)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
            for fn in filenames:
                if fn in SKIP_FILE_NAMES:
                    continue
                full = os.path.join(dirpath, fn)
                arc = os.path.relpath(full, ROOT).replace("\\", "/")
                z.write(full, arc)
                count += 1

print("packed %d files -> %s" % (count, OUT))
print("size: %.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))
