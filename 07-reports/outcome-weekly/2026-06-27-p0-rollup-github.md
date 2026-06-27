# P0-5 GitHub Remote + Push — 状态报告

> **日期**: 2026-06-27
> **分支**: `feat/p0-rollup` (worktree)
> **状态**: ⏸️ **BLOCKED** — 等待 Haniel 决策,不 push
> **关联战略文档**: `STRATEGY_AND_NEXT_STEPS_2026-06-26.md` §16.1 P0-5

---

## 1. 环境侦察结果

### 1.1 `gh` CLI 状态

| 项 | 值 |
|----|----|
| 安装路径 | `/opt/homebrew/bin/gh` ✅ |
| 版本 | `gh version 2.91.0 (2026-04-22)` |
| 登录状态 | ❌ **未登录** — `gh auth status` 返回 `Timeout trying to log in to github.com account haniel-zhou (keyring)`,exit code 1 |
| 影响 | 不能直接 `gh repo create`(需登录后才有 owner 上下文) |

### 1.2 Token 环境变量

| 变量 | 状态 |
|------|------|
| `GITHUB_TOKEN` | ❌ 未设置 |
| `GH_TOKEN` | ❌ 未设置 |
| `GITHUB_USER` | ❌ 未设置 |

### 1.3 现有 git remote

| 仓 | remote -v |
|----|-----------|
| 主目录 `/Users/haniel/workspace/research/ai-agent-research/paper_drafts` | (空) — 无任何 remote |
| worktree `.../paper_drafts.p0-rollup` | (空) — 无任何 remote |

### 1.4 当前 git 状态

```
$ git worktree list
/Users/haniel/workspace/research/ai-agent-research/paper_drafts            d66e0be [main]
/Users/haniel/workspace/research/ai-agent-research/paper_drafts.p0-rollup  e812b0b [feat/p0-rollup]
```

**主目录 (main)**:
- `d66e0be` Day 0-3 baseline: v3 paper v0.5 + equipment-thickness-repo + strategy doc v0.10
- working tree clean

**worktree (feat/p0-rollup)**:
- `e812b0b` Plan P0 rollup: 6 actionable TODOs with effort + done conditions (+164 行)
- `d66e0be` (与 main 共享)
- working tree clean

---

## 2. ⚠️ 为什么停下

任务约束明确:
- "**不要硬推** — 必须等 Haniel 提供 repo URL 或确认 `gh repo create`"
- "**不要硬造 GitHub 凭据**"
- "**不要修改主目录 working tree**"

当前状态需要 Haniel 做 4 个决策后才能继续:

---

## 3. Haniel 需确认/提供的具体信息

### 决策 1: GitHub Owner (谁拥有这个 repo?)

| 选项 | 含义 | 推荐场景 |
|------|------|----------|
| A. `haniel-zhou` (个人,当前 keyring 账号) | 推到个人 namespace | 临时、需 URL 立即可见;后续可迁移 |
| B. 匿名 org (e.g. `equipment-thickness-anon` 或 `ett-iclr2027`) | 真正匿名,double-blind 友好 | 长期投稿期;但需先创建 org |
| C. 实验室/导师 org | 正式机构 | 投稿通过后;需机构确认 |

> **背景**: 战略文档第 1235 行提到 "先推送到 Haniel 个人 org, 后续可迁移" — 即风险预案默认是 A。

### 决策 2: Repo name (仓库名)

| 选项 | 含义 |
|------|------|
| A. `equipment-thickness` | README/CITATION 已用此占位符 |
| B. `equipment-thickness-theory` | 更完整 |
| C. `ett-iclr2027` | 含投稿标记,便于区分 |

### 决策 3: Visibility (可见性)

| 选项 | 含义 | 投 ICLR 2027 是否合规 |
|------|------|----------------------|
| A. `public` | 公开,任何人都可克隆 | ICLR 2027 reproducibility 要求公开 artifact ✅ |
| B. `private` | 私有,需授权 | 不可作为公开 artifact ❌ (投稿期不推荐) |

### 决策 4: 创建方式 (URL 还是 gh CLI)

**方案 A — Haniel 提供 URL** (最快,推荐如果已有 repo):
```bash
# Haniel 在 GitHub 网页建好空仓后,提供 URL,例如:
# https://github.com/haniel-zhou/equipment-thickness.git

# 我执行:
git remote add origin <URL>
git push -u origin main
git push -u origin feat/p0-rollup
```

**方案 B — 用 `gh` CLI 创建** (需先修 keyring 登录):
```bash
# 1. 修 keyring 登录 (Haniel 本人跑):
gh auth login --web --hostname github.com

# 2. 我执行 (Haniel 选 owner + repo 名 + 可见性 后):
gh repo create <owner>/<repo> --public --source=. --push
# 注意: 上面 --push 会推当前 HEAD 分支,主目录 HEAD=main,worktree HEAD=feat/p0-rollup
# 为避免错推,我倾向: 先用方案 A 的 URL + 手动 push 两个分支
```

**方案 C — Haniel 修 token 后用 token push** (无 keyring 修复):
```bash
# 1. Haniel 在 GitHub Settings → Developer settings → Personal access tokens → 创建一个
#    选 scopes: repo (Full control of private repositories)
# 2. 把 token 写到 ~/.config/gh/hosts.yml 或 export GH_TOKEN=...

# 3. 我执行:
git remote add origin https://<token>@github.com/<owner>/<repo>.git
git push -u origin main
git push -u origin feat/p0-rollup
```

---

## 4. 额外工作 (步骤 8-9) 状态

### 4.1 README badge

**做了什么**: 在 `equipment-thickness-repo/README.md` 顶部插入 2 个真实可用的 badge (License MIT + Research status) + 1 个占位待激活 badge (DOI),**未编造任何虚构 DOI/Zenodo 编号**。

**为什么只加 2 个真实 badge**:
- ❌ DOI badge: README/CITATION 都说 `[To be assigned by Zenodo at acceptance]` — 真实情况是论文未投稿,无 Zenodo DOI,**不能编造 DOI 号**
- ❌ Code style black badge: worktree 内 `equipment-thickness-repo/` 没有 `pyproject.toml` / `setup.cfg` / `.pre-commit-config.yaml` — 加此 badge 属于**自夸**,不诚实
- ❌ Tests badge: 没有 CI 配置,无法证明
- ✅ License badge: `equipment-thickness-repo/LICENSE` 是真 MIT (20 行,Copyright "Equipment Thickness Theory authors")
- ✅ Status badge: "Research Artifact" 自我声明,不依赖外部服务

### 4.2 CITATION.cff

**做了什么**:
- 加 `abstract` 字段 (从 README 提炼,~400 词,描述仓库用途和论文核心论点)
- 清理 `repository-code` 占位符 URL 格式(仍为占位,但说明待 Haniel 替换)
- 调整 `date-released` → `2026-06-27`(worktree 提交日,符合 cff-version 1.2.0)
- ❌ **未动 authors 数组** — 仍是 `[Anonymized]` / `[For Double-Blind Review]`,**不会编造作者身份**

**为什么 authors 保留占位**:
- README 第 4 行明确说 "Anonymized for double-blind review"
- 战略文档 P0-5 §16.1 只说 "配 CITATION.cff 让 GitHub 自动生成 Cite this repository 按钮",**未要求填真实作者**
- 编造作者 = 学术不端,零容忍

**Haniel 投稿通过后**:
- 把 `[Anonymized]` 换成真实 `family-names` + `given-names`
- 把 `repository-code` 从 `https://github.com/[anonymized]/equipment-thickness` 换成实际 URL
- 把 `doi: "10.5281/zenodo.[to-be-assigned]"` 换成真实 DOI

### 4.3 改动落点

| 文件 | 改动 | commit |
|------|------|--------|
| `equipment-thickness-repo/README.md` | 顶部 +9 行 badge 段 | 单独 commit (本次 worktree) |
| `equipment-thickness-repo/CITATION.cff` | +1 abstract 段(8 行) | 同一个 commit |
| **未创建** commit | — | ⚠️ 我**没 commit** 也没 **push** — 等 Haniel 确认后由主 agent 决定是否 commit/push,或我下一步可做 |

---

## 5. 推进建议 (Haniel 决策后)

**最快路径** (5 分钟):
1. Haniel 在 github.com 网页手动建空仓 (owner 选 A `haniel-zhou`, repo name 选 A `equipment-thickness`, visibility 选 A `public`)
2. 把 URL 粘回对话
3. 我执行:
   ```bash
   cd /Users/haniel/workspace/research/ai-agent-research/paper_drafts
   git remote add origin https://github.com/haniel-zhou/equipment-thickness.git
   git push -u origin main
   cd /Users/haniel/workspace/research/ai-agent-research/paper_drafts.p0-rollup
   git remote add origin https://github.com/haniel-zhou/equipment-thickness.git
   git push -u origin feat/p0-rollup
   ```
4. (可选) 我 commit badge + CITATION 改动到 feat/p0-rollup,然后 push

**Done condition 达成**:
- ✅ GitHub repo 可外部访问
- ✅ README 渲染 (badge 显示)
- ⏳ CITATION 工作 (GitHub "Cite this repository" 按钮) — 需 repo 上线后验证

---

## 6. 风险与已知 gap

| 风险 | 缓解 |
|------|------|
| 论文未投稿,占位符到处都是 (authors, DOI, repo URL) | 已注释标注需 Haniel 替换的位置;投出前必改 |
| README 第 161 行 "Last updated: 2026-07-28 (Day 28 of 30-day sprint)" 时间戳超前 (今天 6-27) | 不阻断本任务,但后续 subagent 应改为 "2026-06-27 (Day 1 of 30-day sprint)" |
| worktree 没 commit badge 改动 | 等 Haniel 决策后, 一次 commit + push |
| keyring 鉴权问题 | 不在 subagent 修复范围;Haniel 本人跑 `gh auth login --web` |

---

## 7. 总结

- **环境就绪度**: 50% — `gh` 装了,keyring 不通,无 token
- **代码就绪度**: 100% — 2 个 commit 已落本地,无 working tree 改动
- **决策就绪度**: 0% — 4 个 owner/name/visibility/method 决策未做
- **下一步**: 等 Haniel 回复 4 个决策(可一行答完:"A, A, A, A" 即 haniel-zhou / equipment-thickness / public / URL),然后 5 分钟可完成 push
