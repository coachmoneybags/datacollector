#!/usr/bin/env python3
import csv
import os
from datetime import datetime

SENSORS = {
    "tank_probe_1": "28-00000021dcd5",
    "tank_probe_2": "28-000000220ef3",
}
LOG_FILE = "/home/jakeman/tank_temp_log.csv"

def read_temp(device_id):
    path = f"/sys/bus/w1/devices/{device_id}/w1_slave"
    with open(path, "r") as f:
        lines = f.readlines()
    if "YES" not in lines[0]:
        return None
    temp_str = lines[1].split("t=")[-1].strip()
    return round(int(temp_str) / 1000.0, 2)

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"timestamp": timestamp}
    for name, device_id in SENSORS.items():
        row[name + "_C"] = read_temp(device_id)

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

if __name__ == "__main__":
    main()
