"""
TCollection_ExtendedString

Python port of OCCT C++ class.
Original: src/*/TCollection_ExtendedString.cxx
"""

from typing import Optional, List, Tuple, Any

class TCollection_ExtendedString:
    """
    Represents a OCCT class.
    """

    def __init__(self, astring: Const standardExtstring):
        """Initialize the class."""
        pass

    def __init__(self, the_string_utf: Optional[Const standardWidechar]):
        """Initialize the class."""
        pass

    def __init__(self, a_char: Const standardCharacter):
        """Initialize the class."""
        pass

    def __init__(self, a_char: Const standardExtcharacter):
        """Initialize the class."""
        pass

    def __init__(self, value: Const standardInteger):
        """Initialize the class."""
        pass

    def __init__(self, value: Const standardReal):
        """Initialize the class."""
        pass

    def __init__(self, astring: Optional[Const tcollectionExtendedstring]):
        """Initialize the class."""
        pass


    def assign_cat(self, other: Optional[Const tcollectionExtendedstring]):
        """
        AssignCat method.
        """
        pass

    def assign_cat(self, the_char: Const standardUtf16char):
        """
        AssignCat method.
        """
        pass

    def cat(self, other: Optional[Const tcollectionExtendedstring]):
        """
        Cat method.
        """
        pass

    def cat(self):
        """
        Cat method.
        """
        pass

    def clear(self):
        """
        Clear method.
        """
        pass

    def copy(self, fromwhere: Optional[Const tcollectionExtendedstring]):
        """
        Copy method.
        """
        pass

    def move(self, the_other: Optional[TcollectionExtendedstring]):
        """
        Move method.
        """
        pass

    def swap(self, the_other: Optional[TcollectionExtendedstring]):
        """
        Swap method.
        """
        pass

    def insert(self, where: Const standardInteger, what: Const standardExtcharacter):
        """
        Insert method.
        """
        pass

    def insert(self, where: Const standardInteger, what: Optional[Const tcollectionExtendedstring]):
        """
        Insert method.
        """
        pass

    # ... and 37 more methods