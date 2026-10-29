"""Fill template.md with the fragments in out/ and write reports/stage_e32b_ranking.md."""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE.parents[2] / "stage_e32b_ranking.md"


def main() -> None:
    text = (HERE / "template.md").read_text()
    now = subprocess.run(["date", "+%Y-%m-%d %H:%M %Z"], capture_output=True, text=True,
                         env={"TZ": "America/Vancouver"}).stdout.strip()
    text = text.replace("{{NOW}}", now)
    for name in re.findall(r"\{\{(sec\w+)\}\}", text):
        text = text.replace("{{" + name + "}}", (HERE / "out" / f"{name}.md").read_text())
    left = re.findall(r"\{\{\w+\}\}", text)
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    TARGET.write_text(text)
    print(TARGET, len(text.splitlines()), "lines")


if __name__ == "__main__":
    main()
