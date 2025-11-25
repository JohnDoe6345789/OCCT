#!/usr/bin/env python3
"""
Walk C++ sources with libclang and emit a structured JSON summary.

The script is intentionally conservative: it records top-level declarations
(namespaces, records, enums, aliases, free functions, templates) and enough
type information to resemble the shape shown in the sample JSON. Function and
method bodies are not expanded to keep the output tractable for the full
`src` tree.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

import clang
from clang import cindex
from clang.cindex import (
    AccessSpecifier,
    Cursor,
    CursorKind,
    ExceptionSpecificationKind,
    TranslationUnit,
    Type,
    TypeKind,
)


BUILTIN_KINDS: Set[TypeKind] = {
    TypeKind.VOID,
    TypeKind.BOOL,
    TypeKind.CHAR_U,
    TypeKind.UCHAR,
    TypeKind.USHORT,
    TypeKind.UINT,
    TypeKind.ULONG,
    TypeKind.ULONGLONG,
    TypeKind.CHAR_S,
    TypeKind.SCHAR,
    TypeKind.WCHAR,
    TypeKind.SHORT,
    TypeKind.INT,
    TypeKind.LONG,
    TypeKind.LONGLONG,
    TypeKind.FLOAT,
    TypeKind.DOUBLE,
    TypeKind.LONGDOUBLE,
    TypeKind.NULLPTR,
    TypeKind.UINT128,
    TypeKind.INT128,
    TypeKind.CHAR16,
    TypeKind.CHAR32,
    TypeKind.FLOAT128,
}

if hasattr(TypeKind, "BFLOAT16"):
    BUILTIN_KINDS.add(getattr(TypeKind, "BFLOAT16"))

NOEXCEPT_KINDS: Set[ExceptionSpecificationKind] = {
    ExceptionSpecificationKind.BASIC_NOEXCEPT,
    ExceptionSpecificationKind.DYNAMIC_NONE,
}
if hasattr(ExceptionSpecificationKind, "COMPUTED_NOEXCEPT"):
    NOEXCEPT_KINDS.add(getattr(ExceptionSpecificationKind, "COMPUTED_NOEXCEPT"))

NON_TYPE_TEMPLATE_PARAM_KIND = getattr(CursorKind, "NON_TYPE_TEMPLATE_PARAMETER", None)
if NON_TYPE_TEMPLATE_PARAM_KIND is None:
    NON_TYPE_TEMPLATE_PARAM_KIND = getattr(CursorKind, "TEMPLATE_NON_TYPE_PARAMETER", None)

TEMPLATE_PARAM_KINDS: List[CursorKind] = [
    CursorKind.TEMPLATE_TYPE_PARAMETER,
    CursorKind.TEMPLATE_TEMPLATE_PARAMETER,
]
if NON_TYPE_TEMPLATE_PARAM_KIND is not None:
    TEMPLATE_PARAM_KINDS.append(NON_TYPE_TEMPLATE_PARAM_KIND)


def configure_libclang(explicit_library: Optional[str]) -> Optional[Path]:
    """
    Point clang.cindex at a usable libclang shared library.

    Preference order:
      1. CLI override
      2. lib packaged with the Python `clang` wheel (clang/native/libclang.so)
      3. LIBCLANG_LIBRARY_FILE environment variable
    """
    if explicit_library:
        lib_path = Path(explicit_library)
        cindex.Config.set_library_file(str(lib_path))
        return lib_path

    bundled = Path(clang.__file__).with_name("native") / "libclang.so"
    if bundled.exists():
        cindex.Config.set_library_file(str(bundled))
        return bundled

    env_path = os.environ.get("LIBCLANG_LIBRARY_FILE")
    if env_path and Path(env_path).exists():
        cindex.Config.set_library_file(env_path)
        return Path(env_path)

    return None


def detect_resource_includes() -> List[str]:
    """
    Try to locate Clang's resource include directory so <...> headers resolve.
    Returns a list of `-isystem <path>` arguments (or an empty list on failure).
    """
    try:
        resource_dir = subprocess.check_output(
            ["clang", "-print-resource-dir"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    include_dir = Path(resource_dir) / "include"
    if include_dir.exists():
        return ["-isystem", str(include_dir)]
    return []


def gather_sources(root: Path, extensions: Sequence[str]) -> List[Path]:
    exts = {ext.lower() for ext in extensions}
    return sorted(
        p
        for p in root.rglob("*")
        if p.suffix.lower() in exts and p.is_file() and "CMakeFiles" not in p.parts
    )


def in_source_tree(cursor: Cursor, roots: Iterable[Path]) -> bool:
    file = cursor.location.file
    if file is None:
        return False
    path = Path(file.name).resolve()
    return any(str(path).startswith(str(root.resolve())) for root in roots)


def access_name(access: AccessSpecifier) -> str:
    mapping = {
        AccessSpecifier.INVALID: "public",
        AccessSpecifier.PUBLIC: "public",
        AccessSpecifier.PRIVATE: "private",
        AccessSpecifier.PROTECTED: "protected",
    }
    return mapping.get(access, "public")


def base_is_virtual(cursor: Cursor) -> bool:
    """
    Return whether a base specifier is virtual, falling back to False on older
    libclang bindings that lack Cursor.is_virtual_base().
    """
    checker = getattr(cursor, "is_virtual_base", None)
    if not callable(checker):
        return False
    try:
        return bool(checker())
    except Exception:
        return False


def is_inline_namespace(cursor: Cursor) -> bool:
    checker = getattr(cursor, "is_inline_namespace", None)
    if not callable(checker):
        return False
    try:
        return bool(checker())
    except Exception:
        return False


def type_to_json(tp: Type) -> Dict[str, Any]:
    if not tp or tp.kind == TypeKind.INVALID:
        return {"kind": "unknown_type", "name": ""}

    try:
        num_template_args = tp.get_num_template_arguments()
    except Exception:
        num_template_args = -1

    if tp.kind in BUILTIN_KINDS:
        return {"kind": "builtin_type", "name": tp.spelling}
    if tp.kind == TypeKind.LVALUEREFERENCE:
        return {"kind": "lvalue_ref_type", "pointee": type_to_json(tp.get_pointee())}
    if tp.kind == TypeKind.RVALUEREFERENCE:
        return {"kind": "rvalue_ref_type", "pointee": type_to_json(tp.get_pointee())}
    if tp.kind == TypeKind.POINTER:
        return {"kind": "pointer_type", "pointee": type_to_json(tp.get_pointee())}

    if num_template_args and num_template_args > 0:
        args: List[Dict[str, Any]] = []
        for i in range(num_template_args):
            arg_type = tp.get_template_argument_type(i)
            if arg_type and arg_type.kind != TypeKind.INVALID:
                args.append(type_to_json(arg_type))
                continue
            try:
                value = tp.get_template_argument_value(i)
            except Exception:
                value = None
            args.append({"kind": "non_type_template_argument", "value": value})
        base_name = tp.spelling.split("<", 1)[0].strip()
        return {
            "kind": "template_instantiation_type",
            "template_name": base_name,
            "arguments": args,
        }

    if tp.kind == TypeKind.RECORD:
        return {"kind": "record_type", "name": tp.spelling, "template_arguments": []}
    if tp.kind == TypeKind.ENUM:
        return {"kind": "enum_type", "name": tp.spelling}
    if tp.kind == TypeKind.TYPEDEF:
        return {"kind": "typedef", "name": tp.spelling}
    if tp.kind == TypeKind.AUTO:
        return {"kind": "auto_type", "name": tp.spelling}

    return {"kind": "type", "name": tp.spelling}


def param_to_json(cursor: Cursor) -> Dict[str, Any]:
    return {"name": cursor.spelling, "type": type_to_json(cursor.type)}


def enum_to_json(cursor: Cursor, seen: Set[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)
    return {
        "kind": "enum",
        "name": cursor.spelling,
        "scoped": cursor.is_scoped_enum(),
        "underlying_type": type_to_json(cursor.enum_type),
        "enumerators": [
            {"name": child.spelling, "value": child.enum_value}
            for child in cursor.get_children()
            if child.kind == CursorKind.ENUM_CONSTANT_DECL
        ],
    }


def using_alias_to_json(cursor: Cursor, seen: Set[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)
    aliased = cursor.underlying_typedef_type
    return {
        "kind": "using_alias",
        "name": cursor.spelling,
        "aliased_type": type_to_json(aliased),
    }


def method_common(cursor: Cursor) -> Dict[str, Any]:
    exception_kind = getattr(cursor, "exception_specification_kind", None)
    is_noexcept = exception_kind in NOEXCEPT_KINDS if exception_kind is not None else False
    return {
        "access": access_name(cursor.access_specifier),
        "name": cursor.spelling,
        "is_const": cursor.is_const_method() if cursor.kind == CursorKind.CXX_METHOD else False,
        "is_virtual": cursor.is_virtual_method()
        if cursor.kind == CursorKind.CXX_METHOD
        else False,
        "is_pure_virtual": cursor.is_pure_virtual_method()
        if cursor.kind == CursorKind.CXX_METHOD
        else False,
        "is_static": cursor.is_static_method()
        if cursor.kind == CursorKind.CXX_METHOD
        else False,
        "is_noexcept": is_noexcept,
        "params": [param_to_json(arg) for arg in cursor.get_arguments()],
    }


def constructor_to_json(cursor: Cursor) -> Dict[str, Any]:
    data = method_common(cursor)
    data.update(
        {
            "kind": "constructor",
            "is_explicit": cursor.is_explicit_method(),
            "is_default": cursor.is_default_constructor(),
            "is_copy": cursor.is_copy_constructor(),
            "is_move": cursor.is_move_constructor(),
        }
    )
    return data


def destructor_to_json(cursor: Cursor) -> Dict[str, Any]:
    data = method_common(cursor)
    data.update(
        {
            "kind": "destructor",
            "is_virtual": cursor.is_virtual_method(),
        }
    )
    return data


def method_to_json(cursor: Cursor) -> Dict[str, Any]:
    data = method_common(cursor)
    data.update(
        {
            "kind": "virtual_function" if cursor.is_virtual_method() else "method",
            "return_type": type_to_json(cursor.result_type),
        }
    )
    return data


def static_field_to_json(cursor: Cursor) -> Dict[str, Any]:
    return {
        "kind": "static_field",
        "name": cursor.spelling,
        "access": access_name(cursor.access_specifier),
        "type": type_to_json(cursor.type),
    }


def field_to_json(cursor: Cursor) -> Dict[str, Any]:
    return {
        "kind": "field",
        "name": cursor.spelling,
        "access": access_name(cursor.access_specifier),
        "type": type_to_json(cursor.type),
    }


def record_to_json(cursor: Cursor, roots: Iterable[Path], seen: Set[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)

    members: List[Dict[str, Any]] = []
    bases: List[Dict[str, Any]] = []
    for child in cursor.get_children():
        if child.kind == CursorKind.CXX_BASE_SPECIFIER:
            bases.append(
                {
                    "access": access_name(child.access_specifier),
                    "is_virtual": base_is_virtual(child),
                    "type": type_to_json(child.type),
                }
            )
            continue
        if not in_source_tree(child, roots):
            continue

        if child.kind == CursorKind.FIELD_DECL:
            members.append(field_to_json(child))
        elif child.kind == CursorKind.VAR_DECL:
            members.append(static_field_to_json(child))
        elif child.kind == CursorKind.CXX_METHOD:
            members.append(method_to_json(child))
        elif child.kind == CursorKind.CONSTRUCTOR:
            members.append(constructor_to_json(child))
        elif child.kind == CursorKind.DESTRUCTOR:
            members.append(destructor_to_json(child))
        elif child.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
            nested = record_to_json(child, roots, seen)
            if nested:
                members.append(nested)
        elif child.kind == CursorKind.FUNCTION_TEMPLATE:
            templ = function_template_to_json(child, roots, seen)
            if templ:
                members.append(templ)

    return {
        "kind": "class" if cursor.kind == CursorKind.CLASS_DECL else "struct",
        "name": cursor.spelling,
        "access": access_name(cursor.access_specifier),
        "is_abstract": cursor.is_abstract_record(),
        "bases": bases,
        "template_params": [],
        "members": members,
    }


def class_template_to_json(cursor: Cursor, roots: Iterable[Path], seen: Set[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)

    params: List[Dict[str, Any]] = []
    members: List[Dict[str, Any]] = []

    for child in cursor.get_children():
        if child.kind in TEMPLATE_PARAM_KINDS:
            params.append(
                {
                    "kind": child.kind.name.lower(),
                    "name": child.spelling,
                    "type": type_to_json(child.type),
                }
            )
        elif child.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
            members.append(record_to_json(child, roots, seen))

    return {
        "kind": "class_template",
        "name": cursor.spelling,
        "template_params": params,
        "bases": [],
        "members": members,
        "access": access_name(cursor.access_specifier),
    }


def function_to_json(cursor: Cursor, seen: Set[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)

    exception_kind = getattr(cursor, "exception_specification_kind", None)
    is_noexcept = exception_kind in NOEXCEPT_KINDS if exception_kind is not None else False

    storage = cursor.storage_class.name.lower() if cursor.storage_class else "none"
    return {
        "kind": "function",
        "name": cursor.spelling,
        "linkage": cursor.linkage.name.lower(),
        "storage_class": storage,
        "return_type": type_to_json(cursor.result_type),
        "is_variadic": cursor.type.is_function_variadic(),
        "is_noexcept": is_noexcept,
        "params": [param_to_json(arg) for arg in cursor.get_arguments()],
    }


def function_template_to_json(cursor: Cursor, roots: Iterable[Path], seen: Set[str]) -> Optional[Dict[str, Any]]:
    usr = cursor.get_usr()
    if usr and usr in seen:
        return None
    if usr:
        seen.add(usr)

    params: List[Dict[str, Any]] = []
    func_decl: Optional[Cursor] = None
    for child in cursor.get_children():
        if child.kind in TEMPLATE_PARAM_KINDS:
            params.append(
                {
                    "kind": child.kind.name.lower(),
                    "name": child.spelling,
                    "type": type_to_json(child.type),
                }
            )
        elif child.kind == CursorKind.FUNCTION_DECL:
            func_decl = child

    func_json: Dict[str, Any] = (
        function_to_json(func_decl, seen) if func_decl is not None else {"kind": "function"}
    )
    func_json.update({"kind": "function_template", "template_params": params})
    return func_json


def namespace_to_json(cursor: Cursor, roots: Iterable[Path], seen: Set[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)
    decls: List[Dict[str, Any]] = []
    for child in cursor.get_children():
        if not in_source_tree(child, roots):
            continue
        child_json = cursor_to_decl(child, roots, seen)
        if child_json:
            decls.append(child_json)

    return {
        "kind": "namespace",
        "name": cursor.spelling,
        "inline": is_inline_namespace(cursor),
        "decls": decls,
    }


def cursor_to_decl(cursor: Cursor, roots: Iterable[Path], seen: Set[str]) -> Optional[Dict[str, Any]]:
    usr = cursor.get_usr()
    if usr and usr in seen:
        return None

    if cursor.kind == CursorKind.NAMESPACE:
        return namespace_to_json(cursor, roots, seen)
    if cursor.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
        if not cursor.is_definition():
            return None
        return record_to_json(cursor, roots, seen)
    if cursor.kind == CursorKind.CLASS_TEMPLATE:
        return class_template_to_json(cursor, roots, seen)
    if cursor.kind == CursorKind.ENUM_DECL:
        return enum_to_json(cursor, seen)
    if cursor.kind in (CursorKind.TYPE_ALIAS_DECL, CursorKind.TYPEDEF_DECL):
        return using_alias_to_json(cursor, seen)
    if cursor.kind == CursorKind.FUNCTION_TEMPLATE:
        return function_template_to_json(cursor, roots, seen)
    if cursor.kind == CursorKind.FUNCTION_DECL:
        if not cursor.is_definition():
            return None
        return function_to_json(cursor, seen)
    if cursor.kind == CursorKind.VAR_DECL and cursor.semantic_parent.kind == CursorKind.TRANSLATION_UNIT:
        if usr:
            seen.add(usr)
        return {
            "kind": "global_variable",
            "name": cursor.spelling,
            "type": type_to_json(cursor.type),
        }
    if cursor.kind == CursorKind.INCLUSION_DIRECTIVE:
        return {
            "kind": "include",
            "spelling": cursor.spelling,
            "is_system": cursor.is_in_system_header(),
        }
    return None


def translation_unit_includes(tu: TranslationUnit, root: Path, source_path: Path) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for inc in tu.get_includes():
        if not inc.include:
            continue
        include_path = Path(inc.include.name)
        try:
            resolved = include_path.resolve()
        except FileNotFoundError:
            resolved = include_path
        if not inc.location or not inc.location.file:
            continue
        if Path(inc.location.file.name).resolve() != source_path.resolve():
            continue
        is_system = not str(resolved).startswith(str(root.resolve()))
        result.append(
            {
                "kind": "include",
                "spelling": inc.include.name,
                "is_system": is_system,
            }
        )
    return result


def diagnostics_to_json(path: Path, tu: TranslationUnit) -> List[Dict[str, Any]]:
    diags: List[Dict[str, Any]] = []
    for diag in tu.diagnostics:
        location = getattr(diag, "location", None)
        loc_data: Dict[str, Any] = {}
        if location:
            loc_data = {
                "file": location.file.name if location.file else str(path),
                "line": location.line,
                "column": location.column,
            }
        diags.append(
            {
                "severity": diag.severity,
                "category": diag.category_name,
                "message": diag.spelling,
                "location": loc_data,
            }
        )
    return diags


def parse_translation_unit(
    index: cindex.Index, path: Path, args: Sequence[str], options: int
) -> Optional[TranslationUnit]:
    try:
        return index.parse(str(path), args=args, options=options)
    except cindex.TranslationUnitLoadError as exc:
        print(f"[clang-ast] Failed to parse {path}: {exc}", file=sys.stderr)
        return None


def run() -> None:
    parser = argparse.ArgumentParser(description="Export libclang AST to JSON.")
    parser.add_argument("--root", default="src", help="Root folder to scan (default: src)")
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".h", ".hh", ".hpp", ".hxx", ".cpp", ".cxx", ".cc"],
        help="File extensions to include.",
    )
    parser.add_argument(
        "--compile-arg",
        dest="compile_args",
        action="append",
        default=[],
        help="Extra argument forwarded to clang (repeatable).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Parse only the first N files (useful for testing).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ast.json"),
        help="Where to write the resulting JSON (default: ast.json).",
    )
    parser.add_argument(
        "--libclang",
        default=None,
        help="Explicit path to libclang shared library if auto-detection fails.",
    )
    args = parser.parse_args()

    lib_used = configure_libclang(args.libclang)
    if lib_used:
        print(f"[clang-ast] Using libclang at {lib_used}", file=sys.stderr)
    else:
        print("[clang-ast] Warning: no libclang override found; relying on defaults", file=sys.stderr)

    root_path = Path(args.root)
    sources = gather_sources(root_path, args.extensions)
    if args.limit:
        sources = sources[: args.limit]
    if not sources:
        print(f"[clang-ast] No sources found under {root_path}", file=sys.stderr)
        sys.exit(1)

    include_args = detect_resource_includes()
    parse_args = ["-std=c++17", f"-I{root_path}"] + include_args + args.compile_args

    index = cindex.Index.create()
    options = (
        TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
    )

    program_files: List[Dict[str, Any]] = []
    include_seen: Set[tuple[str, bool]] = set()
    diagnostics: List[Dict[str, Any]] = []

    for path in sources:
        tu = parse_translation_unit(index, path, parse_args, options)
        if not tu:
            continue
        diagnostics.extend(diagnostics_to_json(path, tu))

        file_decls: List[Dict[str, Any]] = []
        for inc in translation_unit_includes(tu, root_path, path):
            key = (inc["spelling"], inc["is_system"])
            if key not in include_seen:
                include_seen.add(key)
            file_decls.append(inc)

        local_seen: Set[str] = set()
        for child in tu.cursor.get_children():
            if not in_source_tree(child, [root_path]):
                continue
            loc_file = child.location.file.name if child.location and child.location.file else None
            if not loc_file or Path(loc_file).resolve() != path.resolve():
                continue
            decl_json = cursor_to_decl(child, [root_path], local_seen)
            if decl_json:
                file_decls.append(decl_json)

        try:
            rel_path = str(path.relative_to(root_path))
        except ValueError:
            rel_path = str(path)
        program_files.append({"file": rel_path, "decls": file_decls})

    output: Dict[str, Any] = {"program": {"files": program_files}, "diagnostics": diagnostics}
    args.output.write_text(json.dumps(output, indent=2))
    print(
        f"[clang-ast] Wrote {args.output} with {sum(len(f['decls']) for f in program_files)} decls",
        file=sys.stderr,
    )


if __name__ == "__main__":
    run()
