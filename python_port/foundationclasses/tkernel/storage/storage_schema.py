"""
Storage_Schema

Python port of OCCT C++ class.
Original: src/*/Storage_Schema.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Storage_Schema(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def set_version(self, a_version: Optional[Const tcollectionAsciistring]):
        """
        SetVersion method.
        """
        pass

    def version(self):
        """
        Version method.
        """
        pass

    def set_name(self, a_schema_name: Optional[Const tcollectionAsciistring]):
        """
        SetName method.
        """
        pass

    def name(self):
        """
        Name method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def icreation_date(self):
        """
        ICreationDate method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def remove_read_unknown_type_call_back(self, a_type_name: Optional[Const tcollectionAsciistring]):
        """
        RemoveReadUnknownTypeCallBack method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def clear_call_back_list(self):
        """
        ClearCallBackList method.
        """
        pass

    # ... and 11 more methods