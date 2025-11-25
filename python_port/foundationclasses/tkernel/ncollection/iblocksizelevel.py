"""
IBlockSizeLevel

Python port of OCCT C++ class.
Original: src/*/IBlockSizeLevel.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import unsigned short

class IBlockSizeLevel(unsigned short):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
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