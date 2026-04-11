import pandas as pd
from pathlib import Path
import glob
import json

# Project root
project_root = Path(__file__).resolve().parent.parent

# Directories
mesh_dir = project_root / "results/csv"            # FreeFEM output
fea_results_dir = project_root / "python/results/csv"  # Python FEA input
fea_results_dir.mkdir(parents=True, exist_ok=True)

data_dir = project_root / "python/data"
data_dir.mkdir(parents=True, exist_ok=True)

# Material CSV files
soft_file = data_dir / "soft_magnetic_materials.csv"
hard_file = data_dir / "hard_magnetic_materials.csv"

# Create dummy CSVs if missing
if not soft_file.exists():
    pd.DataFrame({"Name": ["SoftIron"], "CoreLoss": [1.0], "FluxDensity": [1.0], "MagField": [50]}).to_csv(soft_file, index=False)
if not hard_file.exists():
    pd.DataFrame({"Name": ["HardAlloy"], "CoreLoss": [2.0], "FluxDensity": [1.5], "MagField": [100]}).to_csv(hard_file, index=False)

# Load material data
soft = pd.read_csv(soft_file)
hard = pd.read_csv(hard_file)

# Convert FreeFEM CSV meshes to FEA-ready format
csv_mesh_files = glob.glob(str(mesh_dir / "*_mesh.csv"))
mesh_files_for_octave = {}

if not csv_mesh_files:
    print("⚠️ No mesh CSV files found in results/csv/ — skipping mesh conversion.")
else:
    for csv_file in csv_mesh_files:
        mesh_name = Path(csv_file).stem
        df = pd.read_csv(csv_file, header=None, names=["x", "y", "Bz"])
        fea_csv = fea_results_dir / f"{mesh_name}.csv"
        df.to_csv(fea_csv, index=False)
        mesh_files_for_octave[mesh_name] = str(fea_csv)
        print(f"✅ Converted FreeFEM CSV → FEA CSV: {fea_csv}")

# Combine soft and hard material data for FEA input
combined = pd.concat([soft, hard])
fea_input_file = fea_results_dir / "fea_input.csv"
combined.to_csv(fea_input_file, index=False)
print(f"✅ FEA input prepared: {fea_input_file}")

# Save mesh mapping for Octave to use
mesh_map_file = fea_results_dir / "mesh_map.json"
with open(mesh_map_file, "w") as f:
    json.dump(mesh_files_for_octave, f)
print(f"✅ Mesh map saved for Octave: {mesh_map_file}")
