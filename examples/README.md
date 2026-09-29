# Examples

Open them in this order.

| File | What it shows | Needs an API key? |
|---|---|---|
| [start_here.py](start_here.py) | The basics, every line explained. **Run this one first.** | No |
| [anthropic_example.py](anthropic_example.py) | Adding costcheck to an agent that uses Claude | Yes, to run it for real |
| [openai_example.py](openai_example.py) | The same thing with OpenAI (only the model name changes) | Yes, to run it for real |

Run the first one from the main project folder:

```bash
python3 examples/start_here.py
python3 -m costcheck report
```

The other two are for reading. They show the three costcheck lines inside
realistic code, so you can copy the pattern into your own agent.
