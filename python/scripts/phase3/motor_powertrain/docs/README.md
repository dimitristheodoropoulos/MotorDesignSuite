# Motor Powertrain – Phase 3

## Overview

This module simulates electric motor and drive unit performance, performs
multi-criteria optimization, and visualizes optimal design candidates.
Targets the **Electrical Engineer – Motor Powertrain** role.

---

## Files

| File | Description |
|------|-------------|
| `python/motor_powertrain.py` | Motor performance metrics, multi-criteria optimization, plots |
| `octave/motor_powertrain.m` | Octave equivalent for motor simulation |
| `freefem/motor_model.edp` | FreeFEM++ FEA motor model |
| `ngspice/motor_drive.cir` | Ngspice drive unit circuit |

---

## Inputs

From `common_inputs/csv/`:
- `fea_results.csv` — FEA output per material
- `soft_summary.csv`, `hard_summary.csv`

---

## Outputs

Saved to `results/` (relative to this folder):

| File | Description |
|------|-------------|
| `csv/motor_powertrain_summary.csv` | Efficiency, Torque, Heat, MultiCriteriaScore per candidate |
| `plots/motor_efficiency.png` | Bar chart of motor efficiency |
| `plots/motor_torque.png` | Bar chart of motor torque |

---

## Criteria Optimized

- **Efficiency** — maximize
- **Torque [Nm]** — maximize
- **Heat [W]** — minimize
- **MultiCriteriaScore** = Efficiency / Heat — composite metric

---

## How to Run

```bash
source venv/bin/activate
python3 python/scripts/phase3/motor_powertrain/python/motor_powertrain.py
```

---

## Role Coverage

| Job Requirement | Coverage |
|----------------|----------|
| Motor & drive unit simulation | ✅ motor_powertrain.py + motor_drive.cir |
| Multi-criteria optimization | ✅ MultiCriteriaScore |
| Advanced FEA processing | ✅ FreeFEM motor_model.edp |
| Visualization of optimal designs | ✅ efficiency & torque plots |