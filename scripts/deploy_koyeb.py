#!/usr/bin/env python3
"""Create and deploy the ZhiYaoTong app on Koyeb via the public REST API.

Usage:
    python scripts/deploy_koyeb.py <KOYEB_TOKEN>

The token is created in Koyeb: sidebar bottom -> user name -> User settings
-> Personal access tokens -> Create access token.
"""
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

API = "https://api.koyeb.com/v1"
REPO = "github.com/wuhu2331936/zyt"
BRANCH = "main"
APP_NAME = "zhiyaotong"
SERVICE_NAME = "zhiyaotong"

# SSL verification can fail in restricted sandboxes; keep it on by default,
# but allow an explicit opt-out for troubleshooting.
SSL_CTX = ssl.create_default_context()
if os.environ.get("KOYEB_INSECURE") == "1":
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE


def call(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        print("HTTP %s on %s %s: %s" % (e.code, method, path, raw[:1200]))
        raise SystemExit(1)


def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/deploy_koyeb.py <KOYEB_TOKEN>")
        raise SystemExit(2)
    token = sys.argv[1].strip()

    dash = os.environ.get("DASHSCOPE_API_KEY", "")
    deep = os.environ.get("DEEPSEEK_API_KEY", "")
    env = [
        {"key": "PORT", "value": "8080"},
        {"key": "QWEN_VL_MODEL", "value": "qwen3-vl-plus"},
        {"key": "RAG_ENABLED", "value": "0"},
        {"key": "DEMO_MODE", "value": "1"},
    ]
    if dash:
        env.append({"key": "DASHSCOPE_API_KEY", "value": dash})
    if deep:
        env.append({"key": "DEEPSEEK_API_KEY", "value": deep})

    print("1/3 creating app ...")
    apps = call("GET", "/apps?limit=100", token)
    app_id = None
    for a in apps.get("apps", []):
        if a.get("name") == APP_NAME:
            app_id = a["id"]
            print("   existing app found: %s" % app_id)
            break
    if app_id is None:
        res = call("POST", "/apps", token, {"name": APP_NAME})
        app_id = res["app"]["id"]
        print("   created app: %s" % app_id)

    definition = {
        "name": SERVICE_NAME,
        "type": "WEB",
        "regions": ["was"],
        "instance_types": [{"type": "free"}],
        "ports": [{"port": 8080, "protocol": "http"}],
        "routes": [{"port": 8080, "path": "/"}],
        "scalings": [{"min": 1, "max": 1}],
        "env": env,
        "git": {
            "repository": REPO,
            "branch": BRANCH,
            "builder": "dockerfile",
            "dockerfile": {"path": "Dockerfile"},
        },
    }

    print("2/3 creating service ...")
    res = call("POST", "/services", token, {"app_id": app_id, "definition": definition})
    svc = res.get("service", {})
    print("   service id: %s" % svc.get("id"))
    print("3/3 done. Deploys are listed at:")
    print("   https://app.koyeb.com/apps/%s" % app_id)


if __name__ == "__main__":
    main()
