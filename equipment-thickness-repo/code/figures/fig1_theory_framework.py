"""Figure 1: Equipment Thickness Theory framework.

X-axis: equipment rate rho in [0, 1].
Y-axis: capability C(rho) showing concave saturation.
Three curves: beta = 0.3, 0.5, 0.7 (different saturation speeds).
Vertical line at rho_min = 0.5.
"""
import os
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "figures", "fig1_theory_framework.png")
OUT = os.path.abspath(OUT)

rho = np.linspace(0, 1, 500)


def capability(rho, beta):
    """C(rho) = 1 - exp(-beta * rho)."""
    return 1 - np.exp(-beta * rho)


fig, ax = plt.subplots(figsize=(8, 5))
betas = [0.3, 0.5, 0.7]
colors = ["#4C9BE8", "#3D9970", "#E08A3C"]
labels = [r"$\beta = 0.3$ (slow saturation)", r"$\beta = 0.5$ (moderate)", r"$\beta = 0.7$ (fast)"]

for beta, c, l in zip(betas, colors, labels):
    ax.plot(rho, capability(rho, beta), color=c, lw=2.5, label=l)

# rho_min threshold
rho_min = 0.5
ax.axvline(rho_min, color="#D7263D", ls="--", lw=2, label=r"$\rho_{min} = 0.5$")
ax.axhline(capability(rho_min, 0.5), color="#888", ls=":", lw=1)

# Annotate uncontrolled emergence zone (rho < rho_min)
ax.axvspan(0, rho_min, color="#D7263D", alpha=0.08)
ax.text(0.08, 0.05, "Uncontrolled emergence zone\n(ρ < ρ_min → capability < 0.22)",
        fontsize=9, color="#7a1a2a", style="italic")

# Reference point at rho = 0.5
ax.scatter([rho_min], [capability(rho_min, 0.5)], s=80, color="#D7263D",
           zorder=5, edgecolors="white", lw=1.5)

ax.set_xlabel(r"Equipment rate $\rho$", fontsize=12)
ax.set_ylabel(r"Capability $C(\rho) = 1 - e^{-\beta \rho}$", fontsize=12)
ax.set_title("Equipment Thickness Theory: capability as a concave function of equipment rate",
             fontsize=12, pad=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.02)
ax.grid(alpha=0.25)
ax.legend(loc="lower right", fontsize=10, framealpha=0.9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=140, bbox_inches="tight")
print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes)")