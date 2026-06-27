"""Figure 4: Minimum viable configuration threshold (scatter).

X-axis: equipment rate rho.
Y-axis: dispatch success rate.
Vertical line rho_min = 0.5 with shaded uncontrolled-emergence zone.
"""
import os
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "figures", "fig4_minimum_viable.png")
OUT = os.path.abspath(OUT)

# (agent, rho, dispatch_success_rate)
agents = [
    ("Agent-A", 0.95, 0.78),
    ("Agent-B", 0.90, 0.72),
    ("Agent-C", 0.75, 0.58),
    ("Agent-D", 0.60, 0.41),
    ("Agent-E", 0.60, 0.39),
    ("Agent-F", 0.75, 0.55),
    ("Agent-G", 0.65, 0.46),
    ("Agent-H", 0.70, 0.51),
    ("Agent-I", 0.35, 0.12),
]

fig, ax = plt.subplots(figsize=(8, 5))
for name, rho, sr in agents:
    color = "#3D9970" if rho >= 0.5 else "#D7263D"
    ax.scatter([rho], [sr], s=140, color=color, edgecolors="white", lw=1.5, zorder=3)
    ax.annotate(name, (rho, sr), xytext=(5, 5), textcoords="offset points",
                fontsize=9, color="#222")

# rho_min threshold
ax.axvline(0.5, color="#D7263D", ls="--", lw=2, label=r"$\rho_{min} = 0.5$")
ax.axvspan(0, 0.5, color="#D7263D", alpha=0.08)
ax.text(0.05, 0.05, "Uncontrolled emergence\n(ρ < ρ_min)", fontsize=9,
        color="#7a1a2a", style="italic")

# Trend line
import numpy as np
xs = np.array([a[1] for a in agents])
ys = np.array([a[2] for a in agents])
slope, intercept = np.polyfit(xs, ys, 1)
xfit = np.linspace(0.2, 1.0, 50)
yfit = slope * xfit + intercept
ax.plot(xfit, yfit, color="#1f4f7a", lw=1.6, ls="-",
        label=f"linear fit (slope={slope:.2f})")

ax.set_xlabel(r"Equipment rate $\rho$", fontsize=12)
ax.set_ylabel("Dispatch success rate", fontsize=12)
ax.set_title(r"Minimum viable configuration: success rate vs equipment rate",
             fontsize=12, pad=10)
ax.set_xlim(0.2, 1.02)
ax.set_ylim(0, 1.0)
ax.grid(alpha=0.25)
ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=140, bbox_inches="tight")
print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")