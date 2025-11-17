# Python Port TODO

This backlog tracks the next steps for the lightweight OCCT Python ports so
that contributors can coordinate efforts.

**For automated conversion tasks, see [`../conversion_tools/`](../conversion_tools/)**

## Infrastructure

- [ ] Publish the modules as an installable package (``python_port``) so they
  can be consumed without copying files manually.
- [ ] Add ``pytest``-based regression tests that exercise every public method
  described in the API specification.
- [ ] Wire the directory into the top-level CMake or CI configuration so
  ``python -m pytest`` runs as part of the regular validation process.
- [ ] Add type-checking (``pyproject.toml`` + ``mypy``) to keep the Python
  translation aligned with the original C++ signatures.

## Documentation

- [ ] Cross-link every translated module back to its upstream ``src`` file in
  the ``dox`` documentation set for easier verification.
- [ ] Expand ``tools/python_port/README.md`` with a quick-start example showing
  how to instantiate and operate on a ``QuantityPeriod``.
- [ ] Keep ``API_SPEC.md`` in sync whenever new classes land.

## Module roadmap

- [ ] Port ``Quantity_Period::Divide`` and other helper routines that do not yet
  exist in ``quantity/period.py``.
- [ ] Translate additional utility classes frequently used in scripting
  (``gp_XYZ``, ``TColStd_Array1OfInteger``, etc.) when they can be expressed
  without external C++ dependencies.
- [ ] Provide serialization helpers that convert Python port objects to the
  textual diagnostics printed by the C++ counterparts for easier comparison.
