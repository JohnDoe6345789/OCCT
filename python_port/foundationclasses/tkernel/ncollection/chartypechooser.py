"""
CharTypeChooser

Python port of OCCT C++ class.
Original: src/*/CharTypeChooser.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import std::conditional
# from . import StandardUtf8char
# from . import typename std::conditional
# from . import StandardUtf16char
# from . import typename std::conditional
# from . import StandardUtf32char
# from . import void>::type>::type>

class CharTypeChooser(std::conditional, StandardUtf8char, typename std::conditional, StandardUtf16char, typename std::conditional, StandardUtf32char, void>::type>::type>):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def read_utf8(self):
        """
        readUTF8 method.
        """
        pass

    def read_utf16(self):
        """
        readUTF16 method.
        """
        pass

    def read_next(self):
        """
        readNext method.
        """
        pass

    def read_next(self):
        """
        readNext method.
        """
        pass

    def advance_bytes(self):
        """
        advanceBytes method.
        """
        pass

    def advance_bytes(self):
        """
        advanceBytes method.
        """
        pass

    def advance_bytes_utf32(self):
        """
        AdvanceBytesUtf32 method.
        """
        pass

    def get_utf(self):
        """
        getUtf method.
        """
        pass

    def get_utf(self):
        """
        getUtf method.
        """
        pass

    def get_utf(self):
        """
        getUtf method.
        """
        pass