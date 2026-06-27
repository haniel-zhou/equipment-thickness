#!/usr/bin/env python3
"""
Make the 2 figures for paper B (Misevolution + MLAS).
Outputs to equipment-thickness-repo/docs/figures/paper_b_*.png
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path("/Users/haniel/workspace/research/ai-agent-research/paper_drafts.p0-rollup/equipment-thickness-repo/docs/figures")
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# Figure 1: Misevolution 4-path + MLAS 5x5 scatter (events by module x lifecycle)
# ----------------------------------------------------------------------
# Real MLAS check data (3 checks, all on M2-L2 with 2 hits / 1 miss)
# + 4 Misevolution events classified by path and target lifecycle
# Misevolution events from misevolution_incidents.jsonl (real data, 2026-05-15)
misevo = [
    {"ts": "2026-05-15T15:18:33", "agent": "D", "path": "memory", "lifecycle": "operation", "action": "write diary content", "outcome": "block"},
    {"ts": "2026-05-15T17:51:36", "agent": "D", "path": "memory", "lifecycle": "modification", "action": "overwrite diary.md", "outcome": "block"},
    {"ts": "2026-05-15T17:51:36", "agent": "H", "path": "model", "lifecycle": "modification", "action": "self_finetune new dataset", "outcome": "block"},
    {"ts": "2026-05-15T17:51:36", "agent": "A", "path": "tool", "lifecycle": "initialization", "action": "create new tool", "outcome": "block"},
]

# MLAS check history (3 checks, all M2-L2, 2 hits / 1 miss)
mlas_checks = [
    {"ts": "2026-06-26T10:46:03", "cell": "M2-L2", "agent": "C", "hit": True, "desc": "shared lessons broadcast backdoor"},
    {"ts": "2026-06-26T10:48:16", "cell": "M2-L2", "agent": "C", "hit": True, "desc": "shared lessons broadcast backdoor injection"},
    {"ts": "2026-06-26T10:48:16", "cell": "M2-L2", "agent": "C", "hit": False, "desc": "NEXUS 5 bridge dispatch works"},
]

# Meridian incident (2026-06-08 memory overwrite)
meridian = {"ts": "2026-06-08T20:31:00", "agent": "D", "path": "memory", "lifecycle": "modification",
            "action": "overwrite diary.md (44KB)", "outcome": "block"}

# Module-to-x mapping (5 modules → 0..4 on x axis)
module_x = {"model": 0, "memory": 1, "tool": 2, "workflow": 3, "governance": 4}
# Lifecycle-to-y mapping (5 stages → 0..4 on y axis)
lifecycle_y = {"initialization": 0, "operation": 1, "modification": 2, "shutdown": 3, "recovery": 4}
# Path to module mapping
path_to_module = {"model": "model", "memory": "memory", "tool": "tool", "workflow": "workflow"}

fig, ax = plt.subplots(figsize=(8, 6))

# Background grid: 5x5 with cell labels
for mx in range(5):
    for ly in range(5):
        rect = plt.Rectangle((mx - 0.5, ly - 0.5), 1, 1, fill=False, edgecolor="lightgray", linewidth=0.5)
        ax.add_patch(rect)
        # Mark criticality from MLAS (model layer: critical L1-L4, managed L5; same for others)
        # Simpler: shade "covered" cells lightly
        covered = {
            (0, 0): True, (0, 1): True,   # M1-L1, M1-L2 partial
            (1, 0): True, (1, 1): True,   # M2-L1, M2-L2 partial
            (2, 4): "full",               # M3-L5 full
            (3, 0): "full",               # M4-L1 full
        }
        if covered.get((mx, ly)) == "full":
            ax.add_patch(plt.Rectangle((mx - 0.5, ly - 0.5), 1, 1, fill=True, facecolor="lightgreen", alpha=0.3))
        elif covered.get((mx, ly)):
            ax.add_patch(plt.Rectangle((mx - 0.5, ly - 0.5), 1, 1, fill=True, facecolor="lightyellow", alpha=0.3))

# Plot Misevolution 4 events
for e in misevo:
    mx = module_x[path_to_module[e["path"]]]
    ly = lifecycle_y[e["lifecycle"]]
    ax.scatter(mx, ly, s=200, c="steelblue", marker="o", edgecolors="black", linewidth=1.5, zorder=5, label="Misevolution event" if e == misevo[0] else None)
    ax.annotate(f"Agent-{e['agent']}\n{e['action'][:25]}...", (mx, ly), xytext=(8, 8), textcoords="offset points", fontsize=7)

# Plot Meridian (highlighted as red star)
mx_m = module_x["memory"]; ly_m = lifecycle_y["modification"]
ax.scatter(mx_m, ly_m, s=400, c="red", marker="*", edgecolors="black", linewidth=1.5, zorder=6, label="Meridian 2026-06 incident")
ax.annotate("Meridian 2026-06\nmemory overwrite\n(blocked, 0 data loss)", (mx_m, ly_m), xytext=(15, -25), textcoords="offset points", fontsize=8, color="darkred", weight="bold")

# Plot MLAS checks (3 on M2-L2)
mx_mlas = module_x["memory"]; ly_mlas = lifecycle_y["operation"]
for i, c in enumerate(mlas_checks):
    color = "orange" if c["hit"] else "gray"
    marker = "X" if c["hit"] else "x"
    ax.scatter(mx_mlas + (i - 1) * 0.15, ly_mlas, s=120, c=color, marker=marker, edgecolors="black", linewidth=1, zorder=5, label="MLAS check (hit)" if (i == 0 and c["hit"]) else ("MLAS check (miss)" if (i == 0 and not c["hit"]) else None))

ax.set_xticks(range(5))
ax.set_xticklabels(["M1\nmodel", "M2\nmemory", "M3\ntool", "M4\nworkflow", "M5\ngovernance"])
ax.set_yticks(range(5))
ax.set_yticklabels(["L1\ninit", "L2\nop", "L3\nmod", "L4\nshutdown", "L5\nrecovery"])
ax.set_xlabel("MLAS module (5)", fontsize=10)
ax.set_ylabel("MLAS lifecycle stage (5)", fontsize=10)
ax.set_title("Figure 1: Misevolution 4 events (●) + MLAS 3 checks (✕) on the 5×5 matrix\nBackground: green=full coverage, yellow=partial, white=no coverage yet", fontsize=10)
ax.set_xlim(-0.7, 4.7)
ax.set_ylim(-0.7, 4.7)
ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
ax.grid(False)
plt.tight_layout()
plt.savefig(OUT / "paper_b_fig1_misevolution_mlas_scatter.png", dpi=150, bbox_inches="tight")
print(f"Saved Figure 1: {OUT / 'paper_b_fig1_misevolution_mlas_scatter.png'}")
plt.close()

# ----------------------------------------------------------------------
# Figure 2: MLAS coverage status over 60 days (line plot)
# ----------------------------------------------------------------------
# We show cumulative MLAS coverage by cell, measured at 3 time points
# (Day 0 = 2026-04-15, Day 30 = 2026-05-15, Day 60 = 2026-06-13)
# "Coverage" = number of critical cells with full coverage

# Actual snapshots from system history:
# Day 0: 0 full / 0 partial / 25 none
# Day 30: 0 full / 12 partial / 13 none (action policy + cron SLO + inbox decay operational)
# Day 60: 2 full / 18 partial / 5 none (current)
days = [0, 30, 60]
full = [0, 0, 2]
partial = [0, 12, 18]
none = [25, 13, 5]
critical_uncovered = [19, 12, 5]  # subset of none/partial that are critical

fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.plot(days, full, "o-", color="green", label="Full coverage (n=2)", linewidth=2, markersize=10)
ax2.plot(days, partial, "s-", color="goldenrod", label="Partial coverage (n=18 at Day 60)", linewidth=2, markersize=10)
ax2.plot(days, none, "^-", color="crimson", label="No coverage (n=5 at Day 60)", linewidth=2, markersize=10)
ax2.plot(days, critical_uncovered, "D--", color="purple", label="Critical & uncovered (n=5 at Day 60)", linewidth=2, markersize=10, alpha=0.7)
ax2.fill_between(days, 0, critical_uncovered, alpha=0.15, color="purple", label="Critical-uncovered gap (closure target)")
ax2.annotate("Cron SLO\n+ A2A decay", (60, 2), xytext=(45, 5), textcoords="data", fontsize=8, arrowprops=dict(arrowstyle="->", color="green"))
ax2.annotate("Meridian 2026-06\nmemory-path\nevent caught", (60, 5), xytext=(40, 12), textcoords="data", fontsize=8, arrowprops=dict(arrowstyle="->", color="crimson"))
ax2.set_xlabel("Days from observation start (2026-04-15)", fontsize=10)
ax2.set_ylabel("MLAS cells (count of 25)", fontsize=10)
ax2.set_title("Figure 2: MLAS 5×5 coverage evolution over 60 days\n(2026-04-15 → 2026-06-13; 8-agent system)", fontsize=10)
ax2.set_xticks(days)
ax2.set_ylim(-1, 27)
ax2.legend(loc="upper right", fontsize=8, framealpha=0.9)
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "paper_b_fig2_mlas_coverage_timeline.png", dpi=150, bbox_inches="tight")
print(f"Saved Figure 2: {OUT / 'paper_b_fig2_mlas_coverage_timeline.png'}")
plt.close()

print("Done. 2 figures saved.")
