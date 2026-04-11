import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[5]

out_dir = PROJECT_ROOT / "results" / "plots"
csv_dir = PROJECT_ROOT / "results" / "csv"

out_dir.mkdir(parents=True, exist_ok=True)
csv_dir.mkdir(parents=True, exist_ok=True)

# Design parameter ranges
Rs = np.linspace(0.01, 0.05, 30)
kfe = np.linspace(0.5, 2.0, 30)

points = []

# Sweep design space
for r in Rs:
    for k in kfe:

        torque = 200
        speed = 6000

        # Loss models
        copper = r * torque**2
        iron = k * speed * 0.01
        mech = 200

        loss = copper + iron + mech

        # Mechanical output power
        power = torque * speed * 2*np.pi/60

        # Efficiency
        eff = power / (power + loss)

        # Simplified motor mass model
        mass = 50 + 200*r + 5*k

        points.append([eff, mass, r, k])

# Create dataframe
df = pd.DataFrame(points, columns=["efficiency", "mass", "Rs", "kfe"])

# Save full design space
df.to_csv(csv_dir / "pareto_motor.csv", index=False)

# ------------------------------------------------
# Pareto Frontier Extraction
# ------------------------------------------------

df_sorted = df.sort_values("mass")

pareto_points = []
best_eff = 0

for _, row in df_sorted.iterrows():
    if row["efficiency"] > best_eff:
        pareto_points.append(row)
        best_eff = row["efficiency"]

pareto_df = pd.DataFrame(pareto_points)

# Save Pareto frontier
pareto_df.to_csv(csv_dir / "pareto_frontier.csv", index=False)

# ------------------------------------------------
# Plot
# ------------------------------------------------

plt.figure(figsize=(8,6))

# All design points
plt.scatter(
    df["mass"],
    df["efficiency"],
    s=10,
    alpha=0.5,
    label="Design Space"
)

# Pareto frontier
plt.plot(
    pareto_df["mass"],
    pareto_df["efficiency"],
    linewidth=3,
    label="Pareto Frontier"
)

plt.xlabel("Motor Mass (kg)")
plt.ylabel("Efficiency")
plt.title("Motor Design Pareto Trade-off")
plt.legend()

plt.savefig(out_dir / "pareto_motor.png", dpi=300)

print("✅ pareto_motor.csv saved")
print("✅ pareto_frontier.csv saved")
print("✅ pareto_motor.png saved")