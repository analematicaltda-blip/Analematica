"""Compile pure policy and optionally Android collector against an official SDK jar."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--android-jar',type=Path);args=parser.parse_args()
source=ROOT/'pool-03-integrity/android/src/main/java/co/analematica/integrity'
files=list(source.glob('*.java')) if args.android_jar else [source/'IntegrityPolicy.java']
compiler=[shutil.which('javac')] if shutil.which('javac') else ['java','-m','jdk.compiler/com.sun.tools.javac.Main']
with tempfile.TemporaryDirectory(prefix='sgacd-integrity-') as temp:
    flags=['-cp',str(args.android_jar)] if args.android_jar else []
    subprocess.run([*compiler,'-source','17','-target','17','-Xlint:all,-options',*flags,'-d',temp,*map(str,files),str(ROOT/'pool-03-integrity/tests/java/co/analematica/integrity/IntegrityCheck.java')],check=True,timeout=60)
    subprocess.run(['java','-cp',temp,'co.analematica.integrity.IntegrityCheck'],check=True,timeout=60)
