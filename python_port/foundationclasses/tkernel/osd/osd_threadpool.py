"""
OSD_ThreadPool

Python port of OCCT C++ class.
Original: src/*/OSD_ThreadPool.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class OSD_ThreadPool(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self, the_nb_threads: int = -1):
        """Initialize the class."""
        pass


    def handle(self):
        """
        Handle method.
        """
        pass

    def upper_thread_index(self):
        """
        UpperThreadIndex method.
        """
        pass

    def is_in_use(self):
        """
        IsInUse method.
        """
        pass

    def init(self, the_nb_threads: int):
        """
        Init method.
        """
        pass

    def perform(self, the_thread_index: int):
        """
        Perform method.
        """
        pass

    def lock(self):
        """
        Lock method.
        """
        pass

    def free(self):
        """
        Free method.
        """
        pass

    def wake_up(self, the_job: Optional[JobInterface], the_to_catch_fpe: bool):
        """
        WakeUp method.
        """
        pass

    def wait_idle(self):
        """
        WaitIdle method.
        """
        pass

    def perform_thread(self):
        """
        performThread method.
        """
        pass

    # ... and 9 more methods