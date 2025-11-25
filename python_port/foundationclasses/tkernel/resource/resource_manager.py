"""
Resource_Manager

Python port of OCCT C++ class.
Original: src/*/Resource_Manager.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Resource_Manager(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def save(self):
        """
        Save method.
        """
        pass

    def find(self, a_resource: Const standardCstring):
        """
        Find method.
        """
        pass

    def integer(self, a_resource_name: Const standardCstring):
        """
        Integer method.
        """
        pass

    def real(self, a_resource_name: Const standardCstring):
        """
        Real method.
        """
        pass

    def value(self, a_resource_name: Const standardCstring):
        """
        Value method.
        """
        pass

    def ext_value(self, a_resource_name: Const standardCstring):
        """
        ExtValue method.
        """
        pass