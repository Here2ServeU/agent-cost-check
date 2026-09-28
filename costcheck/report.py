"""The numbers, and the card you can paste somewhere."""
from __future__ import annotations

import statistics
from typing import Any

from .store import read_all

WAITLIST = "https://github.com/Here2ServeU/agent-cost-control"   # replace with your waitlist URL

G, Y, R, D, B, OFF = "\033[92m", "\033[93m", "\033[91m", "\033[2m", "\033[1m", "\033[0m"


def summarize(runs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    runs = read_all() if runs is None else runs
    if not runs:
        return {"runs": 0}

    ok = [r for r in runs if r["result"] == "success"]
    bad = [r for r in runs if r["result"] != "success"]
    total = sum(r["cost_usd"] for r in runs)
    wasted = sum(r["cost_usd"] for r in bad)
    steps = [r["steps"] for r in runs if r["steps"]]

    # Pace, measured from your own runs: seconds per model call. This is what
    # makes the overnight number yours rather than a number we made up.
    #
    # The floor matters. A real model call does not return in 40ms, so anything
    # faster than MIN_PACE is a mock, a cache or a replay; using it would produce
    # a six-figure overnight number that nobody sane would believe, and the
    # moment a reader disbelieves one number they disbelieve all of them.
    MIN_PACE = 0.25
    paced = [(r["duration_s"] / r["steps"]) for r in runs
             if r["steps"] and (r["duration_s"] / r["steps"]) >= MIN_PACE]
    sec_per_step = statistics.median(paced) if paced else 3.0
    measured_pace = bool(paced)

    # The most expensive step you have actually seen. A loop repeats steps
    # like these, so this is the right unit for the exposure number.
    per_step = [r["cost_usd"] / r["steps"] for r in runs if r["steps"]]
    worst_step = max(per_step) if per_step else 0.0
    overnight = worst_step * (3600 / sec_per_step) * 12      # one loop, twelve hours

    return {
        "runs": len(runs), "ok": len(ok), "bad": len(bad),
        "total": total, "wasted": wasted,
        "per_request": total / len(runs),
        "per_success": (total / len(ok)) if ok else None,
        "waste_share": (wasted / total) if total else 0.0,
        "median_steps": statistics.median(steps) if steps else 0,
        "max_steps": max(steps) if steps else 0,
        "sec_per_step": sec_per_step, "measured_pace": measured_pace,
        "worst_step": worst_step, "overnight": overnight,
        "approx_priced": any(not r.get("priced_exactly", True) for r in runs),
        "models": sorted({r["model"] for r in runs}),
    }


def _gap(s: dict[str, Any]) -> float | None:
    if not s.get("per_success"):
        return None
    return (s["per_success"] / s["per_request"] - 1) * 100


def render_report(s: dict[str, Any]) -> str:
    if not s["runs"]:
        return ("\n  Nothing recorded yet.\n\n"
                "  Wrap one task with costcheck.run(), run it a few times, then come back.\n"
                "  Or see it work on fake data first:  python3 -m costcheck demo\n")

    L = []
    a = L.append
    a("")
    a(f"  {B}YOUR AGENT COST CHECK{OFF}")
    a(f"  {D}{s['runs']} runs · {', '.join(s['models'])}{OFF}")
    a("  " + "─" * 62)
    a(f"  runs recorded           {s['runs']}")
    a(f"  succeeded               {s['ok']}      {D}<- the denominator{OFF}")
    a(f"  did not                 {s['bad']}      {D}<- still counts on top{OFF}")
    a(f"  total spend             ${s['total']:.4f}")
    a("  " + "─" * 62)
    a(f"  cost per request        ${s['per_request']:.4f}   {D}(pays by the mile){OFF}")
    if s["per_success"]:
        gap = _gap(s)
        a(f"  {B}cost per SUCCESSFUL      ${s['per_success']:.4f}{OFF}   {D}(pays for arrival){OFF}")
        col = R if gap > 25 else (Y if gap > 5 else G)
        a(f"  the gap                 {col}{gap:.0f}% higher{OFF}{D}, and it is the true number{OFF}")
    else:
        a(f"  {R}cost per SUCCESSFUL      undefined{OFF}{D}; nothing succeeded, which is the finding{OFF}")
    tax_col = R if s["waste_share"] > 0.30 else (Y if s["waste_share"] > 0.12 else G)
    a(f"  failed-run tax          {tax_col}${s['wasted']:.4f}  ({s['waste_share']*100:.0f}% of spend){OFF}")
    a("  " + "─" * 62)
    a(f"  {B}if one run loops overnight{OFF}")
    a(f"  most expensive step     ${s['worst_step']:.4f}")
    pace = "measured from your runs" if s["measured_pace"] else "assumed; your calls returned too fast to be real"
    a(f"  your pace               {s['sec_per_step']:.1f}s per model call   {D}({pace}){OFF}")
    a(f"  {R}{B}twelve hours unattended  ${s['overnight']:,.2f}{OFF}")
    a("  " + "─" * 62)
    a(f"  longest run so far      {s['max_steps']} steps   {D}(median {s['median_steps']:.0f}){OFF}")
    if s["approx_priced"]:
        a(f"  {Y}note{OFF}                    {D}a model was not in the price table; default pricing used{OFF}")
    a("")
    a(f"  {D}Share it:  python3 -m costcheck card{OFF}")
    a(f"  {D}Fix it:    {WAITLIST}{OFF}")
    a("")
    return "\n".join(L)


def render_card(s: dict[str, Any], readiness: tuple[int, list[str]] | None = None) -> str:
    """A plain-text card, sized for a social post. No colour; it gets pasted."""
    if not s["runs"]:
        return "Nothing recorded yet. Run: python3 -m costcheck demo"

    w = 54
    def line(t: str = "") -> str:
        return "│ " + t.ljust(w - 4) + " │"

    L = ["┌" + "─" * (w - 2) + "┐",
         line("MY AGENT COST CHECK"),
         line(f"{s['runs']} runs · {s['ok']} succeeded · {s['bad']} did not"),
         "├" + "─" * (w - 2) + "┤"]
    L.append(line(f"cost per request      ${s['per_request']:.4f}"))
    if s["per_success"]:
        L.append(line(f"cost per SUCCESS      ${s['per_success']:.4f}   ({_gap(s):.0f}% higher)"))
    L.append(line(f"failed-run tax        {s['waste_share']*100:.0f}% of spend"))
    L.append("├" + "─" * (w - 2) + "┤")
    L.append(line("IF ONE RUN LOOPS OVERNIGHT"))
    L.append(line(f"12 hours unattended   ${s['overnight']:,.2f}"))
    if readiness:
        score, _ = readiness
        L.append("├" + "─" * (w - 2) + "┤")
        L.append(line(f"readiness             {score} of 6  " + "■" * score + "□" * (6 - score)))
    L += ["└" + "─" * (w - 2) + "┘",
          "",
          "Measured with costcheck, in about ten minutes:",
          "github.com/Here2ServeU/agent-cost-check"]
    return "\n".join(L)
