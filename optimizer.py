#!/usr/bin/env python3
"""
optimizer.py – Multi-Objective Motor Design Optimizer
Pareto front: Efficiency vs Torque density vs Total losses
Optimizes: R_s, k_fe, k_mech, speed_op, torque_op
Run once → saves results to CSV → dashboard reads them
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import product
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent
OUT_CSV   = ROOT / "results/csv"
OUT_PLOTS = ROOT / "results/plots"
OUT_CSV.mkdir(parents=True, exist_ok=True)
OUT_PLOTS.mkdir(parents=True, exist_ok=True)

# ── Motor model ───────────────────────────────────────────────────────────────
def evaluate_motor(R_s, k_fe, k_mech, speed_rpm, torque_nm, n_poles=8):
    """Evaluate motor at one operating point. Returns (efficiency, torque_density, losses)."""
    omega   = speed_rpm * 2 * np.pi / 60
    P_out   = torque_nm * omega

    I_phase  = torque_nm / (n_poles * 0.1)
    P_copper = 3 * R_s * I_phase**2
    P_iron   = k_fe   * omega**2
    P_mech   = k_mech * omega
    P_loss   = P_copper + P_iron + P_mech
    P_in     = P_out + P_loss

    eta           = P_out / P_in if P_in > 0 else 0.0
    torque_density = torque_nm / (R_s * 1000 + 1)  # simplified [Nm/kg proxy]
    return float(np.clip(eta, 0, 1)), float(torque_density), float(P_loss)

# ── Design space (subsampled for i7-3520M) ────────────────────────────────────
# ~300-400 evaluations → <20s on old hardware
R_s_vals    = np.linspace(0.02, 0.15, 6)    # stator resistance [Ω]
k_fe_vals   = np.linspace(0.001, 0.008, 5)  # iron loss coefficient
k_mech_vals = np.linspace(0.2,   1.5,   5)  # mechanical loss coefficient
speed_vals  = np.linspace(2000,  10000, 6)  # operating speed [rpm]
torque_vals = np.linspace(50,    250,   5)  # operating torque [Nm]

total = (len(R_s_vals) * len(k_fe_vals) * len(k_mech_vals) *
         len(speed_vals) * len(torque_vals))
print(f"🔍 Design space: {total} evaluations")
print(f"⏳ Running optimization on i7-3520M (estimated <30s)...")

t0 = time.time()

results = []
for R_s, k_fe, k_mech, spd, trq in product(
        R_s_vals, k_fe_vals, k_mech_vals, speed_vals, torque_vals):
    eta, td, loss = evaluate_motor(R_s, k_fe, k_mech, spd, trq)
    results.append({
        "R_s":           round(R_s, 4),
        "k_fe":          round(k_fe, 4),
        "k_mech":        round(k_mech, 3),
        "Speed_rpm":     round(spd, 1),
        "Torque_Nm":     round(trq, 1),
        "Efficiency":    round(eta * 100, 2),
        "TorqueDensity": round(td, 3),
        "TotalLosses_W": round(loss, 2),
    })

df = pd.DataFrame(results)
elapsed = time.time() - t0
print(f"✅ Evaluated {len(df)} designs in {elapsed:.1f}s")

# ── Pareto front (3-objective) ────────────────────────────────────────────────
# Objectives:  maximize Efficiency, maximize TorqueDensity, minimize TotalLosses
# Normalize to [0,1] for dominance check
def is_pareto(df):
    """Return boolean mask of Pareto-optimal solutions (maximizing all 3)."""
    # Convert to: maximize Efficiency, maximize TorqueDensity, maximize (-Losses)
    obj = np.column_stack([
        df["Efficiency"].values,
        df["TorqueDensity"].values,
        -df["TotalLosses_W"].values,
    ])
    n = len(obj)
    pareto_mask = np.ones(n, dtype=bool)
    for i in range(n):
        if not pareto_mask[i]:
            continue
        # i is dominated if any j dominates it
        dominated = np.all(obj >= obj[i], axis=1) & np.any(obj > obj[i], axis=1)
        dominated[i] = False
        if np.any(dominated):
            pareto_mask[i] = False
    return pareto_mask

print("📐 Computing Pareto front...")
t1 = time.time()

# Speed up: subsample top candidates first
df_top = df[df["Efficiency"] > df["Efficiency"].quantile(0.5)].copy()
pareto_mask = is_pareto(df_top.reset_index(drop=True))
df_pareto   = df_top[pareto_mask].copy()
df_pareto["IsPareto"] = True
df["IsPareto"] = False
df.loc[df_top[pareto_mask].index, "IsPareto"] = True

print(f"✅ Pareto front: {pareto_mask.sum()} solutions in {time.time()-t1:.1f}s")

# ── Save CSVs ─────────────────────────────────────────────────────────────────
df.to_csv(OUT_CSV / "optimization_all.csv", index=False)
df_pareto.to_csv(OUT_CSV / "optimization_pareto.csv", index=False)
print(f"✅ optimization_all.csv    ({len(df)} rows)")
print(f"✅ optimization_pareto.csv ({len(df_pareto)} rows)")

# ── Plot 1: Pareto front — Efficiency vs Losses ───────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#0d0d0d')

pairs = [
    ("Efficiency",    "TotalLosses_W",  "Efficiency [%]",    "Total Losses [W]"),
    ("Efficiency",    "TorqueDensity",  "Efficiency [%]",    "Torque Density [proxy]"),
    ("TorqueDensity", "TotalLosses_W",  "Torque Density",    "Total Losses [W]"),
]

for ax, (x_col, y_col, xl, yl) in zip(axes, pairs):
    ax.set_facecolor('#0d0d0d')
    ax.scatter(df[x_col],        df[y_col],
               c='#333333', s=4, alpha=0.4, label='All designs')
    ax.scatter(df_pareto[x_col], df_pareto[y_col],
               c='#CC0000', s=20, zorder=5, label='Pareto front')
    ax.set_xlabel(xl, color='white', fontsize=9)
    ax.set_ylabel(yl, color='white', fontsize=9)
    ax.tick_params(colors='white')
    ax.legend(fontsize=7, facecolor='#1a1a1a', labelcolor='white')
    ax.grid(True, color='#333', alpha=0.4)
    for sp in ax.spines.values(): sp.set_edgecolor('#444')

fig.suptitle("Motor Design Pareto Front – 3 Objectives",
             color='#CC0000', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(OUT_PLOTS / "pareto_front.png", dpi=130, facecolor='#0d0d0d')
plt.close()
print("✅ pareto_front.png saved")

# ── Plot 2: Top 10 designs table ──────────────────────────────────────────────
top10 = df_pareto.nlargest(10, "Efficiency")[
    ["R_s","k_fe","Speed_rpm","Torque_Nm","Efficiency","TorqueDensity","TotalLosses_W"]
].round(3)

fig, ax = plt.subplots(figsize=(12, 4), facecolor='#0d0d0d')
ax.set_facecolor('#0d0d0d')
ax.axis('off')
tbl = ax.table(
    cellText=top10.values,
    colLabels=top10.columns,
    cellLoc='center', loc='center',
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(8)
for (r, c), cell in tbl.get_celld().items():
    cell.set_facecolor('#CC0000' if r == 0 else ('#1a1a1a' if r % 2 else '#111'))
    cell.set_text_props(color='white')
    cell.set_edgecolor('#333')
ax.set_title("Top 10 Pareto-Optimal Motor Designs",
             color='#CC0000', fontsize=12, pad=10)
plt.tight_layout()
plt.savefig(OUT_PLOTS / "top10_designs.png", dpi=130, facecolor='#0d0d0d')
plt.close()
print("✅ top10_designs.png saved")

# ── Summary ───────────────────────────────────────────────────────────────────
best = df_pareto.loc[df_pareto["Efficiency"].idxmax()]
print(f"\n🏆 Best design:")
print(f"  Efficiency    : {best['Efficiency']:.2f}%")
print(f"  Torque Density: {best['TorqueDensity']:.3f}")
print(f"  Total Losses  : {best['TotalLosses_W']:.1f} W")
print(f"  R_s={best['R_s']}Ω  k_fe={best['k_fe']}  k_mech={best['k_mech']}")
print(f"  Speed={best['Speed_rpm']} rpm  Torque={best['Torque_Nm']} Nm")
print(f"\n⏱️  Total time: {time.time()-t0:.1f}s")