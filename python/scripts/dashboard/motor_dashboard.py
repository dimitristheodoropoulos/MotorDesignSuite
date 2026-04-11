import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# PROJECT ROOT (safe relative path)
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[3]

csv_path = PROJECT_ROOT / "results" / "csv" / "efficiency_map.csv"
out_dir = PROJECT_ROOT / "results" / "plots"

out_dir.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(csv_path)

# =========================================================
# NORMALIZE COLUMN NAMES
# =========================================================
df = df.rename(columns={
    "Speed_rpm": "speed_rpm",
    "Torque_Nm": "torque_nm",
    "Efficiency_%": "efficiency"
})

# =========================================================
# EFFICIENCY HEATMAP
# =========================================================
fig1 = px.density_heatmap(
    df,
    x="speed_rpm",
    y="torque_nm",
    z="efficiency",
    title="Motor Efficiency Map",
    color_continuous_scale="Viridis"
)

fig1.update_layout(
    xaxis_title="Speed (RPM)",
    yaxis_title="Torque (Nm)"
)

# =========================================================
# TORQUE-SPEED CURVE
# =========================================================
fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=df["speed_rpm"],
        y=df["torque_nm"],
        mode="lines+markers",
        name="Torque-Speed Curve"
    )
)

fig2.update_layout(
    title="Torque-Speed Curve",
    xaxis_title="Speed (RPM)",
    yaxis_title="Torque (Nm)"
)

# =========================================================
# SAVE HTML DASHBOARDS ONLY (NO KVALEIDO / NO PNG)
# =========================================================
heatmap_html = out_dir / "efficiency_map_dashboard.html"
curve_html   = out_dir / "torque_speed_dashboard.html"

fig1.write_html(heatmap_html)
fig2.write_html(curve_html)

# =========================================================
# OUTPUT INFO
# =========================================================
print("✅ Dashboard exported successfully (HTML only)")
print(f"   - {heatmap_html}")
print(f"   - {curve_html}")