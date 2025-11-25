"""
NCollection_UtfIterator

Python port of OCCT C++ class.
Original: src/*/NCollection_UtfIterator.cxx
"""

from typing import Optional, List, Tuple, Any

class NCollection_UtfIterator:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def advance_bytes_utf8(self):
        """
        AdvanceBytesUtf8 method.
        """
        pass

    def advance_bytes_utf16(self):
        """
        AdvanceBytesUtf16 method.
        """
        pass

    def advance_code_units_utf16(self):
        """
        AdvanceCodeUnitsUtf16 method.
        """
        pass

    def standard_integer(self):
        """
        Standard_Integer method.
        """
        pass

    def get_utf8(self, the_buffer: Optional[StandardUtf8char]):
        """
        GetUtf8 method.
        """
        pass

    def get_utf8(self, the_buffer: Optional[StandardUtf8uchar]):
        """
        GetUtf8 method.
        """
        pass

    def get_utf16(self, the_buffer: Optional[StandardUtf16char]):
        """
        GetUtf16 method.
        """
        pass

    def get_utf32(self, the_buffer: Optional[StandardUtf32char]):
        """
        GetUtf32 method.
        """
        pass

    def advance_bytes(self):
        """
        advanceBytes method.
        """
        pass

    def read_utf8(self):
        """
        readUTF8 method.
        """
        pass

    # ... and 9 more methods