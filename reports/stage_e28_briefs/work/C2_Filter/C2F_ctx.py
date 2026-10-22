"""C2_Filter helper: print short context windows around a regex in a saved text file.
Usage: python -I C2F_ctx.py <file> <regex> [width=120] [max_hits=5]
"""
import re
import sys


def main() -> None:
    path, pat = sys.argv[1], sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    max_hits = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    text = open(path, errors="ignore").read()
    text = re.sub(r"\s+", " ", text)
    for i, m in enumerate(re.finditer(pat, text, flags=re.I)):
        if i >= max_hits:
            break
        a, b = max(0, m.start() - width), min(len(text), m.end() + width)
        print(f"[{m.start()}] ...{text[a:b]}...")


if __name__ == "__main__":
    main()
