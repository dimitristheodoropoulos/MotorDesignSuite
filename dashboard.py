#!/usr/bin/env python3
"""
dashboard.py – MotorDesignSuite Interactive Dashboard
Run with: streamlit run dashboard.py
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
from scipy.integrate import solve_ivp
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MotorDesignSuite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT    = Path(__file__).parent
PHASE3  = ROOT / "python/scripts/phase3"
MP_CSV  = PHASE3 / "motor_powertrain/results/csv"
OT_CSV  = PHASE3 / "optimus_thermal/results/csv"
RES_CSV = ROOT / "results/csv"

# ── Custom CSS (Tesla-inspired dark style) ────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0d0d0d; }
[data-testid="stSidebar"]          { background-color: #1a1a1a; }
h1, h2, h3                         { color: #CC0000 !important; }
.metric-label                      { color: #888 !important; }
.stTabs [data-baseweb="tab"]       { color: #ccc; }
.stTabs [aria-selected="true"]     { color: #CC0000 !important;
                                     border-bottom: 2px solid #CC0000; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ MotorDesignSuite")
    st.markdown("**Multi-Physics Simulation Framework**")
    st.markdown("---")
    st.markdown("### Motor Parameters")
    R_s    = st.slider("Stator resistance R_s [Ω]", 0.01, 0.20, 0.05, 0.01)
    n_poles= st.slider("Number of poles",            4,    16,   8,    2)
    k_fe   = st.slider("Iron loss coeff k_fe",       0.001,0.010,0.002,0.001,
                        format="%.3f")
    k_mech = st.slider("Mech loss coeff k_mech",     0.1,  2.0,  0.5,  0.1)

    st.markdown("---")
    st.markdown("### LPTN Parameters")
    Q_winding = st.slider("Winding heat [W]",  20.0, 200.0, 80.0, 5.0)
    Q_stator  = st.slider("Stator heat [W]",   5.0,  80.0,  30.0, 5.0)
    T_amb     = st.slider("Ambient temp [°C]", 15.0, 45.0,  25.0, 1.0)

    st.markdown("---")
    st.caption("MotorDesignSuite · Dimitris Theodoropoulos")

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("# ⚡ MotorDesignSuite Dashboard")
st.markdown("*Electric Motor Multi-Physics Simulation Framework*")
st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Efficiency Map",
    "🌡️ Thermal LPTN",
    "🚗 Vehicle Dynamics",
    "📊 Summary",
    "🧬 Optimization",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: Efficiency Map
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## EV Motor Efficiency Map")
    st.markdown("Real-time computation based on sidebar motor parameters.")

    col1, col2 = st.columns([3, 1])
    with col2:
        speed_min = st.number_input("Speed min [rpm]", 100,  2000,  500)
        speed_max = st.number_input("Speed max [rpm]", 3000, 15000, 12000)
        torq_min  = st.number_input("Torque min [Nm]", 1,    50,    5)
        torq_max  = st.number_input("Torque max [Nm]", 50,   600,   300)
        resolution= st.slider("Grid resolution", 20, 80, 50)

    speed_rpm = np.linspace(speed_min, speed_max, resolution)
    torque_nm = np.linspace(torq_min,  torq_max,  resolution)
    omega     = speed_rpm * 2 * np.pi / 60
    T_grid, W_grid = np.meshgrid(torque_nm, omega)

    P_out    = T_grid * W_grid
    I_phase  = T_grid / (n_poles * 0.1)
    P_copper = 3 * R_s * I_phase**2
    P_iron   = k_fe   * W_grid**2
    P_mech   = k_mech * W_grid
    P_loss   = P_copper + P_iron + P_mech
    P_in     = P_out + P_loss
    with np.errstate(invalid='ignore', divide='ignore'):
        eta = np.where(P_in > 0, P_out / P_in, 0.0)
    eta = np.clip(eta, 0.0, 1.0) * 100

    with col1:
        fig, ax = plt.subplots(figsize=(8, 5),
                               facecolor='#0d0d0d')
        ax.set_facecolor('#0d0d0d')
        cf = ax.contourf(speed_rpm, torque_nm, eta.T,
                         levels=np.arange(40, 100, 2),
                         cmap='RdYlGn')
        ct = ax.contour(speed_rpm, torque_nm, eta.T,
                        levels=[70, 80, 85, 90, 92, 94, 95],
                        colors='white', linewidths=0.6, alpha=0.7)
        ax.clabel(ct, fmt='%d%%', fontsize=7, colors='white')
        cbar = fig.colorbar(cf, ax=ax)
        cbar.set_label('Efficiency [%]', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')
        ax.set_xlabel('Speed [rpm]', color='white')
        ax.set_ylabel('Torque [Nm]', color='white')
        ax.set_title('Motor Efficiency Map', color='#CC0000', fontsize=13)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#444')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Metrics row
    peak = eta.max()
    idx  = np.unravel_index(eta.argmax(), eta.shape)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Peak Efficiency",  f"{peak:.1f}%")
    m2.metric("At Speed",         f"{speed_rpm[idx[0]]:.0f} rpm")
    m3.metric("At Torque",        f"{torque_nm[idx[1]]:.0f} Nm")
    m4.metric("Mean Efficiency",  f"{eta[eta>50].mean():.1f}%")

    # Peak eff vs speed
    st.markdown("### Peak Efficiency vs Speed")
    fig2, ax2 = plt.subplots(figsize=(8, 3), facecolor='#0d0d0d')
    ax2.set_facecolor('#0d0d0d')
    ax2.plot(speed_rpm, eta.max(axis=1), color='#CC0000', linewidth=2)
    ax2.set_xlabel('Speed [rpm]', color='white')
    ax2.set_ylabel('Peak Efficiency [%]', color='white')
    ax2.tick_params(colors='white')
    ax2.set_ylim(60, 100)
    ax2.grid(True, color='#333', linestyle='--', alpha=0.5)
    for spine in ax2.spines.values(): spine.set_edgecolor('#444')
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: Thermal LPTN
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## LPTN Thermal Network Simulation")
    st.markdown("Transient thermal response of motor nodes (Radau ODE solver).")

    NODES = ['Winding', 'Stator', 'Rotor', 'Housing', 'Coolant']
    N     = len(NODES)

    R = np.array([
        [0,    0.30, 0.48, 0,    0   ],
        [0.30, 0,    0.24, 0.36, 0   ],
        [0.48, 0.24, 0,    0,    0.42],
        [0,    0.36, 0,    0,    0.18],
        [0,    0,    0.42, 0.18, 0   ],
    ])
    R_amb = np.array([0, 0, 0, 0.60, 0.30])
    C     = np.array([0.5, 2.0, 1.5, 3.0, 4.0])
    Q_gen = np.array([Q_winding, Q_stator, 20.0, 5.0, 0.0])

    G = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j and R[i,j] > 0:
                g = 1.0 / R[i,j]
                G[i,j] -= g; G[i,i] += g

    Q_amb = np.zeros(N)
    for i in range(N):
        if R_amb[i] > 0:
            g = 1.0 / R_amb[i]
            G[i,i]  += g
            Q_amb[i] = g * T_amb
    Q_total = Q_gen + Q_amb

    def ode(t, T): return (Q_total - G @ T) / C

    t_sim = st.slider("Simulation time [s]", 30, 600, 300, 30)
    sol   = solve_ivp(ode, (0, t_sim), np.ones(N)*T_amb,
                      method='Radau', t_eval=np.linspace(0, t_sim, 400),
                      rtol=1e-8, atol=1e-10)

    history = sol.y.T
    time    = sol.t
    steady  = history[-1]

    col1, col2 = st.columns(2)
    node_colors = ['#CC0000','#4488FF','#FF8800','#44CC44','#AA44CC']

    with col1:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#0d0d0d')
        ax.set_facecolor('#0d0d0d')
        for i, node in enumerate(NODES):
            ax.plot(time, history[:,i], label=node,
                    color=node_colors[i], linewidth=2)
        ax.axhline(T_amb, color='#666', linestyle='--', linewidth=1, label='Ambient')
        ax.set_xlabel('Time [s]', color='white')
        ax.set_ylabel('Temperature [°C]', color='white')
        ax.set_title('Transient Response', color='#CC0000')
        ax.tick_params(colors='white')
        ax.legend(fontsize=7, facecolor='#1a1a1a', labelcolor='white')
        ax.grid(True, color='#333', alpha=0.5)
        for sp in ax.spines.values(): sp.set_edgecolor('#444')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='#0d0d0d')
        ax.set_facecolor('#0d0d0d')
        bars = ax.bar(NODES, steady, color=node_colors)
        ax.axhline(T_amb, color='#666', linestyle='--', linewidth=1)
        ax.set_ylabel('Temperature [°C]', color='white')
        ax.set_title('Steady-State Temperatures', color='#CC0000')
        ax.tick_params(colors='white')
        ax.grid(True, axis='y', color='#333', alpha=0.5)
        for sp in ax.spines.values(): sp.set_edgecolor('#444')
        for bar, val in zip(bars, steady):
            ax.text(bar.get_x()+bar.get_width()/2, val+0.5,
                    f'{val:.1f}°C', ha='center', va='bottom',
                    color='white', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Steady-state table
    st.markdown("### Steady-State Temperatures")
    df_ss = pd.DataFrame({'Node': NODES, 'Temperature [°C]': steady.round(1),
                           'Rise above ambient [°C]': (steady - T_amb).round(1)})
    st.dataframe(df_ss, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: Vehicle Dynamics
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## Vehicle Dynamics Simulation")

    col1, col2, col3 = st.columns(3)
    mass   = col1.number_input("Mass [kg]",             500,  3000, 1200)
    F_trac = col2.number_input("Traction force [N]",    1000, 10000,4000)
    F_res  = col3.number_input("Resistive force [N]",   50,   1000, 300)
    t_end  = st.slider("Simulation time [s]", 5, 60, 20)

    dt = 0.05
    t  = np.arange(0, t_end+dt, dt)
    v  = np.zeros(len(t))
    x  = np.zeros(len(t))
    a  = (F_trac - F_res) / mass

    for k in range(1, len(t)):
        v[k] = v[k-1] + a * dt
        x[k] = x[k-1] + v[k-1]*dt + 0.5*a*dt**2

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), facecolor='#0d0d0d')
    for ax in (ax1, ax2):
        ax.set_facecolor('#0d0d0d')
        ax.tick_params(colors='white')
        ax.grid(True, color='#333', alpha=0.5)
        for sp in ax.spines.values(): sp.set_edgecolor('#444')

    ax1.plot(t, v, color='#4488FF', linewidth=2)
    ax1.set_ylabel('Velocity [m/s]', color='white')
    ax1.set_title('Vehicle Velocity', color='#CC0000')

    ax2.plot(t, x, color='#44CC44', linewidth=2)
    ax2.set_ylabel('Position [m]', color='white')
    ax2.set_xlabel('Time [s]', color='white')
    ax2.set_title('Vehicle Position', color='#CC0000')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    c1, c2, c3 = st.columns(3)
    c1.metric("Final Velocity",   f"{v[-1]:.1f} m/s  ({v[-1]*3.6:.0f} km/h)")
    c2.metric("Distance covered", f"{x[-1]:.0f} m")
    c3.metric("Acceleration",     f"{a:.2f} m/s²")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: Summary
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## Project Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Simulation Modules", "7")
    c2.metric("Output Plots",       "13+")
    c3.metric("Tools Used",         "5")
    c4.metric("Tesla Role Match",   "~80%")

    st.markdown("### Tesla Role Alignment")
    alignment = {
        "Electromagnetic FEA":          85,
        "Thermal Modeling (LPTN)":      90,
        "EV Efficiency Mapping":        85,
        "Powertrain Optimization":      80,
        "Python / Octave Programming":  95,
        "Vehicle Dynamics":             70,
        "Multi-criteria Optimization":  75,
    }
    for skill, pct in alignment.items():
        col1, col2 = st.columns([3, 1])
        col1.progress(pct, text=skill)
        col2.markdown(f"**{pct}%**")

    st.markdown("---")
    st.markdown("### Framework Pipeline")
    st.code("""
Magnetic FEA (FreeFEM++)
    ↓
Python Preprocessing (materials, FEA input)
    ↓
Octave Simulations (core analysis, thermal map, vehicle dynamics)
    ↓
Phase 3a: Powertrain Modeling (multi-criteria optimization)
Phase 3b: Motor Powertrain + Efficiency Map
Phase 3c: Optimus Thermal (LPTN, validation vs FEA)
    ↓
Ngspice Circuit Simulation
    ↓
PDF Engineering Report
    """, language="text")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: Pareto Optimization
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("## Multi-Objective Motor Optimization")
    st.markdown("Pareto front across **3 objectives**: Efficiency ↑ · Torque Density ↑ · Losses ↓")

    pareto_csv = ROOT / "results/csv/optimization_pareto.csv"
    all_csv    = ROOT / "results/csv/optimization_all.csv"

    col_run, col_info = st.columns([1, 3])
    with col_run:
        run_opt = st.button("▶ Run Optimizer", type="primary")
    with col_info:
        if pareto_csv.exists():
            df_p = pd.read_csv(pareto_csv)
            st.success(f"✅ Pareto data loaded: {len(df_p)} optimal designs")
        else:
            st.warning("⚠️ No optimization data yet. Click 'Run Optimizer'.")
            df_p = None

    if run_opt:
        import subprocess, sys as _sys
        with st.spinner("Running multi-objective optimization (~20-30s)..."):
            result = subprocess.run(
                [_sys.executable, str(ROOT / "optimizer.py")],
                capture_output=True, text=True
            )
        if result.returncode == 0:
            st.success("✅ Optimization complete!")
            st.code(result.stdout)
            df_p = pd.read_csv(pareto_csv)
        else:
            st.error("❌ Optimizer failed")
            st.code(result.stderr)
            df_p = None

    if df_p is not None and len(df_p) > 0:
        st.markdown("### Pareto Front Visualization")
        df_all = pd.read_csv(all_csv) if all_csv.exists() else df_p

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4), facecolor="#0d0d0d")
            ax.set_facecolor("#0d0d0d")
            ax.scatter(df_all["Efficiency"], df_all["TotalLosses_W"],
                       c="#333", s=4, alpha=0.3, label="All designs")
            ax.scatter(df_p["Efficiency"], df_p["TotalLosses_W"],
                       c="#CC0000", s=25, zorder=5, label="Pareto front")
            ax.set_xlabel("Efficiency [%]", color="white")
            ax.set_ylabel("Total Losses [W]", color="white")
            ax.set_title("Efficiency vs Losses", color="#CC0000")
            ax.tick_params(colors="white")
            ax.legend(fontsize=7, facecolor="#1a1a1a", labelcolor="white")
            ax.grid(True, color="#333", alpha=0.4)
            for sp in ax.spines.values(): sp.set_edgecolor("#444")
            plt.tight_layout()
            st.pyplot(fig); plt.close()

        with col2:
            fig, ax = plt.subplots(figsize=(6, 4), facecolor="#0d0d0d")
            ax.set_facecolor("#0d0d0d")
            sc = ax.scatter(df_p["Efficiency"], df_p["TorqueDensity"],
                            c=df_p["TotalLosses_W"], cmap="RdYlGn_r", s=40)
            cbar = fig.colorbar(sc, ax=ax)
            cbar.set_label("Losses [W]", color="white")
            cbar.ax.yaxis.set_tick_params(color="white")
            plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")
            ax.set_xlabel("Efficiency [%]", color="white")
            ax.set_ylabel("Torque Density", color="white")
            ax.set_title("Pareto: Eff vs Torque (color=Losses)", color="#CC0000")
            ax.tick_params(colors="white")
            ax.grid(True, color="#333", alpha=0.4)
            for sp in ax.spines.values(): sp.set_edgecolor("#444")
            plt.tight_layout()
            st.pyplot(fig); plt.close()

        st.markdown("### Top 10 Optimal Designs")
        top10 = df_p.nlargest(10, "Efficiency")[[
            "R_s","k_fe","k_mech","Speed_rpm","Torque_Nm",
            "Efficiency","TorqueDensity","TotalLosses_W"
        ]].round(3)
        st.dataframe(top10, use_container_width=True, hide_index=True)

        best = df_p.loc[df_p["Efficiency"].idxmax()]
        st.markdown("### 🏆 Best Design Point")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Efficiency",     f"{best['Efficiency']:.2f}%")
        b2.metric("Torque Density", f"{best['TorqueDensity']:.3f}")
        b3.metric("Total Losses",   f"{best['TotalLosses_W']:.1f} W")
        b4.metric("Speed / Torque", f"{best['Speed_rpm']:.0f} rpm / {best['Torque_Nm']:.0f} Nm")