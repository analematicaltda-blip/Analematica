"""Compile native policy/client; optionally compile Android screen protection."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--android-jar',type=Path);args=p.parse_args()
source=ROOT/'pool-04-anti-phishing/android/src/main/java/co/analematica/protection'
files=list(source.glob('*.java')) if args.android_jar else [source/'OriginPinPolicy.java',source/'PinnedHttpsClient.java']
compiler=[shutil.which('javac')] if shutil.which('javac') else ['java','-m','jdk.compiler/com.sun.tools.javac.Main']
with tempfile.TemporaryDirectory(prefix='sgacd-protection-') as temp:
    flags=['-cp',str(args.android_jar)] if args.android_jar else []
    subprocess.run([*compiler,'-source','17','-target','17','-Xlint:all,-options',*flags,'-d',temp,*map(str,files),str(ROOT/'pool-04-anti-phishing/tests/java/co/analematica/protection/ProtectionCheck.java')],check=True,timeout=60)
    subprocess.run(['java','-cp',temp,'co.analematica.protection.ProtectionCheck'],check=True,timeout=60)
