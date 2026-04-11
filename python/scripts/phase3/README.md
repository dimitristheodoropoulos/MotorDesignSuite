# Phase 3 – Powertrain Engineering & Thermal Design

## Overview

Phase 3 extends MotorDesignSuite with three specialized engineering workflows:

### 1. Powertrain Modeling Engineer
- Octave/MATLAB functions for powertrain modeling
- Multi-physics integration (electromagnetic + thermal + mechanical)
- Multi-criteria optimization (efficiency, torque, thermal)
- Large-scale data processing & visualization from Phase 2 outputs

### 2. Electrical Engineer – Motor Powertrain
- Motor and drive unit simulation
- Multi-criteria optimization (efficiency, cost, torque, heat)
- Drive unit simulation tools
- Advanced FEA processing and visualization

### 3. Thermal Design Engineer – Optimus Actuators *(new)*
- Lumped Parameter Thermal Network (LPTN) for motor actuators
- Transient thermal simulation (scipy Radau solver)
- Steady-state temperature per node (Winding, Stator, Rotor, Housing, Coolant)
- Validation against FEA reference data

---

## Inputs

Phase 3 uses Phase 2 outputs from:
- `python/scripts/phase3/common_inputs/csv/`
- `python/scripts/phase3/common_inputs/plots/`
- `python/scripts/phase3/common_inputs/reports/`

Key files: `fea_results.csv`, `soft_summary.csv`, `hard_summary.csv`

---

## Outputs

| Module | Results folder |
|--------|---------------|
| Powertrain Modeling | `python/scripts/phase3/powertrain_modeling/results/` |
| Motor Powertrain | `python/scripts/phase3/motor_powertrain/results/` |
| Optimus Thermal | `python/scripts/phase3/optimus_thermal/results/` |

---

## Tools

- Python (NumPy, Pandas, Matplotlib, SciPy)
- Octave / MATLAB
- FreeFEM++
- Ngspice

---

## How to Run

```bash
source venv/bin/activate

# Full Phase 3
bash run_all.sh

# Thermal module only
python3 python/scripts/phase3/optimus_thermal/python/lptn_model.py
octave --silent python/scripts/phase3/optimus_thermal/octave/thermal_network.m
