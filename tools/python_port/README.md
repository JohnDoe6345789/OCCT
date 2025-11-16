# Python Ports

This directory stores focused Python translations of small OCCT utility
classes so they can be reused without pulling the whole C++ toolchain.  Each
subfolder mirrors the original module hierarchy from `src/` and contains a
README that points back to the upstream implementation.

Currently available ports:

- `quantity/period.py`: translation of
  `src/FoundationClasses/TKernel/Quantity/Quantity_Period.cxx`.

## Codex automation CLI

The `codex_cli.py` helper automates the "Continue with python port until
feature parity" workflow used in Codex prompts.  It records each prompt run and
captures the current git status in a pseudo pull-request payload so the steps
can be repeated deterministically.  Each automation cycle includes a reference
to <https://github.com/openai/codex?tab=readme-ov-file> so coders know which
public instructions to follow.

Run the automation with the default prompt:

```bash
python tools/python_port/codex_cli.py
```

To preview the steps without touching the filesystem, enable `--dry-run`:

```bash
python tools/python_port/codex_cli.py --dry-run
```

## Quick start

```python
from tools.python_port import QuantityPeriod

# Build a period by composing days/hours/minutes/seconds components.
period = QuantityPeriod(hours=1, minutes=30, seconds=15)
print(period.values())  # (0, 1, 30, 15, 0, 0)

# Create another period directly from seconds + microseconds and add them.
pause = QuantityPeriod.from_seconds(30, 500_000)
print((period + pause).values_seconds())  # (5415, 500000)
```

## Contributor docs

- [`API_SPEC.md`](API_SPEC.md) documents the supported interfaces so downstream
  scripts can rely on stable behaviour.
- [`TODO.md`](TODO.md) tracks upcoming work for the Python ports, including
  testing, packaging, and future modules to translate.
