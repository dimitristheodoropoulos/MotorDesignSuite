#!/bin/bash
echo "=== Running Phase 3 Ngspice Simulations ==="

# Base directories
script_dir=$(dirname "$(realpath "$0")")
project_root=$(dirname "$(dirname "$script_dir")")  # up two levels
results_dir="$project_root/phase3_results/ngspice"

# Δημιουργία φακέλου για αποτελέσματα
mkdir -p "$results_dir"

# Ngspice circuits relative to phase3/scripts folder
declare -A circuits
circuits["motor_drive"]="motor_powertrain/ngspice/motor_drive.cir"
circuits["powertrain_modeling"]="powertrain_modeling/ngspice/modeling.cir"

# Loop over circuits
for name in "${!circuits[@]}"; do
    cir_path="$script_dir/${circuits[$name]}"
    if [[ ! -f "$cir_path" ]]; then
        echo "⚠️ Circuit file missing: $cir_path"
        continue
    fi

    echo "Running $name simulation..."
    log_file="$results_dir/${name}.log"

    # Run Ngspice in batch mode
    ngspice -b "$cir_path" -o "$log_file"
    if [[ $? -eq 0 ]]; then
        echo "✅ $name simulation completed. Log: $log_file"
    else
        echo "⚠️ $name simulation failed. Check $log_file"
    fi
done

echo "=== Ngspice Phase 3 Simulation Completed ✅ ==="
