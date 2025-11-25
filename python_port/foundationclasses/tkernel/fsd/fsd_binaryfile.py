"""
FSD_BinaryFile

Python port of OCCT C++ class.
Original: src/*/FSD_BinaryFile.cxx
"""

from typing import Optional, List, Tuple, Any
# from . import StorageBasedriver

class FSD_BinaryFile(StorageBasedriver):
    """
    Represents a OCCT class.
    """

    def __init__(self):
        """Initialize the class."""
        pass


    def is_good_file_type(self, a_name: Optional[Const tcollectionAsciistring]):
        """
        IsGoodFileType method.
        """
        pass

    def end_write_info_section(self, the_ostream: Optional[StandardOstream]):
        """
        EndWriteInfoSection method.
        """
        pass

    def begin_write_comment_section(self, the_ostream: Optional[StandardOstream]):
        """
        BeginWriteCommentSection method.
        """
        pass

    def end_write_comment_section(self, the_ostream: Optional[StandardOstream]):
        """
        EndWriteCommentSection method.
        """
        pass

    def type_section_size(self, the_istream: Optional[StandardIstream]):
        """
        TypeSectionSize method.
        """
        pass

    def root_section_size(self, the_istream: Optional[StandardIstream]):
        """
        RootSectionSize method.
        """
        pass

    def ref_section_size(self, the_istream: Optional[StandardIstream]):
        """
        RefSectionSize method.
        """
        pass

    def get_reference(self, the_istream: Optional[StandardIstream], a_value: Optional[int]):
        """
        GetReference method.
        """
        pass

    def get_integer(self, the_istream: Optional[StandardIstream], a_value: Optional[int]):
        """
        GetInteger method.
        """
        pass

    def destroy(self):
        """
        Destroy method.
        """
        pass

    # ... and 13 more methods