"""
Message_MsgFile

Python port of OCCT C++ class.
Original: src/*/Message_MsgFile.cxx
"""

from typing import Optional, List, Tuple, Any

class Message_MsgFile:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def load_file(self, the_fname: Const standardCstring):
        """
        LoadFile method.
        """
        pass

    def has_msg(self, key: Optional[Const tcollectionAsciistring]):
        """
        HasMsg method.
        """
        pass

    def msg(self, key: Const standardCstring):
        """
        Msg method.
        """
        pass

    def msg(self, key: Optional[Const tcollectionAsciistring]):
        """
        Msg method.
        """
        pass