"""Focused regressions for the implicit-invocation metadata and plan boundary."""
import ast
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('workflow_security',ROOT/'scripts/workflows.py')
workflow=importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)

class SecurityBoundaryTests(unittest.TestCase):
    def test_agent_metadata_does_not_add_tools_permissions_or_commands(self):
        expected={'interface','display_name','short_description','default_prompt','policy','allow_implicit_invocation'}
        files=list((ROOT/'skills').glob('*/agents/openai.yaml'))
        self.assertEqual(len(files),44)
        for path in files:
            with self.subTest(path=path.relative_to(ROOT)):
                text=path.read_text(encoding='utf-8')
                keys=set(re.findall(r'^\s*([a-z_]+):',text,re.M))
                self.assertEqual(keys,expected)
                self.assertIn('allow_implicit_invocation: true',text)
                self.assertNotIn('allowed-tools:',text)

    def test_plan_is_declarative_for_every_registered_repository(self):
        tree=ast.parse((ROOT/'scripts/workflows.py').read_text(encoding='utf-8'))
        plan_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='plan')
        forbidden={'eval','exec','compile','open','subprocess','socket','requests','urllib','system','popen'}
        names={n.id for n in ast.walk(plan_node) if isinstance(n,ast.Name)}
        self.assertFalse(names & forbidden)
        rows=json.loads((ROOT/'registry.json').read_text(encoding='utf-8'))
        for row in rows:
            for intent in workflow.INTENTS:
                for mode in ('individual','combined'):
                    result=workflow.plan(rows,row['repository'],intent,mode)
                    self.assertEqual(result['status'],'PLAN_ONLY')
                    self.assertFalse(result['executed'])
                    self.assertFalse(result['background_enabled'])

if __name__=='__main__': unittest.main()
