import csv
import os
import datetime

LOG_FILE = "traffic_log.csv"
HEADERS = ["timestamp", "direction", "vehicle_count", "density", "green_time", "event"]

def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()

def log_cycle(analyzed_data, signals):
    init_log()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        for item in analyzed_data:
            direction = item["direction"]
            writer.writerow({
                "timestamp": item["timestamp"],
                "direction": direction,
                "vehicle_count": item["vehicle_count"],
                "density": item["density"],
                "green_time": signals[direction]["green_time"],
                "event": item["event"]
            })

def compute_stats():
    init_log()
    rows = []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {"avg_waiting_time": 0, "most_congested": "N/A", "total_cycles": 0}

    direction_counts = {}
    direction_total = {}

    for row in rows:
        d = row["direction"]
        count = int(row["vehicle_count"])
        direction_counts[d] = direction_counts.get(d, 0) + 1
        direction_total[d] = direction_total.get(d, 0) + count

    most_congested = max(direction_total, key=direction_total.get)

    green_times = [int(r["green_time"]) for r in rows if r["green_time"].isdigit()]
    avg_wait = round(sum(green_times) / len(green_times), 2) if green_times else 0

    return {
        "avg_waiting_time": avg_wait,
        "most_congested": most_congested,
        "total_cycles": len(rows) // 4
    }

def get_recent_logs(limit=20):
    init_log()
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows[-limit:]