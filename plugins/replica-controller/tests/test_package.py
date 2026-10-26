from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from package_web import package

class PackageTests(unittest.TestCase):
    def test_web_archive_contains_all_entry_skills_and_no_runtime_caches(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'portable.zip'
            result=package(output)
            self.assertEqual(result['skills'],15)
            with zipfile.ZipFile(output) as archive:
                names=archive.namelist()
                self.assertEqual(sum(n.endswith('/SKILL.md') for n in names),15)
                for name in ('replica-workflow','superpowers-workflow','arena-workflow','replica-power-arena'):
                    self.assertIn('skills/'+name+'/agents/openai.yaml',names)
                self.assertIn('scripts/workflow.py',names)
                self.assertFalse(any('__pycache__' in n or n.endswith('.pyc') for n in names))

if __name__=='__main__': unittest.main()
