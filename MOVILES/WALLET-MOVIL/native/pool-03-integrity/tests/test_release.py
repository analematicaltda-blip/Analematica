"""Policy/tool-output fixtures only: positive cases do not certify an actual release."""
import importlib.util
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[1]/'release/verify_release.py'
spec=importlib.util.spec_from_file_location('release_gate',SOURCE)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
A='a'*64;B='b'*64
ANDROID={'platform':'android','application_id':'co.analematica.wallet','minimum_version':10,'signer_sha256':[A]}
IOS={'platform':'ios','application_id':'co.analematica.wallet','minimum_version':10,'team_id':'AB12345678'}

class ReleaseChecks(unittest.TestCase):
    def android(self,signature=None,badging=None,xml=None):
        responses=[signature or f'Verified using v2 scheme (APK Signature Scheme v2): true\nSigner #1 certificate SHA-256 digest: {A}\n',
                   badging or "package: name='co.analematica.wallet' versionCode='10' versionName='1'\n",xml or 'E: manifest\nE: application\n']
        def runner(args): return responses.pop(0).encode(),b''
        return gate.android(Path('fixture.apk'),ANDROID,'apksigner','aapt',runner)
    def test_android_policy_output_fixture(self):
        self.assertEqual(self.android()['version'],10)
    def test_missing_or_unapproved_signers(self):
        for signature in ['Verified using v2 scheme: true\n',f'Verified using v2 scheme: true\nSigner #1 certificate SHA-256 digest: {B}\n',f'Verified using v2 scheme: true\nSigner #1 certificate SHA-256 digest: {A}\nSigner #2 certificate SHA-256 digest: {B}\n']:
            with self.subTest(signature=signature),self.assertRaises(gate.Rejected):self.android(signature=signature)
    def test_v1_only_rejected(self):
        with self.assertRaisesRegex(gate.Rejected,'MODERN_APK'):self.android(signature=f'Verified using v1 scheme: true\nSigner #1 certificate SHA-256 digest: {A}\n')
    def test_other_package_or_version_rejected(self):
        for badging in ["package: name='co.other.wallet' versionCode='10'", "package: name='co.analematica.wallet' versionCode='9'",'invalid manifest']:
            with self.subTest(badging=badging),self.assertRaises(gate.Rejected):self.android(badging=badging)
    def test_debug_and_test_flags_rejected(self):
        with self.assertRaises(gate.Rejected):self.android(badging="package: name='co.analematica.wallet' versionCode='10'\napplication-debuggable\n")
        for flag in ['debuggable','testOnly']:
            for value in ['(type 0x12)0xffffffff','"false"','unknown']:
                with self.subTest(flag=flag,value=value),self.assertRaises(gate.Rejected):self.android(xml=f'A: android:{flag}(0x1234)={value}\n')
        self.assertEqual(self.android(xml='A: android:debuggable(0x1234)=(type 0x12)0x0\n')['version'],10)
    def test_real_tool_failure_cannot_be_accepted(self):
        def failure(args):raise gate.Rejected('SIGNATURE_OR_ARTIFACT_REJECTED')
        with self.assertRaises(gate.Rejected):gate.android(Path('fixture.apk'),ANDROID,'apksigner','aapt',failure)
    def test_missing_verification_binary_fails_closed(self):
        with self.assertRaisesRegex(gate.Rejected,'TOOL_UNAVAILABLE'):gate.run_tool(['/nonexistent-sgacd-verifier'])
    def test_policies_require_explicit_identity_and_trust(self):
        for policy in [{}, {**ANDROID,'minimum_version':True},{**ANDROID,'minimum_version':0},{**ANDROID,'signer_sha256':[]},{**ANDROID,'signer_sha256':[A,A]},{**ANDROID,'signer_sha256':['wrong']},{**ANDROID,'skip_verify':True},{**IOS,'team_id':'untrusted"'}]:
            with self.subTest(policy=policy),self.assertRaises(gate.Rejected):gate.policy_from(policy)
        self.assertEqual(gate.policy_from(ANDROID),ANDROID)
        self.assertEqual(gate.policy_from(IOS),IOS)
    def ios(self,folder,info=None,entitlements=None):
        metadata={'CFBundleVersion':'10','CFBundleIdentifier':'co.analematica.wallet','CFBundleSupportedPlatforms':['iPhoneOS']}
        metadata.update(info or {});(folder/'Info.plist').write_bytes(plistlib.dumps(metadata))
        entitlement={'application-identifier':'AB12345678.co.analematica.wallet','com.apple.developer.team-identifier':'AB12345678','get-task-allow':False}
        entitlement.update(entitlements or {})
        def runner(args):
            if '--verify' in args:
                requirement=args[args.index('--test-requirement')+1]
                self.assertIn('anchor apple generic',requirement);self.assertIn('certificate leaf[subject.OU]',requirement)
                return b'',b''
            return plistlib.dumps(entitlement),b''
        return gate.ios(folder,IOS,runner=runner)
    def test_ios_apple_chain_requirement_is_mandatory(self):
        with tempfile.TemporaryDirectory() as temp:self.assertEqual(self.ios(Path(temp))['version'],10)
    def test_ios_simulator_debug_other_team_and_bundle_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for info in [{'CFBundleVersion':'9'},{'CFBundleVersion':'1.0'},{'CFBundleIdentifier':'co.other.wallet'},{'CFBundleSupportedPlatforms':['iPhoneSimulator']}]:
                with self.subTest(info=info),self.assertRaises(gate.Rejected):self.ios(Path(temp),info=info)
            for entitlements in [{'get-task-allow':True},{'get-task-allow':'false'},{'application-identifier':'AB12345678.co.other.wallet'},{'com.apple.developer.team-identifier':'OTHERTEAM0'}]:
                with self.subTest(entitlements=entitlements),self.assertRaises(gate.Rejected):self.ios(Path(temp),entitlements=entitlements)
    def test_ios_invalid_signature_or_adhoc_chain_rejected(self):
        def failure(args):raise gate.Rejected('SIGNATURE_OR_ARTIFACT_REJECTED')
        with self.assertRaises(gate.Rejected):gate.ios(Path('Fixture.app'),IOS,runner=failure)
    def test_snapshot_is_stable_and_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);source=folder/'candidate.apk';source.write_bytes(b'fixture')
            digest=gate.snapshot(source,folder/'copy.apk');source.write_bytes(b'tampered')
            self.assertEqual((folder/'copy.apk').read_bytes(),b'fixture')
            self.assertNotEqual(digest,gate.snapshot(source,folder/'changed.apk'))
    def test_directory_snapshot_binds_file_names_and_contents(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);source=folder/'App';source.mkdir();(source/'x').write_bytes(b'fixture')
            digest=gate.snapshot(source,folder/'first');(source/'x').rename(source/'y')
            self.assertNotEqual(digest,gate.snapshot(source,folder/'second'))
    def test_symlink_and_oversize_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);source=folder/'source';source.write_bytes(b'fixture');link=folder/'link';link.symlink_to(source)
            with self.assertRaises(gate.Rejected):gate.snapshot(link,folder/'copy')
            with patch.object(gate,'MAX_BYTES',1),self.assertRaises(gate.Rejected):gate.snapshot(source,folder/'large')

if __name__=='__main__': unittest.main()
