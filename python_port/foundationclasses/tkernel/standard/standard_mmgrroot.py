"""
Standard_MMgrRoot

Python port of OCCT C++ class.
Original: src/*/Standard_MMgrRoot.cxx
"""

from typing import Optional, List, Tuple, Any

class Standard_MMgrRoot:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def allocate(self, the_size: Const standardSize):
        """
        Allocate method.
        """
        pass

    def free(self, the_ptr: StandardAddress):
        """
        Free method.
        """
        pass

    def purge(self, is_destroyed: bool = ...  # Standard_False):
        """
        Purge method.
        """
        pass