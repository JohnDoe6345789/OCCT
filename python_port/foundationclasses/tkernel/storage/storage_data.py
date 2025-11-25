"""
Storage_Data

Python port of OCCT C++ class.
Original: src/*/Storage_Data.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Storage_Data(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def error_status(self):
        """
        ErrorStatus method.
        """
        pass

    def clear_error_status(self):
        """
        ClearErrorStatus method.
        """
        pass

    def error_status_extension(self):
        """
        ErrorStatusExtension method.
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

    # ... and 25 more methods