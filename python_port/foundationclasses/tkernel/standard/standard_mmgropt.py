"""
Standard_MMgrOpt

Python port of OCCT C++ class.
Original: src/*/Standard_MMgrOpt.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardMmgrroot

class Standard_MMgrOpt(StandardMmgrroot):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def allocate(self, a_size: Const standardSize):
        """
        Allocate method.
        """
        pass

    def free(self, the_ptr: StandardAddress):
        """
        Free method.
        """
        pass

    def purge(self, is_destroyed: bool):
        """
        Purge method.
        """
        pass

    def set_call_back_function(self, p_func: TPCallBackFunc):
        """
        SetCallBackFunction method.
        """
        pass

    def initialize(self):
        """
        Initialize method.
        """
        pass

    def alloc_memory(self, a_size: Optional[StandardSize]):
        """
        AllocMemory method.
        """
        pass

    def free_memory(self, a_ptr: StandardAddress, a_size: Const standardSize):
        """
        FreeMemory method.
        """
        pass

    def free_pools(self):
        """
        FreePools method.
        """
        pass