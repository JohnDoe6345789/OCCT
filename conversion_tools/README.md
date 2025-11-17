# OCCT C++ to Python Conversion Tooling

Automated tools for converting OCCT C/C++ source code to Python.

## Overview

This tooling suite provides:

- **C++ Parser** (`cpp_parser.py`): Extracts class definitions, methods, and dependencies from C++ headers
- **Python Generator** (`python_generator.py`): Generates Python stub files with proper signatures and documentation
- **Source Analyzer**: Maps OCCT source structure and determines conversion priority
- **Conversion Runner** (`conversion_runner.py`): Orchestrates the end-to-end conversion process

## Installation

```bash
cd conversion_tools
pip install -r requirements.txt  # if dependencies needed
```

## Usage

### Analyze Source Structure

View the OCCT source structure and recommended conversion priority:

```bash
python conversion_runner.py --analyze
```

Output shows all modules, toolkits, and file counts:
```
OCCT SOURCE STRUCTURE ANALYSIS
============================================================
FoundationClasses: 2 toolkits, X files
  - TKernel: Y header files
  - TKMath: Z header files

...

Conversion Priority Order:
1. FoundationClasses        / TKernel               (Y files)
2. FoundationClasses        / TKMath                (Z files)
...
```

### Convert a Module

Convert a specific module and toolkit:

```bash
# Convert FoundationClasses/TKernel
python conversion_runner.py --module FoundationClasses --toolkit TKernel

# Dry run - show what would be converted
python conversion_runner.py --module FoundationClasses --toolkit TKernel --dry-run

# Specify custom output directory
python conversion_runner.py --module FoundationClasses --toolkit TKernel \
  --output-root /path/to/output
```

## Architecture

### cpp_parser.py

**Main Classes:**
- `CppParameter`: Represents a function parameter
- `CppMethod`: Represents a class method
- `CppClass`: Represents a complete class definition
- `CppHeaderParser`: Parses a single C++ header file
- `SourceAnalyzer`: Analyzes the entire source tree

**Example:**
```python
from cpp_parser import CppHeaderParser, SourceAnalyzer
from pathlib import Path

# Parse a single header
parser = CppHeaderParser(Path('src/FoundationClasses/TKernel/gp/gp_Pnt.hxx'))
classes = parser.parse()

# Analyze entire source
analyzer = SourceAnalyzer(Path('src'))
modules = analyzer.analyze()
priority = analyzer.get_priority_order()
```

### python_generator.py

**Main Classes:**
- `PythonMethodGenerator`: Converts C++ methods to Python signatures
- `PythonClassGenerator`: Generates complete Python class files
- `DirectoryStructureGenerator`: Creates package directory structure

**Features:**
- Automatic type conversion (Standard_Real → float, etc.)
- CamelCase → snake_case conversion
- Template generation with placeholders
- Proper Python package structure

**Example:**
```python
from python_generator import PythonClassGenerator, PythonMethodGenerator
from cpp_parser import CppClass
from pathlib import Path

cpp_class = CppClass(name='gp_Pnt', filename='gp_Pnt.hxx')
generator = PythonClassGenerator(Path('python_port'), cpp_class)
content = generator.generate_class_file()
generator.save(Path('python_port/gp/gp_pnt.py'))
```

### conversion_runner.py

**Entry point for the conversion pipeline.**

Features:
- Source structure analysis
- Batch conversion by module/toolkit
- Dry-run mode for validation
- Progress tracking

## Type Conversion Mappings

| C++ Type | Python Type |
|----------|------------|
| `Standard_Real` | `float` |
| `Standard_Integer` | `int` |
| `Standard_Boolean` | `bool` |
| `void` | `None` |
| `Handle(ClassName)` | `ClassName` (direct reference) |
| `Standard_Transient*` | `Optional[ClassName]` |
| `TColStd_Array*` | `List[T]` |
| Toolkit_ClassName | ToolkitClassName (concatenated) |

## Naming Conventions

### Classes
- C++: `Toolkit_ClassName` → Python: `ToolkitClassName`
- Example: `gp_Pnt` → `GpPnt`, `Geom_Circle` → `GeomCircle`

### Methods
- Convert to snake_case for public methods
- `GetX()` → `x()`, `IsDone()` → `is_done()`
- Keep consistent with Python naming conventions

### Parameters
- Convert to snake_case
- `theRadius` → `radius`, `thePoint` → `point`

### Files and Packages
- All lowercase with underscores
- Class `GeomCircle` lives in `geom_circle.py`
- Package `gp` lives in directory `gp/`

## Workflow

### Step 1: Analyze
```bash
python conversion_runner.py --analyze
```

Review priority order and identify target modules.

### Step 2: Batch Conversion
```bash
# Convert high-priority foundation classes first
python conversion_runner.py --module FoundationClasses --toolkit TKernel
python conversion_runner.py --module FoundationClasses --toolkit TKMath

# Then modeling data
python conversion_runner.py --module ModelingData --toolkit TKG2d
```

### Step 3: Manual Review and Refinement
- Review generated Python files in `python_port/`
- Add detailed docstrings linking to C++ source
- Implement methods with actual logic (not just stubs)
- Add comprehensive unit tests

### Step 4: Integration
- Update `python_port/CONVERSION_STATUS.md`
- Add to `python_port/README.md` if public
- Create API specification document
- Submit PR with changes

## Output Structure

Generated files follow this structure:

```
python_port/
├── module_name/
│   ├── __init__.py
│   ├── toolkit_name/
│   │   ├── __init__.py
│   │   ├── class_name.py
│   │   └── another_class.py
│   └── README.md
```

Each Python file contains:
```python
"""Class documentation with links to original C++ source."""

from typing import Optional, List

class ToolkitClassName:
    """Represents OCCT C++ class."""
    
    def __init__(self, ...):
        """Initialize."""
        pass
    
    def method_name(self, param: type) -> ReturnType:
        """Method documentation."""
        pass
```

## Configuration

### Source Root
Default: `../src` relative to conversion_tools
Override: `--src-root /path/to/src`

### Output Root
Default: `../python_port` relative to conversion_tools
Override: `--output-root /path/to/output`

## Performance

### Optimization Tips
- Use `--dry-run` before committing large batches
- Convert high-level modules first (fewer dependencies)
- Run analysis periodically to track progress

### Limitations
- Parser is simplified - complex C++ templates may not parse correctly
- Some types may need manual adjustment
- External dependencies are tracked but not automatically resolved

## Troubleshooting

### Parser Errors
Some C++ constructs may not parse correctly. In these cases:
1. Check the generated `.py` files manually
2. Remove unparseable content from the file
3. Add the issue to `../python_port/TODO.md`

### Type Conversion Issues
If a type doesn't convert properly:
1. Check type mappings in `PythonMethodGenerator._convert_cpp_type`
2. Add custom mapping if needed
3. Update this documentation

### Module Dependencies
Ensure dependencies are converted before dependent modules:
- TKernel before TKMath
- ModelingData before ModelingAlgorithms
- ModelingAlgorithms before DataExchange

## Future Enhancements

- [ ] Handle complex template types
- [ ] Extract and port documentation strings
- [ ] Generate comprehensive type stubs (.pyi files)
- [ ] Integrate with python_port package testing
- [ ] Add support for translating actual C++ code logic to Python
- [ ] Create specialized generators for geometry classes
- [ ] Generate Python bindings for performance-critical code

## Contributing

To improve the conversion tooling:

1. Add test cases for new C++ patterns
2. Improve type conversion mappings
3. Enhance parser robustness
4. Optimize performance for large source trees
5. Improve generated code quality

## References

- [Python Port Guide](../python_port/CONVERSION_GUIDE.md)
- [Conversion Status](../python_port/CONVERSION_STATUS.md)
- [OCCT Documentation](https://www.opencascade.com/doc/)
