import csv
from functools import cache
from pathlib import Path

LOCALITIES = Path(__file__).resolve().parent.parent / "data" / "cbs_localities.csv"


@cache
def _names() -> dict[int, str]:
    with LOCALITIES.open(encoding="utf-8") as file:
        rows = csv.DictReader(line for line in file if not line.startswith("#"))
        return {int(row["code"]): row["name"] for row in rows}


def city_name(value: str) -> str:
    """Store files give either a CBS locality code (Rami Levy: 3000) or a name (Shufersal). 0 means unknown."""
    value = " ".join(value.split())
    if not value.isdigit():
        return value
    code = int(value)
    if code == 0:
        return ""
    return _names().get(code, value)
