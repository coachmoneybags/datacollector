#!/usr/bin/env python3
import csv
import smtplib
from email.message import EmailMessage
from pathlib import Path

from generate_report import load_rows

CREDENTIALS_FILE = Path.home() / ".mail_credentials"
LOG_FILE = "/home/jakeman/tank_temp_log.csv"
OUT_CSV = "/home/jakeman/tank_report_hourly.csv"
RECIPIENTS = ["jake.t@uspapermill.us", "shane.t@uspapermill.us", "ren@usmedicalglove.com"]
HOURS = 1

def read_credentials():
    creds = {}
    with open(CREDENTIALS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            creds[key.strip()] = val.strip()
    return creds["SMTP_USER"], creds["SMTP_PASS"]

def write_csv(rows, out_path):
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "Nitrile tank line 3 (C)", "Coagulant tank line 3 (C)"])
        for r in rows:
            writer.writerow([r["_ts"].strftime("%Y-%m-%d %H:%M:%S"), r.get("tank_probe_1_C", ""), r.get("tank_probe_2_C", "")])

def main():
    rows = load_rows(HOURS, LOG_FILE)
    write_csv(rows, OUT_CSV)

    smtp_user, smtp_pass = read_credentials()

    msg = EmailMessage()
    msg["Subject"] = "Tank Temp Report - hourly"
    msg["From"] = smtp_user
    msg["To"] = ", ".join(RECIPIENTS)

    latest = rows[-1] if rows else None
    if latest:
        body = (
            "Latest reading: " + latest["_ts"].strftime("%Y-%m-%d %H:%M:%S") + "\n"
            "Nitrile tank line 3 (C): " + str(latest.get("tank_probe_1_C", "N/A")) + "\n"
            "Coagulant tank line 3 (C): " + str(latest.get("tank_probe_2_C", "N/A")) + "\n\n"
            "CSV of the last " + str(HOURS) + " hour(s) attached (" + str(len(rows)) + " reading(s))."
        )
    else:
        body = "No readings found in the last " + str(HOURS) + " hour(s)."
    msg.set_content(body)

    with open(OUT_CSV, "rb") as f:
        msg.add_attachment(f.read(), maintype="text", subtype="csv", filename="tank_report_hourly.csv")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print("Email sent to", ", ".join(RECIPIENTS))

if __name__ == "__main__":
    main()
