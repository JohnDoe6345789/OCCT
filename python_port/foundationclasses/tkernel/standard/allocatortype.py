"""
AllocatorType

Python port of OCCT C++ class.
Original: src/*/AllocatorType.cxx
"""

from typing import Optional, List, Tuple, Any

class AllocatorType:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def get_allocator_type(self):
        """
        GetAllocatorType method.
        """
        pass

    def allocate(self, the_size: Const standardSize):
        """
        Allocate method.
        """
        pass

    def allocate_optimal(self, the_size: Const standardSize):
        """
        AllocateOptimal method.
        """
        pass

    def free(self, the_ptr: Const standardAddress):
        """
        Free method.
        """
        pass

    def free_aligned(self, the_ptr_aligned: Const standardAddress):
        """
        FreeAligned method.
        """
        pass

    def purge(self):
        """
        Purge method.
        """
        pass