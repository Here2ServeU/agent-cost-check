"""OpenAI. Identical, because record() reads either shape."""
from __future__ import annotations

import costcheck
# from openai import OpenAI; client = OpenAI()

def summarize_ticket(client, ticket: str) -> str | None:
    with costcheck.run(task="support-summary") as r:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Summarise: {ticket}"}],
        )
        r.record(resp)                              # prompt_tokens / completion_tokens
        text = resp.choices[0].message.content
        if text and len(text) > 20:
            r.succeeded("produced a summary")
            return text
        r.failed("empty or too short")
        return None
