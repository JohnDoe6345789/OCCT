"""
NCollection_BaseAllocator

Python port of OCCT C++ class.
Original: src/*/NCollection_BaseAllocator.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class NCollection_BaseAllocator(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def allocate(self, the_size: Const sizeT):
        """
        Allocate method.
        """
        pass

    def allocate_optimal(self, the_size: Const sizeT):
        """
        AllocateOptimal method.
        """
        pass

    def free(self, the_address: Optional[None]):
        """
        Free method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass