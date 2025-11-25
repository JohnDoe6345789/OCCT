"""
Message_AttributeMeter

Python port of OCCT C++ class.
Original: src/*/Message_AttributeMeter.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import MessageAttribute

class Message_AttributeMeter(MessageAttribute):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def has_metric(self, the_metric: Optional[Const messageMetrictype]):
        """
        HasMetric method.
        """
        pass

    def is_metric_valid(self, the_metric: Optional[Const messageMetrictype]):
        """
        IsMetricValid method.
        """
        pass

    def start_value(self, the_metric: Optional[Const messageMetrictype]):
        """
        StartValue method.
        """
        pass

    def stop_value(self, the_metric: Optional[Const messageMetrictype]):
        """
        StopValue method.
        """
        pass