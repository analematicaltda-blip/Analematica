"""Run isolated quality profiles and preserve honest, private, verifiable evidence.
Never installs dependencies, changes Git, deploys, or selects a project database.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
MAX_LOG = 8 * 1024 * 1024
SOURCE_DIRS = ('BACKEND/ANALEMATICA-BACKEND/core_erp', 'BACKEND/ANALEMATICA-BACKEND/deployment', 'BACKEND/deployment', 'BACKEND/SGA-CD-BACKEND/app/services',
               'BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints', 'BACKEND/SGA-CD-BACKEND/app/models',
               'BACKEND/SGA-CD-BACKEND/tests', 'BACKEND/SGA-CD-BACKEND/tools', 'BACKEND/SGA-ERP-TUR-BAKEND',
               'BACKEND/SGA-TUR-BAKEND', 'FRONTEND/deployment', 'FRONTEND/shared',
               'FRONTEND/SGA-ERP-TUR-FRONTEND', 'FRONTEND/SGA-TUR-FRONTEND/src',
               'FRONTEND/ANALEMATICA-FRONTEND', 'INTEGRACIONES/operacion',
               'DESKTOP/asistencia-sgacd', 'DESKTOP/fiscal-signer')
SUFFIXES = {'.py', '.txt', '.toml', '.yaml', '.yml', '.json', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.html', '.css'}
EXCLUDED = {'node_modules', '__pycache__', '.runtime', '.next', '.venv', 'venv', 'dist', 'build'}


def write_private(path, data):
    with open(path, 'xb', opener=lambda name, flags: os.open(name, flags, 0o600)) as stream:
        stream.write(data)


def source_manifest(root=ROOT):
    entries = []
    for directory in SOURCE_DIRS:
        for path in sorted((root / directory).rglob('*')):
            rel = path.relative_to(root)
            if any(part in EXCLUDED or part.startswith('.') for part in rel.parts):
                continue
            if path.suffix not in SUFFIXES or path.is_symlink() or not path.is_file():
                continue
            # Do not follow an ancestor symlink into private/external locations.
            if any(parent.is_symlink() for parent in path.parents if parent != root):
                continue
            entries.append({'path': rel.as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return entries


def digest(entries):
    return hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def execute(name, argv, output, env, timeout=180, kind='unittest'):
    """Bound log storage, terminate process group on timeout, never invoke a shell."""
    log = output / (name + '.log')
    started = time.monotonic()
    state = {'truncated': False, 'bytes': 0, 'write_error': False}
    timed_out = False
    cancelled = False
    try:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, start_new_session=(os.name == 'posix'))
    except OSError:
        write_private(log, b'Test process could not start. Check required local runtime.\n')
        return {'id': name, 'status': 'BLOCKED', 'reason': 'runtime_unavailable',
                'log': log.name, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}

    def drain():
        try:
            with open(log, 'xb', opener=lambda name, flags: os.open(name, flags, 0o600)) as stream:
                while chunk := process.stdout.read(8192):
                    remaining = MAX_LOG - state['bytes']
                    if remaining > 0:
                        stream.write(chunk[:remaining]); state['bytes'] += min(len(chunk), remaining)
                    if len(chunk) > remaining:
                        state['truncated'] = True
        except OSError:
            state['write_error'] = True
        finally:
            process.stdout.close()

    reader = threading.Thread(target=drain, daemon=True); reader.start()
    try:
        process.wait(timeout=timeout)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        timed_out = isinstance(error, subprocess.TimeoutExpired)
        cancelled = isinstance(error, KeyboardInterrupt)
        if os.name == 'posix':
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait()
    reader.join(timeout=5)
    if reader.is_alive():
        # A detached descendant may retain stdout: do not call it a passed test.
        state['write_error'] = True
    raw = log.read_bytes() if log.exists() else b''
    text = raw.decode('utf-8', errors='replace')
    tests = skipped = None
    if kind == 'unittest':
        counts = re.findall(r'Ran (\d+) tests?', text)
        tests = int(counts[-1]) if counts else 0
        match = re.search(r'OK \(.*?skipped=(\d+)', text)
        skipped = int(match.group(1)) if match else 0
        summary_valid = bool(re.search(r'^OK(?: \([^\n]*\))?\s*$', text, re.M)) and tests > 0
    elif kind == 'tap':
        counts = re.findall(r'^# tests (\d+)', text, re.M)
        skips = re.findall(r'^# skipped (\d+)', text, re.M)
        tests = int(counts[-1]) if counts else 0
        skipped = int(skips[-1]) if skips else 0
        summary_valid = tests > 0 and bool(re.search(r'^# fail 0\s*$', text, re.M))
    else:
        summary_valid = True
    if cancelled:
        status = 'CANCELLED'
    elif timed_out:
        status = 'TIMEOUT'
    elif process.returncode != 0 or state['truncated'] or state['write_error'] or not summary_valid:
        status = 'FAILED'
    elif skipped:
        status = 'PASSED_WITH_SKIPS'
    else:
        status = 'PASSED'
    return {'id': name, 'status': status, 'returncode': process.returncode,
            'duration_seconds': round(time.monotonic() - started, 3),
            'tests': tests, 'skipped': skipped, 'log': log.name,
            'log_sha256': hashlib.sha256(raw).hexdigest(),
            'log_truncated': state['truncated'], 'log_write_error': state['write_error']}


def suites(profiles, python, dependencies, output):
    items = []
    def add(name, args, kind='unittest', timeout=180):
        items.append((name, args, kind, timeout))
    if 'core' in profiles:
        add('dependency_consistency', [python, '-m', 'pip', 'check'], 'command')
        add('runner_contract', [python, '-m', 'unittest', 'discover', '-s', 'INTEGRACIONES/operacion/tests', '-v'])
        for name in ['test_assistance*.py', 'test_platform.py', 'test_resources.py']:
            add(name.replace('.py','').replace('*',''), [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/SGA-CD-BACKEND/tests', '-p', name, '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_*.py', '-v'])
        for name in ['domain_security', 'company_scope', 'company_identity', 'accounting_foundation', 'accounting_posting', 'accounting_adapter', 'accounting_delivery', 'accounting_simulation', 'accounting_sql', 'accounting_envelope', 'accounting_invoice', 'accounting_invoice_queue', 'accounting_reservation_source', 'accounting_query', 'accounting_query_parser', 'accounting_reports', 'accounting_reservation_fiscal', 'accounting_reservation_recognition', 'accounting_tax_reconciliation', 'accounting_dian_boundary', 'accounting_dian_receipt', 'accounting_legacy_invoice', 'accounting_remediation_catalog', 'accounting_bank_statement', 'accounting_bank_reconciliation', 'accounting_bank_resolutions', 'accounting_bank_period', 'accounting_opening', 'accounting_tax_policy', 'accounting_commercial_tax', 'accounting_native_purchase', 'accounting_tax_register', 'accounting_benchmark', 'accounting_reservation_policy', 'accounting_sst', 'accounting_dispatch_guard', 'accounting_worker_safety', 'accounting_payroll_boundary', 'accounting_payroll', 'accounting_payroll_earnings', 'accounting_operational_cost', 'accounting_tourism_metrics', 'accounting_environmental', 'accounting_environmental_records', 'accounting_environmental_corrections', 'accounting_customer_package', 'accounting_local_signer', 'accounting_financial_orchestration', 'availability', 'erp_session', 'password_recovery']:
            add(name, [python, f'BACKEND/deployment/tests/{name}_check.py', '-v'])
        add('sqlite_restore', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/deployment/tests', '-p', 'test_sqlite_snapshot.py', '-v'])
        add('editorial_restore', [python, 'INTEGRACIONES/operacion/rehearse_editorial_restore.py'], 'command')
    if 'accounting' in profiles and 'core' not in profiles:
        for name in ['accounting_foundation','accounting_posting','accounting_adapter','accounting_delivery','accounting_simulation', 'accounting_sql', 'accounting_envelope', 'accounting_invoice', 'accounting_invoice_queue', 'accounting_reservation_source', 'accounting_query', 'accounting_query_parser', 'accounting_reports', 'accounting_reservation_fiscal', 'accounting_reservation_recognition', 'accounting_tax_reconciliation', 'accounting_dian_boundary', 'accounting_dian_receipt', 'accounting_legacy_invoice', 'accounting_remediation_catalog', 'accounting_bank_statement', 'accounting_bank_reconciliation', 'accounting_bank_resolutions', 'accounting_bank_period', 'accounting_opening', 'accounting_tax_policy', 'accounting_commercial_tax', 'accounting_native_purchase', 'accounting_tax_register', 'accounting_benchmark', 'accounting_reservation_policy', 'accounting_sst', 'accounting_dispatch_guard', 'accounting_worker_safety', 'accounting_payroll_boundary', 'accounting_payroll', 'accounting_payroll_earnings', 'accounting_operational_cost', 'accounting_tourism_metrics', 'accounting_environmental', 'accounting_environmental_records', 'accounting_environmental_corrections', 'accounting_customer_package', 'accounting_local_signer', 'accounting_financial_orchestration']:
            add(name, [python, f'BACKEND/deployment/tests/{name}_check.py', '-v'])
    if 'accounting' in profiles or 'core' in profiles:
        add('accounting_corporate_bridge', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/SGA-CD-BACKEND/tests', '-p', 'test_corporate_ledger*.py', '-v'],timeout=150)
    if 'backup' in profiles:
        add('encrypted_backup', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/deployment/tests', '-p', 'test_encrypted_backup.py', '-v'])
        if 'core' not in profiles:
            add('editorial_restore', [python, 'INTEGRACIONES/operacion/rehearse_editorial_restore.py'], 'command')
    if 'fresh' in profiles:
        for service in ['erp-tur', 'turismo']:
            directory = str(output / ('fresh-' + service))
            add('install_' + service, [python, 'BACKEND/deployment/fresh_local.py', '--directory', directory, '--service', service], 'command', 300)
            add('installed_' + service, [python, 'BACKEND/deployment/tests/fresh_database_check.py', '--directory', directory, '--service', service, '-v'])
    if 'browser' in profiles:
        for name in ['platform', 'content']:
            add(name + '_browser', ['node', f'FRONTEND/ANALEMATICA-FRONTEND/tests/{name}.cjs'], 'command')
    if 'devices' in profiles:
        tests = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'DESKTOP/asistencia-sgacd/tests').glob('*.test.mjs'))
        add('device_contracts', ['node', '--test', '--test-reporter=tap', *tests], 'tap')
    if 'postgres' in profiles:
        add('postgres_restore_concurrency', [python, 'BACKEND/deployment/tests/mfa_postgres_check.py'], 'command', 300)
    if 'web-build' in profiles:
        add('strict_web_builds', [python, 'FRONTEND/deployment/build_check.py', '--dependencies', str(dependencies), '--output', str(output / 'web-build')], 'command', 600)
    return items


def verify_artifacts(directory):
    directory = Path(directory)
    checksums = json.loads((directory / 'checksums.json').read_text())
    for name, expected in checksums.items():
        if Path(name).name != name or (directory / name).is_symlink():
            raise ValueError('Invalid artifact path')
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Artifact digest mismatch')
    if not {'report.json', 'source-manifest.json'}.issubset(checksums):
        raise ValueError('Incomplete artifact checksums')
    report = json.loads((directory / 'report.json').read_text())
    if report.get('schema') != 'sgacd-local-quality-v1':
        raise ValueError('Unknown report schema')
    for row in report['results']:
        name = row['log']
        if Path(name).name != name or (directory / name).is_symlink():
            raise ValueError('Invalid log path')
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != row['log_sha256']:
            raise ValueError('Log digest mismatch')
    source = json.loads((directory / 'source-manifest.json').read_text())
    if digest(source) != report['source_digest_before']:
        raise ValueError('Source manifest mismatch')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='append', choices=['core','accounting','backup','fresh','browser','devices','postgres','web-build'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--web-dependencies', type=Path)
    parser.add_argument('--verify', type=Path, help='Verify existing log/source hashes only; does not rerun tests')
    args = parser.parse_args()
    if args.verify:
        try:
            verify_artifacts(args.verify)
        except (OSError, ValueError, KeyError, TypeError):
            print('Evidence hashes invalid or incomplete.', file=sys.stderr); return 1
        print('Evidence hashes match. This is not a signature or a production approval.'); return 0
    if args.output is None:
        parser.error('--output is required for a new run')
    profiles = list(dict.fromkeys(args.profile or ['core']))
    if 'web-build' in profiles and args.web_dependencies is None:
        parser.error('--web-dependencies is required for strict builds')
    if args.output.is_symlink():
        parser.error('Output must not be a symbolic link')
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        parser.error('Use a new output directory; existing evidence is never overwritten')
    if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT / '.runtime'):
        parser.error('Keep private logs outside the repository or under ignored .runtime')
    output.mkdir(parents=True, mode=0o700)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(ROOT / 'BACKEND/SGA-CD-BACKEND'),
               DATABASE_URL='sqlite://', SECRET_KEY='isolated-quality-test-not-a-deployed-secret',
               ASSISTANCE_CONTENT_ENABLED='0', ASSISTANCE_CONTENT_OLLAMA_ENABLED='0',
               ASSISTANCE_DUET_ENABLED='0', NEXT_TELEMETRY_DISABLED='1')
    # Browser tests receive fixture tokens internally; never a real provider credential.
    env.setdefault('PLAYWRIGHT_MODULE', str(ROOT / 'DESKTOP/asistencia-sgacd/node_modules/playwright'))
    before = source_manifest()
    write_private(output / 'source-manifest.json', json.dumps(before, indent=2).encode())
    results = []
    for name, argv, kind, timeout in suites(profiles, sys.executable, args.web_dependencies, output):
        print(f'Running {name}…', flush=True)
        result = execute(name, argv, output, env, timeout, kind)
        results.append(result); print(f'{name}: {result["status"]}', flush=True)
        if result['status'] == 'CANCELLED':
            break
    after_digest = digest(source_manifest())
    stable = digest(before) == after_digest
    success = bool(results) and all(row['status'] == 'PASSED' for row in results) and stable
    versions = {}
    for package in ['Django','fastapi','SQLAlchemy','cryptography','httpx','psycopg2-binary']:
        try: versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError: versions[package] = None
    report = {'schema':'sgacd-local-quality-v1', 'created_at':datetime.now(timezone.utc).isoformat(),
              'profiles':profiles, 'local_checks_complete':success, 'production_ready':False,
              'source_digest_before':digest(before), 'source_digest_after':after_digest,
              'source_stable':stable, 'source_scope':list(SOURCE_DIRS),
              'python':platform.python_version(), 'packages':versions, 'results':results,
              'limits':['Scoped source hashes, not a full release image attestation',
                        'No production deployment, hardware qualification or live account actions',
                        'Passing a profile does not complete unselected profiles or the master plan']}
    write_private(output / 'report.json', json.dumps(report, ensure_ascii=False, indent=2).encode())
    checksums = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in output.iterdir() if path.is_file() and not path.is_symlink()}
    write_private(output / 'checksums.json', json.dumps(checksums, indent=2).encode())
    print('Local checks complete.' if success else 'Local checks incomplete; inspect the private report.', flush=True)
    return 0 if success else 2

if __name__ == '__main__':
    sys.exit(main())
