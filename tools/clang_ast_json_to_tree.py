#!/usr/bin/env python3
"""
Load clang_ast_to_json.py output into a typed Python tree.

The loader builds small dataclasses around the JSON schema emitted by
clang_ast_to_json.py so downstream tooling can work with Python objects instead
of raw dictionaries.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class TypeRef:
    kind: str
    name: str = ""
    pointee: Optional["TypeRef"] = None
    template_name: Optional[str] = None
    template_arguments: List["TemplateArgument"] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> "TypeRef":
        if not data:
            return TypeRef(kind="unknown_type", name="")

        kind = data.get("kind", "type")
        if kind in {"lvalue_ref_type", "rvalue_ref_type", "pointer_type"}:
            return TypeRef(kind=kind, pointee=TypeRef.from_dict(data.get("pointee")))

        if kind == "template_instantiation_type":
            args = [TemplateArgument.from_value(arg) for arg in data.get("arguments", [])]
            return TypeRef(
                kind=kind,
                template_name=data.get("template_name", data.get("name", "")),
                template_arguments=args,
            )

        template_args = [
            TemplateArgument.from_value(arg) for arg in data.get("template_arguments", [])
        ]
        return TypeRef(
            kind=kind,
            name=data.get("name", ""),
            template_name=data.get("template_name"),
            template_arguments=template_args,
        )


@dataclass
class TemplateArgument:
    raw_kind: str
    type: Optional[TypeRef] = None
    value: Optional[int] = None

    @staticmethod
    def from_value(data: Any) -> "TemplateArgument":
        if not isinstance(data, dict):
            return TemplateArgument(raw_kind="unknown")
        if data.get("kind") == "non_type_template_argument":
            return TemplateArgument(raw_kind="non_type_template_argument", value=data.get("value"))
        return TemplateArgument(raw_kind=data.get("kind", "type"), type=TypeRef.from_dict(data))


@dataclass
class TemplateParam:
    kind: str
    name: str
    type: TypeRef

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TemplateParam":
        return TemplateParam(
            kind=data.get("kind", ""),
            name=data.get("name", ""),
            type=TypeRef.from_dict(data.get("type")),
        )


@dataclass
class Param:
    name: str
    type: TypeRef

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Param":
        return Param(name=data.get("name", ""), type=TypeRef.from_dict(data.get("type")))


@dataclass
class BaseSpec:
    access: str
    is_virtual: bool
    type: TypeRef

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "BaseSpec":
        return BaseSpec(
            access=data.get("access", "public"),
            is_virtual=bool(data.get("is_virtual", False)),
            type=TypeRef.from_dict(data.get("type")),
        )


@dataclass
class Enumerator:
    name: str
    value: Optional[int]


@dataclass
class Decl:
    kind: str


@dataclass
class IncludeDecl(Decl):
    spelling: str
    is_system: bool


@dataclass
class NamespaceDecl(Decl):
    name: str
    inline: bool
    decls: List[Decl]


@dataclass
class EnumDecl(Decl):
    name: str
    scoped: bool
    underlying_type: TypeRef
    enumerators: List[Enumerator]


@dataclass
class UsingAliasDecl(Decl):
    name: str
    aliased_type: TypeRef


@dataclass
class FieldDecl(Decl):
    name: str
    access: str
    type: TypeRef


@dataclass
class ConstructorDecl(Decl):
    access: str
    name: str
    params: List[Param]
    is_const: bool
    is_virtual: bool
    is_pure_virtual: bool
    is_static: bool
    is_noexcept: bool
    is_explicit: bool
    is_default: bool
    is_copy: bool
    is_move: bool


@dataclass
class DestructorDecl(Decl):
    access: str
    name: str
    params: List[Param]
    is_const: bool
    is_virtual: bool
    is_pure_virtual: bool
    is_static: bool
    is_noexcept: bool


@dataclass
class MethodDecl(Decl):
    access: str
    name: str
    return_type: Optional[TypeRef]
    params: List[Param]
    is_const: bool
    is_virtual: bool
    is_pure_virtual: bool
    is_static: bool
    is_noexcept: bool


@dataclass
class RecordDecl(Decl):
    name: str
    access: str
    is_abstract: bool
    bases: List[BaseSpec]
    template_params: List[TemplateParam]
    members: List[Decl]


@dataclass
class ClassTemplateDecl(Decl):
    name: str
    template_params: List[TemplateParam]
    bases: List[BaseSpec]
    members: List[Decl]
    access: str


@dataclass
class FunctionDecl(Decl):
    name: str
    linkage: str
    storage_class: str
    return_type: Optional[TypeRef]
    params: List[Param]
    is_variadic: bool
    is_noexcept: bool
    template_params: List[TemplateParam] = field(default_factory=list)


@dataclass
class GlobalVariableDecl(Decl):
    name: str
    type: TypeRef


@dataclass
class UnknownDecl(Decl):
    raw: Dict[str, Any]


@dataclass
class ProgramFile:
    path: str
    decls: List[Decl]


@dataclass
class Program:
    files: List[ProgramFile]


@dataclass
class DiagnosticLocation:
    file: str
    line: int
    column: int


@dataclass
class Diagnostic:
    severity: int
    category: str
    message: str
    location: Optional[DiagnosticLocation] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Diagnostic":
        loc_data = data.get("location")
        location = None
        if isinstance(loc_data, dict):
            location = DiagnosticLocation(
                file=loc_data.get("file", ""),
                line=int(loc_data.get("line", 0)),
                column=int(loc_data.get("column", 0)),
            )
        return Diagnostic(
            severity=int(data.get("severity", 0)),
            category=data.get("category", ""),
            message=data.get("message", ""),
            location=location,
        )


@dataclass
class ClangAst:
    program: Program
    diagnostics: List[Diagnostic] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClangAst":
        program_data = data.get("program", {})
        files = []
        for file_data in program_data.get("files", []):
            decls = [_parse_decl(decl) for decl in file_data.get("decls", [])]
            files.append(ProgramFile(path=file_data.get("file", ""), decls=decls))

        diags = [Diagnostic.from_dict(diag) for diag in data.get("diagnostics", [])]
        return cls(program=Program(files=files), diagnostics=diags)

    def walk_decls(self) -> Iterable[Decl]:
        for program_file in self.program.files:
            yield from _walk_decls(program_file.decls)


def _parse_template_params(items: List[Dict[str, Any]]) -> List[TemplateParam]:
    return [TemplateParam.from_dict(item) for item in items or []]


def _parse_params(items: List[Dict[str, Any]]) -> List[Param]:
    return [Param.from_dict(item) for item in items or []]


def _parse_decl(data: Dict[str, Any]) -> Decl:
    kind = data.get("kind", "unknown")

    if kind == "include":
        return IncludeDecl(kind=kind, spelling=data.get("spelling", ""), is_system=bool(data.get("is_system", False)))

    if kind == "namespace":
        return NamespaceDecl(
            kind=kind,
            name=data.get("name", ""),
            inline=bool(data.get("inline", False)),
            decls=[_parse_decl(child) for child in data.get("decls", [])],
        )

    if kind == "enum":
        return EnumDecl(
            kind=kind,
            name=data.get("name", ""),
            scoped=bool(data.get("scoped", False)),
            underlying_type=TypeRef.from_dict(data.get("underlying_type")),
            enumerators=[
                Enumerator(name=item.get("name", ""), value=item.get("value"))
                for item in data.get("enumerators", [])
            ],
        )

    if kind == "using_alias":
        return UsingAliasDecl(
            kind=kind,
            name=data.get("name", ""),
            aliased_type=TypeRef.from_dict(data.get("aliased_type")),
        )

    if kind in {"field", "static_field"}:
        return FieldDecl(
            kind=kind,
            name=data.get("name", ""),
            access=data.get("access", "public"),
            type=TypeRef.from_dict(data.get("type")),
        )

    if kind == "constructor":
        return ConstructorDecl(
            kind=kind,
            access=data.get("access", "public"),
            name=data.get("name", ""),
            params=_parse_params(data.get("params", [])),
            is_const=bool(data.get("is_const", False)),
            is_virtual=bool(data.get("is_virtual", False)),
            is_pure_virtual=bool(data.get("is_pure_virtual", False)),
            is_static=bool(data.get("is_static", False)),
            is_noexcept=bool(data.get("is_noexcept", False)),
            is_explicit=bool(data.get("is_explicit", False)),
            is_default=bool(data.get("is_default", False)),
            is_copy=bool(data.get("is_copy", False)),
            is_move=bool(data.get("is_move", False)),
        )

    if kind == "destructor":
        return DestructorDecl(
            kind=kind,
            access=data.get("access", "public"),
            name=data.get("name", ""),
            params=_parse_params(data.get("params", [])),
            is_const=bool(data.get("is_const", False)),
            is_virtual=bool(data.get("is_virtual", False)),
            is_pure_virtual=bool(data.get("is_pure_virtual", False)),
            is_static=bool(data.get("is_static", False)),
            is_noexcept=bool(data.get("is_noexcept", False)),
        )

    if kind in {"method", "virtual_function"}:
        return MethodDecl(
            kind=kind,
            access=data.get("access", "public"),
            name=data.get("name", ""),
            return_type=TypeRef.from_dict(data.get("return_type")),
            params=_parse_params(data.get("params", [])),
            is_const=bool(data.get("is_const", False)),
            is_virtual=bool(data.get("is_virtual", kind == "virtual_function")),
            is_pure_virtual=bool(data.get("is_pure_virtual", False)),
            is_static=bool(data.get("is_static", False)),
            is_noexcept=bool(data.get("is_noexcept", False)),
        )

    if kind in {"class", "struct"}:
        return RecordDecl(
            kind=kind,
            name=data.get("name", ""),
            access=data.get("access", "public"),
            is_abstract=bool(data.get("is_abstract", False)),
            bases=[BaseSpec.from_dict(base) for base in data.get("bases", [])],
            template_params=_parse_template_params(data.get("template_params", [])),
            members=[_parse_decl(member) for member in data.get("members", [])],
        )

    if kind == "class_template":
        return ClassTemplateDecl(
            kind=kind,
            name=data.get("name", ""),
            template_params=_parse_template_params(data.get("template_params", [])),
            bases=[BaseSpec.from_dict(base) for base in data.get("bases", [])],
            members=[_parse_decl(member) for member in data.get("members", [])],
            access=data.get("access", "public"),
        )

    if kind in {"function", "function_template"}:
        return FunctionDecl(
            kind=kind,
            name=data.get("name", ""),
            linkage=data.get("linkage", ""),
            storage_class=data.get("storage_class", ""),
            return_type=TypeRef.from_dict(data.get("return_type")),
            params=_parse_params(data.get("params", [])),
            is_variadic=bool(data.get("is_variadic", False)),
            is_noexcept=bool(data.get("is_noexcept", False)),
            template_params=_parse_template_params(data.get("template_params", [])),
        )

    if kind == "global_variable":
        return GlobalVariableDecl(
            kind=kind, name=data.get("name", ""), type=TypeRef.from_dict(data.get("type"))
        )

    return UnknownDecl(kind=kind, raw=data)


def _walk_decls(decls: Iterable[Decl]) -> Iterable[Decl]:
    for decl in decls:
        yield decl
        if isinstance(decl, NamespaceDecl):
            yield from _walk_decls(decl.decls)
        elif isinstance(decl, RecordDecl):
            yield from _walk_decls(decl.members)
        elif isinstance(decl, ClassTemplateDecl):
            yield from _walk_decls(decl.members)


def load_clang_ast(path: Path) -> ClangAst:
    data = json.loads(Path(path).read_text())
    return ClangAst.from_dict(data)


def summarize(ast: ClangAst, show_records: bool = False) -> None:
    kind_counts: Dict[str, int] = {}
    record_names: List[str] = []

    for decl in ast.walk_decls():
        kind_counts[decl.kind] = kind_counts.get(decl.kind, 0) + 1
        if isinstance(decl, (RecordDecl, ClassTemplateDecl)):
            record_names.append(decl.name)

    print(f"Files parsed: {len(ast.program.files)}")
    print(f"Total declarations (including nested): {sum(kind_counts.values())}")
    if kind_counts:
        print("Declaration counts:")
        for kind, count in sorted(kind_counts.items(), key=lambda item: item[1], reverse=True):
            print(f"  {kind}: {count}")

    if ast.diagnostics:
        print(f"Diagnostics: {len(ast.diagnostics)}")
        for diag in ast.diagnostics[:5]:
            loc = f"{diag.location.file}:{diag.location.line}" if diag.location else "unknown"
            print(f"  [{diag.severity}] {loc} - {diag.message}")
        if len(ast.diagnostics) > 5:
            print(f"  ... {len(ast.diagnostics) - 5} more")

    if show_records and record_names:
        limit = 25
        print("Records:")
        for name in record_names[:limit]:
            print(f"  - {name}")
        if len(record_names) > limit:
            print(f"  ... {len(record_names) - limit} more")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert clang_ast_to_json.py output into Python objects and print a summary."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="ast.json",
        help="Path to the JSON file emitted by clang_ast_to_json.py (default: ast.json)",
    )
    parser.add_argument(
        "--no-summary",
        dest="summary",
        action="store_false",
        help="Skip printing a summary after loading the AST.",
    )
    parser.add_argument(
        "--records",
        dest="records",
        action="store_true",
        help="List class/struct names in the summary output.",
    )
    args = parser.parse_args()

    ast = load_clang_ast(Path(args.input))
    if args.summary:
        summarize(ast, show_records=args.records)


if __name__ == "__main__":
    main()
