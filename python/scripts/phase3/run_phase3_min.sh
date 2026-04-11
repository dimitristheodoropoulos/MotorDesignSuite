#!/bin/bash
set -e

echo "=== PowertrainSimSuite Phase 3 FULL Workflow (Light Container) ==="

# 1️⃣ Python preprocessing
echo "[1/3] Running Python preprocessing..."
PY_SCRIPT="/app/python/scripts/prepare_fea.py"
if [ -f "$PY_SCRIPT" ]; then
    python3 "$PY_SCRIPT"
    echo "✅ FEA preprocessing completed: soft_mesh.csv & hard_mesh.csv created in /app/data."
else
    echo "⚠️ Python preprocessing script not found. Skipping."
fi

# 2️⃣ FreeFEM simulations
echo "[2/3] Running FreeFEM simulations..."
FF_DIR="/app/python/scripts/phase3/powertrain_modeling/freefem"
if [ -d "$FF_DIR" ]; then
    for edp in "$FF_DIR"/*.edp; do
        if [ -f "$edp" ]; then
            freefem++ "$edp"
            echo "✅ FreeFEM finished: $edp"
        fi
    done
else
    echo "⚠️ FreeFEM folder not found. Skipping."
fi

# 3️⃣ Octave postprocessing (headless)
echo "[3/3] Running Octave postprocessing (headless)..."
OCT_DIR="/app/octave/scripts"
shopt -s globstar nullglob
for mfile in "$OCT_DIR"/**/*.m; do
    if [ -f "$mfile" ]; then
        octave --no-gui --quiet "$mfile"
        echo "✅ Octave finished: $mfile"
    fi
done

echo "=== Phase 3 FULL Workflow Completed ==="
