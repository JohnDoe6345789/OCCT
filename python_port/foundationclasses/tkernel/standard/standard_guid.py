"""
Standard_GUID

Python port of OCCT C++ class.
Original: src/*/Standard_GUID.cxx
"""

from typing import Optional, List, Tuple, Any

class Standard_GUID:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass

    def __init__(self, a_guid: Const standardCstring):
        """Initialize the class."""
        pass

    def __init__(self, a_guid: Const standardExtstring):
        """Initialize the class."""
        pass

    def __init__(self, a_guid: Optional[Const standardUuid]):
        """Initialize the class."""
        pass

    def __init__(self, a_guid: Optional[Const standardGuid]):
        """Initialize the class."""
        pass


    def to_uuid(self):
        """
        ToUUID method.
        """
        pass

    def to_cstring(self, a_str_guid: Const standardPcharacter):
        """
        ToCString method.
        """
        pass

    def to_ext_string(self, a_str_guid: Const standardPextcharacter):
        """
        ToExtString method.
        """
        pass

    def is_same(self, uid: Optional[Const standardGuid]):
        """
        IsSame method.
        """
        pass

    def is_same(self):
        """
        IsSame method.
        """
        pass

    def is_not_same(self, uid: Optional[Const standardGuid]):
        """
        IsNotSame method.
        """
        pass

    def is_not_same(self):
        """
        IsNotSame method.
        """
        pass

    def assign(self, uid: Optional[Const standardGuid]):
        """
        Assign method.
        """
        pass

    def assign(self, uid: Optional[Const standardUuid]):
        """
        Assign method.
        """
        pass

    def shallow_dump(self, a_stream: Optional[StandardOstream]):
        """
        ShallowDump method.
        """
        pass

    # ... and 1 more methods