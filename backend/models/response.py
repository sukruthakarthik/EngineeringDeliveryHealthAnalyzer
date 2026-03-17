from __future__ import annotations

from datetime import datetime, timezone


def make_response(data: object) -> dict:
    return {
        "data": data,
        "meta": {"generated_at": datetime.now(timezone.utc).isoformat()},
    }
