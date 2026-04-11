#!/usr/bin/env python3
"""
efficiency_map.py – EV Motor Efficiency Map Generator
Computes and visualizes motor efficiency across speed/torque operating points.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# PROJECT ROOT (MotorDesignSuite)
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[5]

results_csv   = PROJECT_ROOT / "results" / "csv"
results_plots = PROJECT_ROOT / "results" / "plots"

results_csv.mkdir(parents=True, exist_ok=True)
results_plots.mkdir(parents=True, exist_ok=True)

# =========================================================
# MOTOR PARAMETERS
# =========================================================
R_s     = 0.05    # stator resistance [Ω]
k_fe    = 0.002   # iron loss coefficient
k_mech  = 0.5     # mechanical loss coefficient [W·s/rad]
V_dc    = 400     # DC bus voltage [V]
n_poles = 8       # number of poles

# =========================================================
# OPERATING GRID
# =========================================================
speed_rpm = np.linspace(500, 12000, 60)
torque_nm = np.linspace(5, 300, 60)

omega = speed_rpm * 2 * np.pi / 60

T_grid, W_grid = np.meshgrid(torque_nm, omega)

# =========================================================
# POWER MODEL
# =========================================================
P_out = T_grid * W_grid

I_phase  = T_grid / (n_poles * 0.1)
P_copper = 3 * R_s * I_phase**2

P_iron = k_fe * W_grid**2
P_mech = k_mech * W_grid

P_loss = P_copper + P_iron + P_mech
P_in   = P_out + P_loss

# =========================================================
# EFFICIENCY
# =========================================================
with np.errstate(invalid="ignore", divide="ignore"):
    eta = np.where(P_in > 0, P_out / P_in, 0.0)

eta = np.clip(eta, 0.0, 1.0) * 100  # [%]

# =========================================================
# CSV EXPORT (FIXED + SAFE MAPPING)
# =========================================================
rows = []

step_s = 5
step_t = 5

speed_sample = speed_rpm[::step_s]
torque_sample = torque_nm[::step_t]

for i, s in enumerate(speed_sample):
    for j, t in enumerate(torque_sample):

        rows.append({
            "Speed_rpm": float(s),
            "Torque_Nm": float(t),
            "Efficiency_%": float(eta[i * step_s, j * step_t])
        })

df = pd.DataFrame(rows)
csv_path = results_csv / "efficiency_map.csv"
df.to_csv(csv_path, index=False)

print("✅ efficiency_map.csv saved")

# =========================================================
# HEATMAP PLOT
# =========================================================
fig, ax = plt.subplots(figsize=(9, 6))

cf = ax.contourf(
    speed_rpm,
    torque_nm,
    eta.T,
    levels=np.arange(50, 100, 2),
    cmap="RdYlGn"
)

ct = ax.contour(
    speed_rpm,
    torque_nm,
    eta.T,
    levels=[70, 80, 85, 90, 92, 94, 95],
    colors="black",
    linewidths=0.7
)

ax.clabel(ct, fmt="%d%%", fontsize=8)

cbar = fig.colorbar(cf, ax=ax)
cbar.set_label("Efficiency [%]", fontsize=11)

ax.set_xlabel("Speed [rpm]")
ax.set_ylabel("Torque [Nm]")
ax.set_title("EV Motor Efficiency Map")
ax.grid(True, linestyle="--", alpha=0.4)

plt.tight_layout()

plot_path = results_plots / "efficiency_map.png"
plt.savefig(plot_path, dpi=150)
plt.close()

print("✅ efficiency_map.png saved")

# =========================================================
# PEAK EFFICIENCY CURVE
# =========================================================
peak_eff = eta.max(axis=1)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(speed_rpm, peak_eff, linewidth=2)

ax.set_xlabel("Speed [rpm]")
ax.set_ylabel("Peak Efficiency [%]")
ax.set_title("Peak Motor Efficiency vs Speed")
ax.set_ylim(80, 100)
ax.grid(True)

plt.tight_layout()

peak_path = results_plots / "peak_efficiency_vs_speed.png"
plt.savefig(peak_path, dpi=150)
plt.close()

print("✅ peak_efficiency_vs_speed.png saved")

# =========================================================
# SUMMARY
# =========================================================
max_idx = np.unravel_index(np.argmax(eta), eta.shape)

print("\n📊 Efficiency Map Summary:")
print(f"  Peak efficiency : {eta.max():.1f}%")
print(f"  at Speed        : {speed_rpm[max_idx[0]]:.0f} rpm")
print(f"  at Torque       : {torque_nm[max_idx[1]]:.0f} Nm")
print(f"  Mean efficiency : {eta[eta > 50].mean():.1f}%")