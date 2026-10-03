from pathlib import Path
import os, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from awesome_llm_apps_mirror import plan_mirror, copy_mirror

def test_mirror_excludes_generated_and_large_media_and_unsafe_symlink(tmp_path):
    src=tmp_path/'src'; dst=tmp_path/'dst'; src.mkdir()
    (src/'README.md').write_text('ok')
    (src/'node_modules').mkdir(); (src/'node_modules'/'x.js').write_text('x')
    (src/'small.png').write_bytes(b'x'*10)
    (src/'large.gif').write_bytes(b'x'*(10*1024*1024+1))
    outside=tmp_path/'outside.txt'; outside.write_text('secret')
    os.symlink(outside, src/'escape')
    plan=plan_mirror(src)
    reasons={x['path']:x['reason'] for x in plan if x['action']=='exclude'}
    assert reasons['node_modules/x.js']=='generated_or_dependency_dir'
    assert 'node_modules' not in reasons
    assert reasons['large.gif']=='large_demo_media'
    assert reasons['escape']=='unsafe_symlink'
    result=copy_mirror(src,dst,plan,'abc')
    assert (dst/'README.md').exists()
    assert (dst/'small.png').exists()
    assert not (dst/'large.gif').exists()
    assert any(x['path']=='escape' for x in result['excluded'])
    assert any(x['path']=='node_modules/x.js' for x in result['excluded'])
    assert result['included_files'] == 2
    assert result['excluded_files'] == 3
