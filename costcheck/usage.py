"""Reading the usage block, whatever shape it arrives in.

Every model response carries one. Most code throws it away. This module's
whole job is to find it, whether you hand it an Anthropic response, an
OpenAI response, a dict, or two integers.

If a new SDK shape shows up that this misses, `record()` raises with the
object's own keys in the message, so you can see what you were handed
instead of silently recording a zero.
"""
from __future__ import annotations

from typing import Any

# (input_field, output_field) pairs, in the order we try them.
_PAIRS = [
    ("input_tokens", "output_tokens"),          # Anthropic; OpenAI Responses
    ("prompt_tokens", "completion_tokens"),     # OpenAI Chat Completions
    ("promptTokenCount", "candidatesTokenCount"),  # Gemini
    ("in_tokens", "out_tokens"),
]


def _get(obj: Any, name: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def extract(obj: Any) -> tuple[int, int]:
    """Return (input_tokens, output_tokens) from a response, usage block or dict."""
    if obj is None:
        raise ValueError("record() got None; pass the model response or a usage dict")

    # A response object wrapping a usage block.
    usage = _get(obj, "usage") or _get(obj, "usage_metadata") or obj

    for a, b in _PAIRS:
        i, o = _get(usage, a), _get(usage, b)
        if i is not None and o is not None:
            return int(i), int(o)

    keys = sorted(usage.keys()) if isinstance(usage, dict) else sorted(
        k for k in dir(usage) if not k.startswith("_"))
    raise ValueError(
        "costcheck could not find a usage block on that object.\n"
        f"  what it saw: {keys[:12]}\n"
        "  fix: pass the numbers directly, e.g. r.record(input_tokens=1200, output_tokens=300)"
    )


def model_name(obj: Any) -> str | None:
    """The model id a response says it came from, if it says one."""
    name = _get(obj, "model") if obj is not None else None
    return name if isinstance(name, str) else None
