# Inspector

The Inspector component has been moved to a separate GitHub repository:
https://github.com/Open-Cascade-SAS/Inspector

## Usage with DRAW

To use the Inspector plugin in DRAW:

1. Copy the required dynamic library files (.so, .dll) from the Inspector repository to your OCCT installation folder. For example, on Linux, you can copy the files to the `lib` directory in the OCCT installation directory. For windows, you can copy the files to the `bin` directory in the OCCT installation directory.
2. Load the plugin in your DRAW session

## Documentation

The documentation for Inspector is available at:
https://github.com/Open-Cascade-SAS/Inspector/tree/master/doc

For more details on building and using the Inspector, please refer to the repository's documentation.

# Clang AST JSON exporter

`tools/clang_ast_to_json.py` walks the `src` tree with libclang and emits a structured JSON summary of includes, namespaces, records, enums, aliases, free functions, and templates (function bodies are skipped). Results are grouped per parsed file.

## Quick start

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install clang libclang
   ```
2. Run the exporter (writes `ast.json` by default):
   ```bash
   .venv/bin/python tools/clang_ast_to_json.py --root src --output ast.json
   ```
   Useful flags:
   - `--limit N` to process only the first N files (fast dry-run)
   - `--compile-arg ...` to forward extra compilation flags to clang
   - `--libclang /path/to/libclang.so` to override library discovery

The JSON shape has `program.files[*].decls` plus a top-level `diagnostics` array.

## Output JSON schema (informal)

Below is an informal JSON Schema-style description of the output (trimmed to key fields and union types):

```json
{
  "type": "object",
  "properties": {
    "program": {
      "type": "object",
      "properties": {
        "files": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "file": { "type": "string" },
              "decls": { "type": "array", "items": { "$ref": "#/$defs/Decl" } }
            },
            "required": ["file", "decls"]
          }
        }
      },
      "required": ["files"]
    },
    "diagnostics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "severity": { "type": "integer" },
          "category": { "type": "string" },
          "message": { "type": "string" },
          "location": {
            "type": "object",
            "properties": {
              "file": { "type": "string" },
              "line": { "type": "integer" },
              "column": { "type": "integer" }
            },
            "required": ["file", "line", "column"]
          }
        },
        "required": ["severity", "message"]
      }
    }
  },
  "required": ["program"],
  "$defs": {
    "IncludeDecl": {
      "type": "object",
      "properties": {
        "kind": { "const": "include" },
        "spelling": { "type": "string" },
        "is_system": { "type": "boolean" }
      },
      "required": ["kind", "spelling", "is_system"]
    },
    "NamespaceDecl": {
      "type": "object",
      "properties": {
        "kind": { "const": "namespace" },
        "name": { "type": "string" },
        "inline": { "type": "boolean" },
        "decls": { "type": "array", "items": { "$ref": "#/$defs/Decl" } }
      },
      "required": ["kind", "name", "inline", "decls"]
    },
    "EnumDecl": {
      "type": "object",
      "properties": {
        "kind": { "const": "enum" },
        "name": { "type": "string" },
        "scoped": { "type": "boolean" },
        "underlying_type": { "$ref": "#/$defs/Type" },
        "enumerators": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "value": { "type": "integer" }
            },
            "required": ["name", "value"]
          }
        }
      },
      "required": ["kind", "name", "enumerators"]
    },
    "UsingAliasDecl": {
      "type": "object",
      "properties": {
        "kind": { "const": "using_alias" },
        "name": { "type": "string" },
        "aliased_type": { "$ref": "#/$defs/Type" }
      },
      "required": ["kind", "name", "aliased_type"]
    },
    "RecordDecl": {
      "type": "object",
      "properties": {
        "kind": { "enum": ["class", "struct"] },
        "name": { "type": "string" },
        "access": { "type": "string" },
        "is_abstract": { "type": "boolean" },
        "bases": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "access": { "type": "string" },
              "is_virtual": { "type": "boolean" },
              "type": { "$ref": "#/$defs/Type" }
            },
            "required": ["type"]
          }
        },
        "template_params": { "type": "array" },
        "members": { "type": "array" }
      },
      "required": ["kind", "name", "members"]
    },
    "ClassTemplateDecl": {
      "type": "object",
      "properties": {
        "kind": { "const": "class_template" },
        "name": { "type": "string" },
        "template_params": { "type": "array" },
        "bases": { "type": "array" },
        "members": { "type": "array" },
        "access": { "type": "string" }
      },
      "required": ["kind", "name", "template_params", "members"]
    },
    "FunctionDecl": {
      "type": "object",
      "properties": {
        "kind": { "enum": ["function", "function_template"] },
        "name": { "type": "string" },
        "return_type": { "$ref": "#/$defs/Type" },
        "params": { "type": "array", "items": { "$ref": "#/$defs/Param" } }
      },
      "required": ["kind", "name", "return_type", "params"]
    },
    "GlobalVarDecl": {
      "type": "object",
      "properties": {
        "kind": { "const": "global_variable" },
        "name": { "type": "string" },
        "type": { "$ref": "#/$defs/Type" }
      },
      "required": ["kind", "name", "type"]
    },
    "Decl": {
      "oneOf": [
        { "$ref": "#/$defs/IncludeDecl" },
        { "$ref": "#/$defs/NamespaceDecl" },
        { "$ref": "#/$defs/EnumDecl" },
        { "$ref": "#/$defs/UsingAliasDecl" },
        { "$ref": "#/$defs/RecordDecl" },
        { "$ref": "#/$defs/ClassTemplateDecl" },
        { "$ref": "#/$defs/FunctionDecl" },
        { "$ref": "#/$defs/GlobalVarDecl" }
      ]
    },
    "Type": {
      "type": "object",
      "properties": {
        "kind": { "type": "string" },
        "name": { "type": "string" }
      },
      "required": ["kind", "name"]
    },
    "Param": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "type": { "$ref": "#/$defs/Type" }
      },
      "required": ["name", "type"]
    }
  }
}
```

# JSON -> Python tree loader

`tools/clang_ast_json_to_tree.py` loads the JSON emitted by `clang_ast_to_json.py`
into a small set of dataclasses so downstream tooling can work with Python
objects instead of dictionaries.

Quick examples:

```bash
python3 tools/clang_ast_json_to_tree.py ast.json --records  # prints a summary and record names
```

```python
from pathlib import Path
from tools.clang_ast_json_to_tree import (
    ClassTemplateDecl,
    RecordDecl,
    load_clang_ast,
)

ast = load_clang_ast(Path("ast.json"))
records = [
    decl for decl in ast.walk_decls() if isinstance(decl, (RecordDecl, ClassTemplateDecl))
]
print(f"Loaded {len(records)} records")
```

# Python stubs for every class/function

`tools/clang_ast_to_python_stubs.py` turns the JSON AST into a tree of Python
stub modules under `python_port/generated` (or another output root). The goal is
to guarantee a Python replica exists for each C++ class/function in `src/`
before manual refinement.

Typical workflow:

```bash
# Export AST (headers + sources) to JSON
python3 tools/clang_ast_to_json.py --root src --output ast.json

# Dry-run stub generation (headers only by default)
python3 tools/clang_ast_to_python_stubs.py --ast ast.json --dry-run

# Write stubs to python_port/generated (one file per C++ file)
python3 tools/clang_ast_to_python_stubs.py --ast ast.json --output-root python_port/generated
```

Flags:
- `--limit-files N` to sample a subset while iterating
- `--all-files` to include `.cxx` alongside headers
