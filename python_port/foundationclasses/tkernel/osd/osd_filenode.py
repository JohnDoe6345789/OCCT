"""
OSD_FileNode

Python port of OCCT C++ class.
Original: src/*/OSD_FileNode.cxx
"""

from typing import Optional, List, Tuple, Any

class OSD_FileNode:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass

    def __init__(self, name: Optional[Const osdPath]):
        """Initialize the class."""
        pass


    def path(self, name: Optional[OsdPath]):
        """
        Path method.
        """
        pass

    def set_path(self, name: Optional[Const osdPath]):
        """
        SetPath method.
        """
        pass

    def exists(self):
        """
        Exists method.
        """
        pass

    def remove(self):
        """
        Remove method.
        """
        pass

    def move(self, new_path: Optional[Const osdPath]):
        """
        Move method.
        """
        pass

    def copy(self, to_path: Optional[Const osdPath]):
        """
        Copy method.
        """
        pass

    def protection(self):
        """
        Protection method.
        """
        pass

    def set_protection(self, prot: Optional[Const osdProtection]):
        """
        SetProtection method.
        """
        pass

    def access_moment(self):
        """
        AccessMoment method.
        """
        pass

    def creation_moment(self):
        """
        CreationMoment method.
        """
        pass

    # ... and 4 more methods