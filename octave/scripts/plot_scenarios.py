import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/csv/optimization.csv")

plt.figure()
plt.plot(df["Load"], df["EFF"], "bo-")
plt.xlabel("Load [Nm]")
plt.ylabel("Efficiency")
plt.title("Efficiency vs Load")
plt.grid()
plt.savefig("results/plots/efficiency_vs_load.png")

plt.figure()
plt.plot(df["Load"], df["Losses"], "ro-")
plt.xlabel("Load [Nm]")
plt.ylabel("Losses [W]")
plt.title("Losses vs Load")
plt.grid()
plt.savefig("results/plots/losses_vs_load.png")
