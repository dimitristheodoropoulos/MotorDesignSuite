#!/bin/bash
set -e

echo "=== PowertrainSimSuite Phase 3 FAST Workflow (Octave + Python headless) ==="

# --- Ensure results directories exist ---
mkdir -p ./results/csv ./results/plots

# --- Environment variables for headless plotting ---
export SOFT_MESH_CSV="./results/csv/soft_mesh.csv"
export HARD_MESH_CSV="./results/csv/hard_mesh.csv"

# --- Run Python preprocessing ---
echo "[1/2] Running Python preprocessing..."
if [[ -f "python/scripts/prepare_fea.py" ]]; then
    python3 python/scripts/prepare_fea.py
else
    echo "⚠️ Python preprocessing script not found. Skipping."
fi

# --- Run Octave visualizations & FEA ---
echo "[2/2] Running Octave simulations headless..."
octave --silent --eval "
graphics_toolkit('qt'); 
set(0,'DefaultFigureVisible','off');
set(0,'DefaultAxesFontName','Liberation Sans');
set(0,'DefaultTextFontName','Liberation Sans');
run('octave/scripts/visualization.m');
run('octave/scripts/vehicle_dynamics.m');
"

echo "✅ Phase 3 FAST complete!"
