#!/usr/bin/env python3
"""Action boundary policy engine (Phase 2 of Codex 30-day sprint).

Evaluates high-impact local actions (shell, git, A2A, MCP, fork) against
the action_policy_schema.json ruleset. Returns decision (allow/ask_user/deny)
plus matched rule + audit entry.

Usage:
    action_policy_check.py evaluate \
        --category shell \
        --command "rm -rf /tmp/foo" \
        --args ""

    action_policy_check.py evaluate \
        --category git \
        --command "git push origin main --force" \
        --args "--force origin main"

    action_policy_check.py list-rules [--category SHELL]
    action_policy_check.py validate
    action_policy_check.py dry-run-stats   # aggregate over last audit log entries

Default mode is read-only evaluation (no enforcement). Add --enforce to write
audit entries to action_policy_audit.jsonl.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(__file__).parent / "action_policy_schema.json"
AUDIT_LOG_PATH = Path(__file__).parent / "action_policy_audit.jsonl"
PHASE2_EVAL_PATH = Path(__file__).parent / "action_policy_eval.jsonl"

DECISION_ALLOW = "allow"
DECISION_ALLOW_WITH_AUDIT = "allow_with_audit"
DECISION_ASK_USER = "ask_user"
DECISION_DENY = "deny"
DECISION_ABORT_AND_RECORD = "abort_and_record"


@dataclass
class DecisionRequest:
    category: str          # shell | git | a2a | mcp | fork
    command: str           # e.g., "rm -rf /tmp"
    args: str              # e.g., "-rf /tmp"
    path: str | None       # e.g., "/Users/haniel/workspace/..."
    context: dict[str, Any] | None
    actor: str             # agent_id or human


@dataclass
class MatchedRule:
    rule_id: str
    category: str
    priority: int
    tier: int
    reason: str


@dataclass
class PolicyDecision:
    request: DecisionRequest
    decision: str          # allow | allow_with_audit | ask_user | deny | abort_and_record
    matched_rule: MatchedRule | None
    evaluated_at: str
    schema_version: str
    rationale: str         # human-readable explanation


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_schema() -> dict:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema not found at {SCHEMA_PATH}. "
            "Phase 2 prerequisite: action_policy_schema.json must exist."
        )
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def load_rules(schema: dict) -> list[dict]:
    rules = schema.get("example_rules_v1", [])
    # Sort by priority descending — higher priority rules are evaluated first
    return sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)


def match_rule(rule: dict, req: DecisionRequest) -> bool:
    """Return True if `rule` matches `req` based on rule.match fields."""
    if rule.get("category") != req.category:
        return False

    match = rule.get("match", {})
    cmd_prefix = match.get("command_prefix")
    args_pattern = match.get("args_pattern")
    path_prefix = match.get("path_prefix")
    context_required = match.get("context")

    if cmd_prefix:
        # command_prefix is matched against full command (command + args concatenated)
        full_cmd = f"{req.command} {req.args}".strip()
        if not full_cmd.startswith(cmd_prefix):
            return False

    if args_pattern:
        full_cmd = f"{req.command} {req.args}".strip()
        if not re.search(args_pattern, full_cmd):
            return False

    if path_prefix:
        if not req.path or not req.path.startswith(path_prefix):
            return False

    if context_required:
        # context is a dict like {"has_human_approval": true}
        # All required keys must be present in req.context with matching values
        ctx = req.context or {}
        for k, v in context_required.items():
            if ctx.get(k) != v:
                return False

    return True


def evaluate(req: DecisionRequest, schema: dict | None = None) -> PolicyDecision:
    """Evaluate a DecisionRequest against the policy schema.

    Returns the highest-priority matching rule's decision, or the category's
    default_decision if no rule matches.
    """
    if schema is None:
        schema = load_schema()
    rules = load_rules(schema)

    matched: MatchedRule | None = None
    for rule in rules:
        if match_rule(rule, req):
            matched = MatchedRule(
                rule_id=rule["rule_id"],
                category=rule["category"],
                priority=rule.get("priority", 0),
                tier=rule.get("tier", 1),
                reason=rule.get("reason", ""),
            )
            break

    if matched is not None:
        decision = rule["decision"]
        rationale = (
            f"Matched rule {matched.rule_id} (priority={matched.priority}, "
            f"tier={matched.tier}): {matched.reason}"
        )
    else:
        # No rule matched — use category default
        cat_config = schema.get("categories", {}).get(req.category, {})
        decision = cat_config.get("default_decision", DECISION_ASK_USER)
        rationale = (
            f"No rule matched for category={req.category}. "
            f"Using default_decision={decision}."
        )

    return PolicyDecision(
        request=req,
        decision=decision,
        matched_rule=matched,
        evaluated_at=now_iso(),
        schema_version=schema.get("version", "unknown"),
        rationale=rationale,
    )


def record_audit(decision: PolicyDecision) -> None:
    """Append audit entry to action_policy_audit.jsonl."""
    entry = {
        "evaluated_at": decision.evaluated_at,
        "schema_version": decision.schema_version,
        "category": decision.request.category,
        "command": decision.request.command,
        "args": decision.request.args,
        "path": decision.request.path,
        "context": decision.request.context,
        "actor": decision.request.actor,
        "decision": decision.decision,
        "matched_rule_id": decision.matched_rule.rule_id if decision.matched_rule else None,
        "matched_rule_priority": decision.matched_rule.priority if decision.matched_rule else None,
        "rationale": decision.rationale,
    }
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def cmd_evaluate(args: argparse.Namespace) -> int:
    req = DecisionRequest(
        category=args.category,
        command=args.command,
        args=args.args or "",
        path=args.path,
        context=json.loads(args.context) if args.context else None,
        actor=args.actor or "unknown",
    )
    decision = evaluate(req)

    if args.enforce:
        record_audit(decision)

    # Print structured output as JSON for machine consumption
    output = asdict(decision)
    output["request"] = asdict(req)
    output["matched_rule"] = asdict(decision.matched_rule) if decision.matched_rule else None
    print(json.dumps(output, indent=2, ensure_ascii=False))

    # Exit codes: 0=allow, 1=ask_user, 2=deny, 3=abort_and_record
    exit_map = {
        DECISION_ALLOW: 0,
        DECISION_ALLOW_WITH_AUDIT: 0,
        DECISION_ASK_USER: 1,
        DECISION_DENY: 2,
        DECISION_ABORT_AND_RECORD: 3,
    }
    return exit_map.get(decision.decision, 1)


def cmd_list_rules(args: argparse.Namespace) -> int:
    schema = load_schema()
    rules = load_rules(schema)
    if args.category:
        rules = [r for r in rules if r.get("category") == args.category]
    for r in rules:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate that the schema file is well-formed JSON and required fields exist."""
    try:
        schema = load_schema()
    except Exception as e:
        print(f"FAIL: schema load error: {e}", file=sys.stderr)
        return 1

    required_top = ["$schema", "title", "version", "categories", "example_rules_v1"]
    missing = [k for k in required_top if k not in schema]
    if missing:
        print(f"FAIL: missing top-level keys: {missing}", file=sys.stderr)
        return 1

    required_categories = ["shell", "git", "a2a", "mcp", "fork"]
    missing_cats = [c for c in required_categories if c not in schema["categories"]]
    if missing_cats:
        print(f"FAIL: missing categories: {missing_cats}", file=sys.stderr)
        return 1

    valid_decisions = {
        DECISION_ALLOW, DECISION_ALLOW_WITH_AUDIT,
        DECISION_ASK_USER, DECISION_DENY, DECISION_ABORT_AND_RECORD,
    }
    for rule in schema["example_rules_v1"]:
        if rule.get("decision") not in valid_decisions:
            print(f"FAIL: rule {rule.get('rule_id')} has invalid decision {rule.get('decision')}", file=sys.stderr)
            return 1
        if rule.get("priority", 0) < 1 or rule.get("priority", 0) > 1000:
            print(f"FAIL: rule {rule.get('rule_id')} has out-of-range priority", file=sys.stderr)
            return 1

    print(f"OK: schema {schema.get('version')} validated. "
          f"{len(schema['example_rules_v1'])} rules, "
          f"{len(schema['categories'])} categories.")
    return 0


def cmd_dry_run_stats(args: argparse.Namespace) -> int:
    """Aggregate stats over the last N audit log entries."""
    if not AUDIT_LOG_PATH.exists():
        print("No audit log found yet. Run with --enforce first.")
        return 0

    entries = []
    with open(AUDIT_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        print("Audit log is empty.")
        return 0

    n = min(args.last, len(entries))
    recent = entries[-n:]

    by_decision: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_rule: dict[str, int] = {}
    for e in recent:
        by_decision[e["decision"]] = by_decision.get(e["decision"], 0) + 1
        by_category[e["category"]] = by_category.get(e["category"], 0) + 1
        if e.get("matched_rule_id"):
            by_rule[e["matched_rule_id"]] = by_rule.get(e["matched_rule_id"], 0) + 1

    print(f"=== Dry-run stats over last {n} audit entries ===")
    print(f"\nBy decision:")
    for d, c in sorted(by_decision.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
    print(f"\nBy category:")
    for cat, c in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {c}")
    print(f"\nTop matched rules:")
    for rid, c in sorted(by_rule.items(), key=lambda x: -x[1])[:10]:
        print(f"  {rid}: {c}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Action boundary policy engine (Phase 2)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_eval = sub.add_parser("evaluate", help="Evaluate a DecisionRequest")
    p_eval.add_argument("--category", required=True,
                        choices=["shell", "git", "a2a", "mcp", "fork"])
    p_eval.add_argument("--command", required=True,
                        help="The primary command, e.g. 'rm' or 'git push'")
    p_eval.add_argument("--args", default="",
                        help="The arguments portion, e.g. '-rf /tmp'")
    p_eval.add_argument("--path", default=None,
                        help="Target path if applicable")
    p_eval.add_argument("--context", default=None,
                        help="JSON context dict, e.g. '{\"has_human_approval\": true}'")
    p_eval.add_argument("--actor", default="unknown",
                        help="Actor (agent_id or 'human')")
    p_eval.add_argument("--enforce", action="store_true",
                        help="Write audit entry (default: dry-run)")
    p_eval.set_defaults(func=cmd_evaluate)

    p_list = sub.add_parser("list-rules", help="List all rules")
    p_list.add_argument("--category", default=None,
                        choices=["shell", "git", "a2a", "mcp", "fork"])
    p_list.set_defaults(func=cmd_list_rules)

    p_val = sub.add_parser("validate", help="Validate schema well-formedness")
    p_val.set_defaults(func=cmd_validate)

    p_stats = sub.add_parser("dry-run-stats", help="Aggregate stats from audit log")
    p_stats.add_argument("--last", type=int, default=100,
                         help="Number of recent entries to aggregate (default 100)")
    p_stats.set_defaults(func=cmd_dry_run_stats)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())