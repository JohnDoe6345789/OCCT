"""
OSD_Path

Python port of OCCT C++ class.
Original: src/*/OSD_Path.cxx
"""

from typing import Optional, List, Tuple, Any

class OSD_Path:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def expanded_name(self, a_name: Optional[TcollectionAsciistring]):
        """
        ExpandedName method.
        """
        pass

    def up_trek(self):
        """
        UpTrek method.
        """
        pass

    def down_trek(self, a_name: Optional[Const tcollectionAsciistring]):
        """
        DownTrek method.
        """
        pass

    def trek_length(self):
        """
        TrekLength method.
        """
        pass

    def remove_atrek(self, where: Const standardInteger):
        """
        RemoveATrek method.
        """
        pass

    def remove_atrek(self, a_name: Optional[Const tcollectionAsciistring]):
        """
        RemoveATrek method.
        """
        pass

    def trek_value(self, where: Const standardInteger):
        """
        TrekValue method.
        """
        pass

    def node(self):
        """
        Node method.
        """
        pass

    def user_name(self):
        """
        UserName method.
        """
        pass

    def password(self):
        """
        Password method.
        """
        pass

    # ... and 13 more methods