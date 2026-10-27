import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import sys

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
SCHEMA=json.loads((ROOT/'schemas/agent-plugins-1.0.0.schema.json').read_text(encoding='utf-8'))
VALIDATOR=Draft202012Validator(SCHEMA)
spec=importlib.util.spec_from_file_location('separate_compat',ROOT/'scripts/separate.py')
separate=importlib.util.module_from_spec(spec);spec.loader.exec_module(separate)

class WebCompatibilityTests(unittest.TestCase):
    def check_folder(self,folder):
        portable=json.loads((folder/'plugin.json').read_text(encoding='utf-8'))
        errors=list(VALIDATOR.iter_errors(portable))
        self.assertEqual([e.message for e in errors],[],str(folder))
        overlay=json.loads((folder/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(portable['name'],overlay['name'])
        self.assertEqual(portable['version'],overlay['version'])
        self.assertEqual(portable['extensions']['com.openai']['interface'],overlay['interface'])
        self.assertTrue((folder/overlay['skills']).is_dir())
        self.assertNotIn('hooks',portable['extensions']['com.openai'])
        self.assertNotIn('apps',portable['extensions']['com.openai'])

    def test_all_individual_and_joint_manifests_follow_portable_schema(self):
        folders=list((ROOT/'individual').iterdir())
        self.assertEqual(len(folders),43)
        for folder in folders: self.check_folder(folder)
        self.check_folder(ROOT)

    def test_generated_zips_use_portable_manifest_and_preserve_identity(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'plugins';packages=Path(t)/'packages'
            rows=separate.generate(ROOT,out,packages)
            for row in rows:
                self.check_folder(out/row['name'])
                with zipfile.ZipFile(packages/row['zip']) as z:
                    manifest=json.loads(z.read('plugin.json'))
                    self.assertEqual(list(VALIDATOR.iter_errors(manifest)),[])
                    self.assertEqual(manifest['name'],row['name'])

    def test_legacy_root_fields_are_rejected(self):
        invalid={'name':'test','skills':'./skills/','interface':{'displayName':'Test'}}
        self.assertFalse(VALIDATOR.is_valid(invalid))

if __name__=='__main__': unittest.main()
