"""
Storage_TypeData

Python port of OCCT C++ class.
Original: src/*/Storage_TypeData.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Storage_TypeData(StandardTransient):
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

    def number_of_types(self):
        """
        NumberOfTypes method.
        """
        pass

    def type(self, a_type_num: Const standardInteger):
        """
        Type method.
        """
        pass

    def type(self, a_type_name: Optional[Const tcollectionAsciistring]):
        """
        Type method.
        """
        pass

    def is_type(self, a_name: Optional[Const tcollectionAsciistring]):
        """
        IsType method.
        """
        pass

    def handle(self):
        """
        Handle method.
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

    def clear(self):
        """
        Clear method.
        """
        pass

    # ... and 2 more methods