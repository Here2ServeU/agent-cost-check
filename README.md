# costcheck

**What does your AI agent really cost, including the runs that fail?**

Your dashboard shows what you spent. It does not show:

1. what one **finished** task costs,
2. how much of your bill went to runs that **produced nothing**,
3. what one stuck run would cost if it **looped all night**.

costcheck tells you all three. No dependencies, no account, nothing leaves your
computer.

---

## Step 1: See it work (30 seconds, no API key)

```bash
git clone https://github.com/Here2ServeU/agent-cost-check
cd agent-cost-check
python3 -m costcheck demo
python3 -m costcheck report
```

This uses fake data, so you can see the report before touching your own code.

---

## Step 2: Install it in your project

```bash
pip install git+https://github.com/Here2ServeU/agent-cost-check
```

Needs Python 3.9 or newer. Nothing else gets installed.

---

## Step 3: Add three lines to your agent

Here is a normal model call:

```python
resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=1024, messages=msgs)
print(resp.content[0].text)
```

Here it is with costcheck. Nothing else changes:

```python
import costcheck

with costcheck.run(task="my-first-task") as r:     # 1. start measuring one task
    resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=1024, messages=msgs)
    r.record(resp)                                 # 2. after every model call
    print(resp.content[0].text)
    r.succeeded()                                  # 3. only if the task really worked
```

What each line does:

| Line | What it means |
|---|---|
| `with costcheck.run(task=...) as r:` | "Everything indented below is one task." Your existing code moves inside it. |
| `r.record(resp)` | Reads the token counts and model name from the response. Works with Anthropic, OpenAI and Gemini. |
| `r.succeeded()` | You decide what "worked" means. If you never call it, or your code crashes, the run counts as **failed**. |

Not using an SDK response? Pass the numbers yourself:

```python
r.record(input_tokens=1200, output_tokens=300, model="gpt-4o")
```

If your agent calls the model several times in one task, call `r.record(...)`
after each call, all inside the same `with` block.

---

## Step 4: Read your report

Run your agent a dozen times, then:

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

### The three numbers

**Cost per successful task.** Everything you spent, divided by the runs that
worked. If you switch to a cheaper model that fails more often, this is the
number that goes up. Per-request cost will make it look like you saved money.

**Failed-run tax.** The share of your bill that bought nothing.

**Overnight exposure.** Your most expensive step, at your own measured speed,
repeated for twelve hours. This is what one stuck loop starting at midnight
would cost by morning.

---

## Other commands

```bash
python3 -m costcheck check    # six yes/no questions: what would stop a runaway run?
python3 -m costcheck card     # a plain-text summary you can paste into a post
python3 -m costcheck reset    # delete everything and start over
```

---

## What this does not do

It measures. It does not stop anything. There is no cap, no loop detection, no
kill switch and no alert. That is on purpose: you can't pick a sensible cap
until you know what a normal run costs, and this tool tells you that.

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

Seven sessions, and a capstone repo where each of the six is proven by running
it with the mechanism off and then on. The whole safety layer is under four
hundred lines.

**[Join the waitlist →](https://www.transformed2succeed.com/waitlist)**

---

## What's in this repo

### `costcheck/`: the tool itself

You only ever use `costcheck.run()`, `r.record()` and `r.succeeded()`. The
rest is here if you want to see how it works.

| File | What it does |
|---|---|
| [`__init__.py`](costcheck/__init__.py) | `costcheck.run()` and the `r` object: `record()`, `succeeded()`, `failed()`. Saves one line per task when the `with` block ends. |
| [`usage.py`](costcheck/usage.py) | Finds the token counts and model name in a response, whether it came from Anthropic, OpenAI, Gemini or a plain dict. |
| [`prices.py`](costcheck/prices.py) | The price table, in dollars per million tokens. **Edit this file when prices change** or to add your model. |
| [`store.py`](costcheck/store.py) | Reads and writes `.costcheck/runs.jsonl`, the file all your results go into. |
| [`report.py`](costcheck/report.py) | Turns the saved runs into the three numbers, the report and the shareable card. |
| [`readiness.py`](costcheck/readiness.py) | The six yes/no questions behind `python3 -m costcheck check`. |
| [`__main__.py`](costcheck/__main__.py) | The commands: `demo`, `report`, `check`, `card`, `reset`. |

### `examples/`: start here if you learn by reading code

| File | What it shows | API key? |
|---|---|---|
| [`start_here.py`](examples/start_here.py) | The basics, every line explained. One task that works, one that fails. **Run this first.** | No |
| [`anthropic_example.py`](examples/anthropic_example.py) | costcheck inside an agent loop that calls Claude several times per task. | Only to run it for real |
| [`openai_example.py`](examples/openai_example.py) | The same pattern with OpenAI. Only the client code changes. | Only to run it for real |

The two API examples are meant to be read and copied from. To run them for
real, install the SDK (`pip install anthropic` or `pip install openai`) and set
your key with `export ANTHROPIC_API_KEY=...` or `export OPENAI_API_KEY=...`.
costcheck itself never needs a key.

### Everything else

| File | What it is |
|---|---|
| [`tests/`](tests/test_costcheck.py) | Checks that the arithmetic is right. Run with `python3 -m unittest discover -s tests`. |
| [`pyproject.toml`](pyproject.toml) | Lets `pip install` work. |
| [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | Runs the tests on GitHub every time code is pushed. |

---

## Your data

Everything goes into `.costcheck/runs.jsonl` in the folder you run from, one
line per task. No server, no network calls, no telemetry. Open the file and
read it. Add `.costcheck/` to your `.gitignore` if you don't want it committed.

## Tests

```bash
python3 -m unittest discover -s tests
```

Standard library only. If they pass, every number in the report is arithmetic
you can check by hand.

---

MIT licensed. Built by [Emmanuel Naweji](https://github.com/Here2ServeU).
