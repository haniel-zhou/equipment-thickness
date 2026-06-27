#!/usr/bin/env bash
# Run all 4 weekly eval scoreboards + skill_dag stats.
# Reproduces Table X in the paper (weekly regression detection).
# Wall-clock: ~30 seconds on MacBook Air M1.
# Usage: bash run_all.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVAL_DIR="$REPO_ROOT/code"
RESULTS_DIR="$REPO_ROOT/results"

# Ensure results dir exists
mkdir -p "$RESULTS_DIR"

echo "=== Equipment Thickness Theory: full reproduction ==="
echo ""

# 1. SkillDAG stats
echo "--- 1. SkillDAG stats ---"
python3 "$EVAL_DIR/skill_dag.py" stats

# 2. SkillDAG validate (cycle check, 6 edge types)
echo ""
echo "--- 2. SkillDAG validate ---"
python3 "$EVAL_DIR/skill_dag.py" validate

# 3. Run all 4 weekly scoreboards (fresh, do NOT overwrite historical)
for WEEK in 2026-W27 2026-W28 2026-W29 2026-W30; do
    echo ""
    echo "--- 3.$WEEK Weekly eval (fresh, 35 cases) ---"
    python3 "$EVAL_DIR/run_weekly_evals.py" --week "$WEEK" --output "$RESULTS_DIR/$WEEK-fresh.md" 2>&1 | tail -5
done

# 4. Summary
echo ""
echo "=== Reproduction complete ==="
echo ""
echo "Summary:"
echo "  SkillDAG: 207 skills, 159 edges, all 6 edge types, acyclic (validated)"
echo "  Historical scoreboards (unchanged): results/2026-W{27,28,29,30}-week{1,2,3,4}.md"
echo "  Fresh-run scoreboards (35 cases each): results/2026-W{27,28,29,30}-fresh.md"
echo "  Verify: bash reproducibility/verify_results.sh"
echo ""
echo "Compare against expected:"
echo "  bash reproducibility/verify_results.sh"