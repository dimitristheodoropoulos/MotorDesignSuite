#!/usr/bin/env python3
"""
Convert Phase 2 HTML report to PDF using pdfkit.
Ensures all plots, CSVs, and JSONs appear in the PDF.
"""

import pdfkit
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # PowertrainSimSuite/
REPORTS_DIR = PROJECT_ROOT / "python" / "results" / "reports"
HTML_REPORT = REPORTS_DIR / "Phase2_Report.html"
PDF_REPORT = REPORTS_DIR / "Phase2_Report.pdf"

# -----------------------------
# PDFKit options
# -----------------------------
options = {
    "enable-local-file-access": "",  # Allows wkhtmltopdf to access local images
    "page-size": "A4",
    "margin-top": "15mm",
    "margin-bottom": "15mm",
    "margin-left": "15mm",
    "margin-right": "15mm",
    "encoding": "UTF-8",
    "no-outline": None,
    "zoom": "1.0",  # Ensures images scale correctly
}

# -----------------------------
# Convert HTML to PDF
# -----------------------------
if not HTML_REPORT.exists():
    print(f"❌ HTML report not found: {HTML_REPORT}")
else:
    try:
        pdfkit.from_file(str(HTML_REPORT), str(PDF_REPORT), options=options)
        print(f"✅ PDF report generated: {PDF_REPORT}")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
