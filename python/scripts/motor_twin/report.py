def report(state):
    return f"""
⚡ TESLA-LEVEL DIGITAL TWIN
----------------------------
Speed      : {state.speed:.0f} rpm
Torque     : {state.torque:.0f} Nm
Efficiency : {state.efficiency:.2f} %
Loss       : {state.loss:.1f} W
Temp       : {state.temp:.1f} °C
"""