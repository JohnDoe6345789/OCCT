"""
NCollection_BaseSequence

Python port of OCCT C++ class.
Original: src/*/NCollection_BaseSequence.cxx
"""

from typing import Optional, List, Tuple, Any

class NCollection_BaseSequence:
    """
    Represents a OCCT class.
    """

    def __init__(self, other: Optional[Const ncollectionBasesequence]):
        """Initialize the class."""
        pass


    def is_empty(self):
        """
        IsEmpty method.
        """
        pass

    def clear_seq(self, f_del: NcollectionDelseqnode):
        """
        ClearSeq method.
        """
        pass

    def pappend(self):
        """
        PAppend method.
        """
        pass

    def pappend(self, s: Optional[NcollectionBasesequence]):
        """
        PAppend method.
        """
        pass

    def pprepend(self):
        """
        PPrepend method.
        """
        pass

    def pprepend(self, s: Optional[NcollectionBasesequence]):
        """
        PPrepend method.
        """
        pass

    def pinsert_after(self, the_position: Optional[Iterator]):
        """
        PInsertAfter method.
        """
        pass

    def pinsert_after(self, index: Const standardInteger):
        """
        PInsertAfter method.
        """
        pass

    def pinsert_after(self, index: Const standardInteger, s: Optional[NcollectionBasesequence]):
        """
        PInsertAfter method.
        """
        pass

    def psplit(self, index: Const standardInteger, sub: Optional[NcollectionBasesequence]):
        """
        PSplit method.
        """
        pass

    # ... and 3 more methods