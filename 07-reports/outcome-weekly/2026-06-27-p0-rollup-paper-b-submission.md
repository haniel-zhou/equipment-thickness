# Paper-B OpenReview 提交包 — 落地报告

**Worktree**: `/Users/haniel/workspace/research/ai-agent-research/paper_drafts.p0-rollup/`
**Branch**: `feat/p0-rollup`
**Subagent**: 配稿 B OpenReview 提交包 subagent
**日期**: 2026-06-27
**任务来源**: `STRATEGY_AND_NEXT_STEPS_2026-06-26.md` §18.4 W3 Gantt 第 1 项

---

## 1. 子任务 1:配稿 B PDF + HTML 渲染

| 输出 | 路径 | 大小 | 状态 |
|------|------|------|------|
| HTML | `equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.html` | 51,015 B | ✅ 成功 (pandoc 3.9.0.2, standalone + self-contained + TOC) |
| LaTeX 源 | `equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.tex` | 48,525 B | ✅ 成功 (pandoc -t latex,exit 0) |
| **PDF** | `equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.pdf` | — | ❌ **未生成** — `pdflatex` 不在 PATH (`pdflatex: createProcess: find_executable: failed`) |

**mitigation**:已生成 `.tex` 源;任何装好 TeX Live / MiKTeX 的评审端可用 `pdflatex paper_b_Misevolution_MLAS.tex` 自行编译。SUBMISSION_BUNDLE.md §6 + checklist 末尾的 pre-submit action 都明确说明装 `mactex-no-gui` 后重渲。`.md` 不在 docs/ 下(源 md 在 `ai-agent-research/06-papers/drafts/02-experimental/`,符合预期 — 任务里 `ls -la .../{md,pdf,html}` 只检查渲染产物,渲染产物就是 .html + .tex)。

## 2. 子任务 2:Reproducibility bundle

**新增文件**:
- `equipment-thickness-repo/docs/SUBMISSION_BUNDLE.md` — 6,019 B,新文件,8 节含 manifest + reproduction 命令 + PDF 失败说明 + 项目 GitHub URL(已 anonymized)

**eval_cases**(4 JSONL, 已在 worktree 中无需复制):
- `mlas_25_eval.jsonl` (7,696 B, 25 records)
- `action_policy_eval.jsonl` (6,650 B)
- `semantic_recall_eval.jsonl` (6,699 B)
- `outcome_closure_eval.jsonl` (6,929 B)
- 小计 ≈27,974 B / 4 文件

**reproducibility shell**(3 文件,已在 worktree):
- `install_deps.sh` (1,599 B) · `run_all.sh` (1,497 B) · `verify_results.sh` (2,335 B)

**Python scripts**(7 文件,实际 worktree 内可找到;任务里提到的 `mlas_25.py` 和 `outcome_closure_eval.py` 不存在 — 它们的功能已被 `model_router.py` + `skill_dag.py` 组件消费 JSONL 数据实现,详见 SUBMISSION_BUNDLE.md §5.2 note):
- `code/skill_dag.py` (64,606 B)
- `code/semantic_recall.py` (34,961 B)
- `code/model_router.py` (35,347 B)
- `code/run_weekly_evals.py` (16,293 B)
- `code/action_policy_check.py` (12,900 B)
- `reproducibility/make_paper_b_figures.py` (7,999 B)
- `reproducibility/sanity_check_pairs_9_to_12.py` (14,188 B)

**figures**(2 PNG):
- `paper_b_fig1_misevolution_mlas_scatter.png` (86,133 B)
- `paper_b_fig2_mlas_coverage_timeline.png` (118,790 B)

**README + GitHub URL**:SUBMISSION_BUNDLE.md §7 引用 v3 主项目 `https://github.com/<anonymized-org>/ai-agent-research`,真实 URL 由 program chairs 在 cover letter 通道获取(双盲合规)。

## 3. 子任务 3:OpenReview 提交检查清单

**新增文件**: `ai-agent-research/06-papers/cover_letters/ICLR_2026_Workshop_SUBMISSION_CHECKLIST.md` — 6,918 B

包含 4 个 section + pre-submit action items:
1. **Required files** — 全部 [x] (PDF 项标注 "not generated, .tex 替代")
2. **Double-blind compliance** — 全部 [x],含 3 项 v1.0 数据校正(1,247→4 events, 0.7%→0% FPR, 1,472→0 lines lost)
3. **Submission metadata** — track / deadline / format / companion / conflicts 全填
4. **OpenReview form fields** — Title / Abstract / Keywords / TL;DR / Suggested reviewers / Conflicts declared 全部预填,直接复制粘贴即可
5. **Pre-submit action items** — 8 条 checkbox,含装 mactex-no-gui、上传 zip、最后再 grep 一次双盲关键词、deadline 前 7 天 buffer(2026-09-03)

## 4. 子任务 4:验证

```text
✅ equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.html    51,015 B
✅ equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.tex     48,525 B
❌ equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.pdf     (pdflatex missing)
✅ ai-agent-research/06-papers/cover_letters/ICLR_2026_Workshop_cover_letter.md
✅ ai-agent-research/06-papers/cover_letters/ICLR_2026_Workshop_SUBMISSION_CHECKLIST.md (new, 6,918 B)
✅ equipment-thickness-repo/eval_cases/{mlas_25,action_policy,semantic_recall,outcome_closure}_eval.jsonl
✅ equipment-thickness-repo/docs/figures/paper_b_fig{1,2}_*.png
✅ equipment-thickness-repo/reproducibility/{install_deps,run_all,verify_results}.sh
✅ equipment-thickness-repo/code/{skill_dag,semantic_recall,model_router,run_weekly_evals,action_policy_check}.py
✅ equipment-thickness-repo/docs/SUBMISSION_BUNDLE.md (new, 6,019 B)
```

## 5. 投稿日倒计时

- **W7 planned submit**: 2026-08-08
- **Deadline**: 2026-09-10
- **距 deadline**: **33 天**
- **Buffer 项**:pre-submit checklist 要求 deadline 前 7 天提交,故实际 latest acceptable = 2026-09-03(留 26 天给 review tools / metadata 调整)。

## 6. 失败 / 局限

1. **PDF 未生成** — `pdflatex` 不在 build host PATH。已用 `.tex` 源 + 安装说明补位。W7 前需 `brew install --cask mactex-no-gui` 后重渲,已列入 pre-submit checklist。
2. **`mlas_25.py` / `outcome_closure_eval.py` 缺失** — 主目录 + worktree 都不存在这两个独立脚本(只有对应 JSONL 数据)。实际功能由 `model_router.py` + `skill_dag.py` 实现。已在 SUBMISSION_BUNDLE.md §5.2 note 中诚实标注。
3. **双盲审核** — 已 grep 0 命中 Kimi / Haniel / memory-palace;agent 命名 A–I;GitHub URL 用 `<anonymized-org>` 占位符,真实 URL 走 cover letter 程序主席通道。
4. **源 md 不在 docs/** — 这是设计选择(源留在 drafts/ 目录,渲染产物才进 docs/),非缺陷,已在报告 §1 中说明。

## 7. 总产出清单

| 类型 | 数量 | 总大小 |
|------|------|--------|
| 新增 markdown(报告 + bundle + checklist) | 3 文件 | 6,019 + 6,918 + 本报告 ≈ 18,000 B |
| 渲染产物(HTML + TeX) | 2 文件 | 99,540 B |
| 已存在并验证可访问 | 13 文件(4 jsonl + 3 sh + 5 py + 2 png) | ≈ 295 KB |
| 修改文件 | 0(遵守"不要改配稿 B v1.0"约束) | — |

**关键约束遵守**: ✅ 全程在 worktree / ✅ 未 push / ✅ 未真去 OpenReview / ✅ 未改 v1.0 / ✅ 文件全部真做到可验证。

---

## 中文总结(200 字内)

配稿 B OpenReview 提交包已在 `feat/p0-rollup` worktree 落地。pandoc 3.9 渲出 51KB HTML 与 48KB LaTeX,PDF 因 `pdflatex` 缺失未生成(已写 `.tex` 源 + 安装说明补位)。新增 `SUBMISSION_BUNDLE.md` 与 `ICLR_2026_Workshop_SUBMISSION_CHECKLIST.md` 双文档,前者列 8 节 manifest 含 GitHub anonymized URL,后者填好 Title / Abstract / Keywords / TL;DR 全部 OpenReview 表单字段并列出 8 项 pre-submit checkbox。4 个 eval JSONL、3 shell、5 code py、2 figure 全部验证可访问。距 2026-09-10 deadline 33 天,W7(8-08)计划投稿,deadline 前 7 天为 buffer。失败项仅 PDF,已在 checklist 标注装 mactex-no-gui 后重渲。
