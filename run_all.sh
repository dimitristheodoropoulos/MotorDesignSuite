#!/bin/bash
set -euo pipefail

echo "=== MotorDesignSuite – Full Workflow ==="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/results/logs"
REPORT_DIR="$PROJECT_ROOT/results/reports"

mkdir -p "$PROJECT_ROOT/results/csv" \
         "$PROJECT_ROOT/results/plots" \
         "$REPORT_DIR" \
         "$PROJECT_ROOT/results/optimus_thermal/csv" \
         "$PROJECT_ROOT/results/optimus_thermal/plots" \
         "$LOG_DIR"

trap 'echo "❌ Σφάλμα στο βήμα: $STEP"' ERR

PYTHON="$PROJECT_ROOT/venv/bin/python3"
[[ -f "$PYTHON" ]] || PYTHON=python3

# ─────────────────────────────────────────────
# 1️⃣ FreeFEM
# ─────────────────────────────────────────────
STEP="FreeFEM simulations"
echo "[1/9] $STEP..."
if command -v FreeFem++ &>/dev/null; then
    for f in "$PROJECT_ROOT/freefem/models/"*.edp; do
        [[ -f "$f" ]] || continue
        FreeFem++-nw "$f" -nw \
            > "$LOG_DIR/freefem_$(basename "$f").log" 2>&1 || true
    done
fi

# ─────────────────────────────────────────────
# 2️⃣ Python preprocessing
# ─────────────────────────────────────────────
STEP="Python preprocessing"
echo "[2/9] $STEP..."
cd "$PROJECT_ROOT/python/scripts"
for script in fea_preprocess.py data_processing.py materials.py; do
    [[ -f "$script" ]] || continue
    $PYTHON "$script" > "$LOG_DIR/python_${script%.py}.log" 2>&1 || true
done

# ─────────────────────────────────────────────
# 3️⃣ Octave
# ─────────────────────────────────────────────
STEP="Octave simulations"
echo "[3/9] $STEP..."
cd "$PROJECT_ROOT"
if command -v octave &>/dev/null; then
octave --silent --eval "
graphics_toolkit('gnuplot');
set(0,'DefaultFigureVisible','off');
scripts = {
  'octave/scripts/core_analysis.m',
  'octave/scripts/motor_simulation.m',
  'octave/scripts/visualization.m',
  'octave/scripts/thermal_map.m',
  'octave/scripts/vehicle_dynamics.m'
};
for i = 1:length(scripts)
  if exist(scripts{i}, 'file'), run(scripts{i}); end
end
" > "$LOG_DIR/octave_core.log" 2>&1 || true
fi

# ─────────────────────────────────────────────
# 4️⃣ Powertrain Modeling
# ─────────────────────────────────────────────
STEP="Powertrain Modeling"
echo "[4/9] $STEP..."
PT="$PROJECT_ROOT/python/scripts/phase3/powertrain_modeling/python/powertrain_modeling.py"
[[ -f "$PT" ]] && $PYTHON "$PT" > "$LOG_DIR/phase3_powertrain_modeling.log" 2>&1 || true

# ─────────────────────────────────────────────
# 5️⃣ Motor Powertrain + Efficiency Map + Torque-Speed + Loss Breakdown
# ─────────────────────────────────────────────
STEP="Motor Powertrain"
echo "[5/9] $STEP..."
MP_DIR="$PROJECT_ROOT/python/scripts/phase3/motor_powertrain/python"

for script in motor_powertrain.py efficiency_map.py torque_speed.py loss_breakdown.py; do
    f="$MP_DIR/$script"
    if [[ -f "$f" ]]; then
        $PYTHON "$f" > "$LOG_DIR/phase3_${script%.py}.log" 2>&1 && \
            echo "  ✅ $script" || \
            echo "  ⚠️  $script failed"
    fi
done

# ─────────────────────────────────────────────
# 6️⃣ Thermal LPTN + Cooling Comparison
# ─────────────────────────────────────────────
STEP="Thermal LPTN"
echo "[6/9] $STEP..."
OT_DIR="$PROJECT_ROOT/python/scripts/phase3/optimus_thermal/python"

for script in lptn_model.py cooling_comparison.py; do
    f="$OT_DIR/$script"
    if [[ -f "$f" ]]; then
        $PYTHON "$f" > "$LOG_DIR/phase3_${script%.py}.log" 2>&1 && \
            echo "  ✅ $script" || \
            echo "  ⚠️  $script failed"
    fi
done

# ─────────────────────────────────────────────
# 7️⃣ Ngspice
# ─────────────────────────────────────────────
STEP="Ngspice"
echo "[7/9] $STEP..."
if command -v ngspice &>/dev/null; then
    bash "$PROJECT_ROOT/ngspice/scripts/run_ngspice.sh" \
        > "$LOG_DIR/ngspice.log" 2>&1 || true
fi

# ─────────────────────────────────────────────
# 8️⃣ Optimizer (Pareto)
# ─────────────────────────────────────────────
STEP="Pareto Optimizer"
echo "[8/9] $STEP..."
OPT="$PROJECT_ROOT/optimizer.py"
if [[ -f "$OPT" ]]; then
    $PYTHON "$OPT" > "$LOG_DIR/optimizer.log" 2>&1 && \
        echo "  ✅ optimizer.py" || \
        echo "  ⚠️  optimizer.py failed"
fi

# ─────────────────────────────────────────────
# 9️⃣ Report Generation
# ─────────────────────────────────────────────
STEP="Report Generation"
echo "[9/9] $STEP..."
RPT="$PROJECT_ROOT/generate_report.py"
if [[ -f "$RPT" ]]; then
    cd "$PROJECT_ROOT"
    $PYTHON "$RPT" > "$LOG_DIR/report.log" 2>&1 && \
        echo "  ✅ generate_report.py" || \
        echo "  ⚠️  generate_report.py failed"
fi

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
echo ""
echo "========================================"
echo "✅ FULL WORKFLOW COMPLETE"
echo "========================================"
echo "Reports : $PROJECT_ROOT/results/reports/"
echo "Plots   : $PROJECT_ROOT/results/plots/"
echo "Logs    : $LOG_DIR"
echo ""
echo "Generated files:"
find "$PROJECT_ROOT/results" \
     "$PROJECT_ROOT/python/scripts/phase3" \
     -name "*.png" -o -name "*.csv" 2>/dev/null | \
    grep -v "__pycache__" | \
    sed "s|$PROJECT_ROOT/||" | sort