"""python3 -m costcheck <report|card|check|demo|reset>"""
from __future__ import annotations

import json
import random
import sys
import time

from . import run
from .readiness import ask, render as render_readiness
from .report import render_card, render_report, summarize
from .store import DIR, reset

HELP = """
  costcheck; what your agent actually costs

    python3 -m costcheck demo      see it work on fake data, in 30 seconds
    python3 -m costcheck report    your numbers
    python3 -m costcheck check     six questions, a readiness score
    python3 -m costcheck card      a card you can paste somewhere
    python3 -m costcheck reset     forget everything and start again

  To measure your own agent, three lines:

    import costcheck
    with costcheck.run(task="whatever-this-is") as r:
        resp = client.messages.create(...)
        r.record(resp)
        r.succeeded()

  Everything stays in ./.costcheck/. Nothing is sent anywhere.
"""


def demo() -> None:
    """Twelve runs of a plausible agent, so you can see the output before wiring anything up."""
    print("\n  Running twelve fake tasks; eight that work, four that do not.\n")
    rng = random.Random(11)
    for i in range(12):
        loops = i in (3, 6, 9, 11)
        with run(task=f"demo-{i}", model="claude-sonnet", agent="demo") as r:
            for _ in range(rng.randint(22, 34) if loops else rng.randint(4, 7)):
                r.record(input_tokens=rng.randint(1200, 1900), output_tokens=rng.randint(280, 520))
                time.sleep(0.004)
            if loops:
                r.failed("bouncing between two steps")
            else:
                r.succeeded("produced the required field")
        print(f"  {'✗' if loops else '✓'} demo-{i:<3} {r.steps:>3} steps   ${r.cost_usd:.4f}")
    print("\n  Now run:  python3 -m costcheck report\n")


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "report").lstrip("-")

    if cmd in ("help", "h", "?"):
        print(HELP)
    elif cmd == "demo":
        demo()
    elif cmd == "report":
        print(render_report(summarize()))
    elif cmd == "card":
        s = summarize()
        score = None
        f = DIR / "readiness.json"
        if f.exists():
            d = json.loads(f.read_text())
            score = (d["score"], d["gaps"])
        print()
        print(render_card(s, score))
        print()
    elif cmd == "check":
        score, gaps = ask()
        print(render_readiness(score, gaps))
        DIR.mkdir(parents=True, exist_ok=True)
        (DIR / "readiness.json").write_text(json.dumps({"score": score, "gaps": gaps}))
        s = summarize()
        if s["runs"] and score < 6:
            print(f"  Your overnight exposure, from your own runs: \033[91m${s['overnight']:,.2f}\033[0m")
            print("  Every gap above is one afternoon of work.\n")
    elif cmd == "reset":
        n = reset()
        print(f"\n  Forgot {n} run(s).\n")
    else:
        print(HELP)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
