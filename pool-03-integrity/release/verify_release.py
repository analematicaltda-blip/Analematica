"""Fail-closed, local verification of a signed APK or unpacked iOS .app.

This checks a supplied artifact, never signs it, installs it, trusts a client
boolean or declares a real device safe. Use only SDK/Apple tools you trust.
"""
import argparse
import hashlib
import json
from itertools import islice
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tempfile

MAX_BYTES=512*1024*1024
MAX_OUTPUT=1024*1024

class Rejected(ValueError):
    pass


def run_tool(args):
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            result=subprocess.run(args,stdout=out,stderr=err,timeout=60,check=False,env={**os.environ,'LC_ALL':'C'})
        except (OSError,subprocess.TimeoutExpired) as error:
            raise Rejected('VERIFICATION_TOOL_UNAVAILABLE') from error
        if result.returncode!=0: raise Rejected('SIGNATURE_OR_ARTIFACT_REJECTED')
        if out.tell()>MAX_OUTPUT or err.tell()>MAX_OUTPUT: raise Rejected('TOOL_OUTPUT_LIMIT')
        out.seek(0);err.seek(0)
        return out.read(),err.read()


def policy_from(value):
    if not isinstance(value,dict): raise Rejected('INVALID_POLICY')
    common={'platform','application_id','minimum_version'}
    platform=value.get('platform')
    extra={'signer_sha256'} if platform=='android' else {'team_id'} if platform=='ios' else set()
    if not extra or set(value)!=common|extra: raise Rejected('INVALID_POLICY')
    app=value['application_id'];version=value['minimum_version']
    if not isinstance(app,str) or re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)+',app) is None: raise Rejected('INVALID_POLICY')
    if type(version) is not int or not 1<=version<2**63: raise Rejected('INVALID_POLICY')
    if platform=='android':
        pins=value['signer_sha256']
        if not isinstance(pins,list) or not 1<=len(pins)<=4 or any(not isinstance(p,str) or re.fullmatch('[0-9a-f]{64}',p) is None for p in pins) or len(set(pins))!=len(pins): raise Rejected('INVALID_POLICY')
    elif not isinstance(value['team_id'],str) or re.fullmatch('[A-Z0-9]{10}',value['team_id']) is None: raise Rejected('INVALID_POLICY')
    return value


def android(artifact,policy,apksigner,aapt,runner=run_tool):
    stdout,_=runner([apksigner,'verify','--verbose','--print-certs',str(artifact)])
    text=stdout.decode('utf-8',errors='strict')
    if not re.search(r'^Verified using v(?:2|3|3\.1) scheme[^\n]*: true\s*$',text,re.M): raise Rejected('MODERN_APK_SIGNATURE_REQUIRED')
    pins=re.findall(r'^Signer #[1-9][0-9]* certificate SHA-256 digest: ([0-9a-fA-F]{64})\s*$',text,re.M)
    if not pins or len(pins)>4 or not set(p.lower() for p in pins)<=set(policy['signer_sha256']): raise Rejected('UNAPPROVED_SIGNER')
    stdout,_=runner([aapt,'dump','badging',str(artifact)])
    badging=stdout.decode('utf-8',errors='strict')
    package=re.search(r"^package: name='([^']+)' versionCode='([0-9]+)'",badging,re.M)
    if not package or package[1]!=policy['application_id']: raise Rejected('APPLICATION_ID_MISMATCH')
    if int(package[2])<policy['minimum_version']: raise Rejected('VERSION_TOO_OLD')
    if re.search(r'^application-debuggable\b',badging,re.M): raise Rejected('DEBUG_ARTIFACT')
    stdout,_=runner([aapt,'dump','xmltree',str(artifact),'AndroidManifest.xml'])
    for line in stdout.decode('utf-8',errors='strict').splitlines():
        if re.search(r'A: android:(debuggable|testOnly)\(',line):
            if not re.search(r'=\(type 0x12\)0x0\s*$',line): raise Rejected('DEBUG_OR_TEST_ARTIFACT')
    return {'platform':'android','application_id':package[1],'version':int(package[2]),'signer_sha256':sorted(set(p.lower() for p in pins))}


def ios(artifact,policy,codesign='/usr/bin/codesign',runner=run_tool):
    # Explicit Apple chain requirement: codesign --verify alone can accept ad-hoc
    # signatures or a self-signed certificate that merely claims the same Team ID.
    requirement=f'anchor apple generic and certificate leaf[subject.OU] = "{policy["team_id"]}" and identifier "{policy["application_id"]}"'
    runner([codesign,'--verify','--deep','--strict','--test-requirement',requirement,str(artifact)])
    try:
        if (artifact/'Info.plist').stat().st_size>MAX_OUTPUT: raise Rejected('APP_METADATA_SIZE_LIMIT')
        info=plistlib.loads((artifact/'Info.plist').read_bytes())
        raw=info['CFBundleVersion']
        if not isinstance(raw,str) or not re.fullmatch('[1-9][0-9]*',raw): raise Rejected('INVALID_VERSION')
        if info['CFBundleIdentifier']!=policy['application_id']: raise Rejected('APPLICATION_ID_MISMATCH')
        if int(raw)<policy['minimum_version']: raise Rejected('VERSION_TOO_OLD')
        if info.get('CFBundleSupportedPlatforms')!=['iPhoneOS']: raise Rejected('IOS_DEVICE_BUILD_REQUIRED')
        stdout,_=runner([codesign,'--display','--entitlements',':-',str(artifact)])
        entitlements=plistlib.loads(stdout)
        if entitlements.get('get-task-allow',False) is not False: raise Rejected('DEBUG_ARTIFACT')
        if entitlements.get('com.apple.developer.team-identifier')!=policy['team_id'] or entitlements.get('application-identifier')!=policy['team_id']+'.'+policy['application_id']: raise Rejected('SIGNING_IDENTITY_MISMATCH')
    except (OSError,KeyError,TypeError,plistlib.InvalidFileException) as error: raise Rejected('INVALID_APP_METADATA') from error
    return {'platform':'ios','application_id':info['CFBundleIdentifier'],'version':int(raw),'team_id':policy['team_id']}


def snapshot(source,destination):
    """Verify a private stable copy, so report hash and tool results cover same bytes."""
    if source.is_symlink(): raise Rejected('SYMLINK_ARTIFACT')
    paths=[source] if source.is_file() else list(islice(source.rglob('*'),20001)) if source.is_dir() else []
    if not paths or len(paths)>20000: raise Rejected('INVALID_ARTIFACT')
    total=0
    digest=hashlib.sha256()
    for path in sorted(paths):
        if path.is_symlink() or not (path.is_file() or path.is_dir()): raise Rejected('UNSAFE_ARTIFACT_ENTRY')
        if path.is_dir(): continue
        relative=path.relative_to(source).as_posix() if source.is_dir() else ''
        target=destination/relative if source.is_dir() else destination
        target.parent.mkdir(parents=True,exist_ok=True)
        content_hash=hashlib.sha256();size=0
        # No-follow protects the final component if a source is concurrently swapped.
        descriptor=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(descriptor,'rb') as incoming, target.open('xb') as outgoing:
            import stat
            if not stat.S_ISREG(os.fstat(incoming.fileno()).st_mode): raise Rejected('UNSAFE_ARTIFACT_ENTRY')
            while chunk:=incoming.read(65536):
                total+=len(chunk);size+=len(chunk)
                if total>MAX_BYTES: raise Rejected('ARTIFACT_SIZE_LIMIT')
                content_hash.update(chunk);outgoing.write(chunk)
            # Keep executable permissions needed by codesign, never writable by others.
            os.chmod(target,0o700 if os.fstat(incoming.fileno()).st_mode&0o111 else 0o600)
        digest.update(relative.encode()+b'\0'+str(size).encode()+b'\0'+content_hash.digest())
    return digest.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact',type=Path,required=True);parser.add_argument('--policy',type=Path,required=True)
    parser.add_argument('--apksigner',default='apksigner');parser.add_argument('--aapt',default='aapt')
    args=parser.parse_args()
    try:
        if args.policy.stat().st_size>8192: raise Rejected('INVALID_POLICY')
        policy=policy_from(json.loads(args.policy.read_text()))
        if policy['platform']=='ios' and sys.platform!='darwin': raise Rejected('MACOS_CODESIGN_REQUIRED')
        with tempfile.TemporaryDirectory(prefix='sgacd-release-check-') as temp:
            target=Path(temp)/('candidate.apk' if policy['platform']=='android' else 'Candidate.app')
            digest=snapshot(args.artifact,target)
            result=android(target,policy,args.apksigner,args.aapt) if policy['platform']=='android' else ios(target,policy)
            print(json.dumps({**result,'artifact_tree_sha256':digest,'artifact_verified':True,'physical_device_verified':False,'production_authorized':False},sort_keys=True))
        return 0
    except (Rejected,OSError,ValueError,UnicodeError) as error:
        code=str(error) if isinstance(error,Rejected) else 'INVALID_INPUT_OR_TOOL_OUTPUT'
        print(json.dumps({'artifact_verified':False,'code':code,'production_authorized':False}));return 1

if __name__=='__main__': sys.exit(main())
