"""costcheck; three lines to find out what your agent actually costs.

    import costcheck

    with costcheck.run(task="invoice-4471") as r:
        resp = client.messages.create(...)
        r.record(resp)              # reads the usage block for you
        r.succeeded()               # your definition, not ours

Then:

    python3 -m costcheck report

It writes one appended line per run to .costcheck/runs.jsonl and nothing
else. No server, no dependencies, no network. Delete the folder and it is
as if you never ran it.

Part of The Agent Cost Problem: github.com/Here2ServeU/agent-cost-control
"""
from __future__ import annotations

import os
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

from .prices import cost_usd
from .store import append
from .usage import extract

__version__ = "1.0.0"
__all__ = ["run", "Run", "__version__"]

DEFAULT_MODEL = os.environ.get("COSTCHECK_MODEL", "claude-sonnet")


class Run:
    """One unit of work you would describe to a person as 'a task'.

    Not one model call; one task. A run that takes twelve model calls is
    still one run, because what you actually want to know is what a
    finished piece of work costs, not what a step costs.
    """

    def __init__(self, task: str, model: str, agent: str, team: str) -> None:
        self.id = uuid.uuid4().hex[:8]
        self.task, self.model, self.agent, self.team = task, model, agent, team
        self.steps = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost_usd = 0.0
        self.priced_exactly = True
        self.result: str | None = None      # set by succeeded()/failed()
        self.reason = ""
        self.started = time.time()

    # --- the one call you make per model response ---------------------
    def record(self, response: Any = None, *, input_tokens: int | None = None,
               output_tokens: int | None = None, model: str | None = None) -> "Run":
        """Record one model call. Pass the response, or the two numbers."""
        if input_tokens is None or output_tokens is None:
            input_tokens, output_tokens = extract(response)
        m = model or self.model
        usd, exact = cost_usd(m, input_tokens, output_tokens)
        self.steps += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cost_usd += usd
        self.priced_exactly = self.priced_exactly and exact
        return self

    # --- how it ended -------------------------------------------------
    def succeeded(self, reason: str = "") -> "Run":
        """Call this ONLY when the task actually produced what it was for.

        Not 'it did not crash'. Not 'something came out'. The number this
        tool prints is only as honest as this one call.
        """
        self.result, self.reason = "success", reason
        return self

    def failed(self, reason: str = "") -> "Run":
        self.result, self.reason = "failure", reason
        return self


@contextmanager
def run(task: str = "task", *, model: str | None = None,
        agent: str = "agent", team: str = "default") -> Iterator[Run]:
    """Wrap one task. On exit the run is written to the ledger.

    A run that raises is recorded as a failure, which is the point: the
    money it spent before raising still counts, and it counts on the top
    of the fraction, not the bottom.
    """
    r = Run(task, model or DEFAULT_MODEL, agent, team)
    try:
        yield r
    except BaseException as e:                      # noqa: BLE001
        r.result = "failure"
        r.reason = r.reason or f"{type(e).__name__}: {e}"
        raise
    finally:
        # Never having called succeeded() is a failure. That default is
        # deliberate: if you are not sure it worked, it did not.
        if r.result is None:
            r.result, r.reason = "failure", r.reason or "succeeded() was never called"
        append({
            "run_id": r.id, "task": r.task, "agent": r.agent, "team": r.team,
            "model": r.model, "priced_exactly": r.priced_exactly,
            "result": r.result, "reason": r.reason, "steps": r.steps,
            "input_tokens": r.input_tokens, "output_tokens": r.output_tokens,
            "cost_usd": round(r.cost_usd, 8),
            "duration_s": round(time.time() - r.started, 3),
        })
