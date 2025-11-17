# Python Ports

This directory stores focused Python translations of small OCCT utility
classes so they can be reused without pulling the whole C++ toolchain.  Each
subfolder mirrors the original module hierarchy from `src/` and contains a
README that points back to the upstream implementation.

Currently available ports:

- `quantity/period.py`: translation of
  `src/FoundationClasses/TKernel/Quantity/Quantity_Period.cxx`.

## Codex automation CLI

The Codex automation workflow has been rewritten in TypeScript and is available in
[`tools/typescript_port`](../tools/typescript_port).  It records each prompt run,
captures the current git status in a pseudo pull-request payload, and calls the
public <https://chatgpt.com/codex> API for every prompt execution so the
automation mirrors the real Codex workflow.  Each automation cycle includes a
reference to <https://github.com/openai/codex?tab=readme-ov-file> so coders know
which public instructions to follow.  See the new README for install and usage
details.

## Quick start

```python
from python_port.quantity import QuantityPeriod

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
