"""
Standard_Mutex

Python port of OCCT C++ class.
Original: src/*/Standard_Mutex.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardErrorhandler::callback

class Standard_Mutex(StandardErrorhandler::callback):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def lock(self):
        """
        Lock method.
        """
        pass

    def try_lock(self):
        """
        TryLock method.
        """
        pass

    def unlock(self):
        """
        Unlock method.
        """
        pass

    def pthread_mutex_unlock(self):
        """
        pthread_mutex_unlock method.
        """
        pass