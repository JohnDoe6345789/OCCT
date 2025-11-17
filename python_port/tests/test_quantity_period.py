"""Regression tests for the ``tools.python_port.quantity.period`` module."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.python_port import QuantityPeriod, QuantityPeriodDefinitionError


def test_component_roundtrip() -> None:
    period = QuantityPeriod(days=2, hours=15, minutes=1, seconds=3, milliseconds=250, microseconds=400)
    assert period.values() == (2, 15, 1, 3, 250, 400)

    total_seconds = (2 * 24 * 3600) + (15 * 3600) + 60 + 3
    assert period.values_seconds() == (total_seconds, 250_400)


def test_from_seconds_and_copy_are_consistent() -> None:
    base = QuantityPeriod.from_seconds(5, 750_000)
    clone = base.copy()
    assert clone is not base
    assert clone.values_seconds() == (5, 750_000)

    clone.set_values_seconds(1, 0)
    assert base.values_seconds() == (5, 750_000)


def test_negative_inputs_raise_definition_error() -> None:
    with pytest.raises(QuantityPeriodDefinitionError):
        QuantityPeriod(days=-1)

    period = QuantityPeriod()
    with pytest.raises(QuantityPeriodDefinitionError):
        period.set_values_seconds(-10)


def test_add_and_subtract_follow_occt_rules() -> None:
    first = QuantityPeriod.from_seconds(10, 900_000)
    second = QuantityPeriod.from_seconds(5, 200_000)

    added = first.add(second)
    assert added.values_seconds() == (16, 100_000)

    subtracted = first.subtract(second)
    assert subtracted.values_seconds() == (5, 700_000)

    reverse_subtract = second.subtract(first)
    assert reverse_subtract.values_seconds() == (5, 700_000)


def test_comparisons_align_with_component_checks() -> None:
    shorter = QuantityPeriod(seconds=1)
    longer = QuantityPeriod(seconds=2)

    assert shorter.is_shorter(longer)
    assert longer.is_longer(shorter)
    assert shorter < longer
    assert longer > shorter
    assert shorter != longer
    assert longer == QuantityPeriod(seconds=2)


def test_type_checks_protect_operations() -> None:
    period = QuantityPeriod(seconds=1)

    with pytest.raises(TypeError):
        period.add(object())  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        period.subtract("bad")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        period.is_shorter(3)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        period.is_longer(None)  # type: ignore[arg-type]
