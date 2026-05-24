# MotorDesignSuite

**MotorDesignSuite** is a comprehensive Python/Octave/FreeFEM/Ngspice multi-physics simulation framework for electric motor analysis, thermal modeling, powertrain optimization, and EV performance mapping. It targets motor design and thermal engineering workflows, suitable for software-based development without proprietary hardware.

---

## Key Results

| Metric | Value |
|--------|-------|
| Peak Motor Efficiency | 95.5% |
| Winding Steady-State Temp (Air Cooling) | 93.0°C ✅ |
| Winding Steady-State Temp (Liquid Cooling) | 72.7°C ✅ |
| LPTN vs FEA Error (Winding) | 2.0°C |
| Pareto-Optimal Designs | 26 / 4500 evaluated |
| Peak Power (Torque-Speed) | 52.4 kW |
| Parallel Optimizer Speed | 4500 designs in 0.3s (4 workers) |
| SQL Database Records | 4500 simulation results, avg efficiency 86.99% |

---

## Simulation Pipeline

```
Magnetic FEA (FreeFEM++)
        ↓
Python Preprocessing (materials, FEA input)
        ↓
Octave Simulations (core analysis, thermal map, vehicle dynamics)
        ↓
Phase 3a: Powertrain Modeling      (multi-criteria optimization)
Phase 3b: Motor Powertrain         (efficiency map, torque-speed, loss breakdown)
Phase 3c: Optimus Thermal          (LPTN, cooling scenarios, FEA validation)
        ↓
Parallel Pareto Optimizer          (4 workers, multiprocessing pool)
        ↓
SQLite Persistence                 (SQL queries on 4500+ simulation records)
        ↓
Streamlit Dashboard + PDF Report


---

## Phases Overview

### Phase 1 – Magnetic Materials Simulation
- Magnetostatic FEA of soft and hard magnetic materials (FreeFEM++)
- Core loss analysis and visualization
- Ngspice simulations for magnetic circuits
- Python/Octave preprocessing and report generation

### Phase 2 – Multi-Material & Preprocessing Workflow
- Data preparation and integration of Phase 1 outputs
- Multi-material analysis and visualization
- Intermediate results for powertrain modeling

### Phase 3 – Powertrain Engineering & Thermal Design

**3a. Powertrain Modeling Engineer**
- Octave/MATLAB functions for powertrain modeling
- Multi-physics integration (electromagnetic + thermal + mechanical)
- Multi-criteria optimization (efficiency, torque, thermal)
- Large-scale data processing and visualization

**3b. Electrical Engineer – Motor Powertrain**
- EV motor efficiency map (60×60 grid, 500–12,000 rpm)
- Torque-speed curve with flux weakening (52.4 kW peak power)
- Loss breakdown: copper / iron / mechanical (stacked + pie chart)
- Multi-criteria optimization (efficiency, cost, torque, heat)
- Advanced FEA processing and visualization

**3c. Thermal Design Engineer – Optimus Actuators**
- Lumped Parameter Thermal Network (LPTN): Winding, Stator, Rotor, Housing, Coolant
- Transient ODE solver (scipy Radau — stiff RC network)
- Steady-state validation vs FEA reference: Winding 2°C, Stator 4°C, Rotor 7°C error
- Cooling scenario comparison: No cooling (156°C ⚠️) / Air (93°C ✅) / Liquid (72°C ✅)
- Python (scipy) and Octave/MATLAB implementations

### Phase 4 – Parallel Optimization & SQL Persistence

**Distributed-Ready Simulation Framework**
- Parallel Pareto optimizer using Python `multiprocessing.Pool` (4 workers)
- 4500 design evaluations completed in **0.3 seconds**
- Full SQL persistence via **SQLite** — all simulation results stored and queryable
- Supports complex analytical queries across the entire design space:


-- Example: best designs at mid-range operating speed
SELECT R_s, Efficiency, TotalLosses_W
FROM simulations
WHERE Torque_Nm > 200 AND Speed_rpm BETWEEN 4000 AND 6000
ORDER BY Efficiency DESC LIMIT 10;
```

- Architecture designed for distributed-simulation workflows — scalable to multi-node cluster deployment (Ray / Celery) without code restructuring

---

## Roles Covered

| Role | Phase |
|------|-------|
| Associate Electrical Engineer – System Design & Powertrain Modelling | 1–2 |
| Powertrain Modeling Engineer | 3a |
| Electrical Engineer – Motor Powertrain | 3b |
| Thermal Design Engineer – Tesla Optimus | 3c |
| System Design / Architecture Engineer (Distributed Simulations) | 4 |

---

## Project Structure


MotorDesignSuite/
├── python/scripts/
│   ├── materials.py
│   ├── fea_preprocess.py
│   ├── data_processing.py
│   └── phase3/
│       ├── powertrain_modeling/python/powertrain_modeling.py
│       ├── motor_powertrain/python/
│       │   ├── motor_powertrain.py
│       │   ├── efficiency_map.py        ← EV efficiency heatmap
│       │   ├── torque_speed.py          ← torque-speed + flux weakening
│       │   └── loss_breakdown.py        ← copper/iron/mech loss analysis
│       └── optimus_thermal/python/
│           ├── lptn_model.py            ← LPTN transient + FEA validation
│           └── cooling_comparison.py    ← air vs liquid cooling scenarios
├── octave/scripts/
│   ├── core_analysis.m
│   ├── motor_simulation.m
│   ├── thermal_map.m
│   ├── vehicle_dynamics.m
│   └── visualization.m
├── freefem/models/
│   ├── soft_magnetic.edp               ← magnetostatic FEA
│   └── hard_magnetic.edp
├── ngspice/circuits/
│   ├── motor_model.cir
│   └── hysteresis_model.cir
├── optimizer.py                         ← Pareto 3-objective optimizer (single-threaded)
├── optimizer_parallel_sql.py            ← Parallel optimizer + SQLite persistence ⭐
├── dashboard.py                         ← Streamlit interactive dashboard
├── generate_report.py                   ← Tesla-style PDF report
├── run_all.sh                           ← full 9-step workflow
├── results/
│   ├── csv/
│   ├── plots/
│   ├── reports/
│   ├── optimus_thermal/
│   └── optimization_results.db          ← SQLite database (4500 records) ⭐
└── tests/
    ├── test_python.py
    ├── test_lptn.py
    ├── test_octave_core.m
    └── test_ngspice.sh


---

## Installation & Setup


git clone https://github.com/dimitristheodoropoulos/MotorDesignSuite.git
cd MotorDesignSuite

python3 -m venv venv
source venv/bin/activate

pip install -r python/requirements.txt
pip install streamlit reportlab scipy


External tools (install via apt):

sudo apt install octave freefem++ ngspice sqlite3


---

## Running

### Full workflow (9 steps)

bash run_all.sh


### Parallel optimizer with SQL persistence (recommended)

python3 optimizer_parallel_sql.py


### Query results directly in SQLite

sqlite3 results/optimization_results.db


SELECT COUNT(*) FROM simulations;
SELECT AVG(Efficiency) FROM simulations;
SELECT R_s, Efficiency, TotalLosses_W
FROM simulations
WHERE Torque_Nm > 200 AND Speed_rpm BETWEEN 4000 AND 6000
ORDER BY Efficiency DESC LIMIT 10;


### Interactive dashboard

streamlit run dashboard.py


### Original Pareto optimizer

python3 optimizer.py


### PDF engineering report

python3 generate_report.py


---

## Output Locations

| Type | Location |
|------|----------|
| Main plots | `results/plots/` |
| Main CSVs | `results/csv/` |
| Thermal plots | `results/optimus_thermal/plots/` |
| Thermal CSVs | `results/optimus_thermal/csv/` |
| Motor Powertrain | `python/scripts/phase3/motor_powertrain/results/` |
| LPTN Thermal | `python/scripts/phase3/optimus_thermal/results/` |
| PDF Report | `results/reports/MotorDesignSuite_Report.pdf` |
| **SQL Database** | **`results/optimization_results.db`** |
| Logs | `results/logs/` |

---

## Running Tests


source venv/bin/activate
python3 tests/test_python.py
python3 tests/test_lptn.py
octave --silent tests/test_octave_core.m
bash tests/test_ngspice.sh


---

## Tools & Stack

| Tool | Role |
|------|------|
| Python 3.12 | Main simulation & analysis |
| GNU Octave 8.4 | Motor & dynamics simulation |
| FreeFEM++ 4.13 | Electromagnetic FEA |
| Ngspice 42 | Circuit simulation |
| NumPy / SciPy | Numerical methods, ODE solver |
| Matplotlib | Visualization |
| Streamlit | Interactive dashboard |
| ReportLab | PDF report generation |
| **multiprocessing** | **Parallel simulation workers** |
| **SQLite** | **SQL persistence for simulation results** |

---

## Notes

- Fully software-based — no proprietary hardware required
- All tools are free/open-source
- Parallel optimizer uses `multiprocessing.Pool` — architected for distributed-simulation workflows, scalable to multi-node deployment without code restructuring
- SQLite database supports full SQL analytics on 4500+ simulation records
- Workflow: magnetic materials → FEA → powertrain → thermal → parallel optimization → SQL persistence → dashboard
