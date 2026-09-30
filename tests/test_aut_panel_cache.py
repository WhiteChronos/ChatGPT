from pathlib import Path

from pipeline.aut_panel_cache import ContentAddressedCache
from pipeline.context_manifest import sha256_object


def test_content_addressed_cache_hit_miss_and_invalidation(tmp_path):
    material = {"panel_revision": "R02", "li_hash": "abc", "agent_version": "v1"}
    key = sha256_object(material)
    cache = ContentAddressedCache(tmp_path / "cache")

    miss = cache.lookup(key)
    assert miss.status == "MISS"

    stored = cache.store(
        key=key,
        material=material,
        result={"status": "PASS"},
        metadata={"panel": "PN-AUT-01"},
    )
    assert stored.exists()

    hit = cache.lookup(key)
    assert hit.status == "HIT"
    assert hit.payload["material"] == material
    assert hit.payload["result"]["status"] == "PASS"

    assert cache.invalidate(key) is True
    assert cache.lookup(key).status == "MISS"


def test_cache_key_changes_when_material_changes():
    a = sha256_object({"panel_revision": "R02", "li_hash": "A"})
    b = sha256_object({"panel_revision": "R02", "li_hash": "B"})
    assert a != b
