#!/usr/bin/env python3
"""
torque_speed.py – EV Motor Torque-Speed Curve with Flux Weakening
Shows: constant torque region → flux weakening → power limit
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
T_rated   = 250.0    # rated torque [Nm]
omega_base= 2000.0   # base speed [rpm] — end of constant torque
omega_max = 12000.0  # max speed [rpm]
P_max     = T_rated * omega_base * 2*np.pi/60  # peak power [W]

speed_rpm = np.linspace(100, omega_max, 500)
omega     = speed_rpm * 2*np.pi/60

# Torque profile
torque = np.where(
    speed_rpm <= omega_base,
    T_rated,                          # constant torque region
    P_max / omega                     # flux weakening: T = P/ω
)
power_kw = torque * omega / 1000      # [kW]

# --- Save CSV ---
df = pd.DataFrame({'Speed_rpm': speed_rpm, 'Torque_Nm': torque,
                   'Power_kW': power_kw})
df.to_csv(OUT_CSV / "torque_speed.csv", index=False)
print("✅ torque_speed.csv saved")

# --- Plot ---
fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()

ax1.plot(speed_rpm, torque,    'b-',  linewidth=2.5, label='Torque [Nm]')
ax2.plot(speed_rpm, power_kw,  'r--', linewidth=2,   label='Power [kW]')

ax1.axvline(omega_base, color='gray', linestyle=':', linewidth=1.2)
ax1.text(omega_base+100, T_rated*0.9, 'Base speed\n(flux weakening start)',
         fontsize=8, color='gray')

ax1.fill_between(speed_rpm[speed_rpm<=omega_base],
                 torque[speed_rpm<=omega_base],
                 alpha=0.08, color='blue', label='Constant torque region')
ax1.fill_between(speed_rpm[speed_rpm>omega_base],
                 torque[speed_rpm>omega_base],
                 alpha=0.08, color='red',  label='Flux weakening region')

ax1.set_xlabel('Speed [rpm]', fontsize=11)
ax1.set_ylabel('Torque [Nm]', color='blue', fontsize=11)
ax2.set_ylabel('Power [kW]',  color='red',  fontsize=11)
ax1.set_title('EV Motor Torque-Speed Curve with Flux Weakening', fontsize=13)
ax1.set_ylim(0, T_rated * 1.2)
ax2.set_ylim(0, power_kw.max() * 1.3)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, fontsize=8, loc='upper right')
ax1.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUT_PLOTS / "torque_speed_curve.png", dpi=130)
plt.close()
print("✅ torque_speed_curve.png saved")

print(f"\n📊 Motor Operating Envelope:")
print(f"  Rated torque  : {T_rated:.0f} Nm")
print(f"  Base speed    : {omega_base:.0f} rpm")
print(f"  Max speed     : {omega_max:.0f} rpm")
print(f"  Peak power    : {P_max/1000:.1f} kW")