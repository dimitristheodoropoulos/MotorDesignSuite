import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# paths
PROJECT_ROOT = Path(__file__).resolve().parents[5]
out_dir = PROJECT_ROOT / "results" / "plots"
csv_dir = PROJECT_ROOT / "results" / "csv"

out_dir.mkdir(parents=True, exist_ok=True)
csv_dir.mkdir(parents=True, exist_ok=True)

# base parameters
torque = 200
speed = 6000

Rs_values = np.linspace(0.01, 0.05, 20)
kfe_values = np.linspace(0.5, 2.0, 20)

results = []

for Rs in Rs_values:
    copper_loss = Rs * torque**2

    for kfe in kfe_values:
        iron_loss = kfe * speed * 0.01
        mech_loss = 200

        total_loss = copper_loss + iron_loss + mech_loss
        power_out = torque * speed * 2*np.pi/60
        eff = power_out / (power_out + total_loss)

        results.append([Rs, kfe, eff])

df = pd.DataFrame(results, columns=["Rs","kfe","efficiency"])
df.to_csv(csv_dir / "sensitivity_analysis.csv", index=False)

plt.figure()
plt.scatter(df["Rs"], df["efficiency"], s=10)
plt.xlabel("Stator Resistance Rs")
plt.ylabel("Efficiency")
plt.title("Sensitivity: Efficiency vs Rs")
plt.savefig(out_dir / "sensitivity_rs.png")

print("✅ sensitivity_analysis.csv saved")
print("✅ sensitivity_rs.png saved")