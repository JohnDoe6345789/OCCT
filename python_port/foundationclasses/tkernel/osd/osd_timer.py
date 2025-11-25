"""
OSD_Timer

Python port of OCCT C++ class.
Original: src/*/OSD_Timer.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import OsdChronometer

class OSD_Timer(OsdChronometer):
    """
    Represents a OCCT class.
    """

    def __init__(self, the_this_thread_only: bool = ...  # Standard_False):
        """Initialize the class."""
        pass


    def get_wall_clock_time(self):
        """
        GetWallClockTime method.
        """
        pass

    def reset(self, the_time_elapsed_sec: Const standardReal):
        """
        Reset method.
        """
        pass

    def elapsed_time(self):
        """
        ElapsedTime method.
        """
        pass