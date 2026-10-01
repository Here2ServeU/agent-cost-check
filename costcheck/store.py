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


def folder() -> Path:
    """Where everything lives. Set COSTCHECK_DIR to put it somewhere else."""
    return Path(os.environ.get("COSTCHECK_DIR", ".costcheck"))


def _ledger() -> Path:
    return folder() / "runs.jsonl"


def append(record: dict[str, Any]) -> None:
    folder().mkdir(parents=True, exist_ok=True)
    with _ledger().open("a") as f:
        f.write(json.dumps({"ts": time.time(), **record}) + "\n")


def read_all() -> list[dict[str, Any]]:
    if not _ledger().exists():
        return []
    out = []
    for line in _ledger().read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass          # a half-written line is not a reason to lose the rest
    return out


def reset() -> int:
    n = len(read_all())
    _ledger().unlink(missing_ok=True)
    return n


def save_readiness(score: int, gaps: list[str]) -> None:
    folder().mkdir(parents=True, exist_ok=True)
    (folder() / "readiness.json").write_text(json.dumps({"score": score, "gaps": gaps}))


def load_readiness() -> tuple[int, list[str]] | None:
    f = folder() / "readiness.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    return d["score"], d["gaps"]
