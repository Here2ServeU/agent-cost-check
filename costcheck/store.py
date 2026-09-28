"""The ledger: one appended line per run, in .costcheck/runs.jsonl.

Deliberately boring, deliberately local. Nothing leaves your machine.
Add .costcheck/ to your .gitignore, or do not; it is your data.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

DIR = Path(os.environ.get("COSTCHECK_DIR", ".costcheck"))
LEDGER = DIR / "runs.jsonl"


def append(record: dict[str, Any]) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps({"ts": time.time(), **record}) + "\n")


def read_all() -> list[dict[str, Any]]:
    if not LEDGER.exists():
        return []
    out = []
    for line in LEDGER.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass          # a half-written line is not a reason to lose the rest
    return out


def reset() -> int:
    n = len(read_all())
    if LEDGER.exists():
        LEDGER.unlink()
    return n
