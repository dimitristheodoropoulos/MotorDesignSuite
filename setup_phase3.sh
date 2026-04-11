#!/bin/bash
# setup_phase3.sh
# Δημιουργία skeleton Phase 3 δίπλα στη Phase 2 + copy Phase 2 outputs

PROJECT_ROOT="/home/testuser/PowertrainSimSuite"
PHASE2_DIR="$PROJECT_ROOT/python/scripts/phase2"
PHASE2_RESULTS="$PROJECT_ROOT/python/results"
PHASE2_GLOBAL_RESULTS="$PROJECT_ROOT/results"
PHASE3_DIR="$PROJECT_ROOT/python/scripts/phase3"

echo "=== Δημιουργία Phase 3 skeleton στο $PHASE3_DIR ==="

# Δημιουργία φακέλων Phase 3
mkdir -p $PHASE3_DIR/powertrain_modeling/{octave,python,freefem,ngspice,results,docs}
mkdir -p $PHASE3_DIR/motor_powertrain/{octave,python,freefem,ngspice,results,docs}
mkdir -p $PHASE3_DIR/common_inputs/{csv,plots,reports}

# Placeholders για Powertrain Modeling Engineer
touch $PHASE3_DIR/powertrain_modeling/octave/powertrain_modeling.m
touch $PHASE3_DIR/powertrain_modeling/python/powertrain_modeling.py
touch $PHASE3_DIR/powertrain_modeling/freefem/modeling.edp
touch $PHASE3_DIR/powertrain_modeling/ngspice/modeling.cir
touch $PHASE3_DIR/powertrain_modeling/results/.gitkeep
touch $PHASE3_DIR/powertrain_modeling/docs/README.md

# Placeholders για Electrical Engineer – Motor Powertrain
touch $PHASE3_DIR/motor_powertrain/octave/motor_powertrain.m
touch $PHASE3_DIR/motor_powertrain/python/motor_powertrain.py
touch $PHASE3_DIR/motor_powertrain/freefem/motor_model.edp
touch $PHASE3_DIR/motor_powertrain/ngspice/motor_drive.cir
touch $PHASE3_DIR/motor_powertrain/results/.gitkeep
touch $PHASE3_DIR/motor_powertrain/docs/README.md

# Κοινό README για Phase 3
cat > $PHASE3_DIR/README.md <<EOF
# Phase 3 – Powertrain Engineering

Η Phase 3 περιλαμβάνει δύο ρόλους:

1. **Powertrain Modeling Engineer**
   - MATLAB/Octave functions για powertrain modeling
   - Multi-physics integration (EM + thermal + mechanical)
   - Multi-criteria optimization
   - Big Data processing & visualization από Phase 2 outputs

2. **Electrical Engineer – Motor Powertrain**
   - MATLAB/Octave functions για motor & powertrain performance
   - Multi-criteria optimization (efficiency, cost, torque, heat)
   - Drive unit simulation tools
   - Advanced FEA processing (FreeFEM, Octave, Python)
   - Big Data visualization & επιλογή βέλτιστων σχεδίων

## Inputs
- Phase 2 outputs (CSV, JSON, plots, reports) από:
  - $PHASE2_DIR
  - $PHASE2_RESULTS
  - $PHASE2_GLOBAL_RESULTS

## Tools
- Octave / MATLAB
- FreeFEM++
- Ngspice
- Python (NumPy, Pandas, Matplotlib)

EOF

# Copy Phase 2 outputs σε common_inputs
echo "=== Αντιγραφή Phase 2 outputs σε Phase 3 common_inputs ==="
cp -u $PHASE2_RESULTS/csv/* $PHASE3_DIR/common_inputs/csv/ 2>/dev/null
cp -u $PHASE2_RESULTS/plots/* $PHASE3_DIR/common_inputs/plots/ 2>/dev/null
cp -u $PHASE2_RESULTS/reports/* $PHASE3_DIR/common_inputs/reports/ 2>/dev/null

cp -u $PHASE2_GLOBAL_RESULTS/csv/* $PHASE3_DIR/common_inputs/csv/ 2>/dev/null
cp -u $PHASE2_GLOBAL_RESULTS/plots/* $PHASE3_DIR/common_inputs/plots/ 2>/dev/null
cp -u $PHASE2_GLOBAL_RESULTS/reports/* $PHASE3_DIR/common_inputs/reports/ 2>/dev/null

echo "=== Ολοκληρώθηκε η δημιουργία Phase 3 skeleton με Phase 2 inputs ==="
tree -L 3 $PHASE3_DIR
