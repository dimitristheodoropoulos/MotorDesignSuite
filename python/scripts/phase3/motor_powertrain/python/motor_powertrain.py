#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import glob
import numpy as np

# Paths
base_dir = Path(__file__).parent.parent.parent
common_csv_dir = base_dir / "common_inputs/csv"
results_csv_dir = base_dir / "motor_powertrain/results/csv"
results_plot_dir = base_dir / "motor_powertrain/results/plots"

results_csv_dir.mkdir(parents=True, exist_ok=True)
results_plot_dir.mkdir(parents=True, exist_ok=True)

# --- Read all CSVs automatically ---
csv_files = glob.glob(str(common_csv_dir / "*.csv"))
dataframes = {}
for f in csv_files:
    name = Path(f).stem
    df = pd.read_csv(f)
    dataframes[name] = df
    print(f"✅ Loaded {name}.csv")

# --- Dummy motor performance metrics ---
if 'fea_results' in dataframes:
    fea = dataframes['fea_results']
    motor_metrics = fea.copy()
    motor_metrics['Efficiency'] = np.random.uniform(0.75,0.95,len(fea))
    motor_metrics['Torque'] = np.random.uniform(10,15,len(fea))
    motor_metrics['Heat'] = np.random.uniform(30,50,len(fea))
    motor_metrics['MultiCriteriaScore'] = motor_metrics['Efficiency'] / (motor_metrics['Heat']+1e-6)
else:
    motor_metrics = pd.DataFrame()
    print("⚠️ Missing fea_results CSV")

# --- Save summary CSV ---
summary_file = results_csv_dir / "motor_powertrain_summary.csv"
motor_metrics.to_csv(summary_file, index=False)
print(f"✅ Motor Powertrain summary saved to {summary_file}")

# --- Plot Efficiency ---
plt.figure(figsize=(6,4))
plt.bar(motor_metrics['Material'], motor_metrics['Efficiency'], color=['green','orange'])
plt.title('Motor Efficiency')
plt.ylim(0,1)
plt.savefig(results_plot_dir / "motor_efficiency.png")
plt.close()

# --- Plot Torque ---
plt.figure(figsize=(6,4))
plt.bar(motor_metrics['Material'], motor_metrics['Torque'], color=['purple','cyan'])
plt.title('Motor Torque [Nm]')
plt.savefig(results_plot_dir / "motor_torque.png")
plt.close()

print(f"✅ Plots saved to {results_plot_dir}")
