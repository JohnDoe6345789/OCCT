#!/usr/bin/env python3
"""
Python Stub Generator for OCCT classes.

Converts C++ class definitions to Python stub files with proper structure.
"""

from pathlib import Path
from typing import Dict, List, Optional
from cpp_parser import CppClass, CppMethod, CppParameter


class PythonMethodGenerator:
    """Generates Python method signatures from C++ definitions."""

    @staticmethod
    def generate_method_signature(method: CppMethod, include_docstring: bool = True) -> str:
        """Convert C++ method to Python method signature."""
        params = PythonMethodGenerator._convert_parameters(method.parameters)
        
        if method.is_constructor:
            method_def = f"def __init__(self{', ' + params if params else ''}):"
        elif method.is_destructor:
            method_def = "def __del__(self):"
        else:
            # Convert C++ names to Python snake_case
            py_name = PythonMethodGenerator._to_snake_case(method.name)
            method_def = f"def {py_name}(self{', ' + params if params else ''}):"
        
        return method_def

    @staticmethod
    def _convert_parameters(params: List[CppParameter]) -> str:
        """Convert C++ parameters to Python."""
        py_params = []
        for param in params:
            py_type = PythonMethodGenerator._convert_cpp_type(param.type_)
            py_name = PythonMethodGenerator._to_snake_case(param.name)
            
            if param.default_value:
                default = PythonMethodGenerator._convert_cpp_value(param.default_value)
                py_params.append(f"{py_name}: {py_type} = {default}")
            else:
                py_params.append(f"{py_name}: {py_type}")
        
        return ", ".join(py_params)

    @staticmethod
    def _convert_cpp_type(cpp_type: str) -> str:
        """Convert C++ type to Python type hint."""
        cpp_type = cpp_type.strip()
        
        # Handle pointers and references
        is_pointer = '*' in cpp_type
        is_ref = '&' in cpp_type
        cpp_type = cpp_type.replace('*', '').replace('&', '').strip()
        
        # Map standard types
        type_map = {
            'Standard_Real': 'float',
            'Standard_Integer': 'int',
            'Standard_Boolean': 'bool',
            'void': 'None',
            'double': 'float',
            'int': 'int',
            'bool': 'bool',
            'float': 'float',
            'char': 'str',
            'string': 'str',
            'std::string': 'str',
        }
        
        if cpp_type in type_map:
            py_type = type_map[cpp_type]
        else:
            # For custom classes, convert to PascalCase
            py_type = PythonMethodGenerator._cpp_class_to_py(cpp_type)
        
        if is_pointer or is_ref:
            py_type = f"Optional[{py_type}]"
        
        return py_type

    @staticmethod
    def _cpp_class_to_py(cpp_class: str) -> str:
        """Convert C++ class name to Python class name."""
        # Handle template types
        if '<' in cpp_class:
            cpp_class = cpp_class[:cpp_class.index('<')]
        
        # Remove common prefixes and suffixes
        cpp_class = cpp_class.strip()
        
        # For Toolkit_ClassName style, convert to ToolkitClassName
        parts = cpp_class.split('_')
        if len(parts) > 1:
            # It's a Package_Class style name
            return ''.join(p.capitalize() for p in parts)
        
        return cpp_class

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert CamelCase to snake_case."""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0 and name[i-1].islower():
                result.append('_')
            result.append(char.lower())
        return ''.join(result)

    @staticmethod
    def _convert_cpp_value(value: str) -> str:
        """Convert C++ default value to Python."""
        value = value.strip()
        
        if value in ('true', 'false'):
            return value.capitalize()
        if value.replace('-', '').isdigit():
            return value
        if value.startswith('"') or value.startswith("'"):
            return value
        
        # Default: pass through
        return f"...  # {value}"


class PythonClassGenerator:
    """Generates Python class files from C++ classes."""

    def __init__(self, output_root: Path, cpp_class: CppClass):
        self.output_root = output_root
        self.cpp_class = cpp_class

    def generate_class_file(self) -> str:
        """Generate complete Python class file content."""
        lines = []
        
        # Header
        lines.append('"""')
        lines.append(f'{self.cpp_class.name}')
        lines.append('')
        lines.append(f'Python port of OCCT C++ class.')
        lines.append(f'Original: src/*/{self.cpp_class.name}.cxx')
        lines.append('"""')
        lines.append('')
        
        # Imports
        lines.extend(self._generate_imports())
        lines.append('')
        
        # Class definition
        lines.extend(self._generate_class_definition())
        
        return '\n'.join(lines)

    def _generate_imports(self) -> List[str]:
        """Generate import statements."""
        imports = ['from typing import Optional, List, Tuple, Any']
        
        # Add imports for base classes
        for base in self.cpp_class.base_classes:
            py_base = PythonMethodGenerator._cpp_class_to_py(base)
            # This is simplified - in reality, we'd need to track where these are defined
            imports.append(f'# from . import {py_base}')
        
        return imports

    def _generate_class_definition(self) -> List[str]:
        """Generate class definition and methods."""
        lines = []
        
        # Class header
        base_classes = ', '.join(
            PythonMethodGenerator._cpp_class_to_py(b) 
            for b in self.cpp_class.base_classes
        )
        
        if base_classes:
            lines.append(f'class {self.cpp_class.name}({base_classes}):')
        else:
            lines.append(f'class {self.cpp_class.name}:')
        
        lines.append('    """')
        lines.append('    Represents a OCCT class.')
        lines.append('    """')
        lines.append('')
        
        # Constructor
        constructors = self.cpp_class.constructors()
        if constructors:
            for i, ctor in enumerate(constructors):
                if i > 0:
                    lines.append('')
                lines.append(f'    {PythonMethodGenerator.generate_method_signature(ctor)}')
                lines.append('        """Initialize the class."""')
                lines.append('        pass')
        else:
            lines.append('    def __init__(self):')
            lines.append('        """Initialize the class."""')
            lines.append('        pass')
        
        lines.append('')
        
        # Methods
        public_methods = self.cpp_class.public_methods()
        public_methods = [m for m in public_methods if not m.is_constructor and not m.is_destructor]
        
        for method in public_methods[:10]:  # Limit to first 10 for stub
            lines.append('')
            lines.append(f'    {PythonMethodGenerator.generate_method_signature(method)}')
            lines.append('        """')
            lines.append(f'        {method.name} method.')
            lines.append('        """')
            lines.append('        pass')
        
        if len(public_methods) > 10:
            lines.append('')
            lines.append(f'    # ... and {len(public_methods) - 10} more methods')
        
        return lines

    def save(self, filepath: Path) -> None:
        """Save generated class to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        content = self.generate_class_file()
        filepath.write_text(content, encoding='utf-8')


class DirectoryStructureGenerator:
    """Generates Python package directory structure."""

    @staticmethod
    def create_package_structure(
        root: Path,
        module: str,
        toolkit: str,
        package: Optional[str] = None
    ) -> Path:
        """Create python_port package directory."""
        module_dir = root / module.lower()
        toolkit_dir = module_dir / toolkit.lower()
        
        if package:
            pkg_dir = toolkit_dir / package.lower()
        else:
            pkg_dir = toolkit_dir
        
        pkg_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        DirectoryStructureGenerator._create_init_file(module_dir)
        DirectoryStructureGenerator._create_init_file(toolkit_dir)
        DirectoryStructureGenerator._create_init_file(pkg_dir)
        
        return pkg_dir

    @staticmethod
    def _create_init_file(directory: Path) -> None:
        """Create __init__.py if it doesn't exist."""
        init_file = directory / '__init__.py'
        if not init_file.exists():
            init_file.write_text('', encoding='utf-8')
