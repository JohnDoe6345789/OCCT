"""
OSD

Python port of OCCT C++ class.
Original: src/*/OSD.cxx
"""

from typing import Optional, List, Tuple, Any

class OSD:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def set_floating_signal(self, the_floating_signal: bool):
        """
        SetFloatingSignal method.
        """
        pass

    def signal_mode(self):
        """
        SignalMode method.
        """
        pass

    def to_catch_floating_signals(self):
        """
        ToCatchFloatingSignals method.
        """
        pass

    def sec_sleep(self, the_seconds: Const standardInteger):
        """
        SecSleep method.
        """
        pass

    def milli_sec_sleep(self, the_milliseconds: Const standardInteger):
        """
        MilliSecSleep method.
        """
        pass

    def control_break(self):
        """
        ControlBreak method.
        """
        pass

    def signal_stack_trace_length(self):
        """
        SignalStackTraceLength method.
        """
        pass

    def set_signal_stack_trace_length(self, the_length: int):
        """
        SetSignalStackTraceLength method.
        """
        pass