import numpy as np
import matplotlib.pyplot as plt

# Motor parameters
max_torque = 300      # Nm
base_speed = 4000     # rpm
max_speed = 12000     # rpm
max_power = 160e3     # W

speed = np.linspace(0, max_speed, 200)
torque = []

for s in speed:
    if s <= base_speed:
        torque.append(max_torque)
    else:
        omega = 2*np.pi*s/60
        torque.append(max_power/omega)

torque = np.array(torque)

plt.figure()
plt.plot(speed, torque)
plt.xlabel("Speed (RPM)")
plt.ylabel("Torque (Nm)")
plt.title("Motor Torque-Speed Curve")
plt.grid(True)

plt.savefig("results/plots/torque_speed_curve.png", dpi=300)

print("✅ torque_speed_curve.png saved")