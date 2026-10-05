#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_model import CapabilityRegistry
from runtime.capability_registry import load_capability_registry


@dataclass(frozen=True)
class DependencyViolation:
    provider_id: str
    implementation_version: str
    source_file: str
    target_provider_id: str
    reason: str


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _module_aliases(provider_id: str, root: Path, repo_root: Path) -> tuple[str, ...]:
    values = {provider_id, provider_id.replace("-", "_"), root.name, root.name.replace("-", "_")}
    try:
        relative = root.relative_to(repo_root)
    except ValueError:
        relative = None
    if relative is not None:
        dotted_parts = tuple(part.replace("-", "_") for part in relative.parts)
        if dotted_parts and all(part.isidentifier() for part in dotted_parts):
            values.add(".".join(dotted_parts))
    return tuple(sorted(
        value for value in values
        if value and (value.isidentifier() or all(part.isidentifier() for part in value.split(".")))
    ))


def _matches_module(module: str, aliases: tuple[str, ...]) -> bool:
    return any(module == alias or module.startswith(alias + ".") for alias in aliases)


def _literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _literal_hits_root(literal: str, *, repo_root: Path, source_file: Path, target_root: Path) -> bool:
    raw = Path(literal.replace("\\", "/"))
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw.resolve(strict=False))
    else:
        candidates.append((repo_root / raw).resolve(strict=False))
        candidates.append((source_file.parent / raw).resolve(strict=False))
    return any(_inside(candidate, target_root) for candidate in candidates)


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        if parent is None:
            return None
        return f"{parent}.{node.attr}"
    return None


def _call_name(node: ast.Call) -> str | None:
    return _dotted_name(node.func)


def _scan_python_file(
    *,
    repo_root: Path,
    provider_id: str,
    implementation_version: str,
    source_file: Path,
    other_roots: tuple[tuple[str, Path, tuple[str, ...]], ...],
) -> list[DependencyViolation]:
    try:
        tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))
    except (OSError, SyntaxError, UnicodeError) as exc:
        raise ValueError(f"cannot parse provider source {source_file}: {exc}") from exc

    relative_source = source_file.relative_to(repo_root).as_posix()
    findings: list[DependencyViolation] = []

    def add(target_provider_id: str, reason: str) -> None:
        findings.append(DependencyViolation(
            provider_id=provider_id,
            implementation_version=implementation_version,
            source_file=relative_source,
            target_provider_id=target_provider_id,
            reason=reason,
        ))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                for target_provider_id, _target_root, aliases in other_roots:
                    if _matches_module(imported.name, aliases):
                        add(target_provider_id, f"direct import {imported.name}")
        elif isinstance(node, ast.ImportFrom):
            imported_names: list[str] = []
            if node.module:
                imported_names.append(node.module)
                imported_names.extend(f"{node.module}.{item.name}" for item in node.names)
            else:
                imported_names.extend(item.name for item in node.names)
            for imported_name in imported_names:
                for target_provider_id, _target_root, aliases in other_roots:
                    if _matches_module(imported_name, aliases):
                        prefix = "." * node.level
                        add(target_provider_id, f"direct import-from {prefix}{imported_name}")
        elif isinstance(node, ast.Call):
            name = _call_name(node)
            first_literal = _literal_string(node.args[0]) if node.args else None
            if name in {"importlib.import_module", "__import__"} and first_literal is not None:
                for target_provider_id, _target_root, aliases in other_roots:
                    if _matches_module(first_literal, aliases):
                        add(target_provider_id, f"dynamic import {first_literal}")
            if name in {"sys.path.append", "sys.path.insert"}:
                path_literal = first_literal if name == "sys.path.append" else None
                if name == "sys.path.insert" and len(node.args) >= 2:
                    path_literal = _literal_string(node.args[1])
                if path_literal is not None:
                    for target_provider_id, target_root, _aliases in other_roots:
                        if _literal_hits_root(
                            path_literal,
                            repo_root=repo_root,
                            source_file=source_file,
                            target_root=target_root,
                        ):
                            add(target_provider_id, f"sys.path access {path_literal}")
            if name in {"open", "Path", "pathlib.Path"} and first_literal is not None:
                for target_provider_id, target_root, _aliases in other_roots:
                    if _literal_hits_root(
                        first_literal,
                        repo_root=repo_root,
                        source_file=source_file,
                        target_root=target_root,
                    ):
                        add(target_provider_id, f"literal filesystem access {first_literal}")

    unique = {
        (item.provider_id, item.implementation_version, item.source_file, item.target_provider_id, item.reason): item
        for item in findings
    }
    return list(unique.values())


def _local_provider_roots(
    repo_root: Path,
    registry: CapabilityRegistry,
) -> tuple[tuple[tuple[str, str], Path], ...]:
    repo = repo_root.resolve()
    roots: list[tuple[tuple[str, str], Path]] = []
    for key, manifest in registry.providers.items():
        if manifest.source_type != "local":
            continue
        source = Path(manifest.source)
        root = source.resolve(strict=False) if source.is_absolute() else (repo / source).resolve(strict=False)
        if not _inside(root, repo):
            raise ValueError(
                f"local provider source escapes repository: {manifest.provider_id}@{manifest.implementation_version}: {manifest.source}"
            )
        if not root.exists() or not root.is_dir():
            raise ValueError(
                f"local provider source does not exist: {manifest.provider_id}@{manifest.implementation_version}: {manifest.source}"
            )
        roots.append((key, root))

    roots.sort(key=lambda item: item[0])
    for index, (key_a, root_a) in enumerate(roots):
        for key_b, root_b in roots[index + 1:]:
            if root_a == root_b:
                raise ValueError(f"ambiguous identical provider roots: {key_a!r} and {key_b!r}: {root_a}")
            if _inside(root_a, root_b) or _inside(root_b, root_a):
                raise ValueError(f"ambiguous nested provider roots: {key_a!r}={root_a} and {key_b!r}={root_b}")
    return tuple(roots)


def scan_provider_boundaries(
    repo_root: Path,
    registry: CapabilityRegistry,
) -> tuple[DependencyViolation, ...]:
    repo = Path(repo_root).resolve()
    roots = _local_provider_roots(repo, registry)
    violations: list[DependencyViolation] = []

    for (provider_id, implementation_version), root in roots:
        other_roots = tuple(
            (
                other_provider_id,
                other_root,
                _module_aliases(other_provider_id, other_root, repo),
            )
            for (other_provider_id, _other_version), other_root in roots
            if (other_provider_id, _other_version) != (provider_id, implementation_version)
        )
        for source_file in sorted(root.rglob("*.py")):
            if not source_file.is_file():
                continue
            violations.extend(_scan_python_file(
                repo_root=repo,
                provider_id=provider_id,
                implementation_version=implementation_version,
                source_file=source_file.resolve(),
                other_roots=other_roots,
            ))

    return tuple(sorted(
        violations,
        key=lambda item: (
            item.provider_id,
            item.implementation_version,
            item.source_file,
            item.target_provider_id,
            item.reason,
        ),
    ))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enforce WhiteChronos local provider dependency boundaries.")
    parser.add_argument("--repo", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        registry = load_capability_registry(repo)
        violations = scan_provider_boundaries(repo, registry)
    except ValueError as exc:
        print(f"CAPABILITY_DEPENDENCY_POLICY=FAIL: {exc}", file=sys.stderr)
        return 1
    if violations:
        print("CAPABILITY_DEPENDENCY_POLICY=FAIL")
        for violation in violations:
            print(
                f"{violation.provider_id}@{violation.implementation_version} "
                f"{violation.source_file} -> {violation.target_provider_id}: {violation.reason}"
            )
        return 1
    print("CAPABILITY_DEPENDENCY_POLICY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
