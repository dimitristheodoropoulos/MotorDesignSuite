#!/usr/bin/env python3
import numpy as np
import pandas as pd
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import product
from dask.distributed import Client, LocalCluster
import dask.bag as db
import time

ROOT = Path(__file__).parent
OUT_PLOTS = ROOT / "results/plots"
DB_PATH = ROOT / "results/optimization_results_dask.db"
OUT_PLOTS.mkdir(parents=True, exist_ok=True)

def evaluate_motor(params):
    R_s, k_fe, k_mech, speed_rpm, torque_nm = params
    n_poles = 8
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
    return (round(R_s,4), round(k_fe,4), round(k_mech,3),
            round(speed_rpm,1), round(torque_nm,1),
            round(eta*100,2), round(torque_density,3),
            round(P_loss,2))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            R_s REAL, k_fe REAL, k_mech REAL, Speed_rpm REAL, Torque_Nm REAL,
            Efficiency REAL, TorqueDensity REAL, TotalLosses_W REAL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_eff ON simulations(Efficiency)")
    conn.commit()
    conn.close()

def insert_batch(records):
    conn = sqlite3.connect(DB_PATH)
    conn.executemany("""
        INSERT INTO simulations (R_s, k_fe, k_mech, Speed_rpm, Torque_Nm,
                                 Efficiency, TorqueDensity, TotalLosses_W)
        VALUES (?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    R_s_vals   = np.linspace(0.02, 0.15, 6)
    k_fe_vals  = np.linspace(0.001, 0.008, 5)
    k_mech_vals= np.linspace(0.2, 1.5, 5)
    speed_vals = np.linspace(2000, 10000, 6)
    torque_vals= np.linspace(50, 250, 5)
    param_space = list(product(R_s_vals, k_fe_vals, k_mech_vals, speed_vals, torque_vals))
    print(f"🔍 Design space: {len(param_space)} evaluations")

    print("🚀 Starting Dask local cluster (distributed architecture)...")
    cluster = LocalCluster(n_workers=4, threads_per_worker=1, dashboard_address=":8787")
    client = Client(cluster)
    print(f"📊 Dask dashboard: http://localhost:8787")

    t0 = time.time()
    bag = db.from_sequence(param_space, npartitions=4)
    results = bag.map(evaluate_motor).compute()
    elapsed = time.time() - t0
    print(f"✅ Dask computed {len(results)} designs in {elapsed:.1f}s")

    client.close()
    cluster.close()

    init_db()
    insert_batch(results)
    print(f"💾 Saved to SQLite: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    df_full = pd.read_sql_query("SELECT * FROM simulations", conn)
    conn.close()

    obj = np.column_stack([df_full["Efficiency"], df_full["TorqueDensity"], -df_full["TotalLosses_W"]])
    n = len(obj)
    pareto_mask = np.ones(n, dtype=bool)
    for i in range(n):
        if not pareto_mask[i]: continue
        dominated = np.all(obj >= obj[i], axis=1) & np.any(obj > obj[i], axis=1)
        dominated[i] = False
        if np.any(dominated): pareto_mask[i] = False
    df_pareto = df_full[pareto_mask].copy()

    fig, axes = plt.subplots(1, 3, figsize=(15,5), facecolor='#0d0d0d')
    pairs = [("Efficiency","TotalLosses_W","Efficiency [%]","Total Losses [W]"),
             ("Efficiency","TorqueDensity","Efficiency [%]","Torque Density"),
             ("TorqueDensity","TotalLosses_W","Torque Density","Total Losses [W]")]
    for ax, (x_col, y_col, xl, yl) in zip(axes, pairs):
        ax.set_facecolor('#0d0d0d')
        ax.scatter(df_full[x_col], df_full[y_col], c='#333', s=4, alpha=0.4)
        ax.scatter(df_pareto[x_col], df_pareto[y_col], c='#CC0000', s=20, zorder=5)
        ax.set_xlabel(xl, color='white', fontsize=9)
        ax.set_ylabel(yl, color='white', fontsize=9)
        ax.tick_params(colors='white')
        ax.grid(True, color='#333', alpha=0.4)
        for sp in ax.spines.values(): sp.set_edgecolor('#444')
    fig.suptitle("Pareto Front – Dask Distributed", color='#CC0000')
    plt.tight_layout()
    plt.savefig(OUT_PLOTS / "pareto_front_dask.png", dpi=130, facecolor='#0d0d0d')
    plt.close()
    print("✅ pareto_front_dask.png saved")
    print(f"🏆 Pareto designs: {len(df_pareto)}")