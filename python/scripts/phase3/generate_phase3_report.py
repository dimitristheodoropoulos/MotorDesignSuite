from pathlib import Path
from jinja2 import Template
RESULTS_DIR = Path(__file__).parent.parent.parent.parent / "results/phase3"
plots_dir = RESULTS_DIR / "plots"
reports_dir = RESULTS_DIR / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

template_html = """
<html>
<head><title>Phase 3 Report</title></head>
<body>
<h1>Phase 3 Motor & Powertrain Analysis</h1>
<img src="{{ plot }}" width="600">
<p>All simulations completed using FreeFEM++, Octave, Ngspice & Python.</p>
</body>
</html>
"""

plot_path = plots_dir / "phase3_core_loss_comparison.png"
report_file = reports_dir / "Phase3_Report.html"

with open(report_file, "w") as f:
    f.write(Template(template_html).render(plot=plot_path.name))
