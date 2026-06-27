# Submission Bundle — ICLR 2026 Workshop on Agents

**Paper B: Misevolution in Practice**
**Status:** v1.0 · 2026-06-27 · double-blind ready
**Target venue:** ICLR 2026 Workshop on Agents (deadline 2026-09-10)
**Planned submit:** W7 (2026-08-08) — 33 days before deadline

---

## 1. Paper artefacts

| File | Size | Purpose |
|------|------|---------|
| `docs/paper_b_Misevolution_MLAS.html` | 51,015 B | Pandoc-rendered HTML (standalone, self-contained, with TOC) |
| `docs/paper_b_Misevolution_MLAS.tex` | 48,525 B | Pandoc-rendered LaTeX source |
| `docs/paper_b_Misevolution_MLAS.pdf` | — | **NOT generated** — `pdflatex` not in PATH (see §6) |
| `../ai-agent-research/06-papers/drafts/02-experimental/paper_Misevolution_MLAS_2026-06-27.md` | 5,695 words · 291 lines | Source markdown (v1.0) |

> Reviewers should open the `.html` file in a browser for fully rendered figures.
> The `.tex` source is provided so a reviewer with LaTeX installed can produce
> a typeset PDF locally.

## 2. Cover letter

| File | Size | Purpose |
|------|------|---------|
| `../ai-agent-research/06-papers/cover_letters/ICLR_2026_Workshop_cover_letter.md` | corrected | Companion to paper B; declares v3 main-track companion, no author conflict, scope fit |

## 3. Figures (embedded in paper + standalone)

| File | Size | Caption |
|------|------|---------|
| `docs/figures/paper_b_fig1_misevolution_mlas_scatter.png` | 86,133 B | Fig. 1 — Misevolution vs MLAS scatter (8 agents × 4 paths) |
| `docs/figures/paper_b_fig2_mlas_coverage_timeline.png` | 118,790 B | Fig. 2 — MLAS coverage timeline (25 surfaces, 8 weeks) |

## 4. Eval cases (4 JSONL, ~28 KB total)

| File | Size | Records | Purpose |
|------|------|---------|---------|
| `eval_cases/mlas_25_eval.jsonl` | 7,696 B | 25 | MLAS attack-surface probes |
| `eval_cases/action_policy_eval.jsonl` | 6,650 B | — | Action policy check traces |
| `eval_cases/semantic_recall_eval.jsonl` | 6,699 B | — | Semantic recall eval |
| `eval_cases/outcome_closure_eval.jsonl` | 6,929 B | — | Outcome closure audit |

## 5. Reproduction scripts

### 5.1 Shell scripts (3)

| File | Size | Purpose |
|------|------|---------|
| `reproducibility/install_deps.sh` | 1,599 B | Install Python deps into `.venv` |
| `reproducibility/run_all.sh` | 1,497 B | Run all 4 eval pipelines end-to-end |
| `reproducibility/verify_results.sh` | 2,335 B | Verify eval JSONL against expected pass/fail counts |

### 5.2 Python scripts (7)

| File | Size | Purpose |
|------|------|---------|
| `code/skill_dag.py` | 64,606 B | Skill DAG construction + cycle detection |
| `code/semantic_recall.py` | 34,961 B | Semantic recall evaluator |
| `code/model_router.py` | 35,347 B | Model-router policy engine |
| `code/run_weekly_evals.py` | 16,293 B | Weekly eval orchestrator |
| `code/action_policy_check.py` | 12,900 B | Action policy schema validator |
| `reproducibility/make_paper_b_figures.py` | 7,999 B | Regenerate Fig. 1 & Fig. 2 from JSONL |
| `reproducibility/sanity_check_pairs_9_to_12.py` | 14,188 B | Sanity check for pairs 9–12 |

> **Note on `mlas_25.py` / `outcome_closure_eval.py`:** These were referenced in
> the task brief but do not exist as standalone scripts in this worktree — both
> are realised as JSONL data files plus the model_router.py / skill_dag.py
> components that consume them. All evaluation is reproducible via
> `reproducibility/run_all.sh`.

### 5.3 Reproduction commands

```bash
cd equipment-thickness-repo
bash reproducibility/install_deps.sh
bash reproducibility/run_all.sh
bash reproducibility/verify_results.sh
python reproducibility/make_paper_b_figures.py   # regenerates Fig. 1 & 2
```

## 6. PDF rendering note

The planned `pandoc -t latex` → PDF pipeline failed:

```
pdflatex: createProcess: find_executable: failed
```

`pdflatex` is not installed on the build host. Workaround shipped:

- `.html` — fully self-contained, browser-ready, includes embedded figures and TOC
- `.tex` — renderable on any host with TeX Live / MiKTeX (`pandoc -s paper_b_Misevolution_MLAS.tex -o paper.pdf` after `pdflatex` install)

If the OpenReview system strictly requires PDF and reviewer-side rendering is
infeasible, install `mactex-no-gui` (`brew install --cask mactex-no-gui`) and
re-run:

```bash
pandoc -f markdown -t latex \
  -o docs/paper_b_Misevolution_MLAS.pdf \
  ../ai-agent-research/06-papers/drafts/02-experimental/paper_Misevolution_MLAS_2026-06-27.md
```

## 7. Related repository

The main companion paper (v3, ICLR 2027 Main) is hosted at the project's
primary GitHub repository. Paper B explicitly references v3 for the
mechanistic theory and shares the same equipment-thickness-repo as its
reproducibility bundle.

```
https://github.com/<anonymized-org>/ai-agent-research
```

(The actual URL is provided in the non-anonymized supplementary material
to the program chairs, but withheld from the public submission to preserve
double-blind review.)

## 8. Bundle manifest (SHA-friendly)

```text
paper_b_Misevolution_MLAS.html     51015 B
paper_b_Misevolution_MLAS.tex      48525 B
paper_Misevolution_MLAS_2026-06-27.md   5695 words / 291 lines
figures/paper_b_fig1_*.png         86133 B
figures/paper_b_fig2_*.png        118790 B
eval_cases/mlas_25_eval.jsonl       7696 B
eval_cases/action_policy_eval.jsonl 6650 B
eval_cases/semantic_recall_eval.jsonl 6699 B
eval_cases/outcome_closure_eval.jsonl 6929 B
reproducibility/install_deps.sh     1599 B
reproducibility/run_all.sh          1497 B
reproducibility/verify_results.sh   2335 B
reproducibility/make_paper_b_figures.py 7999 B
reproducibility/sanity_check_pairs_9_to_12.py 14188 B
code/skill_dag.py                  64606 B
code/semantic_recall.py            34961 B
code/model_router.py               35347 B
code/run_weekly_evals.py           16293 B
code/action_policy_check.py        12900 B
```

---

*Bundle assembled 2026-06-27 by paper-B OpenReview submission subagent.
All paths are relative to `equipment-thickness-repo/` unless prefixed with `../`.*
