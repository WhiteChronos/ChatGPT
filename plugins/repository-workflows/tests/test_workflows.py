import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile
import sys

script=Path(__file__).with_name('build.py')
if not script.exists(): script=Path(__file__).resolve().parents[1]/'scripts/workflows.py'
sys.path.insert(0,str(script.parent))
spec = importlib.util.spec_from_file_location('workflows', script)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

class WorkflowsTest(unittest.TestCase):
    def setUp(self):
        self.rows = [{'repository':'owner/repo','skill_name':'wf-owner-repo','skills':[{'path':'skills/a/SKILL.md'}]}]
    def test_exact_target_required(self):
        with self.assertRaises(ValueError): w.plan(self.rows, 'repo', 'review', 'individual')
        with self.assertRaises(ValueError): w.plan(self.rows, 'owner/repo', 'arbitrary shell', 'individual')
    def test_individual_is_independent(self):
        p = w.plan(self.rows, 'owner/repo', 'bugfix', 'individual')
        self.assertEqual(p['steps'], ['wf-owner-repo'])
        self.assertFalse(p['executed'])
    def test_rea_only_for_declared_static_analysis(self):
        self.assertNotIn('whitechronos-lab',w.plan(self.rows,'owner/repo','feature','combined')['steps'])
        p=w.plan(self.rows,'owner/repo','static-analysis','combined')
        self.assertIn('whitechronos-lab',p['steps'])
        self.assertFalse(p['executed'])
    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError): w.plan(self.rows,'owner/repo','review','daemon')
    def test_installation_preflight_preserves_human_files(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); src=root/'src'; dst=root/'dst'
            (src/'a').mkdir(parents=True);(src/'a'/'SKILL.md').write_text('new')
            (src/'b').mkdir();(src/'b'/'SKILL.md').write_text('new')
            (dst/'b').mkdir(parents=True);(dst/'b'/'SKILL.md').write_text('human')
            with self.assertRaises(FileExistsError): w.install(src,dst)
            self.assertFalse((dst/'a').exists())
            self.assertEqual((dst/'b'/'SKILL.md').read_text(),'human')
    def test_unsafe_repo_path_rejected(self):
        with self.assertRaises(ValueError): w.slug('../escape')
    def test_zip_is_portable_and_has_expected_entry(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'skills'/'wf-owner-repo').mkdir(parents=True)
            (root/'skills'/'wf-owner-repo'/'SKILL.md').write_text('skill')
            z=root/'out.zip';w.package(root,z,'Test',['wf-owner-repo'])
            with zipfile.ZipFile(z) as f:
                self.assertIn('plugin.json',f.namelist())
                self.assertIn('skills/wf-owner-repo/SKILL.md',f.namelist())
                self.assertFalse(any('inventory' in n or '__pycache__' in n for n in f.namelist()))
                import json
                self.assertEqual(json.loads(f.read('plugin.json'))['name'],'wf-owner-repo')
    def test_registry_and_generated_adapters_match(self):
        import json
        root=Path(__file__).resolve().parents[1]
        if not (root/'registry.json').exists(): root=Path(__file__).parent/'repository-workflows'
        if not (root/'registry.json').exists(): self.skipTest('Generated registry not present')
        rows=json.loads((root/'registry.json').read_text(encoding='utf-8'))
        names=[r['skill_name'] for r in rows]
        self.assertEqual(len(names),len(set(names)))
        for r in rows:
            folder=root/'skills'/r['skill_name']
            self.assertTrue((folder/'SKILL.md').is_file())
            self.assertIn('$'+r['skill_name'],(folder/'agents/openai.yaml').read_text(encoding='utf-8'))
            source=json.loads((folder/'references/source.json').read_text(encoding='utf-8'))
            self.assertEqual(source['repository'],r['repository'])
            self.assertEqual(source['runtime'],'NOT_VERIFIED')

if __name__=='__main__': unittest.main()
