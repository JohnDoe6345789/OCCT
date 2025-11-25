"""
Block

Python port of OCCT C++ class.
Original: src/*/Block.cxx
"""

from typing import Optional, List, Tuple, Any

class Block:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def restart(self):
        """
        Restart method.
        """
        pass

    def next(self):
        """
        Next method.
        """
        pass

    def iterator(self, the_array: Optional[Const ncollectionSparsearraybase] = ...  # nullptr):
        """
        Iterator method.
        """
        pass

    def init(self, the_array: Optional[Const ncollectionSparsearraybase]):
        """
        init method.
        """
        pass

    def value(self):
        """
        value method.
        """
        pass

    def assign(self, the_other: Optional[Const ncollectionSparsearraybase]):
        """
        assign method.
        """
        pass

    def create_item(self, the_address: StandardAddress, the_other: StandardAddress):
        """
        createItem method.
        """
        pass

    def destroy_item(self, the_address: StandardAddress):
        """
        destroyItem method.
        """
        pass

    def copy_item(self, the_address: StandardAddress, the_other: StandardAddress):
        """
        copyItem method.
        """
        pass

    def alloc_data(self, i_block: Const standardSize):
        """
        allocData method.
        """
        pass

    # ... and 1 more methods