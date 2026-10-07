import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Check for dataset file (support both names)
DATASET_PATH = ROOT_DIR / "data" / "indian_tourism.json"
if not DATASET_PATH.exists():
    DATASET_PATH = ROOT_DIR / "data" / "india_tourism_dataset.json"


def load_json():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_records(data):
    # Case 1: dataset is already a list
    if isinstance(data, list):
        return data

    # Case 2: dataset is a dictionary
    if isinstance(data, dict):
        # If the dataset contains a list under a key, detect it automatically.
        for key, value in data.items():
            if isinstance(value, list):
                return value

    raise ValueError(
        "Could not find a list of tourism records in the JSON dataset."
    )


def clean_string(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    value = value.strip()

    if value == "":
        return None

    return value


def clean_records(records):
    cleaned = []

    for record in records:
        if not isinstance(record, dict):
            continue

        cleaned_record = {}

        for key, value in record.items():
            if isinstance(value, str):
                cleaned_record[key] = clean_string(value)
            else:
                cleaned_record[key] = value

        cleaned.append(cleaned_record)

    return cleaned


def load_clean_data():
    data = load_json()
    records = normalize_records(data)
    cleaned_records = clean_records(records)
    return cleaned_records


if __name__ == "__main__":
    records = load_clean_data()
    print(f"Number of records: {len(records)}")

    if records:
        print("\nFirst cleaned record:")
        print(records[0])
