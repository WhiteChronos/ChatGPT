import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('separate',ROOT/'scripts/separate.py')
separate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(separate)

class IndividualPluginTests(unittest.TestCase):
    def test_each_plugin_has_only_its_repository_and_own_readme(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'plugins';packages=Path(t)/'packages'
            report=separate.generate(ROOT,target,packages)
            self.assertEqual(len(report),43)
            names=set()
            for item in report:
                folder=target/item['name']
                manifest=json.loads((folder/'plugin.json').read_text(encoding='utf-8'))
                self.assertNotIn(manifest['name'],names);names.add(manifest['name'])
                skills=list((folder/'skills').glob('*/SKILL.md'))
                self.assertEqual(len(skills),1)
                self.assertEqual(skills[0].parent.name,item['name'])
                self.assertIn(item['repository'],(folder/'README.md').read_text(encoding='utf-8'))
                workflow=json.loads((folder/'workflow.json').read_text(encoding='utf-8'))
                self.assertEqual(workflow['repository'],item['repository'])
                self.assertEqual(workflow['individual']['steps'],[item['name']])
                self.assertFalse(workflow['individual']['executed'])
                self.assertEqual(workflow['integrations']['rea']['when'],'static-analysis-requested')
                with zipfile.ZipFile(packages/item['zip']) as z:
                    self.assertIn('workflow.json',z.namelist())
                    self.assertEqual(len([p for p in z.namelist() if p.endswith('/SKILL.md')]),1)
                    self.assertFalse(any('repository-systems-workflow' in p for p in z.namelist()))
                    self.assertEqual(json.loads(z.read('plugin.json'))['name'],item['name'])

    def test_generation_preserves_input_skill(self):
        row=json.loads((ROOT/'registry.json').read_text(encoding='utf-8'))[0]
        source=ROOT/'skills'/row['skill_name']/'SKILL.md'
        before=source.read_bytes()
        with tempfile.TemporaryDirectory() as t:
            separate.generate(ROOT,Path(t)/'plugins',Path(t)/'packages')
        self.assertEqual(before,source.read_bytes())

    def test_output_inside_source_skills_is_rejected(self):
        with self.assertRaises(ValueError):
            separate.generate(ROOT,ROOT/'skills'/'bad-output',ROOT/'bad-packages')

    def test_checked_in_copies_preserve_source_metadata_and_provenance(self):
        rows=json.loads((ROOT/'registry.json').read_text(encoding='utf-8'))
        for row in rows:
            name=row['skill_name'];plugin=ROOT/'individual'/name
            self.assertTrue((plugin/'plugin.json').is_file())
            for rel in ('SKILL.md','agents/openai.yaml','references/source.json'):
                self.assertEqual((ROOT/'skills'/name/rel).read_bytes(),
                                 (plugin/'skills'/name/rel).read_bytes(),name+'/'+rel)

if __name__=='__main__': unittest.main()

