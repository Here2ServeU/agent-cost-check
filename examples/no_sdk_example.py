"""No SDK at all; you have the two numbers from somewhere else."""
from __future__ import annotations

import costcheck

with costcheck.run(task="batch-job", model="llama-70b") as r:
    for chunk in range(6):
        r.record(input_tokens=1800, output_tokens=400)
    r.succeeded("all chunks processed")
