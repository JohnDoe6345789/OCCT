"""
OSD_File

Python port of OCCT C++ class.
Original: src/*/OSD_File.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import OsdFilenode

class OSD_File(OsdFilenode):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass

    def __init__(self, name: Optional[Const osdPath]):
        """Initialize the class."""
        pass


    def build(self, mode: Const osdOpenmode, protect: Optional[Const osdProtection]):
        """
        Build method.
        """
        pass

    def open(self, mode: Const osdOpenmode, protect: Optional[Const osdProtection]):
        """
        Open method.
        """
        pass

    def append(self, mode: Const osdOpenmode, protect: Optional[Const osdProtection]):
        """
        Append method.
        """
        pass

    def read(self, buffer: Optional[TcollectionAsciistring], nbyte: Const standardInteger):
        """
        Read method.
        """
        pass

    def write(self, the_buffer: Const standardAddress, the_nb_bytes: Const standardInteger):
        """
        Write method.
        """
        pass

    def seek(self, offset: Const standardInteger, whence: Const osdFromwhere):
        """
        Seek method.
        """
        pass

    def close(self):
        """
        Close method.
        """
        pass

    def is_at_end(self):
        """
        IsAtEnd method.
        """
        pass

    def kind_of_file(self):
        """
        KindOfFile method.
        """
        pass

    def build_temporary(self):
        """
        BuildTemporary method.
        """
        pass

    # ... and 9 more methods