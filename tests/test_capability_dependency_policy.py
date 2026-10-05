from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_model import CapabilityManifest, CapabilityRegistry, RiskProfile

MODULE = REPO / "pipeline" / "capability_dependency_policy.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("capability_dependency_policy", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load capability dependency policy module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _manifest(provider_id: str, source: str, version: str = "1.0.0") -> CapabilityManifest:
    return CapabilityManifest(
        provider_id=provider_id,
        display_name=provider_id,
        implementation_version=version,
        source_type="local",
        source=source,
        revision="deadbeef",
        digest="sha256:" + "a" * 64,
        license_status="MIT",
        provides=(),
        requires=(),
        risk_profile=RiskProfile("NONE", False, False, False, False, "NONE", False, False, False),
        extensions={},
    )


def _registry(*entries: tuple[str, str]) -> CapabilityRegistry:
    providers = {
        (provider_id, "1.0.0"): _manifest(provider_id, source)
        for provider_id, source in entries
    }
    return CapabilityRegistry(contracts={}, providers=providers, events=(), lifecycle={}, adapters={})


def _repo_with_two_providers(tmp_path: Path, provider_a_source: str) -> tuple[Path, CapabilityRegistry]:
    repo = tmp_path / "repo"
    (repo / "plugins/provider-a").mkdir(parents=True)
    (repo / "plugins/provider-b").mkdir(parents=True)
    (repo / "plugins/provider-a/main.py").write_text(provider_a_source, encoding="utf-8")
    (repo / "plugins/provider-b/private.py").write_text("SECRET = 1\n", encoding="utf-8")
    (repo / "plugins/provider-b/private.json").write_text("{}\n", encoding="utf-8")
    return repo, _registry(
        ("provider-a", "plugins/provider-a"),
        ("provider-b", "plugins/provider-b"),
    )


@pytest.mark.parametrize(
    "source",
    [
        "from provider_b import internal\n",
        "import provider_b.internal\n",
        "from plugins import provider_b\n",
        "from ..provider_b import internal\n",
        "from .. import provider_b\n",
        'import importlib\nimportlib.import_module("provider_b.internal")\n',
        '__import__("provider_b.internal")\n',
        'import sys\nsys.path.append("plugins/provider-b")\n',
        'import sys\nsys.path.insert(0, "plugins/provider-b")\n',
        'from pathlib import Path\nPath("plugins/provider-b/private.json")\n',
        'from pathlib import Path\nPath(r"plugins\\provider-b\\private.json")\n',
        'open("plugins/provider-b/private.json")\n',
        'open(r"plugins\\provider-b\\private.json")\n',
    ],
)
def test_cross_provider_private_access_is_rejected(tmp_path, source):
    module = _load_module()
    repo, registry = _repo_with_two_providers(tmp_path, source)
    violations = module.scan_provider_boundaries(repo, registry)
    assert violations
    assert violations[0].provider_id == "provider-a"
    assert violations[0].target_provider_id == "provider-b"


def test_provider_may_reference_its_own_source_root(tmp_path):
    module = _load_module()
    source = 'from pathlib import Path\nPath("plugins/provider-a/private.json")\n'
    repo, registry = _repo_with_two_providers(tmp_path, source)
    (repo / "plugins/provider-a/private.json").write_text("{}\n", encoding="utf-8")
    assert module.scan_provider_boundaries(repo, registry) == ()


def test_local_provider_source_must_not_escape_repository(tmp_path):
    module = _load_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(ValueError, match="escape|outside|repository"):
        module.scan_provider_boundaries(repo, _registry(("provider-a", "../outside")))


def test_local_provider_source_must_exist(tmp_path):
    module = _load_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(ValueError, match="does not exist|missing"):
        module.scan_provider_boundaries(repo, _registry(("provider-a", "plugins/missing")))


def test_identical_provider_roots_fail_closed(tmp_path):
    module = _load_module()
    repo = tmp_path / "repo"
    (repo / "plugins/shared").mkdir(parents=True)
    registry = _registry(("provider-a", "plugins/shared"), ("provider-b", "plugins/shared"))
    with pytest.raises(ValueError, match="identical|overlap|ambiguous"):
        module.scan_provider_boundaries(repo, registry)


def test_nested_provider_roots_fail_closed(tmp_path):
    module = _load_module()
    repo = tmp_path / "repo"
    (repo / "plugins/provider-a/nested").mkdir(parents=True)
    registry = _registry(
        ("provider-a", "plugins/provider-a"),
        ("provider-b", "plugins/provider-a/nested"),
    )
    with pytest.raises(ValueError, match="nested|overlap|ambiguous"):
        module.scan_provider_boundaries(repo, registry)


def test_empty_repository_registry_v2_has_no_boundary_violations():
    module = _load_module()
    from runtime.capability_registry import load_capability_registry

    registry = load_capability_registry(REPO)
    assert module.scan_provider_boundaries(REPO, registry) == ()
