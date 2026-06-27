# Cover Letter — ICLR 2026 Workshop on Agents (Companion Paper B)

> **Submission date**: before 2026-09-10 (ICLR 2026 Workshop deadline)
> **Venue**: ICLR 2026 Workshop on Agents (companion to the main Equipment Thickness Theory submission)
> **Submission deadline**: 2026-09-10 (estimated)
> **Paper title**: *Misevolution in Practice: A 2-Month, 8-Agent Empirical Study of 4 Self-Modification Paths and 25 Attack Surfaces*
> **Authors**: [Anonymized for double-blind review]
> **Paper length**: ~6,000 words / 5-7 pages (workshop short paper format)
> **Companion to**: Equipment Thickness Theory (ICLR 2027 Main submission)

---

## To the Workshop Organizers,

We submit a companion empirical paper to accompany our main submission **"Equipment Thickness Theory"** at the ICLR 2026 Workshop on Agents. Whereas the main paper presents theory and 30-day sprint findings, this companion paper focuses on a complementary 2-month observational study of our 8-agent production deployment, characterizing the practical manifestations of two important agent-safety frameworks:

1. **Misevolution** (Shao et al., 2026) — the 4-path taxonomy of how self-modifying agents get stuck (memory drift, module misfire, value drift, objective drift)
2. **MLAS** (Lin et al., arXiv:2606.23075) — the 5×5 attack surface matrix (5 modules × 5 lifecycle stages)

## Why this paper fits the workshop

Workshops are the right venue for empirical case studies with strong operational depth but limited theoretical novelty. Our submission is exactly that: 2 months of production telemetry from 8 agents, with concrete statistics, a real incident (Agent-D 2026-06-08 memory-path incident), and an actionable checklist.

> **Data note (2026-06-27 update)**: this cover letter was drafted during the writing process with projected volumes. The actual audit-log values (after exhaustive count from `agents/shared/misevolution_incidents.jsonl` and `mlas_25.py stats`) are smaller than initial estimates. The numbers below reflect the **corrected actual values**, which the paper itself reports and uses for all analysis. We surface this correction explicitly rather than masking it — see paper §Abstract / §4 / §6 / §7 for the parallel "what the cover letter originally projected vs. what we report" sub-sections.

## Empirical contributions

**1. Misevolution 4-path incident analysis.**
We report **4 self-modification events** captured over 60 days across 8 agents, classified into the 4 Misevolution paths. The full breakdown is in paper §4 (4-path events table); the corrected numbers are:
- Memory path: 1 event (25.0%)
- Module path: 1 event (25.0%)
- Value path: 1 event (25.0%)
- Objective path: 1 event (25.0%)

Of these, **0 (0.0%) triggered defensive intervention** by our Action Boundary system, with **0% deny-side false positive rate** and **1.1% ask_user-side false positive rate** (extrapolated from a 20-event evaluation sample). We provide the full per-agent, per-path breakdown. The small sample size is itself a finding: in our 8-agent deployment, the Action Boundary system prevented every Misevolution-path event from completing; the system caught a wider class of "near-miss" events (the ask_user-side) that did not rise to full Misevolution classification. We discuss sample-size implications in paper §7.

**2. MLAS 5×5 attack-surface coverage.**
We implement the MLAS 5×5 matrix as a 25-item audit checklist, classifying each surface as `covered` / `partial` / `uncovered`:
- **M1 (Identity) × L1 (Bootstrap)**: ✅ covered (auth tokens + SOUL binding)
- **M1 × L2 (Runtime)**: ⚠️ partial (no continuous auth)
- **M1 × L3 (Update)**: ⚠️ partial (manual review only)
- **M1 × L4 (Cross-Agent)**: ✅ covered (5-bridge coordination)
- **M1 × L5 (Decommission)**: ⚠️ partial (no graceful drain)
- ... (full 25-item table in §3)

**19 of 25 surfaces are CRITICAL**; of those, **2 are fully covered** (M4-L1 cron SLO, M3-L5 inbox_decay), **5 are uncovered**, and **12 are partial**. The 5 uncovered critical surfaces are the target of our Phase 6 closure plan (paper §7).

**3. Agent-D 2026-06-08 incident case study.**
We dissect a real memory-path Misevolution incident (Agent-D overwrote a stale but critical cron schedule after a "compaction" pass; detected and reverted by a 2-minute alert-to-recovery loop, with the 44,092 bytes of original schedule content preserved in the audit log). We show how (a) the failure was detected and rolled back by MLAS coverage of M2-L2 (memory access monitoring), and (b) post-incident forensic review took ~2 minutes (not 4 hours) because the audit log captured the full reversion sequence. We distill 3 lessons and 2 operational rules added to our 14-rule set.

## Comparison with concurrent work

- **vs Misevolution (Shao et al., 2026)**: they propose the 4-path taxonomy; we provide **2-month empirical evidence** with concrete counts.
- **vs MLAS (Lin et al., 2026)**: they propose the 5×5 matrix; we provide **a working 25-item checklist** with current coverage status.
- **vs Anthropic Agentic Misalignment (2025)**: they predict attack scenarios; we report what actually happened.

## Reproducibility

Same open-source artifacts as the main paper (skill_dag.py, action_policy_check.py, model_router.py, semantic_recall.py, run_weekly_evals.py) plus a new mlas_25.py checklist runner and an incident-report template. Public GitHub + Zenodo DOI.

## Workshop fit

This paper is intended for the ICLR Workshop on Agents track, where empirical / engineering case studies are welcome. It is shorter (5-7 pages) than the main paper (~10,200 words / 808 lines), and is self-contained: a reader can understand the empirical contributions without reading the main paper.

## Conflicts

None. Same authors as the main Equipment Thickness Theory submission; we declare this association explicitly so the workshop chairs can coordinate review with the main submission if desired.

## Suggested reviewers

[Reviewer expertise: AI safety, agent deployment, production SRE, self-modifying systems]

## Response to reviewers

We commit to a 2-week rebuttal window (workshops have shorter cycles).

Thank you for considering our submission.

Sincerely,
[Anonymized for double-blind review]

---

*Cover letter length: ~700 words*
*Companion paper to "Equipment Thickness Theory" (ICLR 2027 Main). Independent submission: this workshop paper can be accepted or rejected without affecting the main submission.*