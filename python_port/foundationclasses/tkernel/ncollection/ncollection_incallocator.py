"""
NCollection_IncAllocator

Python port of OCCT C++ class.
Original: src/*/NCollection_IncAllocator.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import NcollectionBaseallocator

class NCollection_IncAllocator(NcollectionBaseallocator):
    """
    Represents a OCCT class.
    """

    def __init__(self, the_block_size: Const sizeT = ...  # THE_DEFAULT_BLOCK_SIZE):
        """Initialize the class."""
        pass


    def set_thread_safe(self, the_is_thread_safe: const bool = True):
        """
        SetThreadSafe method.
        """
        pass

    def reset(self, the_release_memory: const bool = False):
        """
        Reset method.
        """
        pass

    def increase_block_size(self):
        """
        increaseBlockSize method.
        """
        pass

    def reset_block(self, the_block: Optional[IBlock]):
        """
        resetBlock method.
        """
        pass

    def clean(self):
        """
        clean method.
        """
        pass