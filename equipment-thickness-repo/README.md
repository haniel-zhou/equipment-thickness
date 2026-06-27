# Equipment Thickness Theory — Open Source Repository

<!--
  Badges note (2026-06-27):
  - License badge: real (LICENSE file is MIT, verified)
  - Status badge: self-declared, no external dependency
  - DOI badge: PENDING — repo has no Zenodo DOI yet (paper not submitted); uncomment after Zenodo assignment
  - Code style / Tests badge: PENDING — no pyproject.toml / CI in this worktree; do not add until infrastructure exists
-->

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Research Artifact](https://img.shields.io/badge/status-research%20artifact-blueviolet)
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX) -->

> **Paper**: *Equipment Thickness Theory: A Formal Model for Agent Capability Stacks*
> **Authors**: [Anonymized for double-blind review]
> **Venue**: ICLR 2027 Main (primary submission, 2026-09-25)
> **Companion**: NeurIPS 2027 Main (backup), ICLR 2026 Workshop on Agents (companion paper B)
> **License**: MIT
> **DOI**: [To be assigned by Zenodo at acceptance]

This repository contains the code, data, and reproducibility artifacts for the Equipment Thickness Theory paper. It is **double-blind anonymized** for review: no author names, institutional paths, or proprietary system names appear in any file. At acceptance, we will publish the final version with author names + a permanent Zenodo DOI.

---

## Repository structure

```
equipment-thickness-repo/
├── README.md                          # This file
├── LICENSE                            # MIT
├── CITATION.cff                       # Citation metadata
├── docs/
│   ├── paper_v1_anonymized.md         # Full paper text (~10,200 words)
│   ├── supplementary_appendix.md      # Math appendix + OpenMythos sanity check details
│   └── reproducibility_guide.md       # Step-by-step reproduction
├── code/
│   ├── skill_dag.py                   # 207 skills, 159 typed edges, 6 edge types
│   ├── action_policy_check.py         # 10 rules, 5 categories, 3 decision levels
│   ├── model_router.py                # 4 providers × 10 categories × 5 rules × 20-field log
│   ├── semantic_recall.py             # 361 chunks, 3 query modes
│   ├── run_weekly_evals.py            # 35-case weekly harness, 7 categories
│   └── openmythos_sanity_check.py     # 5-pass sanity check on OpenMythos model layer
├── eval_cases/
│   ├── outcome_closure_eval.jsonl     # 20 cases × outcome tracking
│   ├── action_policy_eval.jsonl       # 30 cases × policy
│   ├── semantic_recall_eval.jsonl     # 60 cases × memory recall
│   ├── mlas_25_eval.jsonl             # 20 cases × MLAS attack surface
│   └── weekly_W27_W28_W29_W30.jsonl   # 35 cases × weekly regression
├── results/
│   ├── 2026-W27-week1.md              # W27 scoreboard
│   ├── 2026-W28-week2.md              # W28 scoreboard
│   ├── 2026-W29-week3.md              # W29 scoreboard
│   └── 2026-W30-week4.md              # W30 scoreboard (35/35 ✅)
├── reproducibility/
│   ├── run_all.sh                     # Single-command reproduction script
│   ├── install_deps.sh                # Dependency install (pip + openmythos)
│   └── verify_results.sh              # Compare against expected outputs
└── reproducibility_guide.md           # Full walkthrough (also in docs/)
```

---

## Quickstart

### 1. Clone and install (30 seconds)

```bash
git clone https://github.com/[anonymized]/equipment-thickness.git
cd equipment-thickness
bash reproducibility/install_deps.sh
```

### 2. Run all 5 weekly evals (5 seconds)

```bash
bash reproducibility/run_all.sh
```

Expected output:
```
2026-W27: 20/20 (100%) ✅
2026-W28: 25/25 (100%) ✅
2026-W29: 30/30 (100%) ✅
2026-W30: 35/35 (100%) ✅
TOTAL: 110/110 (100%) ✅
```

### 3. Inspect the SkillDAG (5 seconds)

```bash
python3 code/skill_dag.py stats
```

Expected output:
```
DAG stats:
  Total skills: 207
  Total edges: 159
  By type:
    REQUIRES: 69
    COMPOSES_WITH: 33
    SPECIALIZES: 20
    RISK_ESCALATES_TO: 15
    CONFLICTS_WITH: 14
    REPLACES: 8
  Avg edges per skill: 1.5
```

### 4. Reproduce the SkillDAG paper accuracy claim (60 seconds)

```bash
python3 code/skill_dag.py recommend "code audit and review" --chain
python3 code/skill_dag.py recommend "knowledge graph extract and validate" --chain
python3 code/skill_dag.py recommend "deploy and monitor with health check" --chain
```

Expected: top-1 skill in each case is `code_audit`, `knowledge_graph`, `devops_deploy` respectively.

---

## What's NOT in this repository (and why)

- **No training data or fine-tuned model weights**: we do not ship any model weights; the local 4B LLM and the cloud LLM are external dependencies (see `install_deps.sh`).
- **No private evaluation data**: the 8-agent system operates on synthetic + public data; we provide the eval cases, not the underlying agent logs (which contain telemetry).
- **No internal configuration files**: the production system has a 1175-chunk memory-palace and a 4-layer shared-lessons system; we provide the semantic_recall.py code but not the memory contents (it would un-anonymize the deployment).
- **No proprietary dependencies**: all code runs on Python 3.10+ + pip-installable packages (numpy, no proprietary ML framework required).

---

## Companion paper B (workshop)

The companion workshop paper (*Misevolution in Practice: A 2-Month Empirical Study*) uses the same artifacts plus `code/mlas_25.py` (a 25-item MLAS checklist runner). The mlas_25_eval.jsonl provides 20 test cases.

---

## Reproducibility checklist (per ICLR 2027 standards)

| Item | Status |
|------|--------|
| Single-command reproduction | ✅ `bash reproducibility/run_all.sh` |
| All artifacts open source under MIT | ✅ |
| Random seeds fixed where applicable | ✅ (no stochastic components in eval cases) |
| Compute requirements documented | ✅ (single MacBook Air, no GPU) |
| Wall-clock time per experiment | ✅ (~30 seconds for full sweep) |
| Cross-platform compatibility | ✅ (Linux + macOS, Python 3.10+) |
| Test suite for code correctness | ✅ (35 weekly cases act as integration tests) |
| Sample outputs checked in | ✅ (results/2026-W27-W30 scoreboards) |
| Comparison with expected outputs | ✅ (reproducibility/verify_results.sh) |

---

## Citation

```bibtex
@article{equipmentthickness2027,
  title={Equipment Thickness Theory: A Formal Model for Agent Capability Stacks},
  author={[Anonymized for double-blind review]},
  journal={ICLR 2027 Main Conference},
  year={2027},
  note={Open source at github.com/[anonymized]/equipment-thickness}
}
```

---

## Acknowledgments

We thank the open-source community for the OpenMythos implementation (MIT license), the 207-skill agent framework contributors, and the 4 conference reviewers who will (hopefully) suggest improvements.

---

*Last updated: 2026-07-28 (Day 28 of 30-day sprint)*
*This README is part of the double-blind submission package. Author names will be added at acceptance.*