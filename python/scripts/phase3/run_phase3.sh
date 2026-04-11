#!/bin/bash
set -e

echo "=== PowertrainSimSuite Phase 3 FULL Workflow (Container) ==="

# 1️⃣ CSV → .mesh conversion
echo "[1/3] Converting CSV → .mesh..."
python3 /app/python/scripts/phase3/csv_to_mesh.py

# Validate meshes
for mesh in /app/data/soft_mesh.mesh /app/data/hard_mesh.mesh; do
    if [ ! -s "$mesh" ]; then
        echo "⚠ Mesh $mesh missing. Creating minimal fallback..."
        echo "3,1,0" > "$mesh"
    fi
done
echo "✅ Mesh files validated"

# 2️⃣ FreeFEM simulations
echo "[2/3] Running FreeFEM simulations..."

declare -A mesh_map
mesh_map["powertrain_modeling"]="soft_mesh.mesh"
mesh_map["motor_powertrain"]="soft_mesh.mesh"

for folder in /app/python/scripts/phase3/powertrain_modeling/freefem \
              /app/python/scripts/phase3/motor_powertrain/freefem; do
    if [ -d "$folder" ]; then
        role=$(basename $(dirname "$folder"))
        mesh_file="/app/data/${mesh_map[$role]}"
        for edp in "$folder"/*.edp; do
            if [ -f "$edp" ]; then
                echo "▶ Running FreeFEM: $edp"
                # Replace placeholder with actual mesh path
                tmp_edp=$(mktemp)
                sed "s|__MESH_FILE__|$mesh_file|g" "$edp" > "$tmp_edp"
                FreeFem++ "$tmp_edp"
                rm "$tmp_edp"
                echo "✅ FreeFEM finished: $edp"
            fi
        done
    fi
done

# 3️⃣ Octave postprocessing
echo "[3/3] Running Octave postprocessing..."
shopt -s globstar nullglob
for mfile in /app/octave/scripts/**/*.m; do
    echo "▶ Running Octave: $mfile"
    octave --no-gui --quiet "$mfile"
    echo "✅ Octave finished: $mfile"
done
shopt -u globstar nullglob

echo "=== Phase 3 FULL Workflow Completed ==="
