"""生成比赛提交包 zip（放到桌面）

包含完整源码 + 构建产物 + 文档，排除：
- venv / node_modules / .git / __pycache__（体积巨大，评审不需要）
- backend/.env（含真实 API Key，绝不外泄）
- dist_old_* 等临时目录
"""
from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"
if not DESKTOP.exists():
    DESKTOP = Path(os.path.expanduser("~")) / "Desktop"

VERSION = sys.argv[1] if len(sys.argv) > 1 else "v9"

EXCLUDE_DIRS = {
    "venv", ".venv", "node_modules", ".git", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".vite", "dist_old",
    ".idea", ".vscode", "logs", "chroma_db",
}
EXCLUDE_FILES = {".env", ".DS_Store", "thumbs.db"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".log", ".tmp", ".bak"}


def should_skip(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if any(p.startswith("dist_old") for p in rel.parts):
        return True
    if rel.name in EXCLUDE_FILES:
        return True
    if rel.suffix in EXCLUDE_SUFFIX:
        return True
    return False


def main() -> None:
    out = DESKTOP / f"zhiyaotong-submission-{VERSION}.zip"
    count = 0
    total = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if should_skip(rel):
                continue
            z.write(path, f"zhijiayaotong/{rel.as_posix()}")
            count += 1
            total += path.stat().st_size

    print(f"打包完成: {out}")
    print(f"文件数: {count}  原始体积: {total/1024/1024:.2f} MB  压缩后: {out.stat().st_size/1024/1024:.2f} MB")

    # 自检：确认没有 Key 泄露
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        leak = [n for n in names if n.endswith("/.env") or n.endswith(".env")]
        if leak:
            print("!! 警告：包含 .env 文件 ->", leak)
        else:
            print("安全检查通过：包内无 .env（API Key 未外泄）")
        keys = [n for n in names if "dist/assets" in n or n.endswith("requirements-cloud.txt")]
        print(f"关键文件: {len([n for n in names if 'frontend/dist' in n])} 个前端产物; "
              f"requirements-cloud 在内: {any('requirements-cloud' in n for n in names)}")


if __name__ == "__main__":
    main()
