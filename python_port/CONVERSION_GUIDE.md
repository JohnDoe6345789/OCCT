# OCCT to Python Conversion Guide

This document describes the systematic approach for converting C/C++ OCCT code to Python.

## Module Conversion Priority

The conversion follows a dependency-aware hierarchy to ensure foundational classes are available when needed:

### Phase 1: Foundation (FoundationClasses)
- **TKernel**: Core types, memory management, standard utilities
  - `gp/`: Geometric primitives (Point, Vector, Axis, Transform)
  - `Quantity/`: Physical quantities and measurements
  - `Standard/`: Base types and utilities

- **TKMath**: Mathematical operations
  - `math/`: Numeric algorithms
  - `GeomLProp/`: Local properties

### Phase 2: Modeling Data (ModelingData)
- **TKG2d**: 2D geometry
  - `gp_2D`: 2D primitives
  - `Geom2d_`: Curves and surfaces in 2D

- **TKG3d**: 3D geometry
  - `gp`: 3D primitives
  - `Geom_`: Curves and surfaces in 3D

- **TKGeomBase**: Geometric base classes
- **TKBRep**: Topological representation

### Phase 3: Modeling Algorithms (ModelingAlgorithms)
- **TKGeomAlgo**: Geometric algorithms
- **TKTopAlgo**: Topological algorithms
- **TKBO**: Boolean operations
- **TKFillet**: Fillets and chamfers
- **TKOffset**: Offsetting
- **TKMesh**: Mesh generation

### Phase 4: Data Exchange (DataExchange)
- **TKDE**: Core exchange framework
- **TKDESTEP**: STEP format
- **TKDEIIGES**: IGES format
- **TKDEVRML**: VRML format
- **TKDEGLTF**: glTF format

### Phase 5: Visualization (Visualization)
- **TKService**: Visualization services
- **TKV3d**: 3D view management
- **TKOpenGl**: OpenGL rendering

### Phase 6: Application Framework (ApplicationFramework)
- **TKCDF**: Model data format
- **TKCAF**: Application data model

### Phase 7: Draw (Testing Framework)
- Interactive testing utilities

## Conversion Patterns

### 1. Memory Management
**C++ (Handle-based GC):**
```cpp
Handle(Geom_Circle) circle = new Geom_Circle(gp_Ax2(), radius);
```

**Python (Ref-counted):**
```python
circle = GeomCircle(ax2, radius)
```

### 2. Class Naming
- C++: `Toolkit_ClassName` → Python: `ToolkitClassName`
- Example: `Geom_Circle` → `GeomCircle`

### 3. Package Structure
- C++ module: `src/Module/Toolkit/Package/ClassName.cxx`
- Python: `python_port/module/toolkit/package/class_name.py`

### 4. Type Conversions
| C++ Type | Python Type |
|----------|------------|
| `Standard_Real` | `float` |
| `Standard_Integer` | `int` |
| `Standard_Boolean` | `bool` |
| `gp_Pnt` | `Point` or tuple `(x, y, z)` |
| `Handle(Class)` | Pythonic class instance |
| `TColStd_Array*` | `list` or `array.array` |

### 5. Method Naming
- **Constructors**: Use `__init__` or classmethods like `from_*`
- **Getters**: Remove `Get` prefix if property-like
  - C++: `GetX()` → Python: `x()` or `@property x`
  - C++: `IsDone()` → Python: `is_done()`
- **Setters**: Use Python properties with `@property` and `@*.setter`

### 6. Error Handling
**C++ (status methods):**
```cpp
BRepAlgoAPI_Fuse fuse(shape1, shape2);
if (!fuse.IsDone()) {
  // handle error
}
```

**Python (exceptions):**
```python
try:
    result = boolean_fuse(shape1, shape2)
except BooleanOperationError as e:
    # handle error
```

## File Organization Template

Each converted module should follow this structure:

```
python_port/
├── module_name/
│   ├── __init__.py
│   ├── README.md  (links to src/Module/Toolkit)
│   ├── toolkit_name/
│   │   ├── __init__.py
│   │   ├── class_name.py
│   │   └── class_name_test.py
│   └── api_spec.md  (documents public API)
```

## Conversion Checklist

For each class being converted:

- [ ] Identify source C/C++ file in `src/`
- [ ] Create corresponding Python directory structure
- [ ] Parse class definition and public API
- [ ] Identify dependencies (other classes, external libs)
- [ ] Create Python class with equivalent methods
- [ ] Implement type conversions and validations
- [ ] Add docstrings referencing original C++ code
- [ ] Create unit tests
- [ ] Document public API in `api_spec.md`
- [ ] Update `CONVERSION_STATUS.md`

## Conversion Status

See [`CONVERSION_STATUS.md`](CONVERSION_STATUS.md) for the current progress on all modules.

## Tools and Scripts

- `conversion_analyzer.py`: Scans C/C++ files and generates conversion reports
- `cpp_parser.py`: Parses C/C++ headers and extracts class definitions
- `python_generator.py`: Generates Python stub files
- `conversion_runner.py`: Orchestrates conversions across modules

## Contributing

When adding new conversions:

1. Follow the directory structure and naming conventions
2. Include comprehensive docstrings linking to original C++ source
3. Write tests for each public method
4. Update `CONVERSION_STATUS.md`
5. Submit PR with detailed description of what was ported
