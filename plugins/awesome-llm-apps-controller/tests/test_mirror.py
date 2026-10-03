import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / 'plugins' / 'awesome-llm-apps-controller' / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from awesome_llm_apps_mirror import copy_mirror, plan_mirror


def _write(path: Path, data=b'x'):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding='utf-8')
    else:
        path.write_bytes(data)


def _fixture(tmp_path: Path) -> Path:
    root = tmp_path / 'upstream'
    _write(root / 'README.md', '# Demo')
    _write(root / 'src' / 'app.py', 'print("ok")\n')
    _write(root / 'requirements.txt', 'openai\n')
    _write(root / 'agent_skills' / 'demo' / 'SKILL.md', '---\nname: demo\n---\n')
    for d in ['.git', 'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache', '.next', 'dist', 'build']:
        _write(root / d / 'ignored.bin', b'ignored')
    _write(root / 'docs' / 'small.png', b'png')
    with (root / 'docs' / 'large.gif').open('wb') as f:
        f.truncate(10 * 1024 * 1024 + 1)
    (root / 'links').mkdir(parents=True)
    os.symlink('../src/app.py', root / 'links' / 'inside.py')
    outside = tmp_path / 'outside.txt'
    _write(outside, 'outside')
    os.symlink(str(outside), root / 'links' / 'outside.txt')
    return root


def test_mirror_includes_normal_source_manifest_readme_and_skill(tmp_path):
    plan = {item['path']: item for item in plan_mirror(_fixture(tmp_path))}
    for path in ['README.md', 'src/app.py', 'requirements.txt', 'agent_skills/demo/SKILL.md', 'docs/small.png']:
        assert plan[path]['action'] == 'include'


def test_mirror_excludes_generated_and_dependency_directories_with_stable_reasons(tmp_path):
    plan = plan_mirror(_fixture(tmp_path))
    excluded = {item['path']: item['reason'] for item in plan if item['action'] == 'exclude'}
    for d in ['.git', 'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache', '.next', 'dist', 'build']:
        assert excluded[f'{d}/ignored.bin'] == f'excluded_directory:{d}'


def test_mirror_excludes_large_demo_media_but_keeps_small_image(tmp_path):
    plan = {item['path']: item for item in plan_mirror(_fixture(tmp_path))}
    assert plan['docs/large.gif']['action'] == 'exclude'
    assert plan['docs/large.gif']['reason'] == 'large_demo_media'
    assert plan['docs/small.png']['action'] == 'include'


def test_mirror_preserves_safe_symlink_and_rejects_escaping_symlink(tmp_path):
    root = _fixture(tmp_path)
    plan = {item['path']: item for item in plan_mirror(root)}
    assert plan['links/inside.py']['action'] == 'symlink'
    assert plan['links/outside.txt']['action'] == 'exclude'
    assert plan['links/outside.txt']['reason'] == 'unsafe_symlink'
    dest = tmp_path / 'mirror'
    report = copy_mirror(root, dest, list(plan.values()))
    assert (dest / 'links' / 'inside.py').is_symlink()
    assert os.readlink(dest / 'links' / 'inside.py') == '../src/app.py'
    assert not (dest / 'links' / 'outside.txt').exists()
    assert any(x['path'] == 'links/outside.txt' and x['reason'] == 'unsafe_symlink' for x in report['excluded'])


def test_exclusion_records_have_required_provenance_fields(tmp_path):
    excluded = [x for x in plan_mirror(_fixture(tmp_path)) if x['action'] == 'exclude']
    assert excluded
    for item in excluded:
        assert {'path', 'git_sha', 'size', 'reason', 'upstream_commit'} <= item.keys()
