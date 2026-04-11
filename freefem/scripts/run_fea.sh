#!/bin/bash
project_root=$(dirname "$(realpath "$0")")/..
cd "$project_root" || exit 1

mkdir -p results/csv/

# Loop over all .edp FreeFEM models
for model in freefem/models/*.edp; do
    [[ -f "$model" ]] || continue
    model_name=$(basename "$model" .edp)
    echo "Running FreeFEM model: $model"

    # Run FreeFEM and export CSV directly
    FreeFem++ -nw "$model" -savecsv "results/csv/${model_name}_mesh.csv"

    # Check expected CSV output
    csv_file="results/csv/${model_name}_mesh.csv"
    if [[ -f "$csv_file" ]]; then
        echo "✅ Generated CSV: $csv_file"
    else
        echo "⚠️ CSV not found: $csv_file"
    fi
done
