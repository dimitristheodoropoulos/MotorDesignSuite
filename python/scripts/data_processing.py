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

# Optional: compute some additional stats for validation
if not soft.empty:
    soft_summary = {
        "count": len(soft),
        "mean_CoreLoss": soft["CoreLoss"].mean(),
        "mean_FluxDensity": soft["FluxDensity"].mean(),
        "mean_MagField": soft["MagField"].mean()
    }
    print("Soft magnetic data summary:", soft_summary)

if not hard.empty:
    hard_summary = {
        "count": len(hard),
        "mean_CoreLoss": hard["CoreLoss"].mean(),
        "mean_FluxDensity": hard["FluxDensity"].mean(),
        "mean_MagField": hard["MagField"].mean()
    }
    print("Hard magnetic data summary:", hard_summary)
