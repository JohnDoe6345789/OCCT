#!/usr/bin/env python3
"""
C/C++ Parser for OCCT source files.

Extracts class definitions, methods, and dependencies from C++ headers.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional


@dataclass
class CppParameter:
    """Represents a C++ function parameter."""
    name: str
    type_: str
    default_value: Optional[str] = None

    def __repr__(self) -> str:
        default = f" = {self.default_value}" if self.default_value else ""
        return f"{self.type_} {self.name}{default}"


@dataclass
class CppMethod:
    """Represents a C++ class method."""
    name: str
    return_type: str
    parameters: List[CppParameter] = field(default_factory=list)
    is_const: bool = False
    is_virtual: bool = False
    is_static: bool = False
    access: str = "public"  # public, private, protected
    is_constructor: bool = False
    is_destructor: bool = False

    def __repr__(self) -> str:
        params = ", ".join(str(p) for p in self.parameters)
        const = " const" if self.is_const else ""
        return f"{self.return_type} {self.name}({params}){const}"


@dataclass
class CppClass:
    """Represents a C++ class definition."""
    name: str
    filename: str
    base_classes: List[str] = field(default_factory=list)
    methods: List[CppMethod] = field(default_factory=list)
    members: Dict[str, str] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    namespace: Optional[str] = None

    def public_methods(self) -> List[CppMethod]:
        return [m for m in self.methods if m.access == "public"]

    def constructors(self) -> List[CppMethod]:
        return [m for m in self.methods if m.is_constructor]

    def destructor(self) -> Optional[CppMethod]:
        for m in self.methods:
            if m.is_destructor:
                return m
        return None


class CppHeaderParser:
    """Parses C++ header files to extract class information."""

    def __init__(self, header_path: Path):
        self.header_path = header_path
        self.content = header_path.read_text(encoding='utf-8', errors='ignore')
        self.classes: Dict[str, CppClass] = {}

    def parse(self) -> Dict[str, CppClass]:
        """Parse the header file and extract all classes."""
        # Remove comments
        self._remove_comments()
        # Find namespace if any
        namespace = self._find_namespace()
        # Find all classes
        self._parse_classes(namespace)
        return self.classes

    def _remove_comments(self) -> None:
        """Remove C++ comments from content."""
        # Remove single-line comments
        self.content = re.sub(r'//.*?$', '', self.content, flags=re.MULTILINE)
        # Remove multi-line comments
        self.content = re.sub(r'/\*.*?\*/', '', self.content, flags=re.DOTALL)

    def _find_namespace(self) -> Optional[str]:
        """Find the primary namespace."""
        match = re.search(r'namespace\s+(\w+)', self.content)
        return match.group(1) if match else None

    def _parse_classes(self, namespace: Optional[str]) -> None:
        """Find and parse all class definitions."""
        # Pattern to find class/struct definitions
        class_pattern = r'(?:class|struct)\s+(\w+)(?:\s*:\s*([^{]+?))?\s*\{'
        
        for match in re.finditer(class_pattern, self.content):
            class_name = match.group(1)
            bases_str = match.group(2) or ""
            
            base_classes = [b.strip() for b in bases_str.split(',') if b.strip()]
            base_classes = [self._clean_base_class(b) for b in base_classes]
            
            cpp_class = CppClass(
                name=class_name,
                filename=str(self.header_path),
                base_classes=base_classes,
                namespace=namespace
            )
            
            # Extract methods (simplified - finds public/private keywords and method signatures)
            self._extract_methods(cpp_class, match.start())
            self.classes[class_name] = cpp_class

    def _clean_base_class(self, base: str) -> str:
        """Clean up base class specification."""
        # Remove access specifier (public, private, protected)
        base = re.sub(r'\b(public|private|protected)\s+', '', base)
        # Remove virtual keyword
        base = re.sub(r'\bvirtual\s+', '', base)
        return base.strip()

    def _extract_methods(self, cpp_class: CppClass, class_start: int) -> None:
        """Extract method declarations from class body."""
        # Find the class body (simplified - looks for methods after class name)
        # This is a simplified parser; a full C++ parser would be more complex
        
        # Look for method patterns: return_type method_name(params)
        method_pattern = r'(\w+(?:\*|&)?)\s+(\w+)\s*\((.*?)\)\s*(?:const)?\s*(?:override)?\s*(?:;|=)'
        
        for match in re.finditer(method_pattern, self.content[class_start:]):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)
            
            is_constructor = method_name == cpp_class.name
            is_destructor = method_name.startswith('~')
            
            parameters = self._parse_parameters(params_str)
            
            method = CppMethod(
                name=method_name,
                return_type=return_type,
                parameters=parameters,
                is_constructor=is_constructor,
                is_destructor=is_destructor
            )
            cpp_class.methods.append(method)

    def _parse_parameters(self, params_str: str) -> List[CppParameter]:
        """Parse method parameters."""
        if not params_str.strip():
            return []
        
        parameters = []
        # Split by comma, but be careful with nested templates
        param_parts = re.split(r',(?![^<]*>)', params_str)
        
        for param in param_parts:
            param = param.strip()
            if not param:
                continue
            
            # Pattern: type name [= default]
            match = re.match(r'([\w\s\*&<>,]+?)\s+(\w+)(?:\s*=\s*(.+?))?$', param)
            if match:
                param_type = match.group(1).strip()
                param_name = match.group(2).strip()
                default = match.group(3).strip() if match.group(3) else None
                
                parameters.append(CppParameter(
                    name=param_name,
                    type_=param_type,
                    default_value=default
                ))
        
        return parameters


class SourceAnalyzer:
    """Analyzes OCCT source structure to identify conversion targets."""

    def __init__(self, src_root: Path):
        self.src_root = src_root
        self.modules: Dict[str, Dict[str, List[Path]]] = {}

    def analyze(self) -> Dict[str, Dict[str, List[Path]]]:
        """Analyze source structure."""
        for module_dir in sorted(self.src_root.iterdir()):
            if not module_dir.is_dir():
                continue
            
            module_name = module_dir.name
            toolkits = {}
            
            for toolkit_dir in sorted(module_dir.iterdir()):
                if not toolkit_dir.is_dir():
                    continue
                
                toolkit_name = toolkit_dir.name
                header_files = list(toolkit_dir.rglob('*.hxx'))
                
                if header_files:
                    toolkits[toolkit_name] = header_files
            
            if toolkits:
                self.modules[module_name] = toolkits
        
        return self.modules

    def get_priority_order(self) -> List[tuple[str, str, List[Path]]]:
        """Get modules/toolkits in conversion priority order."""
        priority_order = [
            ('FoundationClasses', 'TKernel'),
            ('FoundationClasses', 'TKMath'),
            ('ModelingData', 'TKG2d'),
            ('ModelingData', 'TKG3d'),
            ('ModelingData', 'TKBRep'),
            ('ModelingAlgorithms', 'TKTopAlgo'),
            ('ModelingAlgorithms', 'TKBO'),
            ('DataExchange', 'TKDE'),
            ('Visualization', 'TKService'),
        ]
        
        result = []
        for module, toolkit in priority_order:
            if module in self.modules and toolkit in self.modules[module]:
                result.append((module, toolkit, self.modules[module][toolkit]))
        
        return result
