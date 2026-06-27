#!/usr/bin/env python3
"""Weekly evaluation harness (Phase 6 Codex 30-day sprint pre-implementation).

Runs a fixed set of 20 evaluation cases against the action policy engine +
model router, and emits a weekly scoreboard. This is the Phase 6 deliverable
in skeleton form; full Phase 6 (20 evals + weekly_history + dashboard)
lands on Day 20-30.

Usage:
    run_weekly_evals.py --week 2026-W27 [--output weekly_report.md]

The 20 cases cover:
  - 6 action_policy_check shell cases (rm -rf, write, etc.)
  - 4 action_policy_check git cases (force-push, reset, rebase)
  - 3 action_policy_check a2a cases (single, broadcast, fork)
  - 2 action_policy_check mcp cases (hung, fast)
  - 5 model_router cases (classification, architecture_review, etc.)

Exit code:
  0 = all cases passed
  1 = some cases failed
  2 = infrastructure error (schema not found, etc.)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


POLICY_DIR = Path(__file__).parent / "policy"
ROUTER_DIR = Path(__file__).parent / "model-router"
REPORTS_DIR = Path(__file__).parent.parent / "results"
ACTION_POLICY_EVAL = Path(__file__).parent.parent / "eval_cases" / "action_policy_eval.jsonl"


@dataclass
class EvalCase:
    case_id: str
    description: str
    category: str          # "shell" | "git" | "a2a" | "mcp" | "model_route"
    command_args: list[str]
    expected_decision: str
    expected_rule_id: str | None = None
    passed: bool = False
    actual_decision: str = ""
    actual_rule_id: str = ""
    error: str = ""


@dataclass
class WeeklyScoreboard:
    week: str
    run_at: str
    total_cases: int
    passed: int
    failed: int
    pass_rate: float
    categories: dict[str, dict[str, int]] = field(default_factory=dict)
    completion_rate_baseline: float | None = None
    completion_rate_current: float | None = None
    local_ratio: float | None = None
    cost_ceiling_violations: int = 0
    notes: str = ""


# 20 fixed weekly eval cases (one canonical set; full eval set is action_policy_eval.jsonl)
WEEKLY_CASES: list[EvalCase] = [
    # 6 shell cases
    EvalCase("W01", "rm -rf / denied", "shell",
             ["evaluate", "--category", "shell", "--command", "rm", "--args", "-rf /",
              "--actor", "kimi", "--enforce"],
             "deny", "shell.destructive.rm_rf_root"),
    EvalCase("W02", "rm -rf workspace ask_user", "shell",
             ["evaluate", "--category", "shell", "--command", "rm", "--args", "-rf /Users/haniel/workspace/foo",
              "--actor", "kimi", "--enforce"],
             "ask_user", "shell.destructive.rm_rf_workspace"),
    EvalCase("W03", "Write workspace allow_with_audit", "shell",
             ["evaluate", "--category", "shell", "--command", "Write", "--args", "",
              "--path", "/Users/haniel/workspace/research/ai-agent-research/", "--actor", "kimi", "--enforce"],
             "allow_with_audit", "shell.write_local.kimi_workspace_safe"),
    EvalCase("W04", "Read workspace default ask_user", "shell",
             ["evaluate", "--category", "shell", "--command", "Read", "--args", "",
              "--path", "/Users/haniel/workspace/research/ai-agent-research/", "--actor", "kimi", "--enforce"],
             "ask_user", None),
    EvalCase("W05", "grep safe ask_user", "shell",
             ["evaluate", "--category", "shell", "--command", "grep", "--args", "-r TODO",
              "--actor", "kimi", "--enforce"],
             "ask_user", None),
    EvalCase("W06", "rm -rf /etc ask_user", "shell",
             ["evaluate", "--category", "shell", "--command", "rm", "--args", "-rf /etc/passwd",
              "--actor", "kimi", "--enforce"],
             "ask_user", "shell.destructive.rm_rf_workspace"),

    # 4 git cases
    EvalCase("W07", "git push main --force denied", "git",
             ["evaluate", "--category", "git", "--command", "git push", "--args", "origin main --force",
              "--actor", "kimi", "--enforce"],
             "deny", "git.destructive.force_push_main_branch"),
    EvalCase("W08", "git push feature --force ask_user", "git",
             ["evaluate", "--category", "git", "--command", "git push", "--args", "origin feature --force",
              "--actor", "kimi", "--enforce"],
             "ask_user", "git.destructive.force_push_any"),
    EvalCase("W09", "git reset --hard ask_user", "git",
             ["evaluate", "--category", "git", "--command", "git reset", "--args=--hard",
              "--actor", "kimi", "--enforce"],
             "ask_user", "git.destructive.reset_hard"),
    EvalCase("W10", "git rebase ask_user", "git",
             ["evaluate", "--category", "git", "--command", "git rebase", "--args", "-i HEAD~3",
              "--actor", "kimi", "--enforce"],
             "ask_user", "git.history_rewrite.rebase"),

    # 3 a2a cases
    EvalCase("W11", "a2a single agent allow_with_audit", "a2a",
             ["evaluate", "--category", "a2a", "--command", "a2a.send", "--args", "recipients=kimi",
              "--actor", "kimi", "--enforce"],
             "allow_with_audit", None),
    EvalCase("W12", "a2a broadcast 6+ ask_user", "a2a",
             ["evaluate", "--category", "a2a", "--command", "a2a.send",
              "--args", "recipients=kimi,sojourner,ezra,meridian,kadmiel,morrow",
              "--actor", "kimi", "--enforce"],
             "ask_user", "a2a.broadcast_to_all"),
    EvalCase("W13", "a2a fork depth=5 denied", "a2a",
             ["evaluate", "--category", "a2a", "--command", "a2a.fork", "--args", "depth=5",
              "--actor", "kimi", "--enforce"],
             "deny", "a2a.fork_depth_too_deep"),

    # 2 mcp cases
    EvalCase("W14", "mcp call fast allow_with_audit", "mcp",
             ["evaluate", "--category", "mcp", "--command", "mcp.call", "--args", "tool=ruflo_search idle_seconds=5",
              "--actor", "kimi", "--enforce"],
             "allow_with_audit", None),
    EvalCase("W15", "mcp hung call 45s abort_and_record", "mcp",
             ["evaluate", "--category", "mcp", "--command", "mcp.call", "--args", "tool=ruflo_search idle_seconds=45",
              "--actor", "kimi", "--enforce"],
             "abort_and_record", "mcp.hung_call"),

    # 5 model router cases
    EvalCase("W16", "model route classification local", "model_route",
             ["route", "--category", "classification", "--actor", "kimi"],
             "local"),
    EvalCase("W17", "model route architecture_review cloud", "model_route",
             ["route", "--category", "architecture_review", "--actor", "kimi"],
             "anthropic"),
    EvalCase("W18", "model route policy_evaluation confidential local", "model_route",
             ["route", "--category", "policy_evaluation", "--data-classification", "confidential",
              "--contains-pii", "--actor", "kimi"],
             "local"),
    EvalCase("W19", "model route research_synthesis google", "model_route",
             ["route", "--category", "research_synthesis", "--input-tokens", "200000",
              "--actor", "kimi"],
             "google"),
    EvalCase("W20", "model route cron_diagnosis local", "model_route",
             ["route", "--category", "cron_diagnosis", "--actor", "kimi"],
             "local"),
    # Phase 4 semantic_recall cases (Week 2 expansion)
    EvalCase("W21", "semantic recall hybrid top-5", "semantic_recall",
             ["query", "DGM self-modifying agent safety", "--mode", "hybrid"],
             "chunk_id"),
    EvalCase("W22", "semantic recall keyword mode top-5", "semantic_recall",
             ["query", "ICA model layer architecture 6 layers", "--mode", "keyword"],
             "chunk_id"),
    EvalCase("W23", "semantic recall semantic mode top-5", "semantic_recall",
             ["query", "anthropic teaching claude why", "--mode", "semantic"],
             "chunk_id"),
    EvalCase("W24", "semantic recall build-index", "semantic_recall",
             ["build-index"],
             "OK"),
    EvalCase("W25", "semantic recall stats", "semantic_recall",
             ["stats"],
             "Total chunks:"),
    # Phase 5 SkillDAG cases (Week 3 expansion)
    EvalCase("W26", "skill_dag validate", "skill_dag",
             ["validate"],
             "OK:"),
    EvalCase("W27", "skill_dag recommend code audit", "skill_dag",
             ["recommend", "code audit and review", "--chain"],
             "code_audit"),
    EvalCase("W28", "skill_dag recommend safety escalate risk", "skill_dag",
             ["recommend", "safety check and policy check", "--chain"],
             "risk_escalation"),
    EvalCase("W29", "skill_dag stats", "skill_dag",
             ["stats"],
             "DAG stats:"),
    EvalCase("W30", "skill_dag top50", "skill_dag",
             ["top50"],
             "most-connected skills:"),
    # Phase 6 W30 expansion: 30 → 35 cases (Codex 30-day sprint Phase 6 closure)
    EvalCase("W31", "skill_dag 207 skills full coverage", "skill_dag",
             ["stats"],
             "Total skills: 207"),
    EvalCase("W32", "skill_dag recommend knowledge graph", "skill_dag",
             ["recommend", "knowledge graph and validate", "--chain"],
             "knowledge_graph"),
    EvalCase("W33", "skill_dag recommend devops deploy", "skill_dag",
             ["recommend", "deploy and monitor with health check", "--chain"],
             "devops_deploy"),
    EvalCase("W34", "skill_dag recommend content SEO", "skill_dag",
             ["recommend", "content seo for blog post", "--chain"],
             "content_seo"),
    EvalCase("W35", "skill_dag 6 edge types all present", "skill_dag",
             ["validate"],
             "all 6 edge types"),
]


def run_one_case(case: EvalCase) -> EvalCase:
    """Run a single eval case and verify it matches expected."""
    CODE_DIR = Path(__file__).parent
    if case.category == "model_route":
        cmd = ["python3", "model_router.py"] + case.command_args
        cwd = CODE_DIR / "model-router"
    elif case.category == "semantic_recall":
        cmd = ["python3", "semantic_recall.py"] + case.command_args
        cwd = CODE_DIR / "memory"
    elif case.category == "skill_dag":
        cmd = ["python3", "skill_dag.py"] + case.command_args
        cwd = CODE_DIR / "skill-dag"
    else:
        cmd = ["python3", "action_policy_check.py"] + case.command_args
        cwd = CODE_DIR / "policy"

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=30)
        if case.category in ("semantic_recall", "skill_dag"):
            # These return JSON or plain text; check stdout for expected substring
            case.actual_decision = "OK" if result.returncode == 0 else f"FAIL rc={result.returncode}"
            case.passed = (
                result.returncode == 0
                and case.expected_decision in (result.stdout + result.stderr)
            )
            if not case.passed:
                case.error = f"missing '{case.expected_decision}' in output"
            return case

        if result.returncode not in (0, 1, 2, 3):
            case.error = f"unexpected rc={result.returncode}: {result.stderr[:200]}"
            return case
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            case.error = f"invalid JSON: {result.stdout[:200]}"
            return case

        if case.category == "model_route":
            case.actual_decision = data["decision"]["decision_provider"]
            case.actual_rule_id = "(route)"
        else:
            case.actual_decision = data["decision"]
            rule = data.get("matched_rule")
            case.actual_rule_id = rule["rule_id"] if rule else "(default)"

        case.passed = (case.actual_decision == case.expected_decision)
        if case.expected_rule_id and case.actual_rule_id != case.expected_rule_id:
            case.passed = False
            case.error = f"rule_id mismatch: expected {case.expected_rule_id} got {case.actual_rule_id}"
    except subprocess.TimeoutExpired:
        case.error = "subprocess timeout (30s)"
    except Exception as e:
        case.error = f"exception: {e}"

    return case


def build_scoreboard(week: str, cases: list[EvalCase]) -> WeeklyScoreboard:
    """Aggregate case results into a weekly scoreboard."""
    by_cat: dict[str, dict[str, int]] = {}
    for c in cases:
        cat = c.category
        if cat not in by_cat:
            by_cat[cat] = {"passed": 0, "failed": 0}
        if c.passed:
            by_cat[cat]["passed"] += 1
        else:
            by_cat[cat]["failed"] += 1

    passed = sum(1 for c in cases if c.passed)
    return WeeklyScoreboard(
        week=week,
        run_at=datetime.now(timezone.utc).isoformat(),
        total_cases=len(cases),
        passed=passed,
        failed=len(cases) - passed,
        pass_rate=round(passed / len(cases), 4) if cases else 0,
        categories=by_cat,
    )


def render_markdown(sb: WeeklyScoreboard, cases: list[EvalCase]) -> str:
    """Render scoreboard as Markdown."""
    lines = [
        f"# Weekly Eval Scoreboard — {sb.week}",
        "",
        f"> **Run at**: {sb.run_at}",
        f"> **Total cases**: {sb.total_cases}",
        f"> **Passed**: {sb.passed} ({sb.pass_rate * 100:.1f}%)",
        f"> **Failed**: {sb.failed}",
        "",
        "## Category breakdown",
        "",
        "| Category | Passed | Failed | Pass rate |",
        "|----------|--------|--------|-----------|",
    ]
    for cat, stats in sorted(sb.categories.items()):
        total = stats["passed"] + stats["failed"]
        rate = stats["passed"] / total * 100 if total else 0
        lines.append(f"| {cat} | {stats['passed']} | {stats['failed']} | {rate:.1f}% |")

    lines.extend([
        "",
        "## Case-level results",
        "",
        "| Case | Description | Expected | Actual | Rule | Pass |",
        "|------|-------------|----------|--------|------|------|",
    ])
    for c in cases:
        status = "✅" if c.passed else "❌"
        lines.append(
            f"| {c.case_id} | {c.description} | {c.expected_decision} | "
            f"{c.actual_decision or '(err)'} | {c.actual_rule_id or '-'} | {status} |"
        )

    failed_cases = [c for c in cases if not c.passed]
    if failed_cases:
        lines.extend(["", "## Failed cases (debug)", ""])
        for c in failed_cases:
            lines.append(f"- **{c.case_id}** ({c.description}): expected={c.expected_decision} "
                         f"actual={c.actual_decision} rule={c.actual_rule_id} error={c.error}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run weekly eval harness")
    parser.add_argument("--week", default="2026-W27",
                        help="ISO week label, e.g. 2026-W27")
    parser.add_argument("--output", default=None,
                        help="Output markdown report path")
    parser.add_argument("--json", action="store_true",
                        help="Also emit JSON scoreboard")
    args = parser.parse_args()

    print(f"Running {len(WEEKLY_CASES)} weekly eval cases for {args.week}...")
    cases = []
    for case in WEEKLY_CASES:
        run_one_case(case)
        cases.append(case)
        status = "✅" if case.passed else "❌"
        print(f"  {status} {case.case_id}: {case.description}")

    scoreboard = build_scoreboard(args.week, cases)
    md = render_markdown(scoreboard, cases)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md)
        print(f"\nMarkdown report: {out}")
    else:
        print("\n" + md)

    if args.json:
        json_out = Path(args.output).with_suffix(".json") if args.output else None
        json_data = {
            "scoreboard": asdict(scoreboard),
            "cases": [asdict(c) for c in cases],
        }
        if json_out:
            json_out.write_text(json.dumps(json_data, indent=2))
            print(f"JSON report: {json_out}")
        else:
            print(json.dumps(json_data, indent=2))

    return 0 if scoreboard.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())