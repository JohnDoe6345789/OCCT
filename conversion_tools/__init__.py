"""
OCCT C++ to Python Conversion Tooling

This package provides automated tools for converting OCCT C/C++ code to Python.

Main modules:
- cpp_parser: Parses C++ headers and extracts class definitions
- python_generator: Generates Python stub files from C++ classes
- conversion_runner: Main orchestration script for conversions
"""

__version__ = '1.0.0'
__author__ = 'OCCT Contributors'

from .cpp_parser import CppHeaderParser, SourceAnalyzer, CppClass, CppMethod
from .python_generator import PythonClassGenerator, PythonMethodGenerator

__all__ = [
    'CppHeaderParser',
    'SourceAnalyzer',
    'CppClass',
    'CppMethod',
    'PythonClassGenerator',
    'PythonMethodGenerator',
]
