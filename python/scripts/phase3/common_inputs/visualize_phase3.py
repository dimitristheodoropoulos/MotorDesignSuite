import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent.parent.parent / "results/phase3"
csv_dir = RESULTS_DIR / "csv"
plots_dir = RESULTS_DIR / "plots"
plots_dir.mkdir(parents=True, exist_ok=True)

# Συνένωση CSVs από motor_powertrain & powertrain_modeling
dfs = []
for csv_file in csv_dir.glob("*.csv"):
    df = pd.read_csv(csv_file)
    dfs.append(df)
full_df = pd.concat(dfs, ignore_index=True)

# Παράδειγμα: core loss vs flux density
plt.figure(figsize=(6,4))
for motor_type in full_df['MotorType'].unique():
    subset = full_df[full_df['MotorType'] == motor_type]
    plt.plot(subset['FluxDensity'], subset['CoreLoss'], label=motor_type)
plt.xlabel('Flux Density [T]')
plt.ylabel('Core Loss [W/kg]')
plt.title('Phase3 Motor Core Loss Comparison')
plt.legend()
plt.grid(True)
plt.savefig(plots_dir / "phase3_core_loss_comparison.png")
plt.close()
