from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
import re


_FULL_SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_COMPARATOR_RE = re.compile(r"^(==|=|>=|<=|>|<)?(.+)$")
_PARTIAL_RELEASE_RE = re.compile(r"^(0|[1-9][0-9]*)(?:\.(0|[1-9][0-9]*))?(?:\.(0|[1-9][0-9]*))?$")


def _prerelease_key(parts: tuple[str, ...]) -> tuple[tuple[int, object], ...]:
    if not parts:
        return ((2, 0),)
    result: list[tuple[int, object]] = []
    for part in parts:
        if part.isdigit():
            result.append((0, int(part)))
        else:
            result.append((1, part))
    result.append((-1, len(parts)))
    return tuple(result)


@total_ordering
@dataclass(frozen=True, eq=False)
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    @classmethod
    def parse(cls, value: str) -> "SemVer":
        if not isinstance(value, str):
            raise ValueError(f"version must be a SemVer string: {value!r}")
        match = _FULL_SEMVER_RE.fullmatch(value)
        if match is None:
            raise ValueError(f"invalid SemVer: {value!r}")
        prerelease = tuple(match.group(4).split(".")) if match.group(4) else ()
        build = tuple(match.group(5).split(".")) if match.group(5) else ()
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=prerelease,
            build=build,
        )

    def precedence_key(self) -> tuple[object, ...]:
        return (self.major, self.minor, self.patch, _prerelease_key(self.prerelease))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return self.precedence_key() == other.precedence_key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return self.precedence_key() < other.precedence_key()

    def __hash__(self) -> int:
        return hash(self.precedence_key())


@dataclass(frozen=True)
class VersionComparator:
    operator: str
    version: SemVer

    def matches(self, version: SemVer) -> bool:
        if self.operator in {"=", "=="}:
            return version == self.version
        if self.operator == ">=":
            return version >= self.version
        if self.operator == "<=":
            return version <= self.version
        if self.operator == ">":
            return version > self.version
        if self.operator == "<":
            return version < self.version
        raise ValueError(f"unsupported comparator operator: {self.operator!r}")


@dataclass(frozen=True)
class VersionRange:
    comparators: tuple[VersionComparator, ...]

    @classmethod
    def parse(cls, value: str) -> "VersionRange":
        if not isinstance(value, str) or not value.strip():
            raise ValueError("version range must be non-empty")
        text = value.strip()
        if any(token in text for token in ("||", ",", "^", "~", "*")) or re.search(r"(?:^|[.])x(?:$|[.])", text, re.IGNORECASE):
            raise ValueError(f"unsupported version range syntax: {value!r}")

        tokens = text.split()
        comparators: list[VersionComparator] = []
        for token in tokens:
            match = _COMPARATOR_RE.fullmatch(token)
            if match is None:
                raise ValueError(f"invalid version comparator: {token!r}")
            operator = match.group(1)
            operand = match.group(2)
            if operator is None:
                version = SemVer.parse(operand)
                operator = "=="
            else:
                version = _parse_comparator_operand(operand)
            comparators.append(VersionComparator(operator=operator, version=version))

        if not comparators:
            raise ValueError("version range must contain at least one comparator")
        return cls(comparators=tuple(comparators))

    def matches(self, version: str | SemVer) -> bool:
        candidate = SemVer.parse(version) if isinstance(version, str) else version
        if not isinstance(candidate, SemVer):
            raise ValueError(f"version must be SemVer or str: {version!r}")
        return all(comparator.matches(candidate) for comparator in self.comparators)


def _parse_comparator_operand(value: str) -> SemVer:
    if "-" in value or "+" in value:
        return SemVer.parse(value)
    match = _PARTIAL_RELEASE_RE.fullmatch(value)
    if match is None:
        raise ValueError(f"invalid comparator version: {value!r}")
    return SemVer(
        major=int(match.group(1)),
        minor=int(match.group(2) or 0),
        patch=int(match.group(3) or 0),
    )
