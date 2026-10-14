"""一键复现脚本：克隆代码后一条命令跑通整个流水线

使用：
    cd zhijiayaotong
    python scripts/bootstrap.py

效果：
    1. 检查 Python / Node 环境
    2. 创建后端 venv + 装依赖
    3. 创建前端 .env.local
    4. （可选）构建向量库
    5. 提示用户填 API Key，然后启动服务

适合评委 / 评委助理 / 同事克隆后一键部署。
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = platform.system() == "Windows"


def colored(s: str, color: str) -> str:
    """跨平台彩色输出（支持 Windows + Unix）"""
    if IS_WINDOWS:
        os.system("color")  # 启用 ANSI
    colors = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "reset": "\033[0m"}
    return f"{colors.get(color, '')}{s}{colors['reset']}"


def run(cmd: str, cwd: Path = ROOT, check: bool = True, shell: bool = IS_WINDOWS) -> int:
    print(colored(f"\n$ {cmd}", "blue"))
    return subprocess.run(
        cmd if shell else cmd.split(),
        cwd=str(cwd),
        shell=shell,
        check=check,
    ).returncode


def check_python():
    """检查 Python 版本"""
    ver = sys.version_info
    if ver < (3, 11):
        print(colored(f"❌ Python 3.11+ required, found {ver.major}.{ver.minor}", "red"))
        sys.exit(1)
    print(colored(f"✅ Python {ver.major}.{ver.minor}.{ver.micro}", "green"))


def check_node():
    """检查 Node 版本"""
    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True)
        ver = r.stdout.strip().lstrip("v")
        major = int(ver.split(".")[0])
        if major < 20:
            print(colored(f"❌ Node.js 20+ required, found {ver}", "red"))
            sys.exit(1)
        print(colored(f"✅ Node.js {ver}", "green"))
    except FileNotFoundError:
        print(colored("❌ Node.js not found. Install from https://nodejs.org/", "red"))
        sys.exit(1)


def setup_backend():
    """后端：创建 venv + 装依赖"""
    print(colored("\n=== 后端设置 ===", "yellow"))
    backend = ROOT / "backend"

    venv_dir = backend / "venv"
    if not venv_dir.exists():
        run(f"{sys.executable} -m venv venv", cwd=backend)
    pip = str(venv_dir / ("Scripts" if IS_WINDOWS else "bin") / ("pip.exe" if IS_WINDOWS else "pip"))
    python = str(venv_dir / ("Scripts" if IS_WINDOWS else "bin") / ("python.exe" if IS_WINDOWS else "python"))

    run(f"{python} -m pip install --upgrade pip", cwd=backend)
    run(f"{pip} install -r requirements.txt", cwd=backend)

    env_example = backend / ".env.example"
    env_file = backend / ".env"
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        print(colored(f"📝 已从 .env.example 复制 .env，请编辑填入真实 API Key：", "yellow"))
        print(colored(f"   {env_file}", "blue"))
        print(colored("   需要填：DASHSCOPE_API_KEY + DEEPSEEK_API_KEY", "yellow"))

    return python


def setup_frontend():
    """前端：装依赖"""
    print(colored("\n=== 前端设置 ===", "yellow"))
    frontend = ROOT / "frontend"
    run("npm install", cwd=frontend)

    env_example = frontend / ".env.example"
    env_file = frontend / ".env.local"
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        print(colored(f"📝 已创建 .env.local（默认本地后端地址）", "yellow"))
    return None


def main():
    print(colored("🚀 智药通一键复现脚本", "green"))
    print(f"📂 项目根目录：{ROOT}\n")

    check_python()
    check_node()

    setup_backend()
    setup_frontend()

    print(colored("\n=== 安装完成 ===", "green"))
    print(colored("\n📝 下一步：", "yellow"))
    print(f"   1. 编辑 backend/.env 填入 DASHSCOPE_API_KEY + DEEPSEEK_API_KEY")
    print(f"   2. (可选) 构建向量库：")
    print(f"        cd backend && python scripts/build_vector_db.py")
    print(f"   3. 启动后端：")
    print(f"        cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
    print(f"   4. 启动前端（新终端）：")
    print(f"        cd frontend && npm run dev")
    print(colored("\n✅ 完事！打开 http://localhost:5173 开始体验。", "green"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n\n⚠️ 用户取消", "yellow"))
