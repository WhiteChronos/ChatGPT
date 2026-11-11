import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('workflow',ROOT/'scripts/workflow.py')
workflow=importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)

class WorkflowTests(unittest.TestCase):
    def test_individual_modes_are_isolated(self):
        for mode in ('replica','superpowers','arena'):
            with self.subTest(mode=mode):
                plan=workflow.plan(mode,'build-from-reference')
                self.assertEqual({s['system'] for s in plan['steps']},{mode})
                self.assertFalse(plan['executed'])

    def test_automatic_routes_and_bugfix_does_not_force_replica(self):
        reference=workflow.plan('auto','build-from-reference')
        self.assertEqual(reference['selected_mode'],'combined')
        bug=workflow.plan('auto','bugfix')
        self.assertEqual(bug['steps'][0]['name'],'systematic-debugging')
        self.assertNotIn('replica',{s['system'] for s in bug['steps']})
        self.assertEqual(workflow.plan('auto','compare')['selected_mode'],'replica')
        self.assertEqual(workflow.plan('auto','review')['selected_mode'],'arena')

    def test_unknown_intent_and_mode_rejected(self):
        with self.assertRaises(ValueError): workflow.plan('auto','arbitrary shell')
        with self.assertRaises(ValueError): workflow.plan('unsafe','bugfix')

    def test_complex_arena_is_planning_not_agent_dispatch(self):
        result=workflow.plan('arena','review',complex_review=True)
        self.assertIn('arena_cards',[s['name'] for s in result['steps']])
        self.assertFalse(result['agents_started'])
        self.assertFalse(result['background_enabled'])

    def test_doctor_reports_missing_and_present_files_without_running(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            plan=workflow.plan('replica','compare')
            self.assertEqual(workflow.doctor(plan,[root])['status'],'BLOCKED')
            target=root/'replica-diff'
            target.mkdir();(target/'SKILL.md').write_text('skill',encoding='utf-8')
            result=workflow.doctor(plan,[root])
            self.assertEqual(result['status'],'LOCAL_FILES_PRESENT')
            self.assertFalse(result['host_discovery_verified'])

if __name__=='__main__': unittest.main()
