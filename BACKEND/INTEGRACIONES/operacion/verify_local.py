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

ROOT = Path(__file__).resolve().parents[3]
MAX_LOG = 8 * 1024 * 1024
SOURCE_DIRS = ('BACKEND/ANALEMATICA-BACKEND/management', 'BACKEND/ANALEMATICA-BACKEND/migrations', 'ANALISIS/gestion-comercial/tools', 'BACKEND/SGA-CD-BACKEND/app/commercial', 'BACKEND/ANALEMATICA-BACKEND/gestion_comercial', 'BACKEND/ANALEMATICA-BACKEND/core_erp', 'BACKEND/ANALEMATICA-BACKEND/deployment', 'BACKEND/deployment', 'BACKEND/SGA-CD-BACKEND/app/services',
               'BACKEND/SGA-CD-BACKEND/app/api/v1/endpoints', 'BACKEND/SGA-CD-BACKEND/app/models',
               'BACKEND/SGA-CD-BACKEND/tests', 'BACKEND/SGA-CD-BACKEND/tools', 'BACKEND/SGA-ERP-TUR-BAKEND',
               'BACKEND/SGA-TUR-BAKEND', 'FRONTEND/deployment', 'FRONTEND/shared',
               'FRONTEND/SGA-CD-WEB.git', 'FRONTEND/SGA-ERP-TUR-FRONTEND', 'FRONTEND/SGA-TUR-FRONTEND/src',
               'FRONTEND/ANALEMATICA-FRONTEND', 'BACKEND/INTEGRACIONES', 'BACKEND/tools', 'BACKEND/tests', 'FRONTEND/tools', 'FRONTEND/tests', 'DESKTOP/tools', 'DESKTOP/tests',
               'DESKTOP/asistencia-sgacd', 'DESKTOP/fiscal-signer','BACKEND/WALLET-BACKEND','FRONTEND/WALLET-FRONTEND','DESKTOP/WALLET-DESKTOP','MOVILES/WALLET-MOVIL','ANALISIS/contabilidad/tools','BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army')
SOURCE_FILES=('BACKEND/ANALEMATICA-BACKEND/agents/legacy_command_staff.py','BACKEND/ANALEMATICA-BACKEND/apps.py','BACKEND/SGA-CD-BACKEND/app/api/v1/api.py','BACKEND/SGA-CD-BACKEND/requirements.txt','BACKEND/ANALEMATICA-BACKEND/urls.py','BACKEND/deployment/Dockerfile',
              'BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army/environment.example',
              'BACKEND/SGA-ERP-TUR-BAKEND/gestion_contable/contabilidad/agent_army/environment.example')
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
    indexed={entry['path'] for entry in entries}
    for name in SOURCE_FILES:
        path=root/name
        if (name in indexed or path.is_symlink() or not path.is_file()
                or any(parent.is_symlink() for parent in path.parents if parent!=root)):
            continue
        entries.append({'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return sorted(entries,key=lambda entry:entry['path'])


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
    if 'commercial-audit' in profiles:
        profiles=set(profiles)|{'commercial-identity-acceptance','commercial-access','commercial-payments','commercial','commercial-closeout','commercial-opportunities','commercial-after-sales','commercial-sales','commercial-pricing','commercial-quotations','commercial-landings','commercial-capture','commercial-library','commercial-video','commercial-adaptation','commercial-email','commercial-mobile','commercial-publishing','commercial-inbox','commercial-ads','commercial-army','commercial-workspaces','commercial-analytics'}
    items = []; indexed = {}
    def add(name, args, kind='unittest', timeout=180):
        if name in indexed:
            pos=indexed[name];old=items[pos]
            if old[1]!=args or old[2]!=kind:raise ValueError('Conflicting quality suite id: '+name)
            items[pos]=(name,args,kind,max(timeout,old[3]));return
        indexed[name]=len(items);items.append((name,args,kind,timeout))
    if 'commercial' in profiles:
        add('pool08_event_binding_native', [python, 'BACKEND/deployment/tests/pool08_event_native_check.py'])
        add('pool08_event_binding_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_event_integrity.py'])
    if 'commercial' in profiles or 'commercial-opportunities' in profiles:
        add('pool08_opportunity_recovery_browser', [python, 'BACKEND/deployment/tests/pool08_opportunity_recovery_browser_check.py'], 'command', 120)
    if 'commercial' in profiles or 'commercial-after-sales' in profiles:
        add('pool08_after_followup_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_after_followup.py'])
        add('pool08_after_sales_lifecycle', ['node', 'FRONTEND/deployment/tests/pool08_after_sales_lifecycle.cjs'], 'command', 120)
    if 'commercial-after-sales' in profiles:
        add('pool08_after_followup_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_after_followup.py'])
        add('pool08_after_sales_native', [python, 'BACKEND/deployment/tests/pool08_after_sales_native_check.py'])
        add('pool08_after_sales_wallet', [python, 'BACKEND/deployment/tests/pool08_after_sales_wallet_check.py'])
        add('pool08_after_sales_sga_http', [python, 'BACKEND/deployment/tests/pool08_after_sales_sga_http_check.py'])
        add('cancellation_timing', [python, 'BACKEND/deployment/tests/cancellation_timing_check.py'])
        add('pool08_after_sales_browser', [python, 'BACKEND/deployment/tests/pool08_after_sales_browser_check.py'], 'command', 360)
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
    if 'commercial' in profiles or 'commercial-sales' in profiles:
        add('pool08_sales_lifecycle', ['node', 'FRONTEND/deployment/tests/pool08_sales_lifecycle.cjs'], 'command', 120)
    if 'commercial-sales' in profiles:
        add('pool08_sales_native', [python, 'BACKEND/deployment/tests/pool08_sales_native_check.py'])
        add('pool08_sales_source', [python, 'BACKEND/deployment/tests/pool08_sales_source_check.py'])
        add('pool08_sales_saga', [python, 'BACKEND/deployment/tests/pool08_sales_saga_check.py'])
        add('pool08_sales_saga_http', [python, 'BACKEND/deployment/tests/pool08_sales_saga_http_check.py'])
        add('pool08_sales_bridge', [python, 'BACKEND/deployment/tests/pool08_sales_bridge_check.py'])
        add('pool08_sales_labor', [python, 'BACKEND/deployment/tests/pool08_sales_labor_check.py'])
        add('pool08_sales_http', [python, 'BACKEND/deployment/tests/pool08_sales_http_check.py'])
        add('pool08_sales_browser', [python, 'BACKEND/deployment/tests/pool08_sales_browser_check.py'], 'command', 360)
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
    if 'commercial-pricing' in profiles:
        add('pool08_pricing_native', [python, 'BACKEND/deployment/tests/pool08_pricing_native_check.py'])
        add('pool08_pricing_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_pricing.py'])
        add('pool08_pricing_http', [python, 'BACKEND/deployment/tests/pool08_pricing_http_check.py'])
        add('pool08_pricing_browser', [python, 'BACKEND/deployment/tests/pool08_pricing_browser_check.py'], 'command', 300)
        add('pool08_quote_delivery', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_quote_delivery.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
    if 'commercial-opportunities' in profiles:
        add('pool08_opportunities_native', [python, 'BACKEND/deployment/tests/pool08_opportunities_native_check.py'])
        add('pool08_opportunities_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_opportunities.py'])
        add('pool08_opportunities_http', [python, 'BACKEND/deployment/tests/pool08_opportunities_http_check.py'])
        add('pool08_opportunities_browser', [python, 'BACKEND/deployment/tests/pool08_opportunities_browser_check.py'], 'command', 300)
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 240)
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('pool08_quote_delivery', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_quote_delivery.py', '-v'])
    if any(p in profiles for p in ('commercial','commercial-library','commercial-landings')):
        add('pool08_crm_recovery_browser', [python, 'BACKEND/deployment/tests/pool08_crm_recovery_browser_check.py'], 'command', 120)
        add('pool08_recovery_browser', [python, 'BACKEND/deployment/tests/pool08_recovery_browser_check.py'], 'command', 120)
    if 'commercial' in profiles or 'commercial-quotations' in profiles:
        add('pool08_quotation_lifecycle', ['node', 'FRONTEND/deployment/tests/pool08_quotation_lifecycle.cjs'], 'command', 120)
        add('pool08_quotation_busy_browser', [python, 'BACKEND/deployment/tests/pool08_quotation_busy_browser_check.py'], 'command', 120)
    if 'commercial-quotations' in profiles:
        add('pool08_quotations_native', [python, 'BACKEND/deployment/tests/pool08_quotations_native_check.py'])
        add('pool08_quotations_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_quotations.py'])
        add('pool08_quotations_http', [python, 'BACKEND/deployment/tests/pool08_quotations_http_check.py'])
        add('pool08_quotations_browser', [python, 'BACKEND/deployment/tests/pool08_quotations_browser_check.py'], 'command', 360)
        add('pool08_quote_delivery', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_quote_delivery.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
    if 'commercial-identity-acceptance' in profiles:
        add('pool08_identity_acceptance_contract', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_identity_acceptance.py', '-v'])
        add('pool08_identity_acceptance_readiness', [python, 'BACKEND/INTEGRACIONES/operacion/commercial_identity_acceptance.py', '--output', str(output / 'identity-acceptance.json')], 'command')
        add('pool08_crm_acceptance_readiness', [python, 'BACKEND/INTEGRACIONES/operacion/commercial_identity_acceptance.py', '--task', 'GC-003', '--output', str(output / 'crm-acceptance.json')], 'command')
    if 'commercial-access' in profiles:
        add('pool08_access_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_access_admin.py'])
        add('pool08_access_native', [python, 'BACKEND/deployment/tests/pool08_access_admin_native_check.py'])
        add('pool08_access_http', [python, 'BACKEND/deployment/tests/pool08_access_admin_http_check.py'])
        add('pool08_access_browser', [python, 'BACKEND/deployment/tests/pool08_access_admin_browser_check.py'], 'command', 360)
    if 'commercial-crm' in profiles:
        add('pool08_crm_domain', [python, 'BACKEND/deployment/tests/pool08_crm_check.py'])
        add('pool08_crm_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_crm.py'])
        add('pool08_crm_native', [python, 'BACKEND/deployment/tests/pool08_crm_native_check.py'])
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_event_binding_native', [python, 'BACKEND/deployment/tests/pool08_event_native_check.py'])
        add('pool08_event_binding_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_event_integrity.py'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
    if 'commercial-payments' in profiles:
        add('pool08_payments_lifecycle', ['node', 'FRONTEND/deployment/tests/pool08_payments_lifecycle.cjs'], 'command')
        for name in ('gateway','native','sga','legacy','http'):
            add('pool08_payments_'+name, [python, 'BACKEND/deployment/tests/pool08_payments_'+name+'_check.py'])
        add('pool08_payments_browser', [python, 'BACKEND/deployment/tests/pool08_payments_browser_check.py'], 'command', 360)
    if 'commercial-audit' in profiles:
        add('commercial_audit_contract', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_commercial_audit.py', '-v'])
    if 'commercial-closeout' in profiles:
        add('pool08_operations_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_operations.py'])
        add('pool08_operations_native', [python, 'BACKEND/deployment/tests/pool08_operations_native_check.py'])
        add('pool08_operations_http', [python, 'BACKEND/deployment/tests/pool08_operations_http_check.py'])
        add('pool08_recovery_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_recovery.py'])
        add('pool08_recovery_native', [python, 'BACKEND/deployment/tests/pool08_recovery_native_check.py'])
        add('pool08_offline_browser', ['node', 'FRONTEND/deployment/tests/pool08_offline_browser.cjs'], 'command', 240)
        add('offline_asset_regression', [python, 'FRONTEND/deployment/tests/accounting_offline_assets_check.py'])
        add('commercial_gate', [python, 'BACKEND/INTEGRACIONES/operacion/commercial_release_gate.py'], 'command')
    if 'commercial-workspaces' in profiles:
        add('pool08_workspace_browser', [python, 'BACKEND/deployment/tests/pool08_workspace_browser_check.py'], 'command', 420)
        add('pool08_native_ui', ['node', 'FRONTEND/deployment/tests/pool08_native_ui_check.cjs'], 'command')
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_opportunities_browser', [python, 'BACKEND/deployment/tests/pool08_opportunities_browser_check.py'], 'command', 360)
        add('pool08_quotations_browser', [python, 'BACKEND/deployment/tests/pool08_quotations_browser_check.py'], 'command', 360)
        add('pool08_capture_browser', [python, 'BACKEND/deployment/tests/pool08_capture_browser_check.py'], 'command', 360)
        add('pool08_email_campaign_browser', [python, 'BACKEND/deployment/tests/pool08_email_campaign_browser_check.py'], 'command', 360)
        add('pool08_publishing_browser', [python, 'BACKEND/deployment/tests/pool08_publishing_browser_check.py'], 'command', 360)
        add('pool08_inbox_browser', [python, 'BACKEND/deployment/tests/pool08_inbox_browser_check.py'], 'command', 360)
        add('pool08_army_browser', [python, 'BACKEND/deployment/tests/pool08_army_browser_check.py'], 'command', 360)
        add('pool08_analytics_browser', [python, 'BACKEND/deployment/tests/pool08_analytics_browser_check.py'], 'command', 360)
        add('pool08_workspace_types', ['node', 'FRONTEND/deployment/tests/pool08_analytics_ui_check.cjs'], 'command')
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial-analytics' in profiles:
        add('pool08_analytics_ui', ['node', 'FRONTEND/deployment/tests/pool08_analytics_ui_check.cjs'], 'command')
        add('pool08_analytics_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_analytics.py'])
        add('pool08_analytics_native', [python, 'BACKEND/deployment/tests/pool08_analytics_native_check.py'])
        add('pool08_analytics_capture', [python, 'BACKEND/deployment/tests/pool08_analytics_capture_check.py'])
        add('pool08_analytics_ledger', [python, 'BACKEND/deployment/tests/pool08_analytics_ledger_check.py'])
        add('pool08_analytics_saga_http', [python, 'BACKEND/deployment/tests/pool08_analytics_saga_http_check.py'])
        add('pool08_analytics_http', [python, 'BACKEND/deployment/tests/pool08_analytics_http_check.py'])
        add('pool08_analytics_browser', [python, 'BACKEND/deployment/tests/pool08_analytics_browser_check.py'], 'command', 360)
        add('pool08_sales_native', [python, 'BACKEND/deployment/tests/pool08_sales_native_check.py'])
        add('pool08_sales_http', [python, 'BACKEND/deployment/tests/pool08_sales_http_check.py'])
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial-army' in profiles:
        add('commercial_staff_truth', [python, 'BACKEND/deployment/tests/pool08_command_staff_truth_check.py'])
        add('pool08_army_native', [python, 'BACKEND/deployment/tests/pool08_army_native_check.py'])
        add('pool08_army_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_commercial_army.py'])
        add('pool08_army_http', [python, 'BACKEND/deployment/tests/pool08_army_http_check.py'])
        add('pool08_army_browser', [python, 'BACKEND/deployment/tests/pool08_army_browser_check.py'], 'command', 360)
        add('pool08_ads_http', [python, 'BACKEND/deployment/tests/pool08_ads_http_check.py'])
        add('pool08_ads_browser', [python, 'BACKEND/deployment/tests/pool08_ads_browser_check.py'], 'command', 360)
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial-ads' in profiles:
        add('pool08_ads_native', [python, 'BACKEND/deployment/tests/pool08_ads_native_check.py'])
        add('pool08_ads_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_ads.py'])
        add('pool08_ads_http', [python, 'BACKEND/deployment/tests/pool08_ads_http_check.py'])
        add('pool08_ads_browser', [python, 'BACKEND/deployment/tests/pool08_ads_browser_check.py'], 'command', 360)
        add('pool08_inbox_http', [python, 'BACKEND/deployment/tests/pool08_inbox_http_check.py'])
        add('pool08_inbox_browser', [python, 'BACKEND/deployment/tests/pool08_inbox_browser_check.py'], 'command', 360)
        add('pool08_publishing_http', [python, 'BACKEND/deployment/tests/pool08_publishing_http_check.py'])
        add('pool08_publishing_browser', [python, 'BACKEND/deployment/tests/pool08_publishing_browser_check.py'], 'command', 360)
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial-inbox' in profiles:
        add('pool08_inbox_native', [python, 'BACKEND/deployment/tests/pool08_inbox_native_check.py'])
        add('pool08_inbox_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_inbox.py'])
        add('pool08_inbox_http', [python, 'BACKEND/deployment/tests/pool08_inbox_http_check.py'])
        add('pool08_inbox_browser', [python, 'BACKEND/deployment/tests/pool08_inbox_browser_check.py'], 'command', 360)
        add('pool08_publishing_http', [python, 'BACKEND/deployment/tests/pool08_publishing_http_check.py'])
        add('pool08_publishing_browser', [python, 'BACKEND/deployment/tests/pool08_publishing_browser_check.py'], 'command', 360)
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial-publishing' in profiles:
        add('publication_legacy_truth', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_publication_legacy_truth.py'])
        add('pool08_publishing_native', [python, 'BACKEND/deployment/tests/pool08_publishing_native_check.py'])
        add('pool08_publishing_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_publishing.py'])
        add('pool08_publishing_http', [python, 'BACKEND/deployment/tests/pool08_publishing_http_check.py'])
        add('pool08_publishing_browser', [python, 'BACKEND/deployment/tests/pool08_publishing_browser_check.py'], 'command', 360)
        add('pool08_mobile_native', [python, 'BACKEND/deployment/tests/pool08_mobile_message_native_check.py'])
        add('pool08_mobile_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_mobile_messages.py'])
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial' in profiles or 'commercial-mobile' in profiles:
        add('pool08_mobile_native', [python, 'BACKEND/deployment/tests/pool08_mobile_message_native_check.py'])
        add('pool08_mobile_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_mobile_messages.py'])
        add('pool08_mobile_http', [python, 'BACKEND/deployment/tests/pool08_mobile_message_http_check.py'])
        add('pool08_mobile_browser', [python, 'BACKEND/deployment/tests/pool08_mobile_message_browser_check.py'], 'command', 360)
    if 'commercial-mobile' in profiles:
        add('pool08_email_campaign_native', [python, 'BACKEND/deployment/tests/pool08_email_campaign_native_check.py'])
        add('pool08_email_campaign_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_email_campaigns.py'])
        add('pool08_crm_native', [python, 'BACKEND/deployment/tests/pool08_crm_native_check.py'])
        add('pool08_crm_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_crm.py'])
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial' in profiles or 'commercial-email' in profiles:
        add('pool08_email_campaign_native', [python, 'BACKEND/deployment/tests/pool08_email_campaign_native_check.py'])
        add('pool08_email_campaign_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_email_campaigns.py'])
        add('pool08_email_campaign_http', [python, 'BACKEND/deployment/tests/pool08_email_campaign_http_check.py'])
        add('pool08_email_campaign_browser', [python, 'BACKEND/deployment/tests/pool08_email_campaign_browser_check.py'], 'command', 300)
    if 'commercial-email' in profiles:
        add('email_legacy_truth', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_email_transport_truth.py'])
        add('pool08_crm_native', [python, 'BACKEND/deployment/tests/pool08_crm_native_check.py'])
        add('pool08_crm_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_crm.py'])
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 300)
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial' in profiles or 'commercial-adaptation' in profiles:
        add('pool08_adaptation_native', [python, 'BACKEND/deployment/tests/pool08_adaptation_native_check.py'])
        add('pool08_adaptation_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_adaptation.py'])
        add('pool08_adaptation_http', [python, 'BACKEND/deployment/tests/pool08_adaptation_http_check.py'])
        add('pool08_adaptation_browser', [python, 'BACKEND/deployment/tests/pool08_adaptation_browser_check.py'], 'command', 360)
    if 'commercial-adaptation' in profiles:
        add('pool08_library_native', [python, 'BACKEND/deployment/tests/pool08_library_native_check.py'])
        add('pool08_library_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_library.py'])
        add('pool08_library_sanitize', [python, 'BACKEND/deployment/tests/pool08_library_sanitize_check.py'])
        add('pool08_library_http', [python, 'BACKEND/deployment/tests/pool08_library_http_check.py'])
        add('pool08_library_browser', [python, 'BACKEND/deployment/tests/pool08_library_browser_check.py'], 'command', 360)
        add('pool08_video_native', [python, 'BACKEND/deployment/tests/pool08_video_native_check.py'])
        add('pool08_video_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_video.py'])
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial' in profiles or 'commercial-video' in profiles:
        add('pool08_video_native', [python, 'BACKEND/deployment/tests/pool08_video_native_check.py'])
        add('pool08_video_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_video.py'])
        add('pool08_video_http', [python, 'BACKEND/deployment/tests/pool08_video_http_check.py'])
        add('pool08_video_browser', [python, 'BACKEND/deployment/tests/pool08_video_browser_check.py'], 'command', 120)
    if 'commercial-video' in profiles:
        add('pool08_generation_native', [python, 'BACKEND/deployment/tests/pool08_generation_native_check.py'])
        add('pool08_generation_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_generation.py'])
        add('pool08_generation_http', [python, 'BACKEND/deployment/tests/pool08_generation_http_check.py'])
        add('pool08_library_native', [python, 'BACKEND/deployment/tests/pool08_library_native_check.py'])
        add('pool08_library_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_library.py'])
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_build_preparation.py', '-v'])
    if 'commercial' in profiles or 'commercial-library' in profiles:
        add('pool08_library_sanitize', [python, 'BACKEND/deployment/tests/pool08_library_sanitize_check.py'])
        add('pool08_library_native', [python, 'BACKEND/deployment/tests/pool08_library_native_check.py'])
        add('pool08_library_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_library.py'])
        add('pool08_library_http', [python, 'BACKEND/deployment/tests/pool08_library_http_check.py'])
        add('pool08_library_browser', [python, 'BACKEND/deployment/tests/pool08_library_browser_check.py'], 'command', 360)
    if 'commercial-library' in profiles:
        add('application_layout', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/tests/structure', '-v'])
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('pool08_crm_native', [python, 'BACKEND/deployment/tests/pool08_crm_native_check.py'])
        add('pool08_crm_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_crm.py'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
        add('pool08_capture_http', [python, 'BACKEND/deployment/tests/pool08_capture_http_check.py'])
        add('pool08_quote_delivery', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_quote_delivery.py', '-v'])
    if 'commercial' in profiles or 'commercial-capture' in profiles:
        add('pool08_capture_native', [python, 'BACKEND/deployment/tests/pool08_capture_native_check.py'])
        add('pool08_capture_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_capture.py'])
        add('pool08_capture_http', [python, 'BACKEND/deployment/tests/pool08_capture_http_check.py'])
        add('pool08_capture_browser', [python, 'BACKEND/deployment/tests/pool08_capture_browser_check.py'], 'command', 360)
    if 'commercial-capture' in profiles:
        add('application_layout', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/tests/structure', '-v'])
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('pool08_landings_domain', [python, 'BACKEND/deployment/tests/pool08_landings_check.py'])
        add('pool08_landings_native', [python, 'BACKEND/deployment/tests/pool08_landings_native_check.py'])
        add('pool08_landings_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_landings.py'])
        add('pool08_crm_native', [python, 'BACKEND/deployment/tests/pool08_crm_native_check.py'])
        add('pool08_crm_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_crm.py'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
    if 'commercial' in profiles or 'commercial-landings' in profiles:
        add('pool08_landings_domain', [python, 'BACKEND/deployment/tests/pool08_landings_check.py'])
        add('pool08_landings_native', [python, 'BACKEND/deployment/tests/pool08_landings_native_check.py'])
        add('pool08_landings_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_landings.py'])
        add('pool08_landings_http', [python, 'BACKEND/deployment/tests/pool08_landings_http_check.py'])
        add('pool08_landings_browser', [python, 'BACKEND/deployment/tests/pool08_landings_browser_check.py'], 'command', 360)
    if 'commercial-landings' in profiles:
        add('application_layout', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/tests/structure', '-v'])
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('pool08_crm_native', [python, 'BACKEND/deployment/tests/pool08_crm_native_check.py'])
        add('pool08_crm_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_crm.py'])
        add('runner', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-p', 'test_verify_local.py', '-v'])
    if 'commercial' in profiles:
        add('pool08_state_integrity_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_state_integrity.py'])
        add('pool08_audit_native', [python, 'BACKEND/deployment/tests/pool08_audit_native_check.py'])
        add('application_layout', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/tests/structure', '-v'])
        add('pool08_plan_registry', [python, '-m', 'unittest', 'discover', '-s', 'ANALISIS/gestion-comercial/tools', '-p', 'test_plan.py', '-v'])
        add('pool08_contract', [python, 'BACKEND/deployment/tests/pool08_contract_check.py', '-v'])
        add('pool08_sga', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/SGA-CD-BACKEND/tests', '-p', 'test_pool08_commercial.py', '-v'])
        add('pool08_native_http', [python, 'BACKEND/deployment/tests/pool08_native_http_check.py', '-v'])
        add('pool08_crm_domain', [python, 'BACKEND/deployment/tests/pool08_crm_check.py'])
        add('pool08_crm_native', [python, 'BACKEND/deployment/tests/pool08_crm_native_check.py'])
        add('pool08_crm_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_crm.py'])
        add('pool08_crm_http', [python, 'BACKEND/deployment/tests/pool08_crm_http_check.py'])
        add('pool08_crm_browser', [python, 'BACKEND/deployment/tests/pool08_crm_browser_check.py'], 'command', 240)
        add('pool08_opportunities_native', [python, 'BACKEND/deployment/tests/pool08_opportunities_native_check.py'])
        add('pool08_opportunities_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_opportunities.py'])
        add('pool08_opportunities_http', [python, 'BACKEND/deployment/tests/pool08_opportunities_http_check.py'])
        add('pool08_opportunities_browser', [python, 'BACKEND/deployment/tests/pool08_opportunities_browser_check.py'], 'command', 300)
        add('pool08_pricing_native', [python, 'BACKEND/deployment/tests/pool08_pricing_native_check.py'])
        add('pool08_pricing_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_pricing.py'])
        add('pool08_pricing_http', [python, 'BACKEND/deployment/tests/pool08_pricing_http_check.py'])
        add('pool08_pricing_browser', [python, 'BACKEND/deployment/tests/pool08_pricing_browser_check.py'], 'command', 300)
        add('pool08_quote_delivery', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_quote_delivery.py', '-v'])
        add('pool08_after_sales_native', [python, 'BACKEND/deployment/tests/pool08_after_sales_native_check.py'])
        add('pool08_after_sales_wallet', [python, 'BACKEND/deployment/tests/pool08_after_sales_wallet_check.py'])
        add('pool08_after_sales_sga_http', [python, 'BACKEND/deployment/tests/pool08_after_sales_sga_http_check.py'])
        add('pool08_after_sales_browser', [python, 'BACKEND/deployment/tests/pool08_after_sales_browser_check.py'], 'command', 360)
        add('pool08_payments_gateway', [python, 'BACKEND/deployment/tests/pool08_payments_gateway_check.py'])
        add('pool08_payments_native', [python, 'BACKEND/deployment/tests/pool08_payments_native_check.py'])
        add('pool08_payments_sga', [python, 'BACKEND/deployment/tests/pool08_payments_sga_check.py'])
        add('pool08_payments_legacy', [python, 'BACKEND/deployment/tests/pool08_payments_legacy_check.py'])
        add('pool08_payments_http', [python, 'BACKEND/deployment/tests/pool08_payments_http_check.py'])
        add('pool08_payments_browser', [python, 'BACKEND/deployment/tests/pool08_payments_browser_check.py'], 'command', 360)
        add('pool08_sales_native', [python, 'BACKEND/deployment/tests/pool08_sales_native_check.py'])
        add('pool08_sales_source', [python, 'BACKEND/deployment/tests/pool08_sales_source_check.py'])
        add('pool08_sales_saga', [python, 'BACKEND/deployment/tests/pool08_sales_saga_check.py'])
        add('pool08_sales_saga_http', [python, 'BACKEND/deployment/tests/pool08_sales_saga_http_check.py'])
        add('pool08_sales_bridge', [python, 'BACKEND/deployment/tests/pool08_sales_bridge_check.py'])
        add('pool08_sales_labor', [python, 'BACKEND/deployment/tests/pool08_sales_labor_check.py'])
        add('pool08_sales_http', [python, 'BACKEND/deployment/tests/pool08_sales_http_check.py'])
        add('pool08_sales_browser', [python, 'BACKEND/deployment/tests/pool08_sales_browser_check.py'], 'command', 360)
        add('pool08_quotations_native', [python, 'BACKEND/deployment/tests/pool08_quotations_native_check.py'])
        add('pool08_quotations_sga', [python, 'BACKEND/SGA-CD-BACKEND/tests/test_pool08_quotations.py'])
        add('pool08_quotations_http', [python, 'BACKEND/deployment/tests/pool08_quotations_http_check.py'])
        add('pool08_quotations_browser', [python, 'BACKEND/deployment/tests/pool08_quotations_browser_check.py'], 'command', 360)
    if 'core' in profiles:
        add('dependency_consistency', [python, '-m', 'pip', 'check'], 'command')
        add('runner_contract', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/INTEGRACIONES/operacion/tests', '-v'])
        for name in ['test_assistance*.py', 'test_platform.py', 'test_resources.py']:
            add(name.replace('.py','').replace('*',''), [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/SGA-CD-BACKEND/tests', '-p', name, '-v'])
        add('web_preparation', [python, '-m', 'unittest', 'discover', '-s', 'FRONTEND/deployment/tests', '-p', 'test_*.py', '-v'])
        for name in ['domain_security', 'company_scope', 'company_identity', 'accounting_foundation','accounting_acc001_acceptance','accounting_acc002_acceptance','accounting_acc003_acceptance','accounting_acc004_acceptance','accounting_acc005_acceptance','accounting_acc006_acceptance','accounting_acc007_acceptance','accounting_acc008_acceptance','accounting_acc008_migration','accounting_acc009_local','accounting_acc010_acceptance','accounting_reviewed_fx','accounting_reviewed_fx_api','accounting_fx_revaluation','accounting_fx_revaluation_api','accounting_fx_settlement','accounting_fx_settlement_api','accounting_ubl_source', 'accounting_posting', 'accounting_adapter', 'accounting_delivery', 'accounting_simulation', 'accounting_sql', 'accounting_envelope', 'accounting_invoice', 'accounting_invoice_queue', 'accounting_reservation_source', 'accounting_query', 'accounting_query_parser', 'accounting_reports', 'accounting_reservation_fiscal', 'accounting_reservation_recognition', 'accounting_tax_reconciliation', 'accounting_dian_boundary', 'accounting_dian_receipt', 'accounting_legacy_invoice', 'accounting_remediation_catalog', 'accounting_bank_statement', 'accounting_bank_reconciliation', 'accounting_bank_resolutions', 'accounting_bank_period','accounting_bank_history','accounting_empty_bank_period', 'accounting_bank_grouped','accounting_group_period','accounting_bank_rollup', 'accounting_bank_partial','accounting_bank_groups','accounting_purchase_recovery','accounting_recovery_tax_register','accounting_esg_recovery', 'accounting_opening','accounting_chunked_opening', 'accounting_tax_policy', 'accounting_commercial_tax', 'accounting_native_purchase','accounting_purchase_concepts','accounting_purchase_item_returns','accounting_purchase_item_return_api','accounting_purchase_history','accounting_purchase_return','accounting_purchase_return_void','accounting_return_final_reversal','cancellation_policy','cancellation_timing','accounting_wallet_refund','accounting_wallet_refund_lifecycle', 'accounting_tax_register', 'accounting_benchmark', 'accounting_reservation_policy', 'accounting_sst', 'accounting_dispatch_guard', 'accounting_worker_safety', 'accounting_payroll_boundary', 'accounting_payroll', 'accounting_payroll_earnings','accounting_payroll_deductions','accounting_payroll_novelties','accounting_payroll_source_earnings','accounting_native_payroll_source','accounting_native_payroll_correction', 'accounting_operational_cost', 'accounting_tourism_metrics', 'accounting_environmental', 'accounting_environmental_records','accounting_esg_reporting', 'accounting_environmental_corrections', 'accounting_customer_package','accounting_customer_recovery', 'accounting_local_signer', 'accounting_financial_orchestration', 'availability', 'erp_session', 'password_recovery']:
            add(name, [python, f'BACKEND/deployment/tests/{name}_check.py', '-v'])
        add('sqlite_restore', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/deployment/tests', '-p', 'test_sqlite_snapshot.py', '-v'])
        add('editorial_restore', [python, 'BACKEND/INTEGRACIONES/operacion/rehearse_editorial_restore.py'], 'command')
    if 'accounting' in profiles and 'core' not in profiles:
        for name in ['accounting_foundation','accounting_acc001_acceptance','accounting_acc002_acceptance','accounting_acc003_acceptance','accounting_acc004_acceptance','accounting_acc005_acceptance','accounting_acc006_acceptance','accounting_acc007_acceptance','accounting_acc008_acceptance','accounting_acc008_migration','accounting_acc009_local','accounting_acc010_acceptance','accounting_reviewed_fx','accounting_reviewed_fx_api','accounting_fx_revaluation','accounting_fx_revaluation_api','accounting_fx_settlement','accounting_fx_settlement_api','accounting_ubl_source','accounting_posting','accounting_adapter','accounting_delivery','accounting_simulation', 'accounting_sql', 'accounting_envelope', 'accounting_invoice', 'accounting_invoice_queue', 'accounting_reservation_source', 'accounting_query', 'accounting_query_parser', 'accounting_reports', 'accounting_reservation_fiscal', 'accounting_reservation_recognition', 'accounting_tax_reconciliation', 'accounting_dian_boundary', 'accounting_dian_receipt', 'accounting_legacy_invoice', 'accounting_remediation_catalog', 'accounting_bank_statement', 'accounting_bank_reconciliation', 'accounting_bank_resolutions', 'accounting_bank_period','accounting_bank_history','accounting_empty_bank_period', 'accounting_bank_grouped','accounting_group_period','accounting_bank_rollup', 'accounting_bank_partial','accounting_bank_groups','accounting_purchase_recovery','accounting_recovery_tax_register','accounting_esg_recovery', 'accounting_opening','accounting_chunked_opening', 'accounting_tax_policy', 'accounting_commercial_tax', 'accounting_native_purchase','accounting_purchase_concepts','accounting_purchase_item_returns','accounting_purchase_item_return_api','accounting_purchase_history','accounting_purchase_return','accounting_purchase_return_void','accounting_return_final_reversal','cancellation_policy','cancellation_timing','accounting_wallet_refund','accounting_wallet_refund_lifecycle', 'accounting_tax_register', 'accounting_benchmark', 'accounting_reservation_policy', 'accounting_sst', 'accounting_dispatch_guard', 'accounting_worker_safety', 'accounting_payroll_boundary', 'accounting_payroll', 'accounting_payroll_earnings','accounting_payroll_deductions','accounting_payroll_novelties','accounting_payroll_source_earnings','accounting_native_payroll_source','accounting_native_payroll_correction', 'accounting_operational_cost', 'accounting_tourism_metrics', 'accounting_environmental', 'accounting_environmental_records','accounting_esg_reporting', 'accounting_environmental_corrections', 'accounting_customer_package','accounting_customer_recovery', 'accounting_local_signer', 'accounting_financial_orchestration']:
            add(name, [python, f'BACKEND/deployment/tests/{name}_check.py', '-v'])
    if 'accounting' in profiles or 'core' in profiles:
        # New accounting contracts must not disappear from the regression profile.
        # Keep processes isolated: each module configures its own disposable Django DB.
        planned = {item[0] for item in items}
        for path in sorted((ROOT / 'BACKEND/deployment/tests').glob('accounting_*_check.py')):
            name = path.stem.removesuffix('_check')
            if name not in planned:
                add(name, [python, str(path.relative_to(ROOT)), '-v'])
                planned.add(name)
        add('schema_readiness', [python, 'BACKEND/deployment/tests/schema_readiness_check.py', '-v'])
        add('accounting_progress_registry',[python,'-m','unittest','discover','-s','ANALISIS/contabilidad/tools','-p','test_progress.py','-v'])
        add('accounting_progress_outputs',[python,'ANALISIS/contabilidad/tools/update_progress.py','--check'],'command')
        for wallet_suite in ['wallet_security','device_approval','attestation_security','access_policy','recovery']:
            add('wallet_'+wallet_suite,[python,'BACKEND/WALLET-BACKEND/tests/'+wallet_suite+'_check.py','-v'])
        for path in sorted((ROOT / 'BACKEND/SGA-CD-BACKEND/tests').glob('test_corporate_ledger*.py')):
            add('corporate_'+path.stem.removeprefix('test_'),
                [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/SGA-CD-BACKEND/tests', '-p', path.name, '-v'],
                timeout=180)
    if 'backup' in profiles:
        add('encrypted_backup', [python, '-m', 'unittest', 'discover', '-s', 'BACKEND/deployment/tests', '-p', 'test_encrypted_backup.py', '-v'])
        if 'core' not in profiles:
            add('editorial_restore', [python, 'BACKEND/INTEGRACIONES/operacion/rehearse_editorial_restore.py'], 'command')
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
    parser.add_argument('--profile', action='append', choices=['core','commercial-identity-acceptance','commercial-access','commercial-crm','commercial-payments','commercial-audit','commercial','commercial-opportunities','commercial-after-sales','commercial-sales','commercial-pricing','commercial-quotations','commercial-landings','commercial-capture','commercial-library','commercial-video','commercial-adaptation','commercial-email','commercial-mobile','commercial-publishing','commercial-inbox','commercial-ads','commercial-army','commercial-closeout','commercial-workspaces','commercial-analytics','accounting','backup','fresh','browser','devices','postgres','web-build'])
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
