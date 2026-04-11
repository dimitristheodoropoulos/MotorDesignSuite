# test_python.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
common_csv   = PROJECT_ROOT / "python/scripts/phase3/common_inputs/csv"
results_csv  = PROJECT_ROOT / "results/csv"

def test_fea_input_exists():
    fea_input = common_csv / "fea_input.csv"
    assert fea_input.exists(), f"FEA input file missing: {fea_input}"
    print("✅ fea_input.csv found")

def test_mesh_files_exist():
    for name in ("soft_mesh.csv", "hard_mesh.csv"):
        f = common_csv / name
        assert f.exists(), f"{name} missing at {f}"
    print("✅ soft_mesh.csv and hard_mesh.csv found")

def test_fea_results_exist():
    f = common_csv / "fea_results.csv"
    assert f.exists(), f"fea_results.csv missing: {f}"
    print("✅ fea_results.csv found")

def test_efficiency_map_exists():
    f = results_csv / "efficiency_map.csv"
    assert f.exists(), f"efficiency_map.csv missing: {f}"
    import pandas as pd
    df = pd.read_csv(f)
    assert len(df) > 0, "efficiency_map.csv is empty"
    print(f"✅ efficiency_map.csv found ({len(df)} rows)")

def test_lptn_results_exist():
    lptn_csv = PROJECT_ROOT / \
        "python/scripts/phase3/optimus_thermal/results/csv/lptn_steady_state.csv"
    assert lptn_csv.exists(), f"lptn_steady_state.csv missing: {lptn_csv}"
    import pandas as pd
    df = pd.read_csv(lptn_csv)
    winding = df[df["Node"]=="Winding"]["SteadyState_C"].values[0]
    assert winding > 25, f"Winding temp {winding}°C should be > ambient"
    print(f"✅ lptn_steady_state.csv found (Winding={winding:.1f}°C)")

if __name__ == "__main__":
    test_fea_input_exists()
    test_mesh_files_exist()
    test_fea_results_exist()
    test_efficiency_map_exists()
    test_lptn_results_exist()
    print("\n✅ All Python tests passed.")