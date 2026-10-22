"""Print only all_ok and unlocks_logged per entry of `data.holdout status` JSON read from stdin."""
import json
import sys

raw = sys.stdin.read()
d = json.loads(raw)


def walk(obj, path=""):
    if isinstance(obj, dict):
        keys = {k: obj[k] for k in ("all_ok", "unlocks_logged") if k in obj}
        if keys:
            print(f"{path or '<top>'}: {json.dumps(keys)}")
        for k, v in obj.items():
            if isinstance(v, dict):
                walk(v, f"{path}.{k}" if path else k)


walk(d)
