import pandas as pd
from pathlib import Path

# Project root
project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "python/data"

# File paths
soft_file = data_dir / "soft_magnetic_materials.csv"
hard_file = data_dir / "hard_magnetic_materials.csv"

def safe_load_csv(file_path):
    if not file_path.exists():
        print(f"Warning: {file_path} not found.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            print(f"Warning: {file_path} is empty.")
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

soft = safe_load_csv(soft_file)
hard = safe_load_csv(hard_file)

# Select best material if data exists
if not soft.empty:
    best_soft = soft.loc[soft['CoreLoss'].idxmin()]
    print("Best soft magnetic material:", best_soft['Name'])
else:
    print("No soft magnetic data available for optimization.")

if not hard.empty:
    best_hard = hard.loc[hard['CoreLoss'].idxmin()]
    print("Best hard magnetic material:", best_hard['Name'])
else:
    print("No hard magnetic data available for optimization.")
