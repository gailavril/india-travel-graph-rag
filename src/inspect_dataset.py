import json
from pathlib import Path


DATASET_PATH = Path("data/indian_tourism.json")


def inspect_json(data, level=0, max_level=3):
    indent = "  " * level

    print(f"{indent}Type: {type(data).__name__}")

    if level >= max_level:
        return

    if isinstance(data, dict):
        print(f"{indent}Keys:")

        for key, value in data.items():
            print(f"{indent}  - {key}")

            if level < max_level:
                print(f"{indent}    Value type: {type(value).__name__}")

                if isinstance(value, (dict, list)):
                    inspect_json(value, level + 1, max_level)

    elif isinstance(data, list):
        print(f"{indent}Number of items: {len(data)}")

        if len(data) > 0:
            print(f"{indent}First item:")
            inspect_json(data[0], level + 1, max_level)

    else:
        print(f"{indent}Value: {data}")


def main():

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("\n========== DATASET STRUCTURE ==========\n")

    inspect_json(data)

    print("\n========== FIRST RECORD ==========\n")

    if isinstance(data, list) and data:
        print(json.dumps(data[0], indent=4, ensure_ascii=False))

    elif isinstance(data, dict):
        print(json.dumps(data, indent=4, ensure_ascii=False)[:5000])


if __name__ == "__main__":
    main()