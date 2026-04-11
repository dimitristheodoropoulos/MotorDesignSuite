import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="EV Motor Cockpit v2", layout="wide")

st.title("⚡ EV Motor Digital Twin v2 (Engineering Mode)")

# =========================
# INPUTS
# =========================
speed = st.sidebar.slider("Speed (RPM)", 0, 18000, 6000)
torque = st.sidebar.slider("Torque (Nm)", 0, 300, 150)
Rs = st.sidebar.slider("Stator Resistance (Ω)", 0.01, 0.1, 0.05)
kfe = st.sidebar.slider("Iron Loss Factor", 0.5, 2.0, 1.0)
cooling = st.sidebar.slider("Cooling (0-1)", 0.1, 1.0, 0.7)

omega = speed * 2 * np.pi / 60

# =========================
# BASE MODEL
# =========================
power_out = torque * omega

copper_loss = Rs * torque**2
iron_loss = kfe * speed * 0.01
mech_loss = 200 * (1 - cooling)

loss = copper_loss + iron_loss + mech_loss

power_in = power_out + loss
eff = power_out / power_in if power_in > 0 else 0
eff_pct = eff * 100

temp = 25 + loss * (0.02 + (1 - cooling) * 0.1)

# =========================
# FLUX WEAKENING MODEL
# =========================
base_speed = 6000
flux_limit = 250 * (base_speed / max(speed, 1))

flux_warning = torque > flux_limit

# =========================
# THERMAL WARNING
# =========================
thermal_limit = 120
thermal_warning = temp > thermal_limit

# =========================
# METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Efficiency", f"{eff_pct:.2f}%")
col2.metric("Power (kW)", f"{power_out/1000:.2f}")
col3.metric("Temp (°C)", f"{temp:.1f}", 
            "⚠️ OVERHEAT" if thermal_warning else "OK")
col4.metric("Flux Status", 
            "WEAKENING" if flux_warning else "OK")

# =========================
# 3D EFFICIENCY SURFACE
# =========================
speeds = np.linspace(0, 18000, 40)
torques = np.linspace(0, 300, 40)

Z = np.zeros((len(torques), len(speeds)))

for i, t in enumerate(torques):
    for j, s in enumerate(speeds):
        w = s * 2 * np.pi / 60
        p_out = t * w
        loss = Rs * t**2 + kfe * s * 0.01 + 200*(1-cooling)
        p_in = p_out + loss
        Z[i, j] = (p_out / p_in) * 100 if p_in > 0 else 0

fig = go.Figure(data=[
    go.Surface(z=Z, x=speeds, y=torques, colorscale="Viridis")
])

fig.update_layout(
    title="3D Efficiency Surface",
    scene=dict(
        xaxis_title="Speed (RPM)",
        yaxis_title="Torque (Nm)",
        zaxis_title="Efficiency (%)"
    )
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# OPERATING POINT
# =========================
fig2 = go.Figure()

fig2.add_trace(go.Scatter3d(
    x=[speed],
    y=[torque],
    z=[eff_pct],
    mode="markers",
    marker=dict(size=6, color="red"),
    name="Operating Point"
))

st.plotly_chart(fig2, use_container_width=True)

# =========================
# WARNING PANEL
# =========================
st.subheader("System Status")

st.write({
    "Flux_Weakening": bool(flux_warning),
    "Thermal_Overload": bool(thermal_warning),
    "Safe_Operation": not (flux_warning or thermal_warning)
})