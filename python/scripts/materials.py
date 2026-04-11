# /home/testuser/PowertrainSimSuite/python/scripts/materials.py
import pandas as pd
from pathlib import Path
import json
import matplotlib.pyplot as plt

# --- Project paths ---
project_root = Path(__file__).resolve().parent.parent.parent  # πάμε στο root
results_csv_dir   = project_root / "results/csv"
results_plots_dir = project_root / "results/plots"
results_plots_dir.mkdir(parents=True, exist_ok=True)

# --- Load material summaries ---
soft_file = results_csv_dir / "soft_summary.csv"
hard_file = results_csv_dir / "hard_summary.csv"
fea_file  = results_csv_dir / "fea_results.csv"

# fallback dummy data αν δεν υπάρχουν τα αρχεία
soft = pd.read_csv(soft_file) if soft_file.exists() else pd.DataFrame([{"mean_core_loss":1.0}])
hard = pd.read_csv(hard_file) if hard_file.exists() else pd.DataFrame([{"mean_core_loss":2.0}])
fea  = pd.read_csv(fea_file)  if fea_file.exists()  else pd.DataFrame([
    {"Material":"soft","MeanCoreLoss":1.0},
    {"Material":"hard","MeanCoreLoss":2.0}
])

# --- Prepare comparison data ---
comparison_data = {
    "soft": {
        "material_core_loss": float(soft["mean_core_loss"].values[0]),
        "fea_core_loss": float(fea.loc[fea.Material=="soft","MeanCoreLoss"].values[0])
    },
    "hard": {
        "material_core_loss": float(hard["mean_core_loss"].values[0]),
        "fea_core_loss": float(fea.loc[fea.Material=="hard","MeanCoreLoss"].values[0])
    }
}

# --- Save comparison JSON ---
with open(results_csv_dir / "fea_comparison.json", "w") as f:
    json.dump(comparison_data, f, indent=2)
print(f"[INFO] Saved FEA comparison JSON: {results_csv_dir / 'fea_comparison.json'}")

# --- Generate FEA comparison plot ---
materials = ["soft", "hard"]
material_loss = [comparison_data[m]["material_core_loss"] for m in materials]
fea_loss      = [comparison_data[m]["fea_core_loss"]      for m in materials]

plt.figure(figsize=(6,4))
x = range(len(materials))
plt.bar([i-0.15 for i in x], material_loss, width=0.3, label="Material")
plt.bar([i+0.15 for i in x], fea_loss, width=0.3, label="FEA")
plt.xticks(x, ["Soft Magnetic", "Hard Magnetic"])
plt.ylabel("Mean Core Loss")
plt.title("Material vs FEA Core Loss Comparison")
plt.legend()
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# --- Save plots στον root results/plots ---
fea_plot_file      = results_plots_dir / "fea_comparison.png"
coreloss_plot_file = results_plots_dir / "core_loss_comparison.png"

plt.savefig(fea_plot_file, dpi=150)
print(f"[INFO] Saved FEA comparison plot: {fea_plot_file}")

plt.savefig(coreloss_plot_file, dpi=150)
print(f"[INFO] Saved core loss comparison plot: {coreloss_plot_file}")

plt.close()
