"""
OSD_Thread

Python port of OCCT C++ class.
Original: src/*/OSD_Thread.cxx
"""

from typing import Optional, List, Tuple, Any

class OSD_Thread:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass

    def __init__(self, func: Optional[Const osdThreadfunction]):
        """Initialize the class."""
        pass

    def __init__(self, other: Optional[Const osdThread]):
        """Initialize the class."""
        pass


    def assign(self, other: Optional[Const osdThread]):
        """
        Assign method.
        """
        pass

    def set_priority(self, the_priority: Const standardInteger):
        """
        SetPriority method.
        """
        pass

    def set_function(self, func: Optional[Const osdThreadfunction]):
        """
        SetFunction method.
        """
        pass

    def detach(self):
        """
        Detach method.
        """
        pass

    def wait(self):
        """
        Wait method.
        """
        pass

    def wait(self, the_result: Optional[StandardAddress]):
        """
        Wait method.
        """
        pass

    def wait(self, time: Const standardInteger, the_result: Optional[StandardAddress]):
        """
        Wait method.
        """
        pass

    def get_id(self):
        """
        GetId method.
        """
        pass

    def current(self):
        """
        Current method.
        """
        pass