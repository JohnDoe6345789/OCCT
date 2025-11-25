"""
NCollection_AccAllocator

Python port of OCCT C++ class.
Original: src/*/NCollection_AccAllocator.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import NcollectionBaseallocator

class NCollection_AccAllocator(NcollectionBaseallocator):
    """
    Represents a OCCT class.
    """

    def __init__(self, the_block_size: Const sizeT = ...  # DefaultBlockSize):
        """Initialize the class."""
        pass


    def allocate_optimal(self):
        """
        AllocateOptimal method.
        """
        pass

    def allocate_new_block(self, the_size: Const standardSize):
        """
        allocateNewBlock method.
        """
        pass