"""Prices, per one million tokens, in US dollars.

They change. This is one file so that when they change, you edit one file.
Input and output are priced differently, which is why every usage block has
two numbers and why you must never average them into one.

Unknown model? costcheck falls back to `default` and says so in the report,
rather than silently pricing your run at zero.
"""
from __future__ import annotations

PRICES: dict[str, dict[str, float]] = {
    # --- Anthropic
    "claude-haiku":  {"input": 0.80,  "output": 4.00},
    "claude-sonnet": {"input": 3.00,  "output": 15.00},
    "claude-opus":   {"input": 15.00, "output": 75.00},
    # --- OpenAI
    "gpt-4o":        {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":   {"input": 0.15,  "output": 0.60},
    "o3-mini":       {"input": 1.10,  "output": 4.40},
    # --- open weights, typical hosted pricing
    "llama-70b":     {"input": 0.60,  "output": 0.60},
    "mistral-large": {"input": 2.00,  "output": 6.00},
    # --- used when nothing matches; the report tells you it was used
    "default":       {"input": 3.00,  "output": 15.00},
}

# Substring matching, longest first, so "claude-3-5-sonnet-20241022" finds
# "claude-sonnet" without you having to maintain every dated model id.
_ALIASES = [
    ("haiku", "claude-haiku"), ("sonnet", "claude-sonnet"), ("opus", "claude-opus"),
    ("gpt-4o-mini", "gpt-4o-mini"), ("4o-mini", "gpt-4o-mini"), ("gpt-4o", "gpt-4o"),
    ("o3-mini", "o3-mini"), ("llama", "llama-70b"), ("mistral", "mistral-large"),
]


def resolve(model: str) -> tuple[str, bool]:
    """Return (price_key, exact). exact=False means the default was used."""
    if not model:
        return "default", False
    m = model.lower()
    if m in PRICES:
        return m, True
    for needle, key in sorted(_ALIASES, key=lambda a: -len(a[0])):
        if needle in m:
            return key, True
    return "default", False


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> tuple[float, bool]:
    key, exact = resolve(model)
    p = PRICES[key]
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000, exact
