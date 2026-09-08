"""Deliberately competent small baseline, independent of Aftertrace."""
import json
import re
import sys


def observations(path, variable):
    data = json.load(open(path, encoding="utf-8"))
    prefix = f"Variable Assign - {variable} = "
    events = sorted((e for e in data["traceEvents"]
                     if e.get("ph") == "i" and e.get("name", "").startswith(prefix)),
                    key=lambda e: e["ts"])
    return [(e, e["name"][len(prefix):]) for e in events]


def first_negative_integer(path, variable):
    for event, text in observations(path, variable):
        if re.fullmatch(r"-?\d+", text) and int(text) < 0:
            return {"value": int(text), "timestampUs": event["ts"],
                    "pid": event["pid"], "tid": event["tid"]}
    return None


if __name__ == "__main__":
    print(json.dumps(first_negative_integer(sys.argv[1], sys.argv[2])))

