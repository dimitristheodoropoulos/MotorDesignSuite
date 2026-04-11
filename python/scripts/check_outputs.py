# /home/testuser/PowertrainSimSuite/python/scripts/check_outputs.py
from pathlib import Path

# --- Project root ---
project_root = Path(__file__).resolve().parent.parent

# --- Paths στα σωστά folders ---
csv_dir     = project_root / "results/csv"
plots_dir   = project_root / "results/plots"
reports_dir = project_root / "results/reports"

# --- Αναμενόμενα αρχεία ---
expected_csvs = [
    "fea_results.csv",
    "fea_comparison.json"
]

expected_plots = [
    "fea_comparison.png",
    "core_loss_comparison.png"
]

expected_reports = [
    "Phase2_Report.html",
    "Phase2_Report.pdf"
]

# --- Συνάρτηση ελέγχου ---
def check_files(folder, expected_files):
    print(f"\nChecking {folder}:")
    for f in expected_files:
        file_path = folder / f
        if file_path.exists():
            print(f"✅ Found: {f}")

# --- Εκτέλεση ελέγχου ---
check_files(csv_dir, expected_csvs)
check_files(plots_dir, expected_plots)
check_files(reports_dir, expected_reports)

print("\n✅ Check complete!")
