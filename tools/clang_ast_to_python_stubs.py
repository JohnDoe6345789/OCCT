#!/usr/bin/env python3
"""
Generate Python stub modules from clang_ast_to_json.py output.

The script reads ast.json (or a supplied file), converts it into the typed tree
from clang_ast_json_to_tree.py, and writes lightweight Python stubs that mirror
every class, struct, enum, and free function found under the C++ src/ tree.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from clang_ast_json_to_tree import (  # noqa: E402
    ClassTemplateDecl,
    ClangAst,
    ConstructorDecl,
    Decl,
    DestructorDecl,
    EnumDecl,
    FieldDecl,
    FunctionDecl,
    GlobalVariableDecl,
    IncludeDecl,
    MethodDecl,
    NamespaceDecl,
    RecordDecl,
    UnknownDecl,
    UsingAliasDecl,
    load_clang_ast,
)


HEADER_EXTS = {".h", ".hh", ".hpp", ".hxx"}


@dataclass
class StubStats:
    files_written: int = 0
    classes: int = 0
    functions: int = 0
    enums: int = 0
    aliases: int = 0
    globals: int = 0
    skipped_empty: int = 0


def to_snake(name: str) -> str:
    name = name.replace("::", "_")
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"__+", "_", name)
    return name.strip("_").lower() or "unnamed"


def camelize_cpp(name: str) -> str:
    parts = re.split(r"[_\s]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def is_header(path: Path) -> bool:
    return path.suffix.lower() in HEADER_EXTS


def file_to_dest(path: str, output_root: Path) -> Path:
    parts = Path(path).parts
    if len(parts) >= 2:
        module, toolkit, *rest = parts
    else:
        module, toolkit, rest = parts[0], "root", []

    dest_parts = [module.lower(), toolkit.lower(), *(p.lower() for p in rest[:-1])]
    dest_file = to_snake(Path(parts[-1]).stem) + ".py"
    return output_root.joinpath(*dest_parts, dest_file)


def format_params(params: Sequence[str], include_self: bool) -> str:
    if include_self:
        return ", ".join(["self", *params])
    return ", ".join(params)


def param_names(method_params: Sequence[str]) -> List[str]:
    names: List[str] = []
    seen: Dict[str, int] = {}
    for idx, raw in enumerate(method_params):
        base = to_snake(raw or f"arg{idx}")
        count = seen.get(base, 0)
        name = base if count == 0 else f"{base}_{count}"
        seen[base] = count + 1
        names.append(name)
    return names


def get_namespace_prefix(namespace: Sequence[str]) -> str:
    return "::".join(namespace) if namespace else ""


def collect_decls(decls: Iterable[Decl], namespace: Tuple[str, ...] = ()) -> List[Tuple[Tuple[str, ...], Decl]]:
    items: List[Tuple[Tuple[str, ...], Decl]] = []
    for decl in decls:
        if isinstance(decl, NamespaceDecl):
            items.extend(collect_decls(decl.decls, namespace + (decl.name,)))
        elif isinstance(decl, IncludeDecl):
            continue
        else:
            items.append((namespace, decl))
    return items


def render_enum(decl: EnumDecl, namespace: Tuple[str, ...]) -> List[str]:
    lines = [f"class {camelize_cpp(decl.name)}(enum.Enum):"]
    if namespace:
        lines.append(f'    """C++: {get_namespace_prefix(namespace + (decl.name,))}"""')
    if not decl.enumerators:
        lines.append("    pass")
        return lines
    for enumerator in decl.enumerators:
        enum_name = to_snake(enumerator.name).upper()
        value_repr = enumerator.value if enumerator.value is not None else "..."
        lines.append(f"    {enum_name} = {value_repr}")
    return lines


def render_global_function(decl: FunctionDecl, namespace: Tuple[str, ...]) -> List[str]:
    params = param_names([p.name for p in decl.params])
    ns_prefix = get_namespace_prefix(namespace)
    header = f"def {to_snake(decl.name)}({format_params(params, include_self=False)}):"
    lines = [header]
    if ns_prefix:
        lines.append(f'    """C++: {ns_prefix}::{decl.name}"""')
    lines.append("    ...")
    return lines


def render_global_variable(decl: GlobalVariableDecl) -> List[str]:
    return [f"{to_snake(decl.name)}: Any = None"]


def render_method(decl: MethodDecl) -> List[str]:
    params = param_names([p.name for p in decl.params])
    header = f"def {to_snake(decl.name)}({format_params(params, include_self=not decl.is_static)}):"
    lines = []
    if decl.is_static:
        lines.append("    @staticmethod")
        header = f"    {header}"
    else:
        header = f"    {header}"
    lines.append(header)
    lines.append("        ...")
    return lines


def render_constructor(decl: ConstructorDecl) -> List[str]:
    params = param_names([p.name for p in decl.params])
    header = f"    def __init__({format_params(params, include_self=True)}):"
    return [header, "        ..."]


def render_destructor(_: DestructorDecl) -> List[str]:
    return ["    def __del__(self):", "        ..."]


def render_record(decl: RecordDecl, namespace: Tuple[str, ...] = ()) -> List[str]:
    bases = [camelize_cpp(base.type.name or base.type.template_name or "object") for base in decl.bases]
    base_expr = f"({', '.join(bases)})" if bases else ""
    lines = [f"class {camelize_cpp(decl.name)}{base_expr}:"]
    if namespace:
        lines.append(f'    """C++: {get_namespace_prefix(namespace + (decl.name,))}"""')
    if not decl.members:
        lines.append("    pass")
        return lines

    for member in decl.members:
        if isinstance(member, ConstructorDecl):
            lines.extend(render_constructor(member))
        elif isinstance(member, DestructorDecl):
            lines.extend(render_destructor(member))
        elif isinstance(member, MethodDecl):
            lines.extend(render_method(member))
        elif isinstance(member, EnumDecl):
            nested = render_enum(member, namespace + (decl.name,))
            lines.extend("    " + line if line else "" for line in nested)
        elif isinstance(member, RecordDecl):
            nested = render_record(member, namespace + (decl.name,))
            lines.extend("    " + line if line else "" for line in nested)
        elif isinstance(member, ClassTemplateDecl):
            nested = render_class_template(member, namespace + (decl.name,))
            lines.extend("    " + line if line else "" for line in nested)
        elif isinstance(member, FieldDecl):
            lines.append(f"    {to_snake(member.name)}: Any = None")
        else:
            continue
    return lines


def render_class_template(decl: ClassTemplateDecl, namespace: Tuple[str, ...] = ()) -> List[str]:
    lines = [f"class {camelize_cpp(decl.name)}:"]
    if namespace:
        lines.append(f'    """C++: {get_namespace_prefix(namespace + (decl.name,))}"""')
    if not decl.members:
        lines.append("    pass")
        return lines
    for member in decl.members:
        if isinstance(member, (RecordDecl, ClassTemplateDecl)):
            nested = (
                render_record(member, namespace + (decl.name,))
                if isinstance(member, RecordDecl)
                else render_class_template(member, namespace + (decl.name,))
            )
            lines.extend("    " + line if line else "" for line in nested)
        elif isinstance(member, ConstructorDecl):
            lines.extend(render_constructor(member))
        elif isinstance(member, DestructorDecl):
            lines.extend(render_destructor(member))
        elif isinstance(member, MethodDecl):
            lines.extend(render_method(member))
        elif isinstance(member, EnumDecl):
            nested = render_enum(member, namespace + (decl.name,))
            lines.extend("    " + line if line else "" for line in nested)
        elif isinstance(member, FieldDecl):
            lines.append(f"    {to_snake(member.name)}: Any = None")
    return lines


def render_alias(decl: UsingAliasDecl) -> List[str]:
    return [f"{to_snake(decl.name)} = None  # alias"]


def render_unknown(decl: UnknownDecl) -> List[str]:
    return [f"# Unhandled decl kind: {decl.kind} ({decl.raw.get('name', '')})"]


def decl_contains_enum(decl: Decl) -> bool:
    if isinstance(decl, EnumDecl):
        return True
    if isinstance(decl, NamespaceDecl):
        return any(decl_contains_enum(child) for child in decl.decls)
    if isinstance(decl, (RecordDecl, ClassTemplateDecl)):
        return any(decl_contains_enum(member) for member in decl.members)
    return False


def ensure_init_files(dest: Path, stop_at: Path) -> None:
    current = dest.parent.resolve()
    stop_at = stop_at.resolve()
    while True:
        init_path = current / "__init__.py"
        if not init_path.exists():
            init_path.write_text("# Auto-generated package marker\n")
        if current == stop_at or current == current.parent:
            break
        current = current.parent


def should_process_file(rel_path: str, headers_only: bool) -> bool:
    if not headers_only:
        return True
    return is_header(Path(rel_path))


def write_stub(
    source_path: str,
    decls: List[Tuple[Tuple[str, ...], Decl]],
    dest_path: Path,
    package_root: Path,
    dry_run: bool,
) -> StubStats:
    stats = StubStats()
    lines: List[str] = []
    has_enum = any(decl_contains_enum(d) for _, d in decls)
    if not decls:
        stats.skipped_empty += 1
        return stats

    lines.append(f'"""Stubs generated from {source_path}."""')
    lines.append("from __future__ import annotations")
    lines.append("from typing import Any")
    if has_enum:
        lines.append("import enum")
    lines.append("")

    for namespace, decl in decls:
        if isinstance(decl, EnumDecl):
            lines.extend(render_enum(decl, namespace))
            stats.enums += 1
        elif isinstance(decl, RecordDecl):
            lines.extend(render_record(decl, namespace))
            stats.classes += 1
        elif isinstance(decl, ClassTemplateDecl):
            lines.extend(render_class_template(decl, namespace))
            stats.classes += 1
        elif isinstance(decl, FunctionDecl):
            lines.extend(render_global_function(decl, namespace))
            stats.functions += 1
        elif isinstance(decl, UsingAliasDecl):
            lines.extend(render_alias(decl))
            stats.aliases += 1
        elif isinstance(decl, GlobalVariableDecl):
            lines.extend(render_global_variable(decl))
            stats.globals += 1
        else:
            lines.extend(render_unknown(decl if isinstance(decl, UnknownDecl) else UnknownDecl(kind=decl.kind, raw={})))
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"

    if not dry_run:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        ensure_init_files(dest_path, package_root)
        dest_path.write_text(content)
    stats.files_written += 0 if dry_run else 1
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create Python stubs from clang_ast_to_json.py output."
    )
    parser.add_argument(
        "--ast",
        default="ast.json",
        help="Path to JSON emitted by clang_ast_to_json.py (default: ast.json).",
    )
    parser.add_argument(
        "--output-root",
        default=Path("python_port/generated"),
        type=Path,
        help="Destination root for generated stubs (default: python_port/generated).",
    )
    parser.add_argument(
        "--headers-only",
        action="store_true",
        default=True,
        help="Generate stubs only for header-like files (default: on).",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Override --headers-only to process every file.",
    )
    parser.add_argument(
        "--limit-files",
        type=int,
        default=None,
        help="Limit the number of files processed (useful for spot checks).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and plan stub generation without writing files.",
    )

    args = parser.parse_args()
    headers_only = not args.all_files and args.headers_only

    ast = load_clang_ast(Path(args.ast))
    stats = StubStats()
    written_paths: set[Path] = set()

    files = ast.program.files
    if args.limit_files is not None:
        files = files[: args.limit_files]

    for program_file in files:
        if not should_process_file(program_file.path, headers_only=headers_only):
            continue
        dest = file_to_dest(program_file.path, args.output_root)
        if dest in written_paths:
            continue
        decls = collect_decls(program_file.decls)
        file_stats = write_stub(
            program_file.path,
            decls,
            dest,
            package_root=args.output_root,
            dry_run=args.dry_run,
        )
        stats.classes += file_stats.classes
        stats.enums += file_stats.enums
        stats.functions += file_stats.functions
        stats.aliases += file_stats.aliases
        stats.globals += file_stats.globals
        stats.files_written += file_stats.files_written
        stats.skipped_empty += file_stats.skipped_empty
        written_paths.add(dest)

    print(f"Files parsed: {len(files)}")
    print(f"Files written: {stats.files_written} (dry-run: {args.dry_run})")
    print(
        f"Classes: {stats.classes}, Enums: {stats.enums}, Functions: {stats.functions}, "
        f"Aliases: {stats.aliases}, Globals: {stats.globals}, Empty: {stats.skipped_empty}"
    )


if __name__ == "__main__":
    main()
