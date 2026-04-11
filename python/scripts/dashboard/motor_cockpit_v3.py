import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="EV Motor Cockpit v3", layout="wide")

st.title("⚡ EV Motor Digital Twin v3 – Optimization & Drive Cycle")

# =========================
# INPUTS
# =========================
speed = st.sidebar.slider("Speed (RPM)", 0, 18000, 6000)
torque = st.sidebar.slider("Torque (Nm)", 0, 300, 150)
Rs = st.sidebar.slider("Stator Resistance (Ω)", 0.01, 0.1, 0.05)
kfe = st.sidebar.slider("Iron Loss Factor", 0.5, 2.0, 1.0)
cooling = st.sidebar.slider("Cooling (0-1)", 0.1, 1.0, 0.7)

mode = st.sidebar.selectbox(
    "Mode",
    ["Normal", "Fault: High Resistance", "Fault: Cooling Loss"]
)

# =========================
# CORE MODEL
# =========================
def motor_model(s, t, Rs, kfe, cooling):
    w = s * 2 * np.pi / 60

    power_out = t * w

    # faults
    if mode == "Fault: High Resistance":
        Rs *= 3
    if mode == "Fault: Cooling Loss":
        cooling *= 0.3

    copper = Rs * t**2
    iron = kfe * s * 0.01
    mech = 200 * (1 - cooling)

    loss = copper + iron + mech
    power_in = power_out + loss

    eff = power_out / power_in if power_in > 0 else 0
    temp = 25 + loss * (0.02 + (1 - cooling) * 0.1)

    return eff * 100, temp, loss

eff, temp, loss = motor_model(speed, torque, Rs, kfe, cooling)

# =========================
# METRICS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Efficiency", f"{eff:.2f}%")
col2.metric("Losses", f"{loss:.1f} W")
col3.metric("Temperature", f"{temp:.1f} °C")

# =========================
# OPTIMIZATION (GENETIC SEARCH SIMPLIFIED)
# =========================
st.subheader("🧠 Optimization Engine (Best Operating Point)")

best = {"eff": 0}

for s in np.linspace(1000, 15000, 25):
    for t in np.linspace(10, 300, 25):
        e, temp_i, loss_i = motor_model(s, t, Rs, kfe, cooling)
        if e > best["eff"]:
            best = {"eff": e, "s": s, "t": t}

st.write({
    "Best Efficiency": best["eff"],
    "Best Speed": best["s"],
    "Best Torque": best["t"]
})

# =========================
# DRIVE CYCLE SIMULATION
# =========================
st.subheader("🚗 Drive Cycle Simulation")

time = np.linspace(0, 30, 100)

speed_profile = 5000 + 3000 * np.sin(time / 5)
torque_profile = 100 + 80 * np.cos(time / 6)

eff_series = []
temp_series = []

for s, t in zip(speed_profile, torque_profile):
    e, temp_i, _ = motor_model(s, t, Rs, kfe, cooling)
    eff_series.append(e)
    temp_series.append(temp_i)

fig = go.Figure()

fig.add_trace(go.Scatter(x=time, y=eff_series, name="Efficiency"))
fig.add_trace(go.Scatter(x=time, y=temp_series, name="Temperature"))

fig.update_layout(
    title="Drive Cycle Response",
    xaxis_title="Time (s)",
    yaxis_title="Value"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# OPERATING POINT VISUAL
# =========================
st.subheader("Operating Map")

speeds = np.linspace(0, 18000, 30)
torques = np.linspace(0, 300, 30)

Z = np.zeros((len(torques), len(speeds)))

for i, t in enumerate(torques):
    for j, s in enumerate(speeds):
        Z[i, j], _, _ = motor_model(s, t, Rs, kfe, cooling)

fig2 = go.Figure(data=go.Heatmap(
    z=Z,
    x=speeds,
    y=torques,
    colorscale="Viridis"
))

fig2.add_trace(go.Scatter(
    x=[speed],
    y=[torque],
    mode="markers",
    marker=dict(size=10, color="red"),
    name="Operating Point"
))

st.plotly_chart(fig2, use_container_width=True)

# =========================
# FAULT WARNING
# =========================
st.subheader("System Status")

st.json({
    "mode": mode,
    "safe": mode == "Normal" and temp < 120,
    "temperature": temp
})