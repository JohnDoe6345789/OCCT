"""
Storage_HeaderData

Python port of OCCT C++ class.
Original: src/*/Storage_HeaderData.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Storage_HeaderData(StandardTransient):
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

    def creation_date(self):
        """
        CreationDate method.
        """
        pass

    def storage_version(self):
        """
        StorageVersion method.
        """
        pass

    def schema_version(self):
        """
        SchemaVersion method.
        """
        pass

    def schema_name(self):
        """
        SchemaName method.
        """
        pass

    def set_application_version(self, a_version: Optional[Const tcollectionAsciistring]):
        """
        SetApplicationVersion method.
        """
        pass

    def application_version(self):
        """
        ApplicationVersion method.
        """
        pass

    def set_application_name(self, a_name: Optional[Const tcollectionExtendedstring]):
        """
        SetApplicationName method.
        """
        pass

    def application_name(self):
        """
        ApplicationName method.
        """
        pass

    def set_data_type(self, a_type: Optional[Const tcollectionExtendedstring]):
        """
        SetDataType method.
        """
        pass

    # ... and 16 more methods