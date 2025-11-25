"""
NCollection_BaseList

Python port of OCCT C++ class.
Original: src/*/NCollection_BaseList.cxx
"""

from typing import Optional, List, Tuple, Any

class NCollection_BaseList:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def initialize(self):
        """
        Initialize method.
        """
        pass

    def more(self):
        """
        More method.
        """
        pass

    def is_empty(self):
        """
        IsEmpty method.
        """
        pass

    def pclear(self, f_del: NcollectionDellistnode):
        """
        PClear method.
        """
        pass

    def premove_first(self, f_del: NcollectionDellistnode):
        """
        PRemoveFirst method.
        """
        pass

    def premove(self, the_iter: Optional[Iterator], f_del: NcollectionDellistnode):
        """
        PRemove method.
        """
        pass

    def pinsert_before(self, the_node: Optional[NcollectionListnode], the_iter: Optional[Iterator]):
        """
        PInsertBefore method.
        """
        pass

    def pinsert_before(self, the_other: Optional[NcollectionBaselist], the_iter: Optional[Iterator]):
        """
        PInsertBefore method.
        """
        pass

    def pinsert_after(self, the_node: Optional[NcollectionListnode], the_iter: Optional[Iterator]):
        """
        PInsertAfter method.
        """
        pass

    def pinsert_after(self, the_other: Optional[NcollectionBaselist], the_iter: Optional[Iterator]):
        """
        PInsertAfter method.
        """
        pass