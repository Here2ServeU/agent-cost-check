# costcheck

**What does your agent cost when it fails? Find out in ten minutes.**

Your dashboard shows a number. That number is what your agent spent. It does not
tell you what a *finished piece of work* costs, how much of the bill went to runs
that produced nothing, or what one unnoticed loop would cost you between midnight
and eight.

This tells you all three. Three lines of code, no dependencies, nothing leaves
your machine.

```bash
git clone https://github.com/Here2ServeU/agent-cost-check
cd agent-cost-check
python3 -m costcheck demo
```

That runs on fake data so you can see the output before wiring anything up. About
thirty seconds.

---

## Then measure your own agent

Three lines. Zero dependencies — pure standard library, Python 3.9+.

```python
import costcheck

with costcheck.run(task="invoice-4471") as r:
    resp = client.messages.create(...)     # your existing call, unchanged
    r.record(resp)                         # reads the usage block for you
    r.succeeded()                          # your definition, not ours
```

`record()` understands Anthropic, OpenAI, Gemini and plain dicts. If it gets
something it does not recognise it tells you what it saw, rather than quietly
recording a zero. You can always pass the numbers yourself:

```python
r.record(input_tokens=1200, output_tokens=300)
```

Run your agent a dozen times. Then:

```bash
python3 -m costcheck report
```

```
  YOUR AGENT COST CHECK
  12 runs · claude-sonnet
  ──────────────────────────────────────────────────────────────
  runs recorded           12
  succeeded                8      <- the denominator
  did not                  4      <- still counts on top
  total spend             $1.6522
  ──────────────────────────────────────────────────────────────
  cost per request        $0.1377   (pays by the mile)
  cost per SUCCESSFUL     $0.2065   (pays for arrival)
  the gap                 50% higher, and it is the true number
  failed-run tax          $1.1966  (72% of spend)
  ──────────────────────────────────────────────────────────────
  if one run loops overnight
  most expensive step     $0.0117
  your pace               3.0s per model call   (measured from your runs)
  twelve hours unattended  $168.95
```

---

## The three numbers, and why they are the ones that matter

**Cost per successful task.** Total spend divided by the runs that actually
worked. Failures go on the top, not the bottom — you paid for them. This is the
only number that catches a change that made things *worse while spending less*:
switch to a cheaper model, fail more often, and per-request cost falls while this
one rises. Nothing else on your dashboard can tell you that.

**The failed-run tax.** The share of your bill that bought nothing. Most teams
guess low. Measure it before you guess.

**Overnight exposure.** Your most expensive step, at your own measured pace, for
twelve unattended hours. This is not a scare number — it is your most expensive
real step multiplied by your own real speed. If a single run started looping at
midnight, that is the bill.

---

## Six questions

```bash
python3 -m costcheck check
```

Six yes/no questions about what would stop that run. No trick ones, and nothing
is inferred — a score you answered yourself is one you believe.

```
  READINESS  2 of 6   ■■□□□□
  You can see some of it. You cannot stop any of it.
```

---

## Share your number

```bash
python3 -m costcheck card
```

Prints a plain-text card sized for a post. Most people are surprised by the gap
between their two cost numbers, and posting it is how other people find out
theirs.

---

## What this does not do

It measures. It does not stop anything.

There is no cap here, no loop detection, no kill switch, no alert. That is
deliberate — you cannot sensibly choose a cap before you know what a normal run
costs, and this is the tool that tells you.

The six mechanisms that *do* stop it are the course:
**[The Agent Cost Problem →](https://github.com/Here2ServeU/agent-cost-control)**

| | | |
|---|---|---|
| 1 | Instrument it | you can see it |
| 2 | Cap it | it is bounded |
| 3 | Detect the loop | 6 steps, not 14 |
| 4 | Checkpoint | stopping is cheap |
| 5 | Cost per successful task | the true number |
| 6 | Alert on burn rate | you find out while it happens |

Seven sessions, and a capstone repo where every one of the six is proven by
running it with the mechanism turned off and then turned on. The whole safety
layer is under four hundred lines.

**Join the waitlist → [YOUR_WAITLIST_URL]**

---

## Your data

Everything is written to `./.costcheck/runs.jsonl` in the directory you run from.
No server, no network calls, no telemetry, no account. Read the file — it is one
JSON object per line. `python3 -m costcheck reset` deletes it.

Add `.costcheck/` to your `.gitignore`, or do not. It is your data.

---

## Tests

```bash
python3 -m unittest discover -s tests
```

Fifteen tests, standard library only. If they pass, the numbers in the report are
arithmetic you can check by hand.

---

MIT licensed. Built by [Emmanuel Naweji](https://github.com/Here2ServeU).
