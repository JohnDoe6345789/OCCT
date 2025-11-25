"""
FunctorInterface

Python port of OCCT C++ class.
Original: src/*/FunctorInterface.cxx
"""

from typing import Optional, List, Tuple, Any

class FunctorInterface:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def operator(self):
        """
        operator method.
        """
        pass

    def to_use_occt_threads(self):
        """
        ToUseOcctThreads method.
        """
        pass

    def set_use_occt_threads(self, the_to_use_occt: bool):
        """
        SetUseOcctThreads method.
        """
        pass

    def nb_logical_processors(self):
        """
        NbLogicalProcessors method.
        """
        pass

    def it(self):
        """
        it method.
        """
        pass

    def a_begin(self):
        """
        aBegin method.
        """
        pass

    def a_end(self):
        """
        aEnd method.
        """
        pass

    def it(self):
        """
        it method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def a_pool_launcher(self):
        """
        aPoolLauncher method.
        """
        pass

    # ... and 2 more methods