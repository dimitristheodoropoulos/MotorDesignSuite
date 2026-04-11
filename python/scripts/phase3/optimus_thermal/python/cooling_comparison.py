#!/usr/bin/env python3
"""
cooling_comparison.py – LPTN Cooling Scenario Comparison
Compares: No cooling / Air cooling / Liquid cooling
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from pathlib import Path

ROOT      = Path(__file__).parent.parent.parent
OUT_CSV   = ROOT / "optimus_thermal/results/csv"
OUT_PLOTS = ROOT / "optimus_thermal/results/plots"
OUT_CSV.mkdir(parents=True, exist_ok=True)
OUT_PLOTS.mkdir(parents=True, exist_ok=True)

NODES  = ['Winding', 'Stator', 'Rotor', 'Housing', 'Coolant']
N      = len(NODES)
T_amb  = 25.0
Q_gen  = np.array([80.0, 30.0, 20.0, 5.0, 0.0])

R_base = np.array([
    [0,    0.30, 0.48, 0,    0   ],
    [0.30, 0,    0.24, 0.36, 0   ],
    [0.48, 0.24, 0,    0,    0.42],
    [0,    0.36, 0,    0,    0.18],
    [0,    0,    0.42, 0.18, 0   ],
])
C = np.array([0.5, 2.0, 1.5, 3.0, 4.0])

# Cooling scenarios: R_amb per node [Housing, Coolant → ambient]
scenarios = {
    'No Cooling':     np.array([0, 0, 0, 2.00, 1.00]),   # very high R → poor cooling
    'Air Cooling':    np.array([0, 0, 0, 0.60, 0.30]),   # baseline
    'Liquid Cooling': np.array([0, 0, 0, 0.15, 0.08]),   # low R → good cooling
}
colors_sc = {'No Cooling': '#CC3333', 'Air Cooling': '#3388CC',
             'Liquid Cooling': '#33AA55'}

t_eval  = np.linspace(0, 300, 400)
results = {}

for name, R_amb in scenarios.items():
    G = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j and R_base[i,j] > 0:
                g = 1.0/R_base[i,j]; G[i,j] -= g; G[i,i] += g
    Q_amb = np.zeros(N)
    for i in range(N):
        if R_amb[i] > 0:
            g = 1.0/R_amb[i]; G[i,i] += g; Q_amb[i] = g*T_amb
    Q_total = Q_gen + Q_amb

    def ode(t, T, G=G, Q=Q_total):
        return (Q - G@T) / C

    sol = solve_ivp(ode, (0,300), np.ones(N)*T_amb,
                    method='Radau', t_eval=t_eval, rtol=1e-8, atol=1e-10)
    results[name] = sol.y.T

# --- Plot 1: Winding temperature comparison ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
for name, hist in results.items():
    ax.plot(t_eval, hist[:,0], color=colors_sc[name],
            linewidth=2.5, label=name)
ax.axhline(T_amb, color='gray', linestyle='--', linewidth=1)
ax.axhline(120, color='orange', linestyle=':', linewidth=1.5,
           label='Winding limit 120°C')
ax.set_xlabel('Time [s]', fontsize=10)
ax.set_ylabel('Winding Temperature [°C]', fontsize=10)
ax.set_title('Cooling Scenario Comparison – Winding Node', fontsize=11)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Plot 2: Steady-state all nodes ---
ax2 = axes[1]
x     = np.arange(N)
width = 0.25
for k, (name, hist) in enumerate(results.items()):
    steady = hist[-1]
    bars = ax2.bar(x + k*width, steady, width,
                   label=name, color=colors_sc[name], alpha=0.85)
ax2.axhline(T_amb, color='gray', linestyle='--', linewidth=1, label='Ambient')
ax2.axhline(120,   color='orange', linestyle=':', linewidth=1.5,
            label='Winding limit')
ax2.set_xticks(x + width)
ax2.set_xticklabels(NODES, fontsize=8)
ax2.set_ylabel('Steady-State Temperature [°C]', fontsize=10)
ax2.set_title('Steady-State Temperature per Node', fontsize=11)
ax2.legend(fontsize=7)
ax2.grid(True, axis='y', alpha=0.3)

plt.suptitle('LPTN Cooling Scenario Analysis', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(OUT_PLOTS / "cooling_comparison.png", dpi=130)
plt.close()
print("✅ cooling_comparison.png saved")

# --- Save summary CSV ---
rows = []
for name, hist in results.items():
    for i, node in enumerate(NODES):
        rows.append({'Scenario': name, 'Node': node,
                     'SteadyState_C': round(hist[-1,i], 1)})
pd.DataFrame(rows).to_csv(OUT_CSV / "cooling_comparison.csv", index=False)
print("✅ cooling_comparison.csv saved")

# --- Print summary ---
print("\n📊 Steady-State Winding Temperature per scenario:")
for name, hist in results.items():
    t_wind = hist[-1, 0]
    safe   = "✅ SAFE" if t_wind < 120 else "⚠️  OVER LIMIT"
    print(f"  {name:<18}: {t_wind:.1f}°C  {safe}")