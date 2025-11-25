"""
EnumeratedThread

Python port of OCCT C++ class.
Original: src/*/EnumeratedThread.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import OsdThread

class EnumeratedThread(OsdThread):
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

    def run_thread(self, the_task: StandardAddress):
        """
        runThread method.
        """
        pass

    def launcher(self, the_pool: Optional[OsdThreadpool], the_max_threads: int = -1):
        """
        Launcher method.
        """
        pass

    def a_data(self):
        """
        aData method.
        """
        pass

    def release(self):
        """
        Release method.
        """
        pass

    def perform(self, the_job: Optional[JobInterface]):
        """
        perform method.
        """
        pass

    # ... and 4 more methods