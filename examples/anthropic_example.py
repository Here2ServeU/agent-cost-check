"""Anthropic. The only new lines are the three costcheck ones."""
from __future__ import annotations

import costcheck
# import anthropic; client = anthropic.Anthropic()

def handle_invoice(client, path: str) -> dict | None:
    with costcheck.run(task=path, model="claude-sonnet", agent="invoice-reader", team="finance-ops") as r:
        result = None
        for _ in range(10):                         # your existing agent loop
            resp = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": f"Extract the total from {path}"}],
            )
            r.record(resp)                          # <- reads resp.usage for you
            result = parse(resp)
            if result:
                break

        # Be strict here. This one call decides whether the number means anything.
        if result and result.get("total"):
            r.succeeded("extracted a total")
        else:
            r.failed("no total found")
        return result


def parse(resp):                                    # your own parsing
    return {}
