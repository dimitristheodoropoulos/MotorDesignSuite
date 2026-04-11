#!/usr/bin/env python3
"""
loss_breakdown.py – Motor Loss Breakdown Analysis
Copper / Iron / Mechanical losses across speed range
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT      = Path(__file__).parent.parent.parent
OUT_CSV   = ROOT / "motor_powertrain/results/csv"
OUT_PLOTS = ROOT / "motor_powertrain/results/plots"
OUT_CSV.mkdir(parents=True, exist_ok=True)
OUT_PLOTS.mkdir(parents=True, exist_ok=True)

# --- Motor parameters ---
R_s    = 0.05
k_fe   = 0.002
k_mech = 0.5
n_poles= 8
torque_op = 150.0   # fixed operating torque [Nm]

speed_rpm = np.linspace(500, 12000, 100)
omega     = speed_rpm * 2*np.pi/60

I_phase  = torque_op / (n_poles * 0.1)
P_copper = np.full_like(omega, 3 * R_s * I_phase**2)   # const (fixed torque)
P_iron   = k_fe   * omega**2
P_mech   = k_mech * omega
P_total  = P_copper + P_iron + P_mech
P_out    = torque_op * omega
eta      = np.clip(P_out / (P_out + P_total), 0, 1) * 100

# --- Save CSV ---
df = pd.DataFrame({
    'Speed_rpm':    speed_rpm,
    'P_copper_W':   P_copper,
    'P_iron_W':     P_iron,
    'P_mech_W':     P_mech,
    'P_total_W':    P_total,
    'Efficiency_%': eta,
})
df.to_csv(OUT_CSV / "loss_breakdown.csv", index=False)
print("✅ loss_breakdown.csv saved")

# --- Plot 1: stacked loss areas ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

ax1.stackplot(speed_rpm,
              P_copper, P_iron, P_mech,
              labels=['Copper losses (I²R)', 'Iron losses (k_fe·ω²)',
                      'Mechanical losses (k_mech·ω)'],
              colors=['#CC3333', '#3388CC', '#33AA55'], alpha=0.85)
ax1.set_ylabel('Power Loss [W]', fontsize=10)
ax1.set_title('Motor Loss Breakdown vs Speed', fontsize=12)
ax1.legend(fontsize=8, loc='upper left')
ax1.grid(True, alpha=0.3)

ax2.plot(speed_rpm, eta, 'k-', linewidth=2.5)
ax2.fill_between(speed_rpm, eta, alpha=0.15, color='green')
ax2.set_xlabel('Speed [rpm]', fontsize=10)
ax2.set_ylabel('Efficiency [%]', fontsize=10)
ax2.set_title('Efficiency vs Speed (T=150 Nm)', fontsize=11)
ax2.set_ylim(70, 100)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUT_PLOTS / "loss_breakdown.png", dpi=130)
plt.close()
print("✅ loss_breakdown.png saved")

# --- Plot 2: pie chart at rated speed ---
speed_rated = 6000
idx = np.argmin(np.abs(speed_rpm - speed_rated))
losses_at_rated = [P_copper[idx], P_iron[idx], P_mech[idx]]
labels = [f'Copper\n{P_copper[idx]:.0f}W',
          f'Iron\n{P_iron[idx]:.0f}W',
          f'Mech\n{P_mech[idx]:.0f}W']

fig, ax = plt.subplots(figsize=(5, 5))
wedges, texts, autotexts = ax.pie(
    losses_at_rated, labels=labels,
    colors=['#CC3333','#3388CC','#33AA55'],
    autopct='%1.1f%%', startangle=90,
    textprops={'fontsize': 9}
)
ax.set_title(f'Loss Distribution at {speed_rated} rpm', fontsize=11)
plt.tight_layout()
plt.savefig(OUT_PLOTS / "loss_pie.png", dpi=130)
plt.close()
print("✅ loss_pie.png saved")

print(f"\n📊 Loss Breakdown at {speed_rated} rpm:")
print(f"  Copper : {P_copper[idx]:.1f} W  ({100*P_copper[idx]/P_total[idx]:.1f}%)")
print(f"  Iron   : {P_iron[idx]:.1f} W  ({100*P_iron[idx]/P_total[idx]:.1f}%)")
print(f"  Mech   : {P_mech[idx]:.1f} W  ({100*P_mech[idx]/P_total[idx]:.1f}%)")
print(f"  Efficiency: {eta[idx]:.1f}%")