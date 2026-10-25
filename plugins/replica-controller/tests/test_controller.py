import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('replica_controller',ROOT/'scripts/replica.py')
controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)/'package with spaces'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__'))
    def tearDown(self): self.temp.cleanup()

    def test_pinned_package_has_eleven_skills_and_six_tools(self):
        lock=controller.verify_package(self.root)
        self.assertEqual(len(lock['skills']),11)
        self.assertEqual(len(lock['tools']),6)

    def test_tampering_and_parent_escape_are_rejected(self):
        script=self.root/'skills/replica-diff/parity.py'
        script.write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError):controller.verify_package(self.root)
        lock=json.loads((self.root/'upstream-lock.json').read_text())
        lock['files']['../outside']='0'*64
        (self.root/'upstream-lock.json').write_text(json.dumps(lock))
        with self.assertRaises(ValueError):controller.verify_package(self.root)

    def test_dispatches_declared_tool_without_shell_and_rejects_unknown_tool(self):
        result=controller.run_tool(self.root,'contrast',[str(self.root/'skills/replica-design/tokens.json')])
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('0 failing AA',result.stdout)
        with self.assertRaises(ValueError):controller.run_tool(self.root,'arbitrary-command',[])

    def test_existing_skill_is_preserved_and_validation_precedes_installation(self):
        dest=Path(self.temp.name)/'skills'; dest.mkdir()
        existing=dest/'replica-recon'; existing.mkdir();(existing/'SKILL.md').write_text('human')
        with self.assertRaises(FileExistsError):controller.install_skills(self.root,dest)
        self.assertEqual((existing/'SKILL.md').read_text(),'human')
        self.assertFalse((dest/'replica-diff').exists())

    def test_installation_is_idempotent_and_returns_receipt(self):
        dest=Path(self.temp.name)/'new skills'
        first=controller.install_skills(self.root,dest)
        second=controller.install_skills(self.root,dest)
        self.assertEqual(first['installed'],12)
        self.assertEqual(second['already_matching'],12)
        self.assertTrue((dest/'replica-diff/parity.py').exists())

if __name__=='__main__': unittest.main()
