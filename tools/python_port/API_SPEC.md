# Python Port API Specification

This document describes the public surface of the lightweight Python ports so
that downstream tools can rely on a stable interface.  The current scope only
covers the ``quantity.period`` module.

## Module ``python_port.quantity.period``

### Exceptions

#### ``QuantityPeriodDefinitionError``
Raised when negative values are provided to ``QuantityPeriod.set_values`` or
``set_values_seconds``.  Subclasses ``ValueError`` and does not define custom
attributes.

### Classes

#### ``QuantityPeriod``
Represents a time interval expressed as seconds + microseconds.

**Construction**

``QuantityPeriod(days=0, hours=0, minutes=0, seconds=0, milliseconds=0,
microseconds=0)``
: Validates that all components are non-negative, converts them into seconds and
  microseconds, and normalizes the microseconds field to be ``< 1_000_000``.

``QuantityPeriod.from_seconds(seconds, microseconds=0)``
: Class method returning a new instance that bypasses component decomposition.

**Inspectors**

``values() -> tuple[int, int, int, int, int, int]``
: Returns (days, hours, minutes, seconds, milliseconds, microseconds).

``values_seconds() -> tuple[int, int]``
: Returns ``(seconds, microseconds)`` directly.

``__repr__() -> str``
: Produces ``QuantityPeriod(seconds=<int>, microseconds=<int>)``.

**Mutators**

``set_values(days, hours, minutes, seconds, milliseconds=0, microseconds=0)``
: Accepts decomposed components and forwards to ``set_values_seconds``.

``set_values_seconds(seconds, microseconds=0)``
: Validates via ``is_valid_seconds`` and stores the normalized values.  Raises
  ``QuantityPeriodDefinitionError`` when either argument is negative.

**Arithmetic**

``copy()``
: Returns a detached copy of the current instance.

``add(other)`` / ``__add__(other)``
: Adds seconds and microseconds individually and normalizes the microseconds
  overflow.

``subtract(other)`` / ``__sub__(other)``
: Implements the same branch structure as the OCCT C++ code to keep behaviour
  consistent even when the difference is negative.

**Comparisons**

``is_equal(other)`` / ``__eq__(other)``
: Equality on both seconds and microseconds.

``is_shorter(other)`` / ``__lt__(other)``
: Lexicographical comparison (seconds first, then microseconds).

``is_longer(other)`` / ``__gt__(other)``
: Lexicographical comparison with inverted predicate.

**Validation helpers**

``is_valid(days, hours, minutes, seconds, milliseconds=0, microseconds=0)``
: ``True`` when all components are non-negative.

``is_valid_seconds(seconds, microseconds=0)``
: ``True`` when both arguments are non-negative.
