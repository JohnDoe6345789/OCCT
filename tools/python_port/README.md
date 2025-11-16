# Python Ports

This directory stores focused Python translations of small OCCT utility
classes so they can be reused without pulling the whole C++ toolchain.  Each
subfolder mirrors the original module hierarchy from `src/` and contains a
README that points back to the upstream implementation.

Currently available ports:

- `quantity/period.py`: translation of
  `src/FoundationClasses/TKernel/Quantity/Quantity_Period.cxx`.

## Contributor docs

- [`API_SPEC.md`](API_SPEC.md) documents the supported interfaces so downstream
  scripts can rely on stable behaviour.
- [`TODO.md`](TODO.md) tracks upcoming work for the Python ports, including
  testing, packaging, and future modules to translate.
