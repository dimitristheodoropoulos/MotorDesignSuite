import streamlit as st
import numpy as np
import plotly.graph_objects as go

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="EV Motor Digital Twin", layout="wide")

st.title("⚡ EV Motor Digital Twin Simulator")

# =========================
# SLIDERS (INPUTS)
# =========================
speed = st.slider("Speed (RPM)", 0, 15000, 6000)
torque = st.slider("Torque (Nm)", 0, 300, 150)
Rs = st.slider("Stator Resistance (Ω)", 0.01, 0.1, 0.05)
cooling = st.slider("Cooling Factor (0=bad, 1=best)", 0.1, 1.0, 0.7)

# =========================
# CORE PHYSICS MODEL (simplified digital twin)
# =========================
omega = speed * 2 * np.pi / 60

power_out = torque * omega

# losses
copper_loss = Rs * torque**2
iron_loss = 0.002 * speed * 0.01
mech_loss = 200 * (1 - cooling)

total_loss = copper_loss + iron_loss + mech_loss

power_in = power_out + total_loss

efficiency = power_out / power_in if power_in > 0 else 0
efficiency_pct = efficiency * 100

# temperature model (lumped)
thermal_resistance = 0.02 + (1 - cooling) * 0.1
temperature = 25 + total_loss * thermal_resistance

# =========================
# DISPLAY METRICS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Efficiency", f"{efficiency_pct:.2f} %")
col2.metric("Losses", f"{total_loss:.1f} W")
col3.metric("Winding Temp", f"{temperature:.1f} °C")

# =========================
# OPERATING POINT VISUAL
# =========================
fig = go.Figure()

fig.add_trace(go.Indicator(
    mode="gauge+number",
    value=efficiency_pct,
    title={"text": "Motor Efficiency"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "green"},
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
# REAL-TIME SUMMARY
# =========================
st.subheader("Operating Point")
st.write({
    "speed_rpm": speed,
    "torque_nm": torque,
    "efficiency_%": efficiency_pct,
    "temperature_C": temperature
})