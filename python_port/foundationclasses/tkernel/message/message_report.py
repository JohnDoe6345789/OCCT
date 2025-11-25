"""
Message_Report

Python port of OCCT C++ class.
Original: src/*/Message_Report.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StandardTransient

class Message_Report(StandardTransient):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def add_alert(self, the_gravity: MessageGravity):
        """
        AddAlert method.
        """
        pass

    def get_alerts(self, the_gravity: MessageGravity):
        """
        GetAlerts method.
        """
        pass

    def has_alert(self):
        """
        HasAlert method.
        """
        pass

    def is_active_in_messenger(self):
        """
        IsActiveInMessenger method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def handle(self):
        """
        Handle method.
        """
        pass

    def add_level(self, the_level: Optional[MessageLevel], the_name: Optional[Const tcollectionAsciistring]):
        """
        AddLevel method.
        """
        pass

    def remove_level(self, the_level: Optional[MessageLevel]):
        """
        RemoveLevel method.
        """
        pass

    def clear(self):
        """
        Clear method.
        """
        pass

    def clear(self, the_gravity: MessageGravity):
        """
        Clear method.
        """
        pass

    # ... and 10 more methods