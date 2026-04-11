#!/usr/bin/env python3
"""
Phase 2: Unified Report Generator
Generates a single HTML report combining CSVs, JSONs, material reports, and all PNG plots.
"""

import json
from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # PowertrainSimSuite/
PYTHON_RESULTS = PROJECT_ROOT / "python/results"
CSV_DIR = PYTHON_RESULTS / "csv"
PLOTS_DIR = PYTHON_RESULTS / "plots"
REPORTS_DIR = PYTHON_RESULTS / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATE_FILE = "report_template.html"

# CSV data preview
csv_summaries = {}
for csv_file in sorted(CSV_DIR.glob("*.csv")):
    try:
        df = pd.read_csv(csv_file)
        csv_summaries[csv_file.name] = df.head(5).to_html(index=True, border=1) if not df.empty else "CSV file is empty"
    except Exception as e:
        csv_summaries[csv_file.name] = f"Error reading CSV: {e}"

# JSON summaries
json_summaries = {}
json_files = list(CSV_DIR.glob("*.json")) + list(PLOTS_DIR.glob("*.json"))
for json_file in sorted(json_files):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        json_summaries[json_file.name] = json.dumps(data, indent=2) if data else "⚠️ Data missing"
    except Exception as e:
        json_summaries[json_file.name] = f"Error reading JSON: {e}"

# Material reports
report_tables = {}
for report_name in ["hard_report.json", "soft_report.json"]:
    report_path = PYTHON_RESULTS / "reports" / report_name
    if report_path.exists():
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            df = pd.DataFrame([data])
            report_tables[report_name] = df.to_html(index=False, border=1)
        except Exception as e:
            report_tables[report_name] = f"Error reading {report_name}: {e}"

# Plots
plots_files = sorted(PLOTS_DIR.glob("*.png"), key=lambda p: (0 if "fea_comparison" in p.name else 1, p.name))
plots = [f"../plots/{p.name}" for p in plots_files]
fea_plot_found = any("fea_comparison" in p.name for p in plots_files)
if not fea_plot_found:
    print("⚠️ FEA comparison plot not found; section will indicate missing data.")

# Render HTML
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
template = env.get_template(TEMPLATE_FILE)

html_report = template.render(
    csv_summaries=csv_summaries,
    json_summaries=json_summaries,
    report_tables=report_tables,
    plots=plots,
    fea_comparison_missing=not fea_plot_found
)

output_file = REPORTS_DIR / "Phase2_Report.html"
with open(output_file, "w") as f:
    f.write(html_report)

print(f"[INFO] Phase 2 report generated: {output_file}")
