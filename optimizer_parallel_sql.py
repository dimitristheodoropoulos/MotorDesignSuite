#!/usr/bin/env python3
"""
optimizer_parallel_sql.py – Multi-Objective Motor Design Optimizer
- Parallel execution using multiprocessing.Pool (4 workers)
- SQLite storage instead of CSV
- Pareto front extraction
"""

import numpy as np
import pandas as pd
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import product
from multiprocessing import Pool, cpu_count
import time

# --- Paths -------------------------------------------------
ROOT      = Path(__file__).parent
OUT_PLOTS = ROOT / "results/plots"
OUT_PLOTS.mkdir(parents=True, exist_ok=True)
DB_PATH   = ROOT / "results/optimization_results.db"

# --- Motor model (same as before) -------------------------
def evaluate_motor(R_s, k_fe, k_mech, speed_rpm, torque_nm, n_poles=8):
    omega = speed_rpm * 2 * np.pi / 60
    P_out = torque_nm * omega
    I_phase = torque_nm / (n_poles * 0.1)
    P_copper = 3 * R_s * I_phase**2
    P_iron = k_fe * omega**2
    P_mech = k_mech * omega
    P_loss = P_copper + P_iron + P_mech
    P_in = P_out + P_loss
    eta = P_out / P_in if P_in > 0 else 0.0
    torque_density = torque_nm / (R_s * 1000 + 1)
    return (round(R_s, 4), round(k_fe, 4), round(k_mech, 3),
            round(speed_rpm, 1), round(torque_nm, 1),
            round(eta * 100, 2), round(torque_density, 3),
            round(P_loss, 2))

# --- Wrapper for parallel execution -----------------------
def run_one(params):
    """Single simulation – to be mapped by Pool."""
    R_s, k_fe, k_mech, spd, trq = params
    return evaluate_motor(R_s, k_fe, k_mech, spd, trq)

# --- Create SQLite tables ---------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")  # faster concurrent writes
    conn.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            R_s REAL,
            k_fe REAL,
            k_mech REAL,
            Speed_rpm REAL,
            Torque_Nm REAL,
            Efficiency REAL,
            TorqueDensity REAL,
            TotalLosses_W REAL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_eff ON simulations(Efficiency)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_loss ON simulations(TotalLosses_W)")
    conn.commit()
    conn.close()

def insert_batch(records):
    """Bulk insert list of tuples into simulations."""
    conn = sqlite3.connect(DB_PATH)
    conn.executemany("""
        INSERT INTO simulations (R_s, k_fe, k_mech, Speed_rpm, Torque_Nm,
                                 Efficiency, TorqueDensity, TotalLosses_W)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    conn.commit()
    conn.close()

def get_pareto_mask_from_db():
    """Load all data from DB, compute Pareto mask, return mask and dataframe."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM simulations", conn)
    conn.close()
    # Pareto on: maximize Efficiency, maximize TorqueDensity, minimize TotalLosses
    obj = np.column_stack([df["Efficiency"], df["TorqueDensity"], -df["TotalLosses_W"]])
    n = len(obj)
    mask = np.ones(n, dtype=bool)
    for i in range(n):
        if not mask[i]:
            continue
        dominated = np.all(obj >= obj[i], axis=1) & np.any(obj > obj[i], axis=1)
        dominated[i] = False
        if np.any(dominated):
            mask[i] = False
    return mask, df

# --- Main --------------------------------------------------
def main():
    # 1. Design space (same as original, ~4500 combos)
    R_s_vals    = np.linspace(0.02, 0.15, 6)
    k_fe_vals   = np.linspace(0.001, 0.008, 5)
    k_mech_vals = np.linspace(0.2,   1.5,   5)
    speed_vals  = np.linspace(2000,  10000, 6)
    torque_vals = np.linspace(50,    250,   5)
    total = len(R_s_vals) * len(k_fe_vals) * len(k_mech_vals) * len(speed_vals) * len(torque_vals)
    print(f"🔍 Design space: {total} evaluations")

    param_space = list(product(R_s_vals, k_fe_vals, k_mech_vals, speed_vals, torque_vals))

    # 2. Parallel execution
    num_workers = min(cpu_count(), 4)   # χρησιμοποίησε max 4 cores
    print(f"🚀 Running on {num_workers} parallel workers...")
    t0 = time.time()
    with Pool(processes=num_workers) as pool:
        results = pool.map(run_one, param_space)
    elapsed = time.time() - t0
    print(f"✅ Computed {len(results)} designs in {elapsed:.1f}s")

    # 3. Store in SQLite
    init_db()
    insert_batch(results)
    print(f"💾 Saved to SQLite database: {DB_PATH}")

    # 4. Compute Pareto front (post‑processing)
    print("📐 Computing Pareto front...")
    pareto_mask, df_full = get_pareto_mask_from_db()
    df_pareto = df_full[pareto_mask].copy()
    df_pareto["IsPareto"] = True
    print(f"✅ Pareto front: {len(df_pareto)} solutions")

    # Optional: export pareto front to CSV for legacy tools
    df_pareto.to_csv(ROOT / "results/csv/optimization_pareto_sql.csv", index=False)

    # 5. Plot Pareto front (same 3 subplots)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#0d0d0d')
    pairs = [
        ("Efficiency",    "TotalLosses_W",  "Efficiency [%]",    "Total Losses [W]"),
        ("Efficiency",    "TorqueDensity",  "Efficiency [%]",    "Torque Density [proxy]"),
        ("TorqueDensity", "TotalLosses_W",  "Torque Density",    "Total Losses [W]"),
    ]
    for ax, (x_col, y_col, xl, yl) in zip(axes, pairs):
        ax.set_facecolor('#0d0d0d')
        ax.scatter(df_full[x_col], df_full[y_col], c='#333333', s=4, alpha=0.4, label='All designs')
        ax.scatter(df_pareto[x_col], df_pareto[y_col], c='#CC0000', s=20, zorder=5, label='Pareto front')
        ax.set_xlabel(xl, color='white', fontsize=9)
        ax.set_ylabel(yl, color='white', fontsize=9)
        ax.tick_params(colors='white')
        ax.legend(fontsize=7, facecolor='#1a1a1a', labelcolor='white')
        ax.grid(True, color='#333', alpha=0.4)
        for sp in ax.spines.values():
            sp.set_edgecolor('#444')
    fig.suptitle("Motor Design Pareto Front – 3 Objectives", color='#CC0000', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT_PLOTS / "pareto_front_sql.png", dpi=130, facecolor='#0d0d0d')
    plt.close()
    print("✅ pareto_front_sql.png saved")

    # 6. Example SQL query – best designs for high torque & efficiency
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT R_s, k_fe, Speed_rpm, Torque_Nm, Efficiency, TotalLosses_W
        FROM simulations
        WHERE Efficiency > 94 AND Torque_Nm > 200
        ORDER BY Efficiency DESC
        LIMIT 5
    """
    top = pd.read_sql_query(query, conn)
    conn.close()
    print("\n🏆 Top 5 designs with Efficiency>94% and Torque>200 Nm:")
    print(top.to_string(index=False))

    # Summary
    best = df_pareto.loc[df_pareto["Efficiency"].idxmax()]
    print(f"\n🏆 Best Pareto design:")
    print(f"  Efficiency    : {best['Efficiency']:.2f}%")
    print(f"  Torque Density: {best['TorqueDensity']:.3f}")
    print(f"  Total Losses  : {best['TotalLosses_W']:.1f} W")
    print(f"  R_s={best['R_s']}Ω  k_fe={best['k_fe']}  k_mech={best['k_mech']}")
    print(f"  Speed={best['Speed_rpm']} rpm  Torque={best['Torque_Nm']} Nm")

if __name__ == "__main__":
    main()