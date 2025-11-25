"""
is_integer

Python port of OCCT C++ class.
Original: src/*/is_integer.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import Std::integralConstant
# from . import Opencascade::std::isIntegral
# from . import bool>::value>

class is_integer(Std::integralConstant, Opencascade::std::isIntegral, bool>::value>):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass
