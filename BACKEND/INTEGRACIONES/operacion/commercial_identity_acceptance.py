"""Read-only preparation for GC-002/GC-003 acceptance; never signs, grants or closes it.

Local evidence can be checked mechanically. Legitimacy of people, authority and
policies requires independent review; this tool has no self-approval input.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REQUIRED_JOBS = {'pool08_access_sga', 'pool08_access_native',
                 'pool08_access_http', 'pool08_access_browser'}
CRM_JOBS = {'pool08_crm_domain', 'pool08_crm_sga', 'pool08_crm_native',
            'pool08_crm_http', 'pool08_crm_browser', 'pool08_event_binding_native',
            'pool08_event_binding_sga'}
CRM_CASES = ('CREATE', 'SEARCH', 'UPDATE', 'FOLLOW_UP', 'DUPLICATE_REVIEW',
             'CONVERT', 'WITHDRAW', 'CONSENT_AND_HISTORY')
PREFIXES = ('BACKEND/SGA-CD-BACKEND/app/commercial/pool08/',
            'BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/pool08/',
            'BACKEND/ANALEMATICA-BACKEND/gestion_comercial/pool08/')
FILES = {'FRONTEND/SGA-CD-WEB.git/js/commercial-crm.js',
         'FRONTEND/SGA-ERP-TUR-FRONTEND/public/js/commercial-crm.js',
         'FRONTEND/ANALEMATICA-FRONTEND/js/commercial-crm.js',
         'BACKEND/SGA-CD-BACKEND/app/services/workspace_service.py',
         'BACKEND/SGA-CD-BACKEND/app/services/role_contracts.py',
         'BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/agent_army_runtime.py',
         'BACKEND/SGA-TUR-BAKEND/apps/turismo/services/company_identity.py'}
EXTERNAL_CHECKS = [
    {'id': 'LEGITIMATE_ADMINISTRATORS', 'required': 'Titularidad y autoridad de los administradores de cada sistema y empresa.'},
    {'id': 'REVIEWED_NATIVE_ROLES', 'required': 'Matriz revisada de roles propios, permisos y separación entre empresas.'},
    {'id': 'REVIEWED_CONSENT_POLICIES', 'required': 'Políticas legítimas de autorización, finalidades, vigencias y revocación.'},
    {'id': 'AUTHORIZED_ACCEPTANCE_CASES', 'required': 'Usuarios y muestras autorizados para recorridos positivos y negativos reales.'},
    {'id': 'TRACEABLE_REVIEW', 'required': 'Acta de revisión identificable, alcance y versión, decisiones y pendientes de los revisores legítimos.'},
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('EVIDENCE_PATH_OUTSIDE_REPOSITORY')
    target = root / path
    if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('EVIDENCE_PATH_OUTSIDE_REPOSITORY')
    if target.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('EVIDENCE_SIZE_LIMIT')
    return target.read_bytes()


def read_json(root, relative):
    return json.loads(blob(root, relative))


def review_quality(root, entry, required_jobs=None):
    required_jobs = REQUIRED_JOBS if required_jobs is None else set(required_jobs)
    info = entry['quality']
    raw = blob(root, info['artifact'])
    if sha(raw) != info['sha256']:
        raise ValueError('QUALITY_HASH_MISMATCH')
    quality = json.loads(raw)
    if not quality['local_checks_complete'] or not quality['source_stable']:
        raise ValueError('LOCAL_CHECKS_INCOMPLETE')
    if quality['source_digest_before'] != quality['source_digest_after'] or info['source_digest'] != quality['source_digest_after']:
        raise ValueError('UNSTABLE_SOURCE_EVIDENCE')
    rows = quality['results']
    ids = [row['id'] for row in rows]
    if len(set(ids)) != len(ids) or not required_jobs <= set(ids):
        raise ValueError('MISSING_OR_DUPLICATE_IDENTITY_SUITES')
    if any(row['status'] != 'PASSED' or row.get('skipped', 0) for row in rows):
        raise ValueError('LOCAL_CHECKS_INCOMPLETE')
    directory = Path(info['artifact']).parent
    checksums = read_json(root, directory / 'checksums.json')
    for name, digest in checksums.items():
        if Path(name).name != name or sha(blob(root, directory / name)) != digest:
            raise ValueError('QUALITY_ARTIFACT_ALTERED')
    for row in rows:
        if Path(row['log']).name != row['log'] or checksums.get(row['log']) != row['log_sha256']:
            raise ValueError('QUALITY_LOG_NOT_COVERED')
    if checksums.get('report.json') != sha(raw) or 'source-manifest.json' not in checksums:
        raise ValueError('QUALITY_MANIFEST_NOT_COVERED')
    manifest = read_json(root, directory / 'source-manifest.json')
    if sha(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()) != quality['source_digest_after']:
        raise ValueError('SOURCE_MANIFEST_DIGEST_MISMATCH')
    expected = {row['path']: row['sha256'] for row in manifest
                if (row['path'].startswith(PREFIXES) and row['path'].endswith('.py')) or row['path'] in FILES}
    if not FILES <= set(expected) or any(not any(name.startswith(prefix) for name in expected) for prefix in PREFIXES):
        raise ValueError('IDENTITY_SOURCE_SCOPE_INCOMPLETE')
    current = set(FILES)
    for prefix in PREFIXES:
        current.update(str(path.relative_to(root)) for path in (root / prefix).rglob('*.py'))
    changed = sorted(current.symmetric_difference(expected))
    for name, digest in expected.items():
        try:
            if sha(blob(root, name)) != digest:changed.append(name)
        except OSError:changed.append(name)
    return {'suite_ids': sorted(required_jobs), 'artifact_integrity_verified': True,
            'identity_sources_current': not changed, 'changed_sources': sorted(set(changed)),
            'checked_source_count': len(expected), 'external_authenticity_verified': False}


def evaluate(root=ROOT, task_id='GC-002'):
    if task_id not in ('GC-002', 'GC-003'):raise ValueError('UNSUPPORTED_ACCEPTANCE_TASK')
    root = Path(root)
    spec = importlib.util.spec_from_file_location('identity_acceptance_progress', root / 'ANALISIS/gestion-comercial/tools/update_plan.py')
    progress_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(progress_module)
    plan = read_json(root, 'ANALISIS/gestion-comercial/plan-pool08.json')
    progress = progress_module.measure(plan)
    task = next(task for task in plan['tasks'] if task['id'] == task_id)
    # The GC-002 verification run also contains the complete CRM regression.
    # Cite it explicitly as supporting evidence, without changing old GC-003 credits.
    origin = next(row for row in plan['tasks'] if row['id'] == 'GC-002')
    reference = origin['milestones'][1]['evidence']
    dependencies = [name for name in task['dependencies'] if name not in progress['accepted_task_ids']]
    local = None
    reason = None
    try:
        if any(m['state'] != 'VERIFICADO' for m in task['milestones'][:2]) or not reference:
            raise ValueError('FUNCTIONALITY_OR_TESTS_PENDING')
        if len(reference) != 1:raise ValueError('AMBIGUOUS_TEST_EVIDENCE')
        ref = reference[0]
        entry = read_json(root, ref['artifact'])
        for key in ref['entry'].split('.'):entry = entry[key]
        local = review_quality(root, entry, CRM_JOBS if task_id=='GC-003' else REQUIRED_JOBS)
        if not local['identity_sources_current']:reason = 'IDENTITY_SOURCES_CHANGED_AFTER_TESTS'
    except (OSError, ValueError, KeyError, TypeError):
        reason = 'LOCAL_EVIDENCE_REVIEW_REQUIRED'
    external = EXTERNAL_CHECKS if task_id=='GC-002' else [
        {'id': 'CRM_'+case, 'required': 'Recorrido aceptado con muestra autorizada en los tres sistemas: '+case}
        for case in CRM_CASES]
    return {'schema': 'commercial-identity-acceptance-readiness-v1', 'task_id': task_id,
            'milestone_id': task['milestones'][2]['id'],
            'gate': 'BLOCKED_LOCAL_EVIDENCE' if reason else ('BLOCKED_DEPENDENCY_AND_EXTERNAL_ACCEPTANCE' if dependencies else 'BLOCKED_EXTERNAL_ACCEPTANCE'),
            'dependencies_without_acceptance': dependencies,
            'local_evidence_origin_task': origin['id'],
            'local_blocker': reason, 'local_evidence': local,
            'external_review': [{**check, 'state': 'NOT_INDEPENDENTLY_VERIFIED'} for check in external],
            'known_materials_availability': plan['remaining_work_plan']['known_unavailable_acceptance_inputs'],
            'credited_milestones': progress['completed_milestones'],
            'credited_milestone_percent': progress['credited_milestone_percent'],
            'new_progress_credit': 0, 'acceptance_complete': False, 'production_enabled': False,
            'permissions_changed': False, 'publication_performed': False,
            'limitations': ['Checksums prove internal consistency, never legitimacy of people or policies.',
                           'No input flag, document hash or synthetic reviewer automatically grants acceptance.',
                           'This preparation tool does not certify an acceptance completed elsewhere.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', choices=['GC-002','GC-003'], default='GC-002')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(task_id=args.task)
    with args.output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({key: result[key] for key in ('gate', 'new_progress_credit', 'acceptance_complete')}))
