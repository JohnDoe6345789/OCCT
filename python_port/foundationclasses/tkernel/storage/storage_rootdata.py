"""
Storage_RootData

Python port of OCCT C++ class.
Original: src/*/Storage_RootData.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Storage_RootData(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def read(self):
        """
        Read method.
        """
        pass

    def number_of_roots(self):
        """
        NumberOfRoots method.
        """
        pass

    def add_root(self):
        """
        AddRoot method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def is_root(self, a_name: Optional[Const tcollectionAsciistring]):
        """
        IsRoot method.
        """
        pass

    def remove_root(self, a_name: Optional[Const tcollectionAsciistring]):
        """
        RemoveRoot method.
        """
        pass

    def error_status(self):
        """
        ErrorStatus method.
        """
        pass

    def error_status_extension(self):
        """
        ErrorStatusExtension method.
        """
        pass

    def clear_error_status(self):
        """
        ClearErrorStatus method.
        """
        pass

    # ... and 3 more methods