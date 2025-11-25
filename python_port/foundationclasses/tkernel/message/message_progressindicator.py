"""
Message_ProgressIndicator

Python port of OCCT C++ class.
Original: src/*/Message_ProgressIndicator.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Message_ProgressIndicator(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def start(self):
        """
        Start method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def show(self, the_scope: Optional[Const messageProgressscope], is_force: Const standardBoolean):
        """
        Show method.
        """
        pass

    def increment(self, the_step: Const standardReal, the_scope: Optional[Const messageProgressscope]):
        """
        Increment method.
        """
        pass