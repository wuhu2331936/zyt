# Contributing

> 比赛是个人赛，本文档用于未来开源协作时规范流程。

## 开发环境

- Node.js ≥ 20
- Python ≥ 3.12
- Git

## 提交规范

本项目遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```
<type>(<scope>): <subject>

<body>
```

| 类型 | 说明 |
|---|---|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档变更 |
| `style` | 代码格式化（不影响逻辑） |
| `refactor` | 重构（既不是新功能也不是 bug 修复） |
| `test` | 添加或修改测试 |
| `chore` | 构建过程或辅助工具变更 |
| `perf` | 性能优化 |

scope 示例：`backend`、`frontend`、`api`、`docs`、`pwa`...

## 分支规范

- `main`：稳定版本，每次提交即可发版
- `feat/*`：新功能开发
- `fix/*`：Bug 修复
- `docs/*`：纯文档

## Code Review

请至少有一位 reviewer 通过。

## 测试

提交前必须：
- ✅ Python：`py_compile` 所有 .py
- ✅ 前端：`npm run build` 通过
- ✅ Lint（如配置）：`npm run lint`
