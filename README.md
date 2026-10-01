# costcheck

**What does your AI agent really cost, including the runs that fail?**

Your dashboard shows what you spent. It does not show:

1. what one **finished** task costs,
2. how much of your bill went to runs that **produced nothing**,
3. what one stuck run would cost if it **looped all night**.

costcheck tells you all three. No dependencies, no account, nothing leaves your
computer.

**New here? Watch the video guide first.** It explains what costcheck measures and walks through it step by step:

<p align="center">
  <a href="https://youtu.be/lo_YUtlCzPs">
    <img src="https://img.youtube.com/vi/lo_YUtlCzPs/hqdefault.jpg" alt="What Does Your AI Agent Really Cost? (Including the Runs That Fail)" width="560">
  </a>
  <br>
  <a href="https://youtu.be/lo_YUtlCzPs">Watch the costcheck video guide on YouTube</a>
</p>

---

## Before you start: Mac or Windows?

Every command in this README runs in a terminal. Open one like this:

| | Mac | Windows |
|---|---|---|
| Open a terminal | Press `Cmd + Space`, type **Terminal**, press Enter | Press the Windows key, type **PowerShell**, press Enter |
| Run Python | `python3` | `py` (if that's not found, try `python`) |
| Check Python is ready | `python3 --version` | `py --version` |

You need Python 3.9 or newer and git. Don't have them?

- **Mac:** run `xcode-select --install` (gives you git and Python), or get Python from [python.org](https://www.python.org/downloads/).
- **Windows:** install Python from [python.org](https://www.python.org/downloads/) and tick **"Add python.exe to PATH"** during setup. Install git from [git-scm.com](https://git-scm.com/download/win). Close and reopen PowerShell afterwards.

**Prefer to watch?** These step-by-step videos install Python, Git and Visual Studio Code from scratch:

| Mac | Windows |
|---|---|
| [![How to install Git, Python and Visual Studio Code on Mac](https://img.youtube.com/vi/8ZIiXg4XOY0/mqdefault.jpg)](https://www.youtube.com/watch?v=8ZIiXg4XOY0) | [![How to install Git, Python and Visual Studio Code on Windows](https://img.youtube.com/vi/f091sbQSv7I/mqdefault.jpg)](https://www.youtube.com/watch?v=f091sbQSv7I) |
| [Watch the Mac video](https://www.youtube.com/watch?v=8ZIiXg4XOY0) | [Watch the Windows video](https://www.youtube.com/watch?v=f091sbQSv7I) |

> **Windows rule of thumb:** wherever this README says `python3`, type `py` instead. Everything else is the same.

---

## Step 1: See it work (30 seconds, no API key)

**Mac:**

```bash
git clone https://github.com/Here2ServeU/agent-cost-check
cd agent-cost-check
python3 -m costcheck demo
python3 -m costcheck report
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/Here2ServeU/agent-cost-check
cd agent-cost-check
py -m costcheck demo
py -m costcheck report
```

This uses fake data, so you can see the report before touching your own code.

---

## Step 2: Add it to your project

costcheck is plain Python with zero dependencies, so it doesn't need installing. You already cloned it in Step 1. From inside the `agent-cost-check` folder, copy the `costcheck` folder into your project:

**Mac:**

```bash
cp -r costcheck /path/to/your-project/
```

**Windows (PowerShell):**

```powershell
Copy-Item -Recurse costcheck C:\path\to\your-project\
```

Replace the path with your own project folder. That's it. From your project folder, `import costcheck` works and `python3 -m costcheck report` (`py -m costcheck report` on Windows) works. No pip involved.

**Prefer pip?** Use `python3 -m pip` (Mac) or `py -m pip` (Windows), not plain `pip`:

```bash
# Mac
python3 -m pip install git+https://github.com/Here2ServeU/agent-cost-check

# Windows
py -m pip install git+https://github.com/Here2ServeU/agent-cost-check
```

This asks Python to run its own pip instead of hoping a `pip` command exists on your `PATH`. It also installs into the same Python you'll run your agent with, which avoids the classic "install succeeded but `import` fails" problem when two Pythons are on your machine.

> On a Mac, if you see `error: externally-managed-environment` (common with Homebrew Python), skip pip and use the copy method above. Or install inside a virtual environment if you already use one.

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
real, install the SDK and set your key:

- **Mac:** `python3 -m pip install anthropic` (or `openai`), then `export ANTHROPIC_API_KEY=...` (or `export OPENAI_API_KEY=...`)
- **Windows (PowerShell):** `py -m pip install anthropic` (or `openai`), then `$env:ANTHROPIC_API_KEY="..."` (or `$env:OPENAI_API_KEY="..."`)

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

## Cleanup

Done trying it out, or want a fresh start? Pick what you need. Run each command
from the folder named in the step.

**1. Clear your results, keep the tool.** From the folder you ran your agent in:

```bash
# Mac
python3 -m costcheck reset

# Windows (PowerShell)
py -m costcheck reset
```

This deletes `.costcheck/runs.jsonl`, including the fake runs from `demo`.
Your next report starts from zero.

**2. Remove the data folder too.** `reset` empties your results; this removes
the folder itself:

```bash
# Mac
rm -rf .costcheck

# Windows (PowerShell)
Remove-Item -Recurse -Force .costcheck
```

**3. Take costcheck out of your project.** Delete the three lines from Step 3
(`import costcheck`, the `with costcheck.run(...)` line, and `r.record` /
`r.succeeded`), move your code back out of the `with` block, then:

- **If you copied the folder:** from your project folder, run `rm -rf costcheck`
  (Mac) or `Remove-Item -Recurse -Force costcheck` (Windows).
- **If you used pip:** run `python3 -m pip uninstall costcheck` (Mac) or
  `py -m pip uninstall costcheck` (Windows).

**4. Delete the cloned repo.** From inside `agent-cost-check`, go up one folder
with `cd ..`, then delete it:

```bash
# Mac
cd ..
rm -rf agent-cost-check

# Windows (PowerShell)
cd ..
Remove-Item -Recurse -Force agent-cost-check
```

**5. Clear any API keys you set for the examples.** Keys set with `export` or
`$env:` only last until you close the terminal. To clear them now:

```bash
# Mac
unset ANTHROPIC_API_KEY OPENAI_API_KEY

# Windows (PowerShell)
Remove-Item Env:ANTHROPIC_API_KEY, Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
```

That's everything. costcheck never installs anything system-wide or sends data
anywhere, so there is nothing else to remove.

## Tests

```bash
python3 -m unittest discover -s tests
```

Standard library only. If they pass, every number in the report is arithmetic
you can check by hand.

---

MIT licensed. Built by [Emmanuel Naweji](https://github.com/Here2ServeU).
