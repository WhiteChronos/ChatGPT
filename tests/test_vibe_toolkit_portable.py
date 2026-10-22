"""Portable reference retrieval must work without MCP, pip or network."""
import hashlib
import asyncio
from importlib.util import find_spec
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = ROOT / 'plugins' / 'vibe-coding-toolkit'
CLI = TOOLKIT / 'reference.py'


class PortableToolkitTests(unittest.TestCase):
    def run_reference(self, *args, cwd=None):
        self.assertTrue(CLI.is_file(), 'Portable reference CLI is missing')
        return subprocess.run([sys.executable, '-I', '-S', str(CLI), *args],
                              cwd=cwd or ROOT, capture_output=True, text=True,
                              encoding='utf-8', timeout=20)

    def test_search_and_fetch_without_site_packages_from_other_directory(self):
        found = self.run_reference('search', 'Graphify', cwd=ROOT.parent)
        self.assertEqual(found.returncode, 0, found.stderr)
        ids = [d['id'] for d in json.loads(found.stdout)['results']]
        self.assertIn('docs/tools/07-graphify.md', ids)
        result = self.run_reference('fetch', 'docs/tools/07-graphify.md', cwd=ROOT.parent)
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = json.loads(result.stdout)
        self.assertIn('Graphify', doc['text'])
        self.assertEqual(doc['metadata']['execution_route'], 'local_reference')
        self.assertNotIn('verification_code', doc['metadata'])
        self.assertEqual(doc['metadata']['source_sha256'],
                         '8315f73c5922e4c7a44d1b96077416354fe517d25d344e080cd169507c1ca236')

    def test_rejects_unknown_path_and_empty_query(self):
        for args in [('fetch', '../.env.local'), ('fetch', 'C:/Windows/win.ini'),
                     ('search', ''), ('search', 'x' * 501)]:
            with self.subTest(args=args):
                result = self.run_reference(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('error', json.loads(result.stdout))
                self.assertNotIn('Traceback', result.stderr)

    def test_snapshot_and_all_documents_have_verified_content(self):
        self.assertTrue((TOOLKIT / 'documents.json').is_file(), 'Portable snapshot missing')
        data = json.loads((TOOLKIT / 'documents.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data), 107)
        provenance = json.loads((TOOLKIT / 'provenance.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256((TOOLKIT / 'documents.json').read_bytes()).hexdigest(),
                         provenance['catalog_sha256'])
        for key, doc in data.items():
            self.assertEqual(doc['id'], key)
            self.assertEqual(hashlib.sha256(doc['text'].encode()).hexdigest(), doc['sha256'], key)

    @unittest.skipUnless(find_spec('packaging'), 'Requirement marker check uses packaging from pytest')
    def test_windows_dependency_is_excluded_on_remote_hosts(self):
        from packaging.requirements import Requirement
        lines = (TOOLKIT / 'requirements-lock.txt').read_text(encoding='utf-8').splitlines()
        requirement = next(Requirement(line) for line in lines if line.startswith('pywin32'))
        self.assertIsNotNone(requirement.marker, 'Windows dependency is unconditional')
        self.assertTrue(requirement.marker.evaluate({'sys_platform': 'win32'}))
        self.assertFalse(requirement.marker.evaluate({'sys_platform': 'linux'}))
        self.assertFalse(requirement.marker.evaluate({'sys_platform': 'darwin'}))

    def test_mcp_launcher_reports_missing_dependency_without_installing(self):
        launcher = TOOLKIT / 'launch_mcp.py'
        self.assertTrue(launcher.is_file(), 'Portable MCP launcher missing')
        result = subprocess.run([sys.executable, '-I', '-S', str(launcher)],
                                capture_output=True, text=True, encoding='utf-8', timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertIn('MCP_SDK_UNAVAILABLE', result.stderr)
        self.assertEqual(result.stdout, '')

    @unittest.skipUnless(find_spec('mcp'), 'Optional MCP SDK is not installed in this test interpreter')
    def test_real_mcp_stdio_roundtrip_all_documents(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def check(audit):
            params = StdioServerParameters(command=sys.executable,
                args=[str(TOOLKIT / 'launch_mcp.py')],
                env={**os.environ, 'TOOLKIT_AUDIT_PATH': str(audit)})
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    self.assertEqual({t.name for t in (await session.list_tools()).tools},
                                     {'search', 'fetch'})
                    self.assertFalse((await session.call_tool('search', {'query': 'Graphify'})).isError)
                    docs = json.loads((TOOLKIT / 'documents.json').read_text(encoding='utf-8'))
                    codes = set()
                    for id, expected in docs.items():
                        result = await session.call_tool('fetch', {'id': id})
                        self.assertFalse(result.isError, id)
                        actual = json.loads(result.content[0].text)
                        self.assertEqual(actual['text'], expected['text'])
                        codes.add(actual['metadata']['verification_code'])
                    self.assertEqual(len(codes), 107)
                    self.assertTrue((await session.call_tool('fetch', {'id': '../.env'})).isError)
            events = [json.loads(line) for line in audit.read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(events), 108)
            self.assertTrue(all(e['status'] == 'success' for e in events))
            self.assertTrue(all(e['upstream_request_hash'] is None for e in events))

        with tempfile.TemporaryDirectory(prefix='toolkit-mcp-') as tmp:
            asyncio.run(check(Path(tmp) / 'audit.jsonl'))


if __name__ == '__main__':
    unittest.main()
