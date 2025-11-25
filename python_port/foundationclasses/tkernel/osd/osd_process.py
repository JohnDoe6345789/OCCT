"""
OSD_Process

Python port of OCCT C++ class.
Original: src/*/OSD_Process.cxx
"""

from typing import Optional, List, Tuple, Any

class OSD_Process:
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def executable_path(self):
        """
        ExecutablePath method.
        """
        pass

    def executable_folder(self):
        """
        ExecutableFolder method.
        """
        pass

    def terminal_type(self, name: Optional[TcollectionAsciistring]):
        """
        TerminalType method.
        """
        pass

    def system_date(self):
        """
        SystemDate method.
        """
        pass

    def user_name(self):
        """
        UserName method.
        """
        pass

    def is_super_user(self):
        """
        IsSuperUser method.
        """
        pass

    def process_id(self):
        """
        ProcessId method.
        """
        pass

    def current_directory(self):
        """
        CurrentDirectory method.
        """
        pass

    def set_current_directory(self, where: Optional[Const osdPath]):
        """
        SetCurrentDirectory method.
        """
        pass

    def failed(self):
        """
        Failed method.
        """
        pass

    # ... and 3 more methods