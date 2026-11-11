"""Failure and evidence integrity contracts for the local operator, not app mocks."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('local_quality',Path(__file__).resolve().parents[1]/'verify_local.py')
quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality)

class QualityContracts(unittest.TestCase):
    def setUp(self):
        self.private=tempfile.TemporaryDirectory();self.output=Path(self.private.name)
    def tearDown(self):self.private.cleanup()
    def execute(self,code,kind='unittest',timeout=5):
        return quality.execute('fixture',[sys.executable,'-c',code],self.output,dict(os.environ),timeout,kind)
    def test_zero_exit_without_test_discovery_is_failure(self):
        result=self.execute('print("No tests actually ran")')
        self.assertEqual(result['status'],'FAILED');self.assertEqual(result['tests'],0)
    def test_nonzero_cannot_be_hidden_by_printed_ok(self):
        result=self.execute('print("Ran 2 tests\\nOK");raise SystemExit(1)')
        self.assertEqual(result['status'],'FAILED')
    def test_skip_is_reported_separately(self):
        result=self.execute('print("Ran 2 tests\\nOK (skipped=1)")')
        self.assertEqual(result['status'],'PASSED_WITH_SKIPS');self.assertEqual(result['skipped'],1)
    def test_real_unittest_result_and_private_log(self):
        result=self.execute('import unittest\nclass Actual(unittest.TestCase):\n def test_assertion(self):self.assertEqual(2+2,4)\nunittest.main()')
        self.assertEqual(result['status'],'PASSED')
        self.assertEqual((self.output/'fixture.log').stat().st_mode&0o777,0o600)
    def test_timeout_is_not_passed(self):
        result=self.execute('import time;time.sleep(10)',timeout=0.1)
        self.assertEqual(result['status'],'TIMEOUT');self.assertNotEqual(result['returncode'],0)
    def test_cancellation_stops_the_child_and_is_not_a_pass(self):
        from unittest.mock import patch
        original=quality.subprocess.Popen
        def spawn(*args,**kwargs):
            child=original(*args,**kwargs)
            real_wait=child.wait
            first=True
            def wait(*args,**kwargs):
                nonlocal first
                if first:
                    first=False;raise KeyboardInterrupt()
                return real_wait(*args,**kwargs)
            child.wait=wait
            return child
        with patch.object(quality.subprocess,'Popen',side_effect=spawn):
            result=self.execute('import time;time.sleep(10)')
        self.assertEqual(result['status'],'CANCELLED')
        self.assertNotEqual(result['returncode'],0)

    def test_missing_runtime_is_blocked(self):
        result=quality.execute('missing',['/nonexistent/quality-runtime'],self.output,dict(os.environ))
        self.assertEqual(result['status'],'BLOCKED')
    def test_log_cap_fails_closed(self):
        from unittest.mock import patch
        with patch.object(quality,'MAX_LOG',32):
            result=self.execute('print("x"*1000)',kind='command')
        self.assertTrue(result['log_truncated']);self.assertEqual(result['status'],'FAILED')
        self.assertEqual((self.output/'fixture.log').stat().st_size,32)
    def test_tap_skips_cannot_be_counted_as_full_completion(self):
        result=self.execute('print("# tests 3\\n# pass 2\\n# fail 0\\n# skipped 1")',kind='tap')
        self.assertEqual(result['status'],'PASSED_WITH_SKIPS');self.assertEqual(result['tests'],3)
    def test_source_manifest_ignores_private_and_symlinked_files(self):
        code=self.output/'INTEGRACIONES/operacion';code.mkdir(parents=True)
        (code/'runner.py').write_text('print("public code")')
        (code/'.runtime').mkdir();(code/'.runtime/private.json').write_text('never read')
        (code/'secret.env').write_text('never read')
        (code/'link.py').symlink_to(code/'secret.env')
        entries=quality.source_manifest(self.output)
        self.assertEqual([r['path'] for r in entries],['INTEGRACIONES/operacion/runner.py'])
        old=quality.digest(entries);(code/'runner.py').write_text('print("new version")')
        self.assertNotEqual(quality.digest(quality.source_manifest(self.output)),old)
    def test_fresh_profile_uses_new_databases_and_no_git_or_deployment(self):
        commands=quality.suites(['fresh'],sys.executable,None,self.output)
        self.assertEqual(len(commands),4)
        for _,argv,_,_ in commands:
            self.assertIn('--directory',argv)
            directory=Path(argv[argv.index('--directory')+1])
            self.assertTrue(directory.is_relative_to(self.output))
            self.assertNotIn('git',argv);self.assertNotIn('docker',argv)

    def test_accounting_profile_covers_all_current_contracts_once(self):
        commands=quality.suites(['accounting'],sys.executable,None,self.output)
        names=[row[0] for row in commands]
        self.assertEqual(len(names),len(set(names)))
        for path in (quality.ROOT/'BACKEND/deployment/tests').glob('accounting_*_check.py'):
            self.assertIn(path.stem.removesuffix('_check'),names,path.name)
        self.assertIn('schema_readiness',names)

    def test_combined_core_accounting_does_not_duplicate_contracts(self):
        commands=quality.suites(['core','accounting'],sys.executable,None,self.output)
        names=[row[0] for row in commands]
        self.assertEqual(len(names),len(set(names)))
        self.assertIn('accounting_acc023_http',names)
        self.assertIn('accounting_acc021_state',names)

    def test_corporate_contracts_have_individual_processes_and_logs(self):
        commands=quality.suites(['accounting'],sys.executable,None,self.output)
        selected=[row for row in commands if row[0].startswith('corporate_')]
        files=list((quality.ROOT/'BACKEND/SGA-CD-BACKEND/tests').glob('test_corporate_ledger*.py'))
        self.assertEqual(len(selected),len(files))
        self.assertEqual({row[1][row[1].index('-p')+1] for row in selected},{p.name for p in files})
        self.assertTrue(all('*' not in row[1][row[1].index('-p')+1] for row in selected))
        self.assertEqual(len({row[0] for row in selected}),len(files))

    def test_accounting_profile_checks_all72_index_and_attestation(self):
        names={row[0] for row in quality.suites(['accounting'],sys.executable,None,self.output)}
        self.assertIn('wallet_attestation_security',names)
        self.assertIn('accounting_progress_registry',names)
        self.assertIn('accounting_progress_outputs',names)
        self.assertIn('ANALISIS/contabilidad/tools',quality.SOURCE_DIRS)

    def test_native_army_source_and_public_deployment_inputs_are_hashed(self):
        package=self.output/'BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army'
        package.mkdir(parents=True);(package/'hierarchy.py').write_text('NATIVE=True')
        (package/'environment.example').write_text('ANA_ACCOUNTING_ARMY_DUET_ENABLED=0')
        directory=self.output/'BACKEND/deployment';directory.mkdir(parents=True)
        (directory/'Dockerfile').write_text('FROM tourism AS analematica-army')
        names={row['path'] for row in quality.source_manifest(self.output)}
        self.assertIn('BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army/hierarchy.py',names)
        self.assertIn('BACKEND/ANALEMATICA-BACKEND/gestion_contable/contabilidad/agent_army/environment.example',names)
        self.assertIn('BACKEND/deployment/Dockerfile',names)

    def evidence(self):
        source=[]
        quality.write_private(self.output/'source-manifest.json',b'[]')
        quality.write_private(self.output/'fixture.log',b'test passed')
        report={'schema':'sgacd-local-quality-v1','source_digest_before':quality.digest(source),'results':[{'log':'fixture.log','log_sha256':hashlib.sha256(b'test passed').hexdigest()}]}
        quality.write_private(self.output/'report.json',json.dumps(report).encode())
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.output.iterdir()}
        quality.write_private(self.output/'checksums.json',json.dumps(hashes).encode())
    def test_evidence_detects_changed_log(self):
        self.evidence();self.assertTrue(quality.verify_artifacts(self.output))
        (self.output/'fixture.log').write_bytes(b'changed')
        with self.assertRaises(ValueError):quality.verify_artifacts(self.output)
    def test_evidence_detects_changed_report(self):
        self.evidence();(self.output/'report.json').write_text('{}')
        with self.assertRaises(ValueError):quality.verify_artifacts(self.output)
    def test_private_writer_never_overwrites(self):
        path=self.output/'existing';quality.write_private(path,b'old')
        with self.assertRaises(FileExistsError):quality.write_private(path,b'new')
        self.assertEqual(path.read_bytes(),b'old')

if __name__=='__main__':unittest.main()
