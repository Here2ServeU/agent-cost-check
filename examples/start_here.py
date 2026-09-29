"""START HERE. The smallest real use of costcheck, with every line explained.

Run it from the main project folder (the one with README.md in it):

    python3 examples/start_here.py
    python3 -m costcheck report

You do not need an AI account or an API key. Instead of calling a real
model, we type in the token counts ourselves, which is exactly what a real
model would have reported.
"""
from __future__ import annotations

# This lets Python find the costcheck folder when you run this file directly.
# You will not need it in your own project once costcheck sits next to your code.
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import costcheck

# --- Task 1: one that works -------------------------------------------------
# "with costcheck.run(...)" starts a stopwatch and a running bill for ONE task.
# When the indented block ends, the result is saved to .costcheck/runs.jsonl.
with costcheck.run(task="summarise-report", model="claude-sonnet") as r:

    # Pretend the agent called the model 3 times. Each call reports two numbers:
    #   input_tokens  = how much text we SENT to the model
    #   output_tokens = how much text the model WROTE back
    for step in range(3):
        r.record(input_tokens=1500, output_tokens=400)

    # We decide the task worked, so we say so.
    r.succeeded("summary was written")

print(f"Task 1 cost ${r.cost_usd:.4f} and succeeded")

# --- Task 2: one that fails -------------------------------------------------
# Same thing, but the agent gets stuck and repeats itself 12 times.
with costcheck.run(task="summarise-report", model="claude-sonnet") as r:
    for step in range(12):
        r.record(input_tokens=1500, output_tokens=400)

    # We say it failed. (If you forget to call either one, costcheck
    # assumes it failed. "Not sure it worked" counts as "did not work".)
    r.failed("got stuck repeating itself")

print(f"Task 2 cost ${r.cost_usd:.4f} and failed, but you still paid for it")

print("\nNow run:  python3 -m costcheck report")
