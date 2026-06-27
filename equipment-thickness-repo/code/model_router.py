#!/usr/bin/env python3
"""Model Router v1.0 (Phase 3 Codex 30-day sprint).

Routes tasks to local vs cloud models based on task category, complexity,
data sensitivity, and cost ceiling. Every routed call emits a decision_log
entry with 10+ fields for audit + post-hoc analysis.

Usage:
    model_router.py route \
        --category code_generation \
        --input-tokens 5000 \
        --complexity 0.8 \
        --data-classification internal \
        --actor kimi

    model_router.py route --category architecture_review --actor kimi
    model_router.py route --category policy_evaluation --data-classification confidential

    model_router.py record-actual \
        --log-id <uuid> \
        --actual-provider anthropic \
        --actual-model claude-sonnet-4.6 \
        --actual-cost 0.012 \
        --latency-ms 850 \
        --success true

    model_router.py stats [--last 100]

Default mode is read-only. Use --enforce to actually invoke the routed model
(not implemented yet — Phase 3 v1 only emits routing decisions; actual model
invocation is the caller's responsibility).
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


POLICY_PATH = Path(__file__).parent / "model_policy.json"
DECISION_LOG_PATH = Path(__file__).parent / "model_decision_log.jsonl"


@dataclass
class RouteRequest:
    category: str
    input_tokens_estimate: int
    complexity_score: float          # 0..1
    data_classification: str         # public|internal|confidential|secret
    cost_ceiling_usd: float | None
    contains_pii_or_secret: bool
    actor: str = "kimi"
    first_call_in_session: bool = False
    session_id: str | None = None


@dataclass
class RouteDecision:
    decision_provider: str
    decision_model: str
    decision_rationale: str
    matched_rule_id: str | None
    fallback_chain: list[dict[str, str]]
    estimated_cost_usd: float
    log_id: str
    timestamp: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_policy() -> dict:
    if not POLICY_PATH.exists():
        raise FileNotFoundError(f"model_policy.json not found at {POLICY_PATH}")
    with open(POLICY_PATH) as f:
        return json.load(f)


def estimate_cost(provider: str, model: str, input_tokens: int,
                 output_tokens: int, policy: dict) -> float:
    """Estimate cost in USD for a given provider+model+token counts."""
    pconfig = policy["providers"].get(provider)
    if not pconfig:
        return 0.0
    cost_per_1k = pconfig.get("cost_per_1k_tokens", 0.0)
    return cost_per_1k * (input_tokens + output_tokens) / 1000


def match_rule(rule: dict, req: RouteRequest, policy: dict,
               cost_ceiling_exceeded: bool = False) -> bool:
    """Return True if `rule` matches `req`."""
    rule_cat = rule.get("category")
    if rule_cat != "*" and rule_cat != req.category:
        return False

    match = rule.get("match", {})

    if "complexity_score_gte" in match:
        if req.complexity_score < match["complexity_score_gte"]:
            return False

    if "min_loc_tokens" in match:
        loc = req.input_tokens_estimate / 4
        if loc < match["min_loc_tokens"]:
            return False

    if "contains_pii_or_secret" in match:
        if bool(match["contains_pii_or_secret"]) != req.contains_pii_or_secret:
            return False

    if "data_classification" in match:
        allowed = match["data_classification"]
        if isinstance(allowed, list) and req.data_classification not in allowed:
            return False
        if isinstance(allowed, str) and req.data_classification != allowed:
            return False

    if "cost_ceiling_exceeded" in match:
        if bool(match["cost_ceiling_exceeded"]) != cost_ceiling_exceeded:
            return False

    if "first_call_in_session" in match:
        if bool(match["first_call_in_session"]) != req.first_call_in_session:
            return False

    return True


def select_route(req: RouteRequest, policy: dict) -> RouteDecision:
    """Resolve a RouteDecision for the given request."""
    cat_config = policy["task_categories"].get(req.category)
    if not cat_config:
        raise ValueError(
            f"Unknown task_category: {req.category}. "
            f"Valid: {list(policy['task_categories'].keys())}"
        )

    # Pre-compute cost ceiling for rule matching
    cost_ceiling = req.cost_ceiling_usd
    if cost_ceiling is None:
        cost_ceiling = cat_config.get("cost_ceiling_per_call_usd", 1.0)
    output_tokens = cat_config.get("max_tokens", 4000) // 4

    # Resolve preferred provider to concrete provider name
    preferred = cat_config["preferred"]
    if preferred == "cloud":
        # Use the provider named in the category (e.g., anthropic, google)
        concrete_provider = cat_config["model"].split("-")[0] if "-" in cat_config["model"] else preferred
        # Map known model prefixes to providers
        if cat_config["model"].startswith("claude"):
            concrete_provider = "anthropic"
        elif cat_config["model"].startswith("gpt"):
            concrete_provider = "openai"
        elif cat_config["model"].startswith("gemini"):
            concrete_provider = "google"
        else:
            concrete_provider = "anthropic"  # safe default for "cloud"
    else:
        concrete_provider = preferred

    # Pre-estimate cost for the default route
    est_cost = estimate_cost(concrete_provider, cat_config["model"],
                             req.input_tokens_estimate, output_tokens, policy)
    cost_exceeded = est_cost > cost_ceiling

    rules = sorted(
        policy["routing_rules"]["rules"],
        key=lambda r: r.get("priority", 0), reverse=True,
    )
    matched_rule_id = None
    decision_provider = None
    decision_model = None
    rationale_parts = []

    for rule in rules:
        if match_rule(rule, req, policy, cost_ceiling_exceeded=cost_exceeded):
            matched_rule_id = rule["rule_id"]
            decision_provider = rule["decision"]
            decision_model = rule["model"]
            rationale_parts.append(f"Matched rule {rule['rule_id']} (priority={rule['priority']}): {rule['reason']}")
            break

    if decision_provider is None:
        decision_provider = concrete_provider
        decision_model = cat_config["model"]
        rationale_parts.append(
            f"No rule matched for category={req.category}. "
            f"Using category default ({decision_provider}/{decision_model})."
        )

    # Re-check cost on the chosen provider
    final_cost = estimate_cost(decision_provider, decision_model,
                               req.input_tokens_estimate, output_tokens, policy)
    if final_cost > cost_ceiling and decision_provider != "local":
        rationale_parts.append(
            f"Cost ${final_cost:.4f} exceeds ceiling ${cost_ceiling:.4f}. "
            f"Downgrading to local/MiniMax-M3."
        )
        decision_provider = "local"
        decision_model = "MiniMax-M3"
        final_cost = 0.0

    fallback_chain = []
    if decision_provider in ("anthropic", "openai", "google") or decision_provider == "cloud":
        fallback_chain.append({"provider": "local", "model": "MiniMax-M3"})

    rationale = " ".join(rationale_parts)
    log_id = str(uuid.uuid4())

    return RouteDecision(
        decision_provider=decision_provider,
        decision_model=decision_model,
        decision_rationale=rationale,
        matched_rule_id=matched_rule_id,
        fallback_chain=fallback_chain,
        estimated_cost_usd=round(final_cost, 6),
        log_id=log_id,
        timestamp=now_iso(),
    )


def emit_decision_log(req: RouteRequest, decision: RouteDecision) -> dict:
    """Build full 10+-field decision_log entry per schema."""
    return {
        "log_id": decision.log_id,
        "timestamp": decision.timestamp,
        "actor": req.actor,
        "task_category": req.category,
        "input_tokens_estimate": req.input_tokens_estimate,
        "output_tokens_estimate": 1000,
        "complexity_score": req.complexity_score,
        "data_classification": req.data_classification,
        "cost_ceiling_usd": req.cost_ceiling_usd,
        "matched_rule_id": decision.matched_rule_id,
        "decision_provider": decision.decision_provider,
        "decision_model": decision.decision_model,
        "decision_rationale": decision.decision_rationale,
        "fallback_chain": decision.fallback_chain,
        "actual_provider_used": None,
        "actual_model_used": None,
        "actual_cost_usd": None,
        "latency_ms": None,
        "success": None,
        "error_class": None,
    }


def write_decision_log(entry: dict) -> None:
    DECISION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DECISION_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def cmd_route(args: argparse.Namespace) -> int:
    req = RouteRequest(
        category=args.category,
        input_tokens_estimate=args.input_tokens,
        complexity_score=args.complexity,
        data_classification=args.data_classification,
        cost_ceiling_usd=args.cost_ceiling,
        contains_pii_or_secret=args.contains_pii,
        actor=args.actor,
        first_call_in_session=args.first_call_in_session,
    )
    policy = load_policy()
    decision = select_route(req, policy)
    entry = emit_decision_log(req, decision)

    if not args.dry_run:
        write_decision_log(entry)
        decision_written_to_log = True
    else:
        decision_written_to_log = False

    output = {
        "decision": asdict(decision),
        "log_entry": entry,
        "audit_logged": decision_written_to_log,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_record_actual(args: argparse.Namespace) -> int:
    """Update an existing decision_log entry with actual call results."""
    if not DECISION_LOG_PATH.exists():
        print(f"No decision log at {DECISION_LOG_PATH}", file=sys.stderr)
        return 1

    entries = []
    with open(DECISION_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    found = False
    for e in entries:
        if e.get("log_id") == args.log_id:
            e["actual_provider_used"] = args.actual_provider
            e["actual_model_used"] = args.actual_model
            e["actual_cost_usd"] = args.actual_cost
            e["latency_ms"] = args.latency_ms
            e["success"] = args.success.lower() == "true"
            if args.error_class:
                e["error_class"] = args.error_class
            found = True
            break

    if not found:
        print(f"log_id {args.log_id} not found", file=sys.stderr)
        return 1

    with open(DECISION_LOG_PATH, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    print(f"Updated log_id={args.log_id}: actual={args.actual_provider}/{args.actual_model}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Aggregate decision_log stats.

    Fallback rate is measured as: (cloud decisions where the actual call
    FELL BACK to local) / total decisions. This is the correct operational
    definition: "how often did our primary cloud route fail and we needed
    the local fallback?" Empty fallback_chain (cloud with no fallback)
    should NOT count toward fallback rate.
    """
    if not DECISION_LOG_PATH.exists():
        print("No decision log yet. Run route first.")
        return 0

    entries = []
    with open(DECISION_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        print("Decision log empty.")
        return 0

    n = min(args.last, len(entries))
    recent = entries[-n:]

    by_provider: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_rule: dict[str, int] = {}
    total_cost_estimate = 0.0
    local_count = 0
    fallback_invoked = 0  # actual call fell back to local

    for e in recent:
        by_provider[e["decision_provider"]] = by_provider.get(e["decision_provider"], 0) + 1
        by_category[e["task_category"]] = by_category.get(e["task_category"], 0) + 1
        rid = e.get("matched_rule_id") or "(category default)"
        by_rule[rid] = by_rule.get(rid, 0) + 1
        total_cost_estimate += e.get("estimated_cost_usd", 0) or 0
        if e["decision_provider"] == "local":
            local_count += 1
        # Fallback invoked = decision was cloud but actual_provider_used is local
        if (e["decision_provider"] != "local"
                and e.get("actual_provider_used") == "local"):
            fallback_invoked += 1

    local_ratio = local_count / n if n else 0
    fallback_rate = fallback_invoked / n if n else 0

    print(f"=== Model Router stats over last {n} decisions ===")
    print(f"\nLocal ratio: {local_ratio:.1%} (target >= 60%)")
    print(f"Fallback invoked rate: {fallback_rate:.1%} (target < 5%, "
          f"only counts when actual call fell back from cloud to local)")
    print(f"Total estimated cost: ${total_cost_estimate:.4f}")
    print(f"\nBy provider:")
    for p, c in sorted(by_provider.items(), key=lambda x: -x[1]):
        print(f"  {p}: {c}")
    print(f"\nBy category:")
    for cat, c in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {c}")
    print(f"\nBy matched rule (top 10):")
    for rid, c in sorted(by_rule.items(), key=lambda x: -x[1])[:10]:
        print(f"  {rid}: {c}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate policy file well-formedness."""
    try:
        policy = load_policy()
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    required_top = ["version", "providers", "task_categories", "routing_rules", "decision_log_schema"]
    missing = [k for k in required_top if k not in policy]
    if missing:
        print(f"FAIL: missing top-level keys: {missing}", file=sys.stderr)
        return 1

    valid_providers = set(policy["providers"].keys()) | {"cloud"}
    for cat, cfg in policy["task_categories"].items():
        if cfg.get("preferred") not in valid_providers:
            print(f"FAIL: category {cat} preferred={cfg.get('preferred')} not in providers", file=sys.stderr)
            return 1

    log_fields = policy["decision_log_schema"]
    required_log_fields = [
        "log_id", "timestamp", "actor", "task_category",
        "decision_provider", "decision_model", "matched_rule_id",
        "decision_rationale", "estimated_cost_usd",
    ]
    missing_log = [f for f in required_log_fields if f not in log_fields]
    if missing_log:
        print(f"FAIL: missing log fields: {missing_log}", file=sys.stderr)
        return 1

    print(f"OK: model_policy.json v{policy['version']} validated. "
          f"{len(policy['providers'])} providers, "
          f"{len(policy['task_categories'])} categories, "
          f"{len(policy['routing_rules']['rules'])} routing rules.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Model Router v1.0 (Phase 3)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_route = sub.add_parser("route", help="Route a task to a model")
    p_route.add_argument("--category", required=True,
                         help="Task category")
    p_route.add_argument("--input-tokens", type=int, default=1000)
    p_route.add_argument("--complexity", type=float, default=0.5)
    p_route.add_argument("--data-classification", default="public",
                         choices=["public", "internal", "confidential", "secret"])
    p_route.add_argument("--cost-ceiling", type=float, default=None)
    p_route.add_argument("--contains-pii", action="store_true")
    p_route.add_argument("--actor", default="kimi")
    p_route.add_argument("--first-call-in-session", action="store_true")
    p_route.add_argument("--dry-run", action="store_true", default=False,
                         help="Don't write decision_log (off by default; logs are audit assets)")
    p_route.set_defaults(func=cmd_route)

    p_rec = sub.add_parser("record-actual", help="Update decision_log with actual call results")
    p_rec.add_argument("--log-id", required=True)
    p_rec.add_argument("--actual-provider", required=True)
    p_rec.add_argument("--actual-model", required=True)
    p_rec.add_argument("--actual-cost", type=float, required=True)
    p_rec.add_argument("--latency-ms", type=int, required=True)
    p_rec.add_argument("--success", default="true")
    p_rec.add_argument("--error-class", default=None)
    p_rec.set_defaults(func=cmd_record_actual)

    p_stats = sub.add_parser("stats", help="Aggregate decision_log stats")
    p_stats.add_argument("--last", type=int, default=100)
    p_stats.set_defaults(func=cmd_stats)

    p_val = sub.add_parser("validate", help="Validate policy file")
    p_val.set_defaults(func=cmd_validate)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())