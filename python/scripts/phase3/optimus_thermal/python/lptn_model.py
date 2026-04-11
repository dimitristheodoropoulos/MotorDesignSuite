#!/usr/bin/env python3
"""
LPTN (Lumped Parameter Thermal Network) – Motor Thermal Model
Nodes: Winding, Stator, Rotor, Housing, Coolant  (Ambient = fixed BC)
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from pathlib import Path

# --- Paths ---
base_dir = Path(__file__).parent.parent.parent
results_csv_dir = base_dir / "optimus_thermal/results/csv"
results_plot_dir = base_dir / "optimus_thermal/results/plots"
results_csv_dir.mkdir(parents=True, exist_ok=True)
results_plot_dir.mkdir(parents=True, exist_ok=True)

# --- Nodes (Ambient = fixed BC at 25°C) ---
NODES = ['Winding', 'Stator', 'Rotor', 'Housing', 'Coolant']
N     = len(NODES)
T_amb = 25.0  # °C

# --- Thermal Resistances between active nodes [K/W] ---
# Scaled for realistic motor temperatures (small actuator ~100W losses)
#        Win   Sta   Rot   Hou   Coo
R = np.array([
    [0,    0.30, 0.48, 0,    0   ],   # Winding
    [0.30, 0,    0.24, 0.36, 0   ],   # Stator
    [0.48, 0.24, 0,    0,    0.42],   # Rotor
    [0,    0.36, 0,    0,    0.18],   # Housing
    [0,    0,    0.42, 0.18, 0   ],   # Coolant
])

# --- Resistance to Ambient [K/W] ---
R_amb = np.array([0, 0, 0, 0.60, 0.30])   # Housing→Amb, Coolant→Amb

# --- Thermal Capacitances [J/K] ---
C = np.array([0.5, 2.0, 1.5, 3.0, 4.0])

# --- Internal heat generation [W] ---
Q_gen = np.array([80.0, 30.0, 20.0, 5.0, 0.0])

# --- Build conductance matrix G ---
G = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        if i != j and R[i, j] > 0:
            g = 1.0 / R[i, j]
            G[i, j] -= g
            G[i, i] += g

# Add ambient conductances to diagonal + source term
Q_amb = np.zeros(N)
for i in range(N):
    if R_amb[i] > 0:
        g = 1.0 / R_amb[i]
        G[i, i] += g
        Q_amb[i] = g * T_amb

Q_total = Q_gen + Q_amb

# --- ODE ---
def ode_rhs(t, T):
    return (Q_total - G @ T) / C

# --- Solve ---
T0     = np.ones(N) * T_amb
t_eval = np.linspace(0, 300, 600)

sol = solve_ivp(ode_rhs, (0, 300), T0, method='Radau',
                t_eval=t_eval, rtol=1e-8, atol=1e-10)

if not sol.success:
    print(f"❌ Solver failed: {sol.message}"); exit(1)

history = sol.y.T
time    = sol.t
steady  = history[-1]

# --- Save CSVs ---
df = pd.DataFrame(history, columns=NODES)
df.insert(0, 'Time_s', time)
df.to_csv(results_csv_dir / "lptn_thermal_transient.csv", index=False)
print("✅ Transient CSV saved")

pd.DataFrame({'Node': NODES, 'SteadyState_C': steady}).to_csv(
    results_csv_dir / "lptn_steady_state.csv", index=False)
print("✅ Steady-state CSV saved")

# --- Plot: transient ---
plt.figure(figsize=(9, 5))
for i, node in enumerate(NODES):
    plt.plot(time, history[:, i], label=node, linewidth=2)
plt.axhline(T_amb, color='gray', linestyle='--', linewidth=1, label='Ambient')
plt.xlabel('Time [s]'); plt.ylabel('Temperature [°C]')
plt.title('LPTN Transient Thermal Response – Motor Nodes')
plt.legend(); plt.grid(True); plt.tight_layout()
plt.savefig(results_plot_dir / "lptn_transient.png", dpi=120)
plt.close()
print("✅ Transient plot saved")

# --- Plot: steady-state bar ---
colors = ['crimson','steelblue','darkorange','seagreen','mediumpurple']
plt.figure(figsize=(7, 4))
plt.bar(NODES, steady, color=colors)
plt.axhline(T_amb, color='black', linestyle='--', linewidth=1, label='Ambient 25°C')
plt.ylabel('Temperature [°C]'); plt.title('LPTN Steady-State Temperatures')
plt.legend(); plt.grid(axis='y'); plt.tight_layout()
plt.savefig(results_plot_dir / "lptn_steady_state.png", dpi=120)
plt.close()
print("✅ Steady-state bar chart saved")

# --- Summary ---
print("\n📊 Steady-State Temperatures:")
for node, val in zip(NODES, steady):
    print(f"  {node:<10}: {val:.1f} °C")

# --- Validation vs FEA reference ---
# Reference values from high-fidelity FEA simulation (illustrative)
fea_ref = {'Winding': 95.0, 'Stator': 75.0, 'Rotor': 70.0}
print("\n📊 Validation vs FEA reference:")
for node, fea_val in fea_ref.items():
    idx = NODES.index(node)
    err = abs(steady[idx] - fea_val)
    status = "✅" if err < 10 else "⚠️ "
    print(f"  {status} {node:<10}: LPTN={steady[idx]:.1f}°C  "
          f"FEA={fea_val:.1f}°C  |Error|={err:.1f}°C")