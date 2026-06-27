"""Figure 3: 8-agent equipment rate timeline (2026-04-01 to 2026-06-30).

X-axis: 90-day timeline.
Y-axis: equipment rate rho in [0, 1].
Horizontal line: rho_min = 0.5.
"""
import os
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "figures", "fig3_8agent_equipment_timeline.png")
OUT = os.path.abspath(OUT)

start = np.datetime64("2026-04-01")
end = np.datetime64("2026-06-30")
days = np.arange(start, end + np.timedelta64(1, "D"), dtype="datetime64[D]")
N = len(days)


def logistic(t, t0, k, floor, ceil):
    """Smooth ramp from floor to ceil, midpoint t0, steepness k (per day)."""
    t = np.asarray(t, dtype="datetime64[D]").astype(int)
    t0_i = (np.datetime64(t0)).astype(int)
    return floor + (ceil - floor) / (1 + np.exp(-k * (t - t0_i)))


# Agent trajectories (8 agents A..I, skipping C from intro since 1.5-month set)
agents = {
    "Agent-A": dict(t0="2026-04-08", k=0.10, floor=0.55, ceil=0.95),
    "Agent-B": dict(t0="2026-04-12", k=0.09, floor=0.50, ceil=0.90),
    "Agent-C": dict(t0="2026-04-18", k=0.08, floor=0.40, ceil=0.75),
    "Agent-D": dict(t0="2026-05-02", k=0.06, floor=0.30, ceil=0.60),
    "Agent-E": dict(t0="2026-05-02", k=0.06, floor=0.30, ceil=0.60),
    "Agent-F": dict(t0="2026-04-22", k=0.07, floor=0.40, ceil=0.75),
    "Agent-G": dict(t0="2026-04-25", k=0.06, floor=0.35, ceil=0.65),
    "Agent-H": dict(t0="2026-04-15", k=0.08, floor=0.45, ceil=0.70),
    "Agent-I": dict(t0="2026-05-20", k=0.04, floor=0.15, ceil=0.35),
}

fig, ax = plt.subplots(figsize=(9, 5))
cmap = plt.cm.tab10
for i, (name, p) in enumerate(agents.items()):
    y = logistic(days, **p)
    ax.plot(days, y, lw=2.0, color=cmap(i), label=name)

ax.axhline(0.5, color="#D7263D", ls="--", lw=1.8, label=r"$\rho_{min} = 0.5$")
ax.axhspan(0, 0.5, color="#D7263D", alpha=0.06)
ax.text(days[5], 0.06, "below ρ_min (uncontrolled emergence zone)", fontsize=9,
        color="#7a1a2a", style="italic")

ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel(r"Equipment rate $\rho$", fontsize=12)
ax.set_title("8-agent equipment rate over 90 days (April–June 2026)", fontsize=12, pad=10)
ax.set_ylim(0, 1.02)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.grid(alpha=0.25)
ax.legend(loc="lower right", ncol=3, fontsize=9, framealpha=0.9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=140, bbox_inches="tight")
print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")