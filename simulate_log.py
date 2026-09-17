#!/usr/bin/env python3
import csv
import os
import random
from datetime import datetime, timedelta

LOG_FILE = "/home/jakeman/tank_temp_log_demo.csv"

def walk(start, low, high, step):
    values = [start]
    for _ in range(7):
        nxt = values[-1] + random.uniform(-step, step)
        nxt = max(low, min(high, nxt))
        values.append(nxt)
    return values

def main():
    now = datetime.now()
    timestamps = [now - timedelta(minutes=15 * i) for i in range(7, -1, -1)]

    coag_values = walk(23.0, 20.0, 27.0, 1.2)
    nitrile_values = walk(24.0, 21.0, 28.0, 1.2)

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "tank_probe_1_C", "tank_probe_2_C"])
        writer.writeheader()
        for ts, coag, nitrile in zip(timestamps, coag_values, nitrile_values):
            writer.writerow({
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "tank_probe_1_C": round(coag, 2),
                "tank_probe_2_C": round(nitrile, 2),
            })
    print("Wrote " + str(len(timestamps)) + " simulated readings to " + LOG_FILE)

if __name__ == "__main__":
    main()
