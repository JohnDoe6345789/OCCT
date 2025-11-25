"""
Standard_Dump

Python port of OCCT C++ class.
Original: src/*/Standard_Dump.cxx
"""

from typing import Optional, List, Tuple, Any

class Standard_Dump:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def text(self, the_stream: Optional[Const standardSstream]):
        """
        Text method.
        """
        pass

    def json_key_to_string(self, the_key: Const standardJsonkey):
        """
        JsonKeyToString method.
        """
        pass

    def json_key_length(self, the_key: Const standardJsonkey):
        """
        JsonKeyLength method.
        """
        pass

    def add_values_separator(self, the_ostream: Optional[StandardOstream]):
        """
        AddValuesSeparator method.
        """
        pass

    def dump_character_values(self, the_ostream: Optional[StandardOstream], the_count: int):
        """
        DumpCharacterValues method.
        """
        pass

    def dump_real_values(self, the_ostream: Optional[StandardOstream], the_count: int):
        """
        DumpRealValues method.
        """
        pass