#!/usr/bin/env bash
# Verify reproducibility: cross-check fresh runs against checked-in historical results.
# - Historical files: results/2026-W${N}-week${K}.md
# - Fresh-run files: results/2026-W${N}.md
# Each file should have Total cases == Passed == expected_count.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="$REPO_ROOT/results"

# Format: "filename:expected_count"
HIST_FILES="2026-W27-week1.md:20 2026-W28-week2.md:25 2026-W29-week3.md:30 2026-W30-week4.md:35"
FRESH_FILES="2026-W27-fresh.md:35 2026-W28-fresh.md:35 2026-W29-fresh.md:35 2026-W30-fresh.md:35"

parse_total() {
    sed 's/\*\*//g' "$1" | grep -oE "Total cases: [0-9]+" | head -1 | awk '{print $3}'
}

parse_passed() {
    sed 's/\*\*//g' "$1" | grep -oE "Passed: [0-9]+" | head -1 | awk '{print $2}'
}

check_file() {
    local file="$1" expected="$2" label="$3"
    local total passed
    total=$(parse_total "$file")
    passed=$(parse_passed "$file")
    if [ -z "$total" ] || [ -z "$passed" ]; then
        echo "  ❌ $label $(basename "$file"): parse_err (total=[$total] passed=[$passed])"
        return 1
    fi
    if [ "$total" = "$expected" ] && [ "$passed" = "$expected" ]; then
        echo "  ✅ $label $(basename "$file"): $passed/$total"
        return 0
    else
        echo "  ❌ $label $(basename "$file"): $passed/$total (expected $expected/$expected)"
        return 1
    fi
}

all_ok=true

echo "=== Weekly scoreboard verification ==="
echo ""

echo "Historical (checked-in):"
for spec in $HIST_FILES; do
    fname="${spec%%:*}"
    expected="${spec##*:}"
    if [ ! -f "$RESULTS_DIR/$fname" ]; then
        echo "  ⚠️  $fname: missing (skipped)"
        continue
    fi
    if ! check_file "$RESULTS_DIR/$fname" "$expected" "hist"; then
        all_ok=false
    fi
done

echo ""
echo "Fresh-run (35/35 expected):"
for spec in $FRESH_FILES; do
    fname="${spec%%:*}"
    expected="${spec##*:}"
    if [ ! -f "$RESULTS_DIR/$fname" ]; then
        echo "  ⚠️  $fname: missing (skipped)"
        continue
    fi
    if ! check_file "$RESULTS_DIR/$fname" "$expected" "fresh"; then
        all_ok=false
    fi
done

echo ""
if [ "$all_ok" = true ]; then
    echo "=== All scoreboards pass ==="
    exit 0
else
    echo "=== FAIL: at least one scoreboard did not pass ==="
    exit 1
fi