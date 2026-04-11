# motor_twin/ui_streamlit.py
import streamlit as st
import numpy as np

from motor_twin.core import MotorModel
from motor_twin.thermal import ThermalModel
from motor_twin.state import MotorState
from motor_twin.optimizer import pareto
from motor_twin.report import report
from motor_twin.drive_cycle import cycle

st.set_page_config(page_title="Tesla-Level EV Digital Twin", layout="wide")

st.title("⚡ Tesla-Level EV Motor Digital Twin")

model = MotorModel()
thermal = ThermalModel()

# ---------------- MODE ----------------
mode = st.selectbox("Mode", ["Single Point", "Drive Cycle", "Optimization"])

# ================= SINGLE POINT =================
if mode == "Single Point":

    speed = st.slider("Speed (rpm)", 0, 12000, 4000)
    torque = st.slider("Torque (Nm)", 0, 300, 120)

    res = model.compute(speed, torque)

    temp = thermal.step(80, res["loss"])

    state = MotorState(speed, torque, temp, res["efficiency"], res["loss"])

    st.metric("Efficiency", f"{state.efficiency:.2f}%")
    st.metric("Loss", f"{state.loss:.1f} W")
    st.metric("Temperature", f"{state.temp:.1f} °C")

    st.text(report(state))

# ================= DRIVE CYCLE =================
elif mode == "Drive Cycle":

    speed, torque = cycle()

    temps = []
    effs = []

    temp = 25

    for s, t in zip(speed, torque):
        r = model.compute(s, t)
        temp = thermal.step(temp, r["loss"])
        temps.append(temp)
        effs.append(r["efficiency"])

    st.line_chart({
        "Temperature": temps,
        "Efficiency": effs
    })

# ================= OPTIMIZATION =================
elif mode == "Optimization":

    speeds = np.linspace(1000, 12000, 20)
    torques = np.linspace(20, 300, 20)

    results = pareto(model, speeds, torques)

    eff = [r[2] for r in results]
    loss = [r[3] for r in results]

    st.scatter_chart({
        "Efficiency": eff,
        "Loss": loss
    })