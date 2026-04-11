import pandas as pd
import glob

print("=== Integration Report ===")

csv_files = glob.glob("results/csv/*.csv")
for f in csv_files:
    print(f"\n--- {f} ---")
    try:
        df = pd.read_csv(f)
        print(df.head())
    except Exception as e:
        print(f"Could not parse {f}: {e}")
