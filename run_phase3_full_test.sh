#!/bin/bash
set -e

echo "=== Running Phase 3 Full Workflow ==="

# 1. Octave simulations
octave --no-gui --eval "core_analysis; motor_simulation; vehicle_dynamics; optimization_scenarios; thermal_map; multi_body"

# 2. Python plotting
python3 python/scripts/plot_scenarios.py

# 3. Collect results
echo "=== Results stored in results/csv and results/plots ==="
