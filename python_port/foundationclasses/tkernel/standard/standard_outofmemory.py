"""
Standard_OutOfMemory

Python port of OCCT C++ class.
Original: src/*/Standard_OutOfMemory.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardProgramerror

class Standard_OutOfMemory(StandardProgramerror):
    """
    Represents a OCCT class.
    """

    def __init__(self, the_message: Const standardCstring = 0):
        """Initialize the class."""
        pass


    def raise(self, the_message: Const standardCstring = ""):
        """
        Raise method.
        """
        pass

    def raise(self, the_message: Optional[StandardSstream]):
        """
        Raise method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass