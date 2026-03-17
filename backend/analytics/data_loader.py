from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from models.issue import Issue

_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "issues.json"


@lru_cache(maxsize=1)
def load_issues() -> list[Issue]:
    with _DATA_PATH.open(encoding="utf-8-sig") as f:
        raw: list[dict] = json.load(f)
    return [Issue(**item) for item in raw]
