import csv
import json
import os

def load_csv_set(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8", newline='') as f:
                reader = csv.reader(f)
                return set(row[0] for row in reader if row)
        except Exception:
            return set()
    return set()

def save_csv_set(data_set, path):
    with open(path, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        for item in data_set:
            writer.writerow([item])

def load_json_set(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            return set()
    return set()

def save_json_set(data_set, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(list(data_set), f)
