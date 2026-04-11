# Powertrain Modeling – Phase 3

## Overview

This module implements multi-physics powertrain modeling and multi-criteria
optimization, integrating electromagnetic, thermal, and mechanical performance.
Targets the **Powertrain Modeling Engineer** role.

---

## Files

| File | Description |
|------|-------------|
| `python/powertrain_modeling.py` | Multi-physics integration, optimization, data processing |
| `octave/powertrain_modeling.m` | Octave equivalent with powertrain performance functions |
| `freefem/motor_model.edp` | FreeFEM++ coupled EM motor model |
| `freefem/modeling.edp` | FreeFEM++ powertrain mesh model |
| `ngspice/modeling.cir` | Ngspice powertrain circuit |

---

## Inputs

From `common_inputs/csv/`:
- `fea_results.csv`
- `soft_summary.csv`, `hard_summary.csv`

---

## Outputs

Saved to `results/` (relative to this folder):

| File | Description |
|------|-------------|
| `csv/powertrain_modeling_summary.csv` | Efficiency, Torque, Thermal score per candidate |
| `plots/powertrain_efficiency.png` | Efficiency comparison |
| `plots/powertrain_torque.png` | Torque comparison |

---

## Criteria Optimized

- **Efficiency** — electromagnetic performance
- **Torque [Nm]** — mechanical output
- **ThermalScore** — thermal management metric
- **MultiCriteriaScore** — composite trade-off index

---

## How to Run

```bash
source venv/bin/activate
python3 python/scripts/phase3/powertrain_modeling/python/powertrain_modeling.py
```

---

## Role Coverage

| Job Requirement | Coverage |
|----------------|----------|
| Multi-physics integration (EM+thermal+mechanical) | ✅ |
| Multi-criteria optimization | ✅ MultiCriteriaScore |
| Large-scale data processing | ✅ pandas + glob CSV loading |
| Visualization of trade-offs | ✅ efficiency & torque plots |
| Octave/MATLAB functions | ✅ powertrain_modeling.m |