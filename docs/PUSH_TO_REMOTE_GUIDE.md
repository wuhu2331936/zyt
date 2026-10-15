# 推送到 GitHub / Gitee 并设为 Public — 详细操作指南

> 适用项目：智药通（zhijiayaotong）
> 当前状态：`master` 分支 · `v0.3.0` tag · 26 次提交 · **未配置任何 remote**

---

## 🚀 快捷入口（桌面上直接双击）

如果嫌项目路径太深找不到脚本，桌面上已经放好了两个入口：

| 桌面文件 | 作用 |
|---|---|
| `智药通-推送到GitHub或Gitee.bat` | 推代码到 GitHub / Gitee，全程中文引导 |
| `智药通-填写API Key.bat` | 自动打开记事本填 `.env`，填完自动校验 |

双击即可，不需要先打开任何终端、也不需要手动切目录。
它们只是启动器，真正的逻辑仍在 `zhijiayaotong\scripts\*.ps1`，改脚本不影响桌面入口。

---

## ⚠️ 第 0 步：推送前的安全检查（最重要！）

你的项目里有真实 API Key 的 `.env` 文件。**推上去前必须确认它不会被推**。

在项目根目录打开 Git Bash，执行一次：

```bash
git ls-files | grep -i '\.env'
```

**正确的输出应该只有这两行**（带 `.example` 的模板文件）：

```
backend/.env.example
frontend/.env.example
```

✅ **如果出现 `backend/.env`（不带 .example）→ 立刻停止！** 先执行：

```bash
git rm --cached backend/.env
git rm --cached frontend/.env
```

再确认 `.gitignore` 里有这一行（现在应该有）：

```bash
cat .gitignore | grep env
```

补充说明：你的 `.env` 目前在历史提交里也从未出现过，所以即使 push 也不会泄露历史 Key。

---

## 路线选择

| 路线 | 适合谁 | 耗时 |
|------|--------|------|
| **A. 一键脚本**（推荐） | 想最快搞定 | 3 分钟 |
| **B. 手动命令行** | 想看清每一步 / 脚本出问题 | 5 分钟 |
| **C. GitHub CLI** | 已装 gh 且已登录 | 2 分钟 |

---

# 路线 A：一键脚本（推荐）

## A1. 先在网页上创建空仓库

**GitHub**：
1. 打开 https://github.com/new
2. Repository name 填 `zyt`
3. 选 **Public**
4. **重要**：下面三个都**不要勾选**
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
5. 点 **Create repository**
6. 停在生成的页面上，待会要用你的用户名

**Gitee**（备选/国内更快）：
1. 打开 https://gitee.com/projects/new
2. 仓库名称填 `zyt`
3. 选 **公开**（=Public）
4. **不要勾选**「使用 Readme 文件初始化这个仓库」
5. 点 **创建**

## A2. 生成 Personal Access Token（PAT）

这是用来代替密码的，只显示一次，**立刻复制保存**。

**GitHub**：
1. 打开 https://github.com/settings/tokens
2. 点 **Generate new token** → **Generate new token (classic)**
3. Note 填 `zyt-push`
4. Expiration 选 `90 days`（或 No expiration）
5. 勾选 **`repo`**（完整仓库读写权限，push 必需）
6. 拉到底点 **Generate token**
7. **复制生成的 `ghp_xxxx...` 字符串**（关掉页面就再也看不到了）

**Gitee**：
1. 打开 https://gitee.com/profile/personal_access_tokens
2. 点 **生成新令牌**
3. 勾选 `projects`（仓库读写）
4. 点 **提交**
5. **复制生成的令牌字符串**

## A3. 双击运行脚本

去文件管理器打开：

```
C:\Users\wuhu\WorkBuddy\2026-10-14-20-41-43\zhijiayaotong\scripts\push_to_github.bat
```

**双击它**。会弹出蓝色 PowerShell 窗口，按提示操作：

```
========================================
  ZhiYaoTong - Push to GitHub / Gitee
========================================

[OK] branch: master  commits: 25  tag: v0.3.0
[no gh CLI] Falling back to HTTPS + Token

Prerequisites:
  1. Create an empty repo on the web ...
  2. Generate a Personal Access Token (PAT) ...

Platform [1=GitHub / 2=Gitee] (default: 1):     ← 直接回车(默认GitHub)，或输 2 选 Gitee
Your username:                                     ← 输入你的 GitHub/Gitee 用户名
Repo name (default: zyt):                  ← 直接回车用默认
Push to https://github.com/xxx/zyt.git ? [y/n]:   ← 输 y 回车

  username: xxx
  password: 粘贴你的 PAT
  （输密码时光标不动是正常的，粘贴后回车即可）
```

## A4. 确认成功

看到这个就是成功了：

```
========================================
  Push complete
  Repo URL: https://github.com/xxx/zyt
  Next: confirm Public status on the web
========================================
Press any key to continue . . .
```

---

# 路线 B：手动命令行

如果你更喜欢自己敲命令看清每一步，用这个。

## B1. 先在网页创建空仓库 + 生成 PAT

同上面的 A1、A2 步骤（空仓库、Public、PAT 都先准备好）。

## B2. 配置 remote 并推送

在项目根目录（`zhijiayaotong\`）打开 **Git Bash**，依次执行。

把 `YOUR_USERNAME` 换成你的用户名，先设置变量避免重复输错：

```bash
USER_NAME="YOUR_USERNAME"
REPO_NAME="zyt"
```

**GitHub 用户执行这几行：**

```bash
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/${USER_NAME}/${REPO_NAME}.git"
git remote -v
```

**Gitee 用户执行这几行：**

```bash
git remote remove origin 2>/dev/null
git remote add origin "https://gitee.com/${USER_NAME}/${REPO_NAME}.git"
git remote -v
```

确认 `git remote -v` 输出的 URL 正确后，推送分支：

```bash
git push -u origin master
```

这时会弹窗或命令行提示输入：

- **Username**：你的用户名
- **Password**：⚠️ **不是登录密码**，粘贴刚才生成的 PAT

粘贴时光标不会动，直接粘贴 + 回车。

推送 tag（`v0.3.0` 这个里程碑，比赛评分会看）：

```bash
git push origin v0.3.0
```

## B3. 常见问题速查

**报错 `remote: Support for password authentication was removed`**
→ 说明你填的是登录密码。必须用 PAT 当密码。

**报错 `repository not found`**
→ 用户名或仓库名拼错了，或者仓库没建成 Public。

**报错 `failed to push some refs`**
→ 网页建仓库时不小心勾了 README。去仓库页面删掉 README，或者执行：

```bash
git pull origin master --allow-unrelated-histories
git push -u origin master
```

**卡住不动**
→ 网络问题。Gitee 在国内通常更快，可以改用 Gitee。

---

# 路线 C：GitHub CLI（如果你装了 gh）

```bash
gh auth login          # 按提示登录一次
gh repo create zyt --public --source=. --remote=origin --push
```

一行搞定，会自动建 Public 仓库并推送。

---

## 第 3 步：确认 Public 状态（必做）

推送完**一定要去网页确认**，因为比赛要求仓库可访问。

### GitHub

1. 打开 `https://github.com/YOUR_USERNAME/zyt`
2. 看仓库名右边有没有一个 **「Public」** 灰色标签
   - ✅ 有 → 完成
   - ❌ 显示 Private → 按下面操作

**如果是 Private，改成 Public**：

1. 点 **Settings**（仓库右上角）
2. 拉到最底部 **Danger Zone**
3. 点 **Change repository visibility**
4. 选 **Change visibility** → **Make public**
5. 输入仓库名 `zyt` 确认
6. 点 **I understand, change repository visibility**

> 注意：GitHub 从 2023 年起，把仓库从 Private 转 Public **不需要**在 Settings 里单独开启，改完即生效。

### Gitee

1. 打开 `https://gitee.com/YOUR_USERNAME/zyt`
2. 看仓库名上方有没有 **「公开」** 标签
   - ✅ 有 → 完成
   - ❌ 显示「私有」→ 按下面操作

**如果是私有，改成公开**：

1. 点 **管理**（仓库右侧）
2. 左侧选 **仓库设置**
3. 找 **开源** 区域
4. 点 **开源** 按钮
5. 勾选协议确认，提交

> ⚠️ Gitee 的仓库转公开后，**需要等待审核**（通常 1-2 个工作日）才会真正对外可见。比赛临近的话优先用 GitHub。

---

## 第 4 步：最终验证清单

推送完成后，逐项确认：

```bash
# 1. remote 已配置
git remote -v

# 2. 分支和 tag 都推上去了
git branch -a
git ls-remote --tags origin

# 3. 确认 .env 没上去（最重要！）
git ls-remote origin 2>/dev/null >/dev/null && \
  echo "--- 检查远端是否有 .env ---" && \
  git ls-tree -r origin/master --name-only | grep -i '\.env$' || echo "✓ 远端无 .env 文件"
```

然后**用无痕窗口**打开你的仓库地址，确认：

- [ ] 能直接看到代码（不用登录）
- [ ] 仓库名旁边显示 **Public / 公开**
- [ ] 有 25 次提交记录
- [ ] 有 `v0.3.0` 的 Release/tag
- [ ] README.md 正常渲染
- [ ] **搜不到任何 `.env` 文件**，也没有 `sk-` 开头的 Key

---

## 第 5 步：回填链接到提交材料

推送成功后，把仓库地址填回去：

1. 打开 `SUBMISSION_CHECKLIST.md`
2. 找到「仓库地址」那一行，填入 `https://github.com/YOUR_USERNAME/zyt`
3. 同样更新 `README.md` 里的仓库链接
4. 重新打包 zip：

```bash
cd C:/Users/wuhu/WorkBuddy/2026-10-14-20-41-43
python -c "
import zipfile, os, pathlib
ROOT = pathlib.Path(r'C:\Users\wuhu\WorkBuddy\2026-10-14-20-41-43\zhijiayaotong')
OUT = pathlib.Path(r'C:\Users\wuhu\WorkBuddy\2026-10-14-20-41-43\zyt-submission.zip')
EX = {'node_modules','venv','.venv','__pycache__','.git','dist','build','.vite','chroma_db','chroma','.pytest_cache'}
n=0
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in ROOT.rglob('*'):
        if p.is_file() and not any(x in EX for x in p.parts) and p.name != '.env':
            z.write(p, str(p.relative_to(ROOT.parent)).replace(chr(92),'/'))
            n+=1
print(f'[done] {n} files, {OUT.stat().st_size/1024:.0f} KB')
"
```

---

## 关于 API Key：我无法代填

`.env` 里的 `DASHSCOPE_API_KEY` 和 `DEEPSEEK_API_KEY` 需要你自己填，原因是：

1. **这些是你的个人私密凭据**，我无法获取，也不应该代你输入
2. 一旦 Key 进了 git 历史，即使后来删除也能被翻出来

自己填的方法 — 双击：

```
zhijiayaotong\scripts\setup_api_keys.bat
```

会自动复制 `.env.example` → `.env`、打开 Notepad 让你填、关闭后自动校验占位符是否替换、并检查 `.env` 是否被 git 追踪。

或者手动：

```bash
cd backend
cp .env.example .env
notepad .env        # 把两个 sk-xxxxx 占位符替换成真实 Key
```

---

## 时间线建议

| 步骤 | 建议时间 |
|------|----------|
| 网页建空仓库 + 生成 PAT | 现在（3 分钟） |
| 双击 push_to_github.bat | 现在（2 分钟） |
| 网页确认 Public | 推送后立即（1 分钟） |
| **Gitee 用户注意**：开源审核 | 提前 1-2 天 |
| 填 API Key + 本地测试 | 推送后 |
| 录演示视频 | 最后 |

---

**一句话总结**：先去网页建一个空的 Public 仓库 + 生成 PAT，然后双击 `scripts\push_to_github.bat`，跟着提示走完，最后去网页确认显示 Public。
