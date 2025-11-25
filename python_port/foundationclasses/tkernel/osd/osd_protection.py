"""
OSD_Protection

Python port of OCCT C++ class.
Original: src/*/OSD_Protection.cxx
"""

from typing import Optional, List, Tuple, Any

class OSD_Protection:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def set_system(self, priv: Const osdSingleprotection):
        """
        SetSystem method.
        """
        pass

    def set_user(self, priv: Const osdSingleprotection):
        """
        SetUser method.
        """
        pass

    def set_group(self, priv: Const osdSingleprotection):
        """
        SetGroup method.
        """
        pass

    def set_world(self, priv: Const osdSingleprotection):
        """
        SetWorld method.
        """
        pass

    def system(self):
        """
        System method.
        """
        pass

    def user(self):
        """
        User method.
        """
        pass

    def group(self):
        """
        Group method.
        """
        pass

    def world(self):
        """
        World method.
        """
        pass

    def add(self, a_prot: Optional[OsdSingleprotection], a_right: Const osdSingleprotection):
        """
        Add method.
        """
        pass

    def sub(self, a_prot: Optional[OsdSingleprotection], a_right: Const osdSingleprotection):
        """
        Sub method.
        """
        pass

    # ... and 1 more methods