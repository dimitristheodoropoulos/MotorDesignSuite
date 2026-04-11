#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import glob

# Paths
base_dir = Path(__file__).parent.parent.parent  # root/python/scripts/phase3
common_csv_dir = base_dir / "common_inputs/csv"
results_csv_dir = base_dir / "powertrain_modeling/results/csv"
results_plot_dir = base_dir / "powertrain_modeling/results/plots"

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

# --- Simple Multi-Criteria Scoring (dummy) ---
# Example: mean_core_loss vs flux density
if 'soft_summary' in dataframes and 'hard_summary' in dataframes:
    soft = dataframes['soft_summary']
    hard = dataframes['hard_summary']
    combined = pd.concat([soft, hard], ignore_index=True)
    combined['Score'] = 1 / (combined['mean_core_loss'] + 1e-6)  # simple score: lower core loss better
else:
    combined = pd.DataFrame()
    print("⚠️ Missing soft_summary or hard_summary CSV")

# --- Save summary CSV ---
summary_file = results_csv_dir / "powertrain_summary.csv"
combined.to_csv(summary_file, index=False)
print(f"✅ Powertrain summary saved to {summary_file}")

# --- Plot core loss comparison ---
plt.figure(figsize=(6,4))
plt.bar(combined['material_count'], combined['mean_core_loss'], color=['blue','red'])
plt.title('Powertrain Mean Core Loss Comparison')
plt.xlabel('Material Count')
plt.ylabel('Mean Core Loss')
plt.savefig(results_plot_dir / "core_loss_comparison.png")
plt.close()
print(f"✅ Plot saved to {results_plot_dir / 'core_loss_comparison.png'}")
