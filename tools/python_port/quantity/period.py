"""Python translation of the OCCT Quantity_Period class.

The original implementation lives in
``src/FoundationClasses/TKernel/Quantity/Quantity_Period.cxx`` and exposes a
small utility for manipulating time intervals stored in seconds and
microseconds.  This module mirrors that behaviour using a more "Pythonic"
interface while keeping the same algorithms for validation, normalization,
addition and subtraction.
"""

from __future__ import annotations

__all__ = [
    "QuantityPeriodDefinitionError",
    "QuantityPeriod",
]


class QuantityPeriodDefinitionError(ValueError):
    """Exception raised when a period receives negative components."""


class QuantityPeriod:
    """Time interval expressed in seconds plus microseconds.

    Parameters mirror the C++ constructor: days, hours, minutes, seconds,
    milliseconds and microseconds.  All components must be non-negative.
    """

    __slots__ = ("_seconds", "_microseconds")

    def __init__(
        self,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        microseconds: int = 0,
    ) -> None:
        self._seconds = 0
        self._microseconds = 0
        self.set_values(days, hours, minutes, seconds, milliseconds, microseconds)

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_seconds(cls, seconds: int, microseconds: int = 0) -> "QuantityPeriod":
        """Build a period directly from seconds and microseconds."""

        instance = cls()
        instance.set_values_seconds(seconds, microseconds)
        return instance

    # ------------------------------------------------------------------
    # Basic value accessors
    # ------------------------------------------------------------------
    def values(self) -> tuple[int, int, int, int, int, int]:
        """Return the decomposed period (days, hours, minutes, seconds, ms, µs)."""

        carry = self._seconds
        days = carry // (24 * 3600)
        carry -= days * 24 * 3600
        hours = carry // 3600
        carry -= hours * 3600
        minutes = carry // 60
        carry -= minutes * 60
        seconds = carry
        milliseconds = self._microseconds // 1000
        microseconds = self._microseconds - milliseconds * 1000
        return days, hours, minutes, seconds, milliseconds, microseconds

    def values_seconds(self) -> tuple[int, int]:
        """Return the total seconds and the remainder microseconds."""

        return self._seconds, self._microseconds

    # ------------------------------------------------------------------
    # Mutators
    # ------------------------------------------------------------------
    def set_values(
        self,
        days: int,
        hours: int,
        minutes: int,
        seconds: int,
        milliseconds: int = 0,
        microseconds: int = 0,
    ) -> None:
        """Assign a period using the full component list."""

        total_seconds = (days * 24 * 3600) + (hours * 3600) + (minutes * 60) + seconds
        total_microseconds = milliseconds * 1000 + microseconds
        self.set_values_seconds(total_seconds, total_microseconds)

    def set_values_seconds(self, seconds: int, microseconds: int = 0) -> None:
        """Assign a period using seconds plus microseconds."""

        if not self.is_valid_seconds(seconds, microseconds):
            raise QuantityPeriodDefinitionError(
                "QuantityPeriod.set_values_seconds received negative values"
            )

        self._seconds = int(seconds)
        self._microseconds = int(microseconds)
        while self._microseconds > 1_000_000:
            self._microseconds -= 1_000_000
            self._seconds += 1

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------
    def copy(self) -> "QuantityPeriod":
        return QuantityPeriod.from_seconds(self._seconds, self._microseconds)

    def subtract(self, other: "QuantityPeriod") -> "QuantityPeriod":
        """Return ``self - other`` following the C++ implementation."""

        result = self.copy()
        result._seconds -= other._seconds
        result._microseconds -= other._microseconds

        if result._seconds >= 0 and result._microseconds < 0:
            result._seconds -= 1
            result._microseconds = 1_000_000 + result._microseconds
        elif result._seconds < 0 and result._microseconds >= 0:
            result._seconds = abs(result._seconds)
            if result._microseconds > 0:
                result._seconds -= 1
                result._microseconds = 1_000_000 - result._microseconds
        elif result._seconds < 0 and result._microseconds < 0:
            result._seconds = abs(result._seconds)
            result._microseconds = abs(result._microseconds)

        return result

    def __sub__(self, other: "QuantityPeriod") -> "QuantityPeriod":
        return self.subtract(other)

    def add(self, other: "QuantityPeriod") -> "QuantityPeriod":
        """Return ``self + other`` following the C++ implementation."""

        result = self.copy()
        result._seconds += other._seconds
        result._microseconds += other._microseconds
        if result._microseconds > 1_000_000:
            result._microseconds -= 1_000_000
            result._seconds += 1
        return result

    def __add__(self, other: "QuantityPeriod") -> "QuantityPeriod":
        return self.add(other)

    # ------------------------------------------------------------------
    # Comparisons
    # ------------------------------------------------------------------
    def is_equal(self, other: "QuantityPeriod") -> bool:
        return self._seconds == other._seconds and self._microseconds == other._microseconds

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuantityPeriod):
            return NotImplemented
        return self.is_equal(other)

    def is_shorter(self, other: "QuantityPeriod") -> bool:
        if self._seconds < other._seconds:
            return True
        if self._seconds > other._seconds:
            return False
        return self._microseconds < other._microseconds

    def __lt__(self, other: "QuantityPeriod") -> bool:
        return self.is_shorter(other)

    def is_longer(self, other: "QuantityPeriod") -> bool:
        if self._seconds > other._seconds:
            return True
        if self._seconds < other._seconds:
            return False
        return self._microseconds > other._microseconds

    def __gt__(self, other: "QuantityPeriod") -> bool:
        return self.is_longer(other)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def is_valid(
        days: int,
        hours: int,
        minutes: int,
        seconds: int,
        milliseconds: int = 0,
        microseconds: int = 0,
    ) -> bool:
        return all(
            component >= 0
            for component in (days, hours, minutes, seconds, milliseconds, microseconds)
        )

    @staticmethod
    def is_valid_seconds(seconds: int, microseconds: int = 0) -> bool:
        return seconds >= 0 and microseconds >= 0

    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        sec, usec = self.values_seconds()
        return f"QuantityPeriod(seconds={sec}, microseconds={usec})"
