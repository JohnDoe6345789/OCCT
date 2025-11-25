"""
Quantity_Period

Python port of OCCT C++ class.
Original: src/*/Quantity_Period.cxx
"""

from typing import Optional, List, Tuple, Any

class Quantity_Period:
    """
    Represents a OCCT class.
    """

    def __init__(self, ss: Const standardInteger, mics: Const standardInteger = 0):
        """Initialize the class."""
        pass


    def values(self, ss: Optional[int], mics: Optional[int]):
        """
        Values method.
        """
        pass

    def set_values(self, ss: Const standardInteger, mics: Const standardInteger = 0):
        """
        SetValues method.
        """
        pass

    def subtract(self, an_other: Optional[Const quantityPeriod]):
        """
        Subtract method.
        """
        pass

    def subtract(self):
        """
        Subtract method.
        """
        pass

    def add(self, an_other: Optional[Const quantityPeriod]):
        """
        Add method.
        """
        pass

    def add(self):
        """
        Add method.
        """
        pass

    def is_equal(self, an_other: Optional[Const quantityPeriod]):
        """
        IsEqual method.
        """
        pass

    def is_equal(self):
        """
        IsEqual method.
        """
        pass

    def is_shorter(self, an_other: Optional[Const quantityPeriod]):
        """
        IsShorter method.
        """
        pass

    def is_shorter(self):
        """
        IsShorter method.
        """
        pass

    # ... and 2 more methods