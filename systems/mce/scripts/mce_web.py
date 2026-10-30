"""Confined transport adapter; engineering and OOXML editing remain canonical."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import re
import shutil
import stat
import subprocess
import sys
import threading
import uuid
import zipfile
from pathlib import Path, PurePosixPath

from defusedxml import ElementTree as SafeET

PRODUCT = Path(__file__).resolve().parents[1]
ENGINE = PRODUCT / '.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py'
SKILLS = ('matriz-causa-efeito', 'engenharia-mce-projeto', 'padronizacao-mce', 'mce-fechamento-operacional', 'mce-operacao-web')
MAX_FILE = 20 * 1024 * 1024
MAX_XML = 4 * 1024 * 1024


def require_windows():
    if sys.platform != 'win32':
        raise ValueError('WINDOWS_ONLY: use native Windows with PowerShell and Python 3.12+')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def name(value):
    if (not isinstance(value, str) or len(value) > 120 or
            not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value) or
            '..' in value or value.lower().endswith(('.pem', '.key', '.env', '.sqlite3'))):
        raise ValueError('Unsafe name')
    return value


def regular(path, *, directory=False):
    info = path.lstat()
    if (path.is_symlink() or getattr(path, 'is_junction', lambda: False)() or
            getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise ValueError('Links and reparse points are forbidden')
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError('Directory required')
    elif (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_FILE):
        raise ValueError('Regular bounded unlinked file required')


def read(path):
    regular(path)
    with path.open('rb') as handle:
        data = handle.read(MAX_FILE + 1)
    if len(data) > MAX_FILE:
        raise ValueError('Input too large')
    return data


def json_file(path):
    data = read(path)
    if len(data) > 1024 * 1024:
        raise ValueError('JSON input too large')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def inspect_zip(path):
    """Bound OOXML before the existing openpyxl inventory/editor sees it."""
    read(path)
    if path.suffix.lower() != '.xlsx':
        raise ValueError('Only macro-free XLSX is accepted')
    try:
        with zipfile.ZipFile(path) as z:
            entries = z.infolist()
            if not 1 <= len(entries) <= 256:
                raise ValueError('ZIP member budget exceeded')
            total, seen, cell_budget = 0, set(), 0
            for entry in entries:
                p = PurePosixPath(entry.filename)
                if (entry.filename in seen or '\\' in entry.filename or p.is_absolute() or
                        '..' in p.parts or ':' in entry.filename or
                        stat.S_ISLNK(entry.external_attr >> 16) or entry.flag_bits & 1):
                    raise ValueError('Unsafe ZIP member')
                seen.add(entry.filename)
                total += entry.file_size
                if entry.file_size > MAX_XML or total > 50 * 1024 * 1024:
                    raise ValueError('Expanded OOXML budget exceeded')
                if entry.filename.lower().endswith('vbaproject.bin'):
                    raise ValueError('Macros forbidden')
                if entry.filename.endswith(('.xml', '.rels')):
                    tree = SafeET.fromstring(z.read(entry))
                    if entry.filename.startswith('xl/worksheets/'):
                        sheet_rows, sheet_columns = 1, 1
                        for element in tree.iter():
                            refs = [element.attrib.get('ref', ''), element.attrib.get('r', '')]
                            for ref in refs:
                                for col, row in re.findall(r'([A-Z]{1,3})([0-9]+)', ref):
                                    number = 0
                                    for char in col:
                                        number = number * 26 + ord(char) - 64
                                    if number > 256 or int(row) > 20000:
                                        raise ValueError('Workbook dimension budget exceeded')
                                    sheet_rows = max(sheet_rows, int(row))
                                    sheet_columns = max(sheet_columns, number)
                        cell_budget += sheet_rows * sheet_columns
                        if cell_budget > 200000:
                            raise ValueError('Total workbook cell budget exceeded')
    except Exception as exc:
        raise ValueError('Unsafe or invalid XLSX') from exc


def core():
    spec = importlib.util.spec_from_file_location('mce_web_canonical_engine', ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sign_approval(request, private_key, approver, *, lifetime_seconds=3600):
    """Operator-only helper; never registered as an MCP operation."""
    if not isinstance(approver, str) or not approver.strip() or not 1 <= lifetime_seconds <= 86400:
        raise ValueError('Named operator and bounded approval lifetime required')
    now = dt.datetime.now(dt.timezone.utc)
    payload = {'schema': 1, 'decision': 'AUTORIZO_ELABORACAO_MCE', 'model_approved': True,
               'approver': approver.strip(), 'request_sha256': digest(canonical(request)),
               'issued_at': now.isoformat(),
               'expires_at': (now + dt.timedelta(seconds=lifetime_seconds)).isoformat()}
    return {'payload': payload, 'signature': private_key.sign(canonical(payload)).hex()}


class MceWeb:
    def __init__(self, root, approvals, public_key):
        require_windows()
        root, approvals = Path(root).absolute(), Path(approvals).absolute()
        regular(root, directory=True)
        regular(approvals, directory=True)
        self.root, self.approvals = root.resolve(), approvals.resolve()
        if self.root.is_relative_to(self.approvals) or self.approvals.is_relative_to(self.root):
            raise ValueError('Approval storage must be outside the remote write root')
        for folder in ('inbox', 'projects'):
            regular(self.root / folder, directory=True)
        self.public_key = public_key
        self.lock = threading.RLock()

    def status(self):
        return {'product': 'MCE_INDEPENDENTE', 'remote_self_approval': False,
                'production_complete': False, 'scope': 'MATRIZ_DE_CAUSA_E_EFEITO',
                'skills': list(SKILLS), 'signing_key_available': self.public_key is not None}

    def read_skill(self, skill):
        if skill not in SKILLS:
            raise ValueError('Unknown MCE skill')
        return {'name': skill, 'instructions': (PRODUCT / '.agents/skills' / skill / 'SKILL.md').read_text(encoding='utf-8')}

    def input(self, filename, suffix=None):
        path = self.root / 'inbox' / name(filename)
        regular(self.root / 'inbox', directory=True)
        regular(path)
        if suffix and path.suffix.lower() != suffix:
            raise ValueError('Unsupported input format')
        return path

    def inspect_model(self, filename):
        path = self.input(filename, '.xlsx')
        inspect_zip(path)
        data = read(path)
        return {'sha256': digest(data), 'inventory': core().inventory(path),
                'model_approved': False, 'production_complete': False}

    def project(self, project_id):
        regular(self.root / 'projects', directory=True)
        path = self.root / 'projects' / name(project_id)
        regular(path, directory=True)
        return path

    def files(self, project):
        result, budget = {}, 0
        def visit(folder):
            nonlocal budget
            regular(folder, directory=True)
            for child in folder.iterdir():
                regular(child, directory=child.is_dir())
                if child.is_dir():
                    visit(child)
                else:
                    data = read(child)
                    budget += len(data)
                    if len(result) >= 300 or budget > 100 * 1024 * 1024:
                        raise ValueError('Workspace budget exceeded')
                    if child.suffix.lower() == '.xlsx':
                        inspect_zip(child)
                    result[child.relative_to(project).as_posix()] = data
        visit(project)
        state = json_file(project / 'state.json')
        for source in state.get('sources', []):
            name(source['name'])
        return result

    def command(self, command, workspace, **options):
        if command not in ('init', 'understand', 'authorize', 'apply', 'audit'):
            raise ValueError('Unsupported operation')
        args = [sys.executable, str(ENGINE), command, '--workspace', str(workspace)]
        for option, value in options.items():
            args.append('--' + option)
            args.extend(str(x) for x in (value if isinstance(value, list) else [value]))
        result = subprocess.run(args, capture_output=True, timeout=45, check=False,
                                text=True, encoding='utf-8', errors='replace')
        if result.returncode:
            raise ValueError('Canonical MCE workflow blocked the operation; inspect the local project and engineering gates')
        report = json.loads(result.stdout)
        return {key: value for key, value in report.items() if key not in ('workspace', 'output', 'approver')}

    def initialize(self, project_id, master, sources):
        with self.lock:
            destination = self.root / 'projects' / name(project_id)
            if destination.exists() or not isinstance(sources, list) or not 1 <= len(sources) <= 40:
                raise ValueError('New project and bounded nonempty sources required')
            self.inspect_model(master)
            inputs = [self.input(item) for item in sources]
            for item in inputs:
                read(item)
            report = self.command('init', destination, master=self.input(master), sources=inputs)
            return {**report, 'project_id': project_id, 'production_complete': False}

    def understand(self, project_id, analysis, contract):
        with self.lock:
            project = self.project(project_id)
            self.files(project)
            state = core().load_state(project)
            if state['status'] != 'INVENTARIADO':
                raise ValueError('Understanding already recorded; create a new revision')
            analysis_path = self.input(analysis, '.json')
            json_file(analysis_path)
            contract_path = self.input(contract, '.json')
            json_file(contract_path)
            shutil.copyfile(contract_path, project / 'contract.json')
            report = self.command('understand', project, analysis=analysis_path)
            return {**report, 'production_complete': False}

    def approval_request(self, project_id, changes):
        project = self.project(project_id)
        files = self.files(project)
        state = core().load_state(project)
        if state['status'] != 'ANALISADO_AGUARDANDO_DECISAO' or '.web-used-approval' in files:
            raise ValueError('Understanding and fresh external approval required')
        # Structural preflight only. The original baseline stays unapproved;
        # only the external signature can approve this exact model and contract.
        core().verify_contract(project, {**state, 'template_classification': 'MODELO_APROVADO'})
        path = self.input(changes, '.json')
        if not isinstance(json_file(path), list):
            raise ValueError('Changes list required')
        return {'product': 'MCE_INDEPENDENTE', 'project_id': project_id,
                'files': {key: digest(value) for key, value in sorted(files.items())},
                'changes_sha256': digest(read(path))}

    def apply(self, project_id, changes, approval):
        with self.lock:
            request = self.approval_request(project_id, changes)
            if self.public_key is None:
                raise ValueError('External operator public key missing')
            try:
                envelope = json_file(self.approvals / name(approval))
                payload = envelope['payload']
                self.public_key.verify(bytes.fromhex(envelope['signature']), canonical(payload))
                now = dt.datetime.now(dt.timezone.utc)
                issued = dt.datetime.fromisoformat(payload['issued_at'])
                expires = dt.datetime.fromisoformat(payload['expires_at'])
                if (payload['schema'] != 1 or payload.get('model_approved') is not True or
                        payload['decision'] != 'AUTORIZO_ELABORACAO_MCE' or
                        not payload['approver'].strip() or not issued <= now < expires or
                        (expires - issued).total_seconds() > 86400 or
                        payload['request_sha256'] != digest(canonical(request))):
                    raise ValueError('Approval is expired or not bound to this request')
            except Exception as exc:
                raise ValueError('External signed approval required') from exc
            project = self.project(project_id)
            files = self.files(project)
            changes_data = read(self.input(changes, '.json'))
            if ({key: digest(value) for key, value in sorted(files.items())} != request['files'] or
                    digest(changes_data) != request['changes_sha256']):
                raise ValueError('Inputs changed after approval check')
            # Consume before executing; failed operations need fresh operator review.
            with (project / '.web-used-approval').open('xb') as marker:
                marker.write(digest(canonical(request)).encode())
            job_id = name(project_id) + '-' + uuid.uuid4().hex
            jobs = self.root / 'jobs'
            if not jobs.exists():
                jobs.mkdir()
            regular(jobs, directory=True)
            job = jobs / job_id
            job.mkdir()
            (job / 'output').mkdir()
            for relative, data in files.items():
                target = job / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            changes_path = job / 'web-approved-changes.json'
            changes_path.write_bytes(changes_data)
            state = core().load_state(job)
            state['template_classification'] = 'MODELO_APROVADO'
            (job / 'state.json').write_bytes(canonical(state))
            analysis = json_file(job / 'analysis.json')
            auth_path = job / 'web-authorization.json'
            auth_path.write_bytes(canonical({'decision': payload['decision'], 'approver': payload['approver'],
                'project': analysis['project'], 'ss': analysis['ss'],
                'source_manifest_sha256': state['source_manifest_sha256']}))
            self.command('authorize', job, authorization=auth_path)
            report = self.command('apply', job, changes=changes_path)
            self.command('audit', job)
            return {**report, 'job_id': job_id, 'output': f'jobs/{job_id}/output/MCE_PRELIMINAR.xlsx',
                    'output_sha256': digest(read(job / 'output/MCE_PRELIMINAR.xlsx')),
                    'production_complete': False}
