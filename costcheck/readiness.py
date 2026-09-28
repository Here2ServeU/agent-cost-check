"""Six yes/no questions. No trick ones.

We could guess some of these from your ledger and we deliberately do not.
A readiness score you answered yourself is one you believe; a score a tool
inferred is one you argue with.
"""
from __future__ import annotations

QUESTIONS = [
    ("cap",
     "If one run went wrong tonight, is there a hard dollar cap that stops it?",
     "A per-run and per-day cap, with the behaviour at the edge chosen on purpose.",
     "Module 3"),
    ("loop",
     "Would anything notice an agent repeating the same step forever?",
     "Loop detection catches it in a few steps; the cap catches it after the whole budget.",
     "Module 4"),
    ("ceiling",
     "Is there a maximum number of steps a single run may take?",
     "The ceiling underneath everything else; whatever detection misses, this catches.",
     "Module 4"),
    ("checkpoint",
     "If you killed a run halfway, would the finished work survive?",
     "Without checkpoints, every stop you build costs you a full restart.",
     "Module 4"),
    ("success",
     "Is 'success' written down somewhere, the same way every time you report it?",
     "A number without its definition is not a measurement; it is a rumour.",
     "Module 5"),
    ("alert",
     "Would you find out about a spending spike while it was still happening?",
     "An alert on the rate, not the total; the total tells you after it is over.",
     "Module 6"),
]


def ask(stream_in=None) -> tuple[int, list[str]]:
    """Interactive. Returns (score out of 6, list of gap keys)."""
    import sys
    rd = stream_in or sys.stdin
    print("\n  SIX QUESTIONS. Answer honestly; nobody is watching.\n")
    score, gaps = 0, []
    for i, (key, q, why, where) in enumerate(QUESTIONS, 1):
        print(f"  {i}. {q}")
        ans = ""
        while ans not in ("y", "n"):
            print("     [y/n] ", end="", flush=True)
            ans = (rd.readline() or "n").strip().lower()[:1] or "n"
        if ans == "y":
            score += 1
            print("     \033[92m✓\033[0m\n")
        else:
            gaps.append(key)
            print(f"     \033[93m✗\033[0m  \033[2m{why}  ({where})\033[0m\n")
    return score, gaps


def render(score: int, gaps: list[str]) -> str:
    bar = "■" * score + "□" * (6 - score)
    verdict = {
        6: "Safe to leave running. Rare, and worth saying out loud.",
        5: "One gap. Close it and you are genuinely done.",
        4: "Two gaps. An afternoon of work stands between you and boring.",
        3: "Half. The half you have will not save you without the half you do not.",
        2: "You can see some of it. You cannot stop any of it.",
        1: "One mechanism. It is better than none, and it is not protection.",
        0: "Nothing is watching. Your overnight number above is not hypothetical.",
    }[score]
    by_key = {k: (q, why, where) for k, q, why, where in QUESTIONS}
    L = ["", f"  READINESS  {score} of 6   {bar}", f"  {verdict}", ""]
    if gaps:
        L.append("  What is missing, and where it is covered:")
        for g in gaps:
            q, why, where = by_key[g]
            L.append(f"    · {q}")
            L.append(f"      \033[2m{why}  ({where})\033[0m")
    L.append("")
    return "\n".join(L)
