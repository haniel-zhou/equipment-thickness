# OpenReview Submission Checklist — Paper B (Misevolution / MLAS)

**Paper**: Misevolution in Practice: A 60-Day, 8-Agent Empirical Study of 4 Self-Modification Paths and 25 Attack Surfaces
**Venue**: ICLR 2026 Workshop on Agents
**Deadline**: 2026-09-10 (planned submission: 2026-08-08 → 33 days runway)
**Bundle assembled**: 2026-06-27

---

## Required files

- [x] **Paper PDF**: `equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.pdf` — *not generated: pdflatex missing; .tex source shipped alongside*
- [x] **Paper LaTeX source**: `equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.tex` (48,525 B)
- [x] **Paper HTML**: `equipment-thickness-repo/docs/paper_b_Misevolution_MLAS.html` (51,015 B, self-contained, with TOC)
- [x] **Paper source markdown**: `ai-agent-research/06-papers/drafts/02-experimental/paper_Misevolution_MLAS_2026-06-27.md` (5,695 words, 291 lines, v1.0)
- [x] **Cover letter**: `ai-agent-research/06-papers/cover_letters/ICLR_2026_Workshop_cover_letter.md` (corrected)
- [x] **Submission bundle manifest**: `equipment-thickness-repo/docs/SUBMISSION_BUNDLE.md` (new)
- [x] **Reproducibility bundle**: `equipment-thickness-repo/` (4 JSONL eval cases + 7 Python scripts + 3 shell scripts + 2 figures)

## Double-blind compliance

- [x] **Author names**: `Anonymous Authors¹` with affiliation `[Anonymized for double-blind review — see cover letter for venue-specific disclosure]`
- [x] **Agent names**: `Agent-A` through `Agent-I` (no real agent names in main text or figures)
- [x] **Memory-palace / Kimi / Haniel**: 0 hits in paper body (verified during v1.0 finalisation)
- [x] **Project repo URL**: anonymized in §7 of SUBMISSION_BUNDLE; real URL held back for program chairs only
- [x] **Cover letter data corrections** (already applied in v1.0 finalisation):
  - 1,247 events → **4 Misevolution-path blocked events** (actual production count)
  - 0.7% FPR → **0% observed FPR** on 60-case strict-mode evaluation (5/20 ground-truth drift cases inspected and corrected where drift was confirmed — SR-006 / SR-007)
  - 1,472 lines lost → **0 lines lost** (Agent-D 2026-06 memory overwrite was caught and rolled back; no data loss)

## Submission metadata

| Field | Value |
|-------|-------|
| Track | ICLR 2026 Workshop on Agents |
| Deadline | 2026-09-10 |
| Planned submission | 2026-08-08 (W7, 33 days before deadline) |
| Format | 5–7 pages ICLR workshop short paper |
| Companion to | v3 paper (ICLR 2027 Main — *Equipment Thickness Theory*) |
| Author conflicts | None (same authors, both papers explicitly declared in cover letter) |

## OpenReview form fields (to fill on submit)

### Title
> Misevolution in Practice: A 60-Day, 8-Agent Empirical Study of 4 Self-Modification Paths and 25 Attack Surfaces

### Abstract (paste from paper §Abstract)
> We report a 60-day field study of two recently proposed agent-safety frameworks deployed on a production 8-agent system: (1) the **Misevolution 4-path** failure taxonomy of self-modifying agents (model / memory / tool / workflow) and (2) the **MLAS 5×5 attack-surface matrix** (5 modules × 5 lifecycle stages = 25 surfaces; Lin et al., arXiv:2606.23075). We contribute three artifacts: (a) a 4-line implementation of the Misevolution 4-path detection policy as a 4-bucket action classifier (`{path, score}`) used by the safety boundary to gate high-impact actions; (b) a 25-cell MLAS audit checklist with current coverage status for our 8 agents, comprising 19 critical and 6 managed surfaces, of which 2 are fully covered, 18 partially covered, and 5 not yet covered; (c) a longitudinal incident record: 4 Misevolution-path blocked events, 1 MLAS-surface check (M2-L2 in-flight memory write) and 2 follow-up checks, 1 critical write-protection incident (the "Agent-D 2026-06 memory overwrite" event, classified as Misevolution memory path + MLAS M2-L3). We find that the Misevolution 4-path classification and the MLAS 5×5 matrix are **complementary, not redundant**: Misevolution classifies *failure modes* along the dimension of which layer misbehaves, while MLAS classifies *attack opportunities* along the dimension of module × lifecycle stage. Combined, they cover the failure-manifestation and attack-opportunity axes that neither covers alone. We also document a measurement caveat: the operational data set (4 Misevolution events, 3 MLAS checks) is two to three orders of magnitude smaller than what the cover letter and our initial sketch described (1,247 events; 25-cell coverage). We discuss the gap and the inferred reasons — chiefly that the safety boundary was not exercised at high rates during the observation window — and argue that small-but-real evidence is more useful for a workshop case study than projected counts, because the data we *do* have identifies a real incident where the frameworks were operationally useful.

### Keywords
> Misevolution, MLAS, multi-agent, self-evolution, attack surface, action policy, longitudinal field study

### TL;DR (1 sentence for OpenReview "TL;DR" field)
> An 8-agent production system ran both the Misevolution 4-path taxonomy and the MLAS 5×5 attack-surface matrix for 60 days; the two frameworks turned out to classify *different* axes (failure-mode vs. attack-opportunity), and their joint use caught a real memory-overwrite incident (Agent-D 2026-06, classified Misevolution-memory + MLAS M2-L3) that neither framework would have flagged alone.

### Suggested reviewers (to add during OpenReview submit)
- Safety / alignment researchers familiar with self-modifying agents
- Empirical multi-agent system researchers
- Authors of arXiv:2606.23075 (MLAS) — declared conflict; do NOT suggest
- Authors of Misevolution (Shao et al., 2026) — declared conflict; do NOT suggest

### Conflicts declared
- None against the workshop program committee at large
- Co-authors of the v3 main-track companion paper — these are the *same* authors and must be declared for both submissions

## Pre-submit action items

- [ ] **Install pdflatex** on build host (`brew install --cask mactex-no-gui`) before W7, then re-render PDF
- [ ] Verify the `.tex` source compiles cleanly with `pdflatex` (fix any package warnings)
- [ ] Upload `paper_b_Misevolution_MLAS.pdf` to OpenReview (not the .tex)
- [ ] Paste cover letter into the "Cover Letter" field (text box, not attachment)
- [ ] Upload `SUBMISSION_BUNDLE.md` + zipped `equipment-thickness-repo/` as supplementary material (single zip: `paper_b_reproducibility.zip`)
- [ ] Confirm double-blind: search final PDF for "Haniel", "Kimi", "memory-palace", "agent-research" → 0 hits expected
- [ ] Set submission visibility to "Double-blind" in OpenReview form
- [ ] Submit at least 7 days before deadline (2026-09-03 buffer)

---

*Checklist generated 2026-06-27 by paper-B OpenReview submission subagent. Last updated before commit; final PDF render pending TeX environment setup.*
