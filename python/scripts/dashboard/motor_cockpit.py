import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="EV Motor Cockpit", layout="wide")

st.title("⚡ EV Motor Design Cockpit (Digital Twin)")

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("Motor Controls")

speed = st.sidebar.slider("Speed (RPM)", 0, 15000, 6000)
torque = st.sidebar.slider("Torque (Nm)", 0, 300, 150)
Rs = st.sidebar.slider("Stator Resistance (Ω)", 0.01, 0.1, 0.05)
kfe = st.sidebar.slider("Iron Loss Factor", 0.5, 2.0, 1.0)
cooling = st.sidebar.slider("Cooling (0-1)", 0.1, 1.0, 0.7)

omega = speed * 2 * np.pi / 60

# =========================
# CORE MODEL
# =========================
power_out = torque * omega

copper_loss = Rs * torque**2
iron_loss = kfe * speed * 0.01
mech_loss = 200 * (1 - cooling)

loss_total = copper_loss + iron_loss + mech_loss

power_in = power_out + loss_total
eff = power_out / power_in if power_in > 0 else 0
eff_pct = eff * 100

temp = 25 + loss_total * (0.02 + (1 - cooling) * 0.08)

# =========================
# TOP METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Efficiency", f"{eff_pct:.2f}%")
col2.metric("Output Power", f"{power_out/1000:.2f} kW")
col3.metric("Losses", f"{loss_total:.1f} W")
col4.metric("Temp", f"{temp:.1f} °C")

# =========================
# DIGITAL TWIN GAUGE
# =========================
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=eff_pct,
    title={"text": "Motor Efficiency"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "blue"},
        "steps": [
            {"range": [0, 70], "color": "red"},
            {"range": [70, 90], "color": "orange"},
            {"range": [90, 100], "color": "green"},
        ],
    }
))

st.plotly_chart(fig, use_container_width=True)

# =========================
# LOSS BREAKDOWN
# =========================
fig2 = go.Figure(data=[
    go.Pie(
        labels=["Copper", "Iron", "Mechanical"],
        values=[copper_loss, iron_loss, mech_loss]
    )
])

st.plotly_chart(fig2, use_container_width=True)

# =========================
# MINI EFFICIENCY MAP (LIVE SLICE)
# =========================
speeds = np.linspace(0, 15000, 40)
torques = np.linspace(0, 300, 40)

Z = np.zeros((len(torques), len(speeds)))

for i, t in enumerate(torques):
    for j, s in enumerate(speeds):
        w = s * 2 * np.pi / 60
        p_out = t * w
        loss = Rs * t**2 + kfe * s * 0.01 + 200*(1-cooling)
        p_in = p_out + loss
        Z[i, j] = (p_out / p_in) * 100 if p_in > 0 else 0

heatmap = go.Figure(data=go.Heatmap(
    z=Z,
    x=speeds,
    y=torques,
    colorscale="Viridis"
))

heatmap.add_trace(go.Scatter(
    x=[speed],
    y=[torque],
    mode="markers",
    marker=dict(size=10, color="red"),
    name="Operating Point"
))

st.subheader("Efficiency Map (Live)")
st.plotly_chart(heatmap, use_container_width=True)

# =========================
# SUMMARY
# =========================
st.subheader("Operating Point Data")

st.json({
    "speed_rpm": speed,
    "torque_nm": torque,
    "efficiency_%": eff_pct,
    "temperature_C": temp,
    "power_kW": power_out / 1000
})