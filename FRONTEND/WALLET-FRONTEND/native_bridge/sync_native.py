"""Mirror our canonical native core into distributable Flutter package resources."""
from pathlib import Path
import argparse
import shutil

ROOT=Path(__file__).resolve().parents[3]/'MOVILES/WALLET-MOVIL/native/pool-01-cryptography'
DEST=Path(__file__).resolve().parent/'src/flutter/sgacd_vault'
parser=argparse.ArgumentParser();parser.add_argument('--sync',action='store_true');args=parser.parse_args()
pairs=[]
for source in (ROOT/'android/src/main/java/co/analematica/vault').glob('*.java'):
    pairs.append((source,DEST/'android/src/main/java/co/analematica/vault'/source.name))
for source in (ROOT/'ios/Sources/SGAVault').glob('*.swift'):
    pairs.append((source,DEST/'ios/Classes/Core'/source.name))
for source in (ROOT.parent/'pool-03-integrity/android/src/main/java/co/analematica/integrity').glob('*.java'):
    pairs.append((source,DEST/'android/src/main/java/co/analematica/integrity'/source.name))
for source in (ROOT.parent/'pool-03-integrity/ios/SGAIntegrity/Sources/SGAIntegrity').glob('*.swift'):
    pairs.append((source,DEST/'ios/Classes/Integrity'/source.name))
for source in (ROOT.parent/'pool-04-anti-phishing/android/src/main/java/co/analematica/protection').glob('*.java'):
    pairs.append((source,DEST/'android/src/main/java/co/analematica/protection'/source.name))
for source in (ROOT.parent/'pool-04-anti-phishing/ios/SGAProtection/Sources/SGAProtection').glob('*.swift'):
    pairs.append((source,DEST/'ios/Classes/Protection'/source.name))
pairs.append((ROOT/'android/src/main/AndroidManifest.xml',DEST/'android/src/main/AndroidManifest.xml'))
for source,target in pairs:
    if args.sync:
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    if not target.is_file() or source.read_bytes()!=target.read_bytes():
        raise SystemExit('Native resource differs from canonical core: '+target.name)
print('Canonical native resources verified:',len(pairs))
