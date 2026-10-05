from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_versioning import SemVer, VersionRange


def test_semver_orders_release_numbers():
    assert SemVer.parse("1.0.0") < SemVer.parse("1.0.1")
    assert SemVer.parse("1.9.9") < SemVer.parse("2.0.0")


def test_semver_prerelease_precedes_release():
    assert SemVer.parse("1.0.0-alpha") < SemVer.parse("1.0.0")


def test_semver_prerelease_follows_semver_identifier_order():
    assert SemVer.parse("1.0.0-alpha.1") < SemVer.parse("1.0.0-alpha.beta")
    assert SemVer.parse("1.0.0-alpha.beta") < SemVer.parse("1.0.0-beta")
    assert SemVer.parse("1.0.0-beta.2") < SemVer.parse("1.0.0-beta.11")


def test_semver_build_metadata_does_not_affect_precedence_or_equality():
    assert SemVer.parse("1.0.0+build.1") == SemVer.parse("1.0.0+build.2")
    assert not (SemVer.parse("1.0.0+build.1") < SemVer.parse("1.0.0+build.2"))


@pytest.mark.parametrize(
    ("range_text", "version", "expected"),
    [
        ("1.2.3", "1.2.3", True),
        ("1.2.3", "1.2.4", False),
        ("=1.2.3", "1.2.3", True),
        ("==1.2.3", "1.2.3", True),
        (">=2.1 <3", "2.9.9", True),
        (">=2.1 <3", "3.0.0", False),
        (">=1.2.0 <2.0.0", "1.9.9", True),
        (">1 <=2.5", "2.5.0", True),
        (">1 <=2.5", "1.0.0", False),
    ],
)
def test_version_range_matches_supported_grammar(range_text, version, expected):
    assert VersionRange.parse(range_text).matches(version) is expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "^1.2.3",
        "~1.2.3",
        "1.2.x",
        ">=1.0.0 || <2.0.0",
        ">=1.0.0,<2.0.0",
        ">=1.2-alpha",
        "1.2",
        "1",
    ],
)
def test_version_range_rejects_unsupported_or_ambiguous_syntax(value):
    with pytest.raises(ValueError):
        VersionRange.parse(value)


def test_comparator_partial_versions_are_zero_filled():
    assert VersionRange.parse(">=2.1 <3").matches("2.1.0")
    assert not VersionRange.parse(">=2.1 <3").matches("2.0.99")


def test_prerelease_operand_requires_full_three_component_version():
    with pytest.raises(ValueError):
        VersionRange.parse(">=1.2-alpha")
    assert VersionRange.parse(">=1.2.0-alpha").matches("1.2.0-alpha.1")
