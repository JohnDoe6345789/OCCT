"""
Quantity_Color

Python port of OCCT C++ class.
Original: src/*/Quantity_Color.cxx
"""

from typing import Optional, List, Tuple, Any

class Quantity_Color:
    """
    Represents a OCCT class.
    """

    def __init__(self, the_rgb: Optional[Const ncollectionVec3]):
        """Initialize the class."""
        pass


    def name(self):
        """
        Name method.
        """
        pass

    def red(self):
        """
        Red method.
        """
        pass

    def green(self):
        """
        Green method.
        """
        pass

    def blue(self):
        """
        Blue method.
        """
        pass

    def change_intensity(self, the_delta: Const standardReal):
        """
        ChangeIntensity method.
        """
        pass

    def change_contrast(self, the_delta: Const standardReal):
        """
        ChangeContrast method.
        """
        pass

    def is_different(self):
        """
        IsDifferent method.
        """
        pass

    def is_equal(self):
        """
        IsEqual method.
        """
        pass

    def delta_e2000(self, the_other: Optional[Const quantityColor]):
        """
        DeltaE2000 method.
        """
        pass

    def a_color(self):
        """
        aColor method.
        """
        pass

    # ... and 8 more methods