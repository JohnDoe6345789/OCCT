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
import logging
import itertools
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set
from uuid import uuid4

try:
    import curses
except Exception:  # pragma: no cover - platform dependent
    curses = None

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

LOGGER = logging.getLogger("clang_ast")


def new_id() -> str:
    return str(uuid4())


def make_node(
    data: Dict[str, Any], parent_id: Optional[str], node_id: Optional[str] = None
) -> Dict[str, Any]:
    node = dict(data)
    node["id"] = node_id or new_id()
    if parent_id is not None:
        node["parent"] = parent_id
    return node


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


def setup_logging(log_file: Path, console_level: str) -> logging.Logger:
    logger = LOGGER
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    if log_file.parent:
        log_file.parent.mkdir(parents=True, exist_ok=True)

    fmt_file = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt_file)
    logger.addHandler(file_handler)

    level = getattr(logging, console_level.upper(), logging.INFO)
    fmt_console = logging.Formatter("[clang-ast] %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(fmt_console)
    logger.addHandler(console_handler)

    logger.debug("Logging configured; console level=%s, file=%s", console_level.upper(), log_file)
    return logger


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


def gather_sources(
    root: Path, extensions: Sequence[str], ui: Optional[Any] = None
) -> List[Path]:
    exts = {ext.lower() for ext in extensions}
    matches: List[Path] = []
    last_path: Path = root
    counter = 0
    try:
        for counter, path in enumerate(root.rglob("*"), start=1):
            last_path = path
            if ui and (counter == 1 or counter % 200 == 0):
                ui.scan_update(counter, path)
            if (
                path.suffix.lower() in exts
                and path.is_file()
                and "CMakeFiles" not in path.parts
            ):
                matches.append(path)
    finally:
        if ui:
            if counter and (counter % 200) != 0:
                ui.scan_update(counter, last_path)
            ui.scan_finish(counter or len(matches))
    return sorted(matches)


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


def enum_to_json(cursor: Cursor, seen: Set[str], parent_id: Optional[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)
    return make_node(
        {
            "kind": "enum",
            "name": cursor.spelling,
            "scoped": cursor.is_scoped_enum(),
            "underlying_type": type_to_json(cursor.enum_type),
            "enumerators": [
                {"name": child.spelling, "value": child.enum_value}
                for child in cursor.get_children()
                if child.kind == CursorKind.ENUM_CONSTANT_DECL
            ],
        },
        parent_id,
    )


def using_alias_to_json(cursor: Cursor, seen: Set[str], parent_id: Optional[str]) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)
    aliased = cursor.underlying_typedef_type
    return make_node(
        {
            "kind": "using_alias",
            "name": cursor.spelling,
            "aliased_type": type_to_json(aliased),
        },
        parent_id,
    )


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


def constructor_to_json(cursor: Cursor, parent_id: Optional[str]) -> Dict[str, Any]:
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
    return make_node(data, parent_id)


def destructor_to_json(cursor: Cursor, parent_id: Optional[str]) -> Dict[str, Any]:
    data = method_common(cursor)
    data.update(
        {
            "kind": "destructor",
            "is_virtual": cursor.is_virtual_method(),
        }
    )
    return make_node(data, parent_id)


def method_to_json(cursor: Cursor, parent_id: Optional[str]) -> Dict[str, Any]:
    data = method_common(cursor)
    data.update(
        {
            "kind": "virtual_function" if cursor.is_virtual_method() else "method",
            "return_type": type_to_json(cursor.result_type),
        }
    )
    return make_node(data, parent_id)


def static_field_to_json(cursor: Cursor, parent_id: Optional[str]) -> Dict[str, Any]:
    return make_node(
        {
            "kind": "static_field",
            "name": cursor.spelling,
            "access": access_name(cursor.access_specifier),
            "type": type_to_json(cursor.type),
        },
        parent_id,
    )


def field_to_json(cursor: Cursor, parent_id: Optional[str]) -> Dict[str, Any]:
    return make_node(
        {
            "kind": "field",
            "name": cursor.spelling,
            "access": access_name(cursor.access_specifier),
            "type": type_to_json(cursor.type),
        },
        parent_id,
    )


def record_to_json(
    cursor: Cursor, roots: Iterable[Path], seen: Set[str], parent_id: Optional[str]
) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)

    node_id = new_id()
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
            members.append(field_to_json(child, node_id))
        elif child.kind == CursorKind.VAR_DECL:
            members.append(static_field_to_json(child, node_id))
        elif child.kind == CursorKind.CXX_METHOD:
            members.append(method_to_json(child, node_id))
        elif child.kind == CursorKind.CONSTRUCTOR:
            members.append(constructor_to_json(child, node_id))
        elif child.kind == CursorKind.DESTRUCTOR:
            members.append(destructor_to_json(child, node_id))
        elif child.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
            nested = record_to_json(child, roots, seen, node_id)
            if nested:
                members.append(nested)
        elif child.kind == CursorKind.FUNCTION_TEMPLATE:
            templ = function_template_to_json(child, roots, seen, node_id)
            if templ:
                members.append(templ)

    return make_node(
        {
            "kind": "class" if cursor.kind == CursorKind.CLASS_DECL else "struct",
            "name": cursor.spelling,
            "access": access_name(cursor.access_specifier),
            "is_abstract": cursor.is_abstract_record(),
            "bases": bases,
            "template_params": [],
            "members": members,
        },
        parent_id,
        node_id=node_id,
    )


def class_template_to_json(
    cursor: Cursor, roots: Iterable[Path], seen: Set[str], parent_id: Optional[str]
) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)

    node_id = new_id()
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
            members.append(record_to_json(child, roots, seen, node_id))

    return make_node(
        {
            "kind": "class_template",
            "name": cursor.spelling,
            "template_params": params,
            "bases": [],
            "members": members,
            "access": access_name(cursor.access_specifier),
        },
        parent_id,
        node_id=node_id,
    )


def function_to_json(
    cursor: Cursor, seen: Set[str], parent_id: Optional[str]
) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)

    exception_kind = getattr(cursor, "exception_specification_kind", None)
    is_noexcept = exception_kind in NOEXCEPT_KINDS if exception_kind is not None else False

    storage = cursor.storage_class.name.lower() if cursor.storage_class else "none"
    return make_node(
        {
            "kind": "function",
            "name": cursor.spelling,
            "linkage": cursor.linkage.name.lower(),
            "storage_class": storage,
            "return_type": type_to_json(cursor.result_type),
            "is_variadic": cursor.type.is_function_variadic(),
            "is_noexcept": is_noexcept,
            "params": [param_to_json(arg) for arg in cursor.get_arguments()],
        },
        parent_id,
    )


def function_template_to_json(
    cursor: Cursor, roots: Iterable[Path], seen: Set[str], parent_id: Optional[str]
) -> Optional[Dict[str, Any]]:
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
        function_to_json(func_decl, seen, parent_id)
        if func_decl is not None
        else {"kind": "function"}
    )
    func_json.update({"kind": "function_template", "template_params": params})
    if "id" not in func_json:
        func_json["id"] = new_id()
    if parent_id is not None:
        func_json["parent"] = parent_id
    return func_json


def namespace_to_json(
    cursor: Cursor, roots: Iterable[Path], seen: Set[str], parent_id: Optional[str]
) -> Dict[str, Any]:
    usr = cursor.get_usr()
    if usr:
        seen.add(usr)
    node_id = new_id()
    decls: List[Dict[str, Any]] = []
    for child in cursor.get_children():
        if not in_source_tree(child, roots):
            continue
        child_json = cursor_to_decl(child, roots, seen, node_id)
        if child_json:
            decls.append(child_json)

    return make_node(
        {
            "kind": "namespace",
            "name": cursor.spelling,
            "inline": is_inline_namespace(cursor),
            "decls": decls,
        },
        parent_id,
        node_id=node_id,
    )


def cursor_status(cursor: Cursor) -> str:
    kind = cursor.kind.name.lower()
    name = cursor.spelling or cursor.displayname or "<anonymous>"
    status = f"{kind}: {name}"
    return status if len(status) <= 120 else status[:117] + "..."


def cursor_to_decl(
    cursor: Cursor, roots: Iterable[Path], seen: Set[str], parent_id: Optional[str]
) -> Optional[Dict[str, Any]]:
    usr = cursor.get_usr()
    if usr and usr in seen:
        return None

    if cursor.kind == CursorKind.NAMESPACE:
        return namespace_to_json(cursor, roots, seen, parent_id)
    if cursor.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
        if not cursor.is_definition():
            return None
        return record_to_json(cursor, roots, seen, parent_id)
    if cursor.kind == CursorKind.CLASS_TEMPLATE:
        return class_template_to_json(cursor, roots, seen, parent_id)
    if cursor.kind == CursorKind.ENUM_DECL:
        return enum_to_json(cursor, seen, parent_id)
    if cursor.kind in (CursorKind.TYPE_ALIAS_DECL, CursorKind.TYPEDEF_DECL):
        return using_alias_to_json(cursor, seen, parent_id)
    if cursor.kind == CursorKind.FUNCTION_TEMPLATE:
        return function_template_to_json(cursor, roots, seen, parent_id)
    if cursor.kind == CursorKind.FUNCTION_DECL:
        if not cursor.is_definition():
            return None
        return function_to_json(cursor, seen, parent_id)
    if cursor.kind == CursorKind.VAR_DECL and cursor.semantic_parent.kind == CursorKind.TRANSLATION_UNIT:
        if usr:
            seen.add(usr)
        return make_node(
            {
                "kind": "global_variable",
                "name": cursor.spelling,
                "type": type_to_json(cursor.type),
            },
            parent_id,
        )
    if cursor.kind == CursorKind.INCLUSION_DIRECTIVE:
        return make_node(
            {
                "kind": "include",
                "spelling": cursor.spelling,
                "is_system": cursor.is_in_system_header(),
            },
            parent_id,
        )
    return None


def translation_unit_includes(
    tu: TranslationUnit, root: Path, source_path: Path, parent_id: Optional[str]
) -> List[Dict[str, Any]]:
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
            make_node(
                {
                    "kind": "include",
                    "spelling": inc.include.name,
                    "is_system": is_system,
                },
                parent_id,
            )
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
        LOGGER.error("Failed to parse %s: %s", path, exc)
        return None


class ProgressReporter:
    def __init__(
        self,
        total: Optional[int],
        enabled: bool,
        stream,
        logger: Optional[logging.Logger] = None,
        unit: str = "item",
    ) -> None:
        self.total: Optional[int] = total
        self.enabled = enabled
        self.stream = stream
        self.is_tty = stream.isatty()
        self.spinner = itertools.cycle("-\\|/")
        self.start = time.monotonic()
        self.last_emit = self.start
        self.last_line_len = 0
        self.last_completed = 0
        self.logger = logger
        self.unit = unit

    def _format_eta(self, seconds: Optional[float]) -> str:
        if seconds is None or not math.isfinite(seconds):
            return "unknown"
        seconds = max(0, seconds)
        if seconds >= 3600:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes:02d}m"
        if seconds >= 60:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs:02d}s"
        return f"{int(seconds)}s"

    def _rel_path(self, path: Path, root: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)

    def update(
        self, completed: int, path: Path, root: Path, status: Optional[str] = None
    ) -> None:
        self.last_completed = completed
        if not self.enabled:
            return

        now = time.monotonic()
        # Avoid spamming when stderr is redirected; otherwise keep the spinner lively.
        if not self.is_tty and (now - self.last_emit) < 5 and completed != self.total:
            return
        self.last_emit = now

        percent: Optional[float] = None
        if self.total:
            percent = completed / self.total * 100
        eta: Optional[float] = None
        elapsed = now - self.start
        if completed > 0 and elapsed > 0 and self.total:
            rate = completed / elapsed
            remaining = max(self.total - completed, 0)
            if rate > 0:
                eta = remaining / rate

        spinner = next(self.spinner) if self.is_tty else "~"
        total_display = str(self.total) if self.total is not None else "?"
        percent_display = f" ({percent:5.1f}%)" if percent is not None else ""
        line = (
            f"[clang-ast] {spinner} {completed}/{total_display}{percent_display} "
            f"ETA {self._format_eta(eta)} · {self._rel_path(path, root)}"
        )
        if status:
            line = f"{line} — {status}"

        if self.is_tty:
            padding = " " * max(0, self.last_line_len - len(line))
            print(f"\r{line}{padding}", end="", file=self.stream, flush=True)
            self.last_line_len = max(self.last_line_len, len(line))
        else:
            print(line, file=self.stream)

    def finish(self, total_override: Optional[int] = None) -> None:
        if not self.enabled and not self.logger:
            return

        duration = time.monotonic() - self.start
        total_done = total_override if total_override is not None else (self.total or self.last_completed)
        rate = (total_done / duration) if duration > 0 and total_done else 0.0
        rate_suffix = f" (~{rate:.1f} {self.unit}/s)" if rate > 0 else ""
        message = f"Processed {total_done} {self.unit}(s) in {duration:.1f}s{rate_suffix}"
        if self.is_tty and self.enabled:
            clear = " " * self.last_line_len
            print(f"\r{clear}\r", end="", file=self.stream)
        if self.logger:
            self.logger.info(message)
        else:
            print(f"[clang-ast] {message}", file=self.stream)


class NullUI:
    def __init__(self) -> None:
        self.root = Path(".")

    def scan_update(self, *args, **kwargs) -> None:
        return

    def scan_finish(self, *args, **kwargs) -> None:
        return

    def parse_update(self, *args, **kwargs) -> None:
        return

    def parse_finish(self, *args, **kwargs) -> None:
        return

    def close(self) -> None:
        return


class ConsoleUI:
    def __init__(self, root: Path, enabled: bool, logger: logging.Logger) -> None:
        self.root = root
        self.logger = logger
        self.enabled = enabled
        self.scan_progress = ProgressReporter(None, enabled, sys.stderr, logger, unit="path")
        self.parse_progress: Optional[ProgressReporter] = None

    def scan_update(self, count: int, path: Path) -> None:
        self.scan_progress.update(count, path, self.root)

    def scan_finish(self, total: int) -> None:
        self.scan_progress.finish(total_override=total)

    def parse_update(self, done: int, total: int, path: Path, status: Optional[str] = None) -> None:
        if self.parse_progress is None:
            self.parse_progress = ProgressReporter(total, self.enabled, sys.stderr, self.logger, unit="file")
        self.parse_progress.update(done, path, self.root, status=status)

    def parse_finish(self, done: int) -> None:
        if self.parse_progress:
            self.parse_progress.finish(total_override=done)

    def close(self) -> None:
        return


class CursesUI:
    def __init__(self, root: Path, logger: logging.Logger) -> None:
        if curses is None:
            raise RuntimeError("curses is not available on this platform")
        self.root = root
        self.logger = logger
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        try:
            curses.curs_set(0)
        except Exception:
            pass
        self.start = time.monotonic()
        self.parse_start: Optional[float] = None
        self.scan_count = 0
        self.scan_path = ""
        self.parse_done = 0
        self.parse_total: Optional[int] = None
        self.parse_path = ""
        self.status = ""

    def _safe_addstr(self, y: int, x: int, text: str) -> None:
        try:
            self.screen.addstr(y, x, text)
        except Exception:
            pass

    def _rel_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except Exception:
            return str(path)

    def _format_eta(self) -> str:
        if not self.parse_total or self.parse_done == 0:
            return "unknown"
        baseline = self.parse_start or self.start
        elapsed = time.monotonic() - baseline
        rate = self.parse_done / elapsed if elapsed > 0 else 0.0
        if rate <= 0:
            return "unknown"
        remaining = max(self.parse_total - self.parse_done, 0)
        seconds = remaining / rate
        if seconds >= 3600:
            return f"{int(seconds // 3600)}h {int((seconds % 3600)//60):02d}m"
        if seconds >= 60:
            return f"{int(seconds // 60)}m {int(seconds % 60):02d}s"
        return f"{int(seconds)}s"

    def _draw(self) -> None:
        self.screen.erase()
        header = "clang-ast: exporting AST to JSON"
        self._safe_addstr(0, 0, header[: curses.COLS - 1])

        scan_line = f"Scanning: {self.scan_count} path(s)"
        if self.scan_path:
            scan_line += f" · {self.scan_path}"
        self._safe_addstr(2, 0, scan_line[: curses.COLS - 1])

        parse_line = f"Parsing: {self.parse_done}"
        if self.parse_total:
            parse_line += f"/{self.parse_total}"
            percent = (self.parse_done / self.parse_total) * 100 if self.parse_total else 0
            parse_line += f" ({percent:5.1f}%)"
        parse_line += f" ETA {self._format_eta()}"
        if self.parse_path:
            parse_line += f" · {self.parse_path}"
        self._safe_addstr(4, 0, parse_line[: curses.COLS - 1])

        if self.status:
            self._safe_addstr(6, 0, f"Status: {self.status}"[: curses.COLS - 1])

        self.screen.refresh()

    def scan_update(self, count: int, path: Path) -> None:
        self.scan_count = count
        self.scan_path = self._rel_path(path)
        self._draw()

    def scan_finish(self, total: int) -> None:
        self.scan_count = total
        self._draw()

    def parse_update(self, done: int, total: int, path: Path, status: Optional[str] = None) -> None:
        self.parse_done = done
        self.parse_total = total
        self.parse_path = self._rel_path(path)
        if self.parse_start is None:
            self.parse_start = time.monotonic()
        if status:
            self.status = status
        self._draw()

    def parse_finish(self, done: int) -> None:
        self.parse_done = done
        self._draw()

    def close(self) -> None:
        try:
            curses.nocbreak()
            curses.echo()
            curses.endwin()
        except Exception:
            pass


def create_ui(root: Path, args: argparse.Namespace) -> Any:
    if args.no_progress:
        return NullUI()
    if getattr(args, "curses_ui", False):
        try:
            if sys.stderr.isatty():
                return CursesUI(root, LOGGER)
            LOGGER.warning("Curses UI requested but stderr is not a TTY; using console progress")
        except Exception as exc:
            LOGGER.warning("Curses UI unavailable (%s); falling back to console progress", exc)
    return ConsoleUI(root, True, LOGGER)


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
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable the interactive progress indicator.",
    )
    parser.add_argument(
        "--curses",
        dest="curses_ui",
        action="store_true",
        help="Use a curses-based UI (TTY only; falls back to console progress).",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("clang_ast.log"),
        help="Path to verbose log output (default: clang_ast.log).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Console log level (default: INFO).",
    )
    args = parser.parse_args()

    setup_logging(args.log_file, args.log_level)

    lib_used = configure_libclang(args.libclang)
    if lib_used:
        LOGGER.info("Using libclang at %s", lib_used)
    else:
        LOGGER.warning("No libclang override found; relying on defaults")

    root_path = Path(args.root)
    ui = create_ui(root_path, args)

    LOGGER.info("Scanning %s for source files...", root_path)
    sources = gather_sources(root_path, args.extensions, ui)
    LOGGER.info("Found %d source files under %s", len(sources), root_path)
    if args.limit:
        sources = sources[: args.limit]
        LOGGER.info("Limiting processing to first %d file(s)", len(sources))
    if not sources:
        LOGGER.error("No sources found under %s", root_path)
        sys.exit(1)

    include_args = detect_resource_includes()
    if include_args:
        LOGGER.debug("Detected resource includes: %s", include_args)
    else:
        LOGGER.debug("No resource includes detected")
    parse_args = ["-std=c++17", f"-I{root_path}"] + include_args + args.compile_args
    LOGGER.debug("Compile arguments: %s", parse_args)

    clang_index = cindex.Index.create()
    options = (
        TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
    )

    program_id = new_id()
    program_files: List[Dict[str, Any]] = []
    include_seen: Set[tuple[str, bool]] = set()
    diagnostics: List[Dict[str, Any]] = []

    try:
        for idx, path in enumerate(sources, start=1):
            ui.parse_update(idx - 1, len(sources), path, status="parsing")
            LOGGER.debug("Parsing %s", path)
            tu = parse_translation_unit(clang_index, path, parse_args, options)
            if tu:
                diagnostics.extend(diagnostics_to_json(path, tu))

                file_decls: List[Dict[str, Any]] = []
                file_id = new_id()
                for inc in translation_unit_includes(tu, root_path, path, file_id):
                    key = (inc["spelling"], inc["is_system"])
                    if key not in include_seen:
                        include_seen.add(key)
                    file_decls.append(inc)

                local_seen: Set[str] = set()
                child_counter = 0
                for child in tu.cursor.get_children():
                    if not in_source_tree(child, [root_path]):
                        continue
                    loc_file = child.location.file.name if child.location and child.location.file else None
                    if not loc_file or Path(loc_file).resolve() != path.resolve():
                        continue
                    child_counter += 1
                    if child_counter % 25 == 0:
                        ui.parse_update(
                            idx - 1, len(sources), path, status=f"processing {cursor_status(child)}"
                        )
                    decl_json = cursor_to_decl(child, [root_path], local_seen, file_id)
                    if decl_json:
                        file_decls.append(decl_json)

                try:
                    rel_path = str(path.relative_to(root_path))
                except ValueError:
                    rel_path = str(path)
                program_files.append(
                    {"id": file_id, "parent": program_id, "file": rel_path, "decls": file_decls}
                )

            ui.parse_update(idx, len(sources), path, status="parsed")
    finally:
        ui.parse_finish(len(sources))
        ui.close()

    output: Dict[str, Any] = {
        "program": {"id": program_id, "files": program_files},
        "diagnostics": diagnostics,
    }
    LOGGER.info("Writing JSON output to %s", args.output)
    args.output.write_text(json.dumps(output, indent=2))
    decl_count = sum(len(f["decls"]) for f in program_files)
    LOGGER.info("Wrote %s with %d decls", args.output, decl_count)


if __name__ == "__main__":
    run()
