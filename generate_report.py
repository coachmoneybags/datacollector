#!/usr/bin/env python3
import csv
import argparse
from datetime import datetime, timedelta

from fpdf import FPDF

DEFAULT_LOG_FILE = "/home/jakeman/tank_temp_log.csv"
SENSOR_LABELS = {
    "tank_probe_1_C": "Nitrile tank line 3 (C)",
    "tank_probe_2_C": "Coagulant tank line 3 (C)",
}

def load_rows(hours, log_file):
    cutoff = datetime.now() - timedelta(hours=hours)
    rows = []
    with open(log_file, newline="") as f:
        for row in csv.DictReader(f):
            ts = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            row["_ts"] = ts
            if ts >= cutoff:
                rows.append(row)
    if not rows:
        with open(log_file, newline="") as f:
            for row in csv.DictReader(f):
                row["_ts"] = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                rows.append(row)
    return rows

def build_pdf(rows, hours, out_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Tank Temperature Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ln=True)
    pdf.cell(0, 6, "Window: last " + str(hours) + " hour(s), " + str(len(rows)) + " reading(s)", ln=True)
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 10)
    col_widths = [35, 30, 45, 50]
    headers = ["Date", "Time"] + list(SENSOR_LABELS.values())
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    for r in rows:
        date_str = r["_ts"].strftime("%Y-%m-%d")
        time_str = r["_ts"].strftime("%H:%M:%S")
        pdf.cell(col_widths[0], 7, date_str, border=1)
        pdf.cell(col_widths[1], 7, time_str, border=1)
        for w, field in zip(col_widths[2:], SENSOR_LABELS.keys()):
            val = r.get(field, "")
            if val not in (None, "", "None"):
                pdf.cell(w, 7, str(val), border=1)
            else:
                pdf.cell(w, 7, "N/A", border=1)
        pdf.ln()

    pdf.output(out_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=float, default=1)
    parser.add_argument("--out", default="/home/jakeman/tank_report.pdf")
    parser.add_argument("--log", default=DEFAULT_LOG_FILE)
    args = parser.parse_args()

    rows = load_rows(args.hours, args.log)
    build_pdf(rows, args.hours, args.out)
    print("Report written to " + args.out)

if __name__ == "__main__":
    main()
