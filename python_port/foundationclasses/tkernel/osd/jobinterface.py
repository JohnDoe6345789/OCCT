"""
JobInterface

Python port of OCCT C++ class.
Original: src/*/JobInterface.cxx
"""

from typing import Optional, List, Tuple, Any

class JobInterface:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
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

    # ... and 5 more methods