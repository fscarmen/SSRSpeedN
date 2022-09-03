import json


def import_result(filename: str) -> list:
    with open(filename, "r", encoding="utf-8") as f:
        fi = json.loads(f.read())
    return fi
