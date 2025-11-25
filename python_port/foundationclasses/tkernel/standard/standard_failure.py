"""
Standard_Failure

Python port of OCCT C++ class.
Original: src/*/Standard_Failure.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Standard_Failure(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass

    def __init__(self, f: Optional[Const standardFailure]):
        """Initialize the class."""
        pass

    def __init__(self, the_desc: Const standardCstring):
        """Initialize the class."""
        pass


    def print(self, the_stream: Optional[StandardOstream]):
        """
        Print method.
        """
        pass

    def get_message_string(self):
        """
        GetMessageString method.
        """
        pass

    def set_message_string(self, the_message: Const standardCstring):
        """
        SetMessageString method.
        """
        pass

    def get_stack_string(self):
        """
        GetStackString method.
        """
        pass

    def set_stack_string(self, the_stack: Const standardCstring):
        """
        SetStackString method.
        """
        pass

    def reraise(self):
        """
        Reraise method.
        """
        pass

    def reraise(self, a_message: Const standardCstring):
        """
        Reraise method.
        """
        pass

    def reraise(self, a_reason: Optional[Const standardSstream]):
        """
        Reraise method.
        """
        pass

    def raise(self, a_message: Const standardCstring = ""):
        """
        Raise method.
        """
        pass

    def raise(self, a_reason: Optional[Const standardSstream]):
        """
        Raise method.
        """
        pass

    # ... and 8 more methods