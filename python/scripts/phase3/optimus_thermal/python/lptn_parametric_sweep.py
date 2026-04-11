import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[5]

out_dir = PROJECT_ROOT / "results" / "plots"
csv_dir = PROJECT_ROOT / "results" / "optimus_thermal" / "csv"

out_dir.mkdir(parents=True, exist_ok=True)
csv_dir.mkdir(parents=True, exist_ok=True)

ambient = 25
loss = 5000

R_values = np.linspace(0.01, 0.2, 50)

temps = []

for R in R_values:
    temp = ambient + loss * R
    temps.append(temp)

df = pd.DataFrame({
    "ThermalResistance":R_values,
    "Temperature":temps
})

df.to_csv(csv_dir / "lptn_parametric_sweep.csv", index=False)

plt.figure()
plt.plot(R_values, temps)
plt.axhline(120, linestyle="--")
plt.xlabel("Thermal Resistance (K/W)")
plt.ylabel("Winding Temperature (°C)")
plt.title("LPTN Parametric Sweep")
plt.savefig(out_dir / "lptn_parametric_sweep.png")

print("✅ lptn_parametric_sweep.csv saved")
print("✅ lptn_parametric_sweep.png saved")