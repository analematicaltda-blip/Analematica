"""Generate an isolated compile-check host, not an update to the user's app."""
import argparse
from pathlib import Path
import plistlib
import re
import subprocess

parser=argparse.ArgumentParser();parser.add_argument('--directory',required=True,type=Path);args=parser.parse_args()
target=args.directory.resolve()
if target.exists():raise SystemExit('Refusing to replace an existing host directory')
plugin=Path(__file__).resolve().parent/'src/flutter/sgacd_vault'
subprocess.run(['flutter','create','--empty','--platforms=android,ios','--org','co.analematica.vaultverify','--project-name','vault_verify',str(target)],check=True)
subprocess.run(['flutter','pub','add','sgacd_vault','--path',str(plugin)],cwd=target,check=True)
android=target/'android'
for path in [*android.rglob('*.kts'),*android.rglob('*.gradle')]:
    text=path.read_text()
    text=re.sub(r'compileSdk\s*=\s*[^\n]+','compileSdk = 35',text)
    text=re.sub(r'minSdk\s*=\s*[^\n]+','minSdk = 31',text)
    text=text.replace('JavaVersion.VERSION_11','JavaVersion.VERSION_17').replace('JavaVersion.VERSION_1_8','JavaVersion.VERSION_17')
    text=re.sub(r'compileSdkVersion\s+[^\n]+','compileSdkVersion 35',text)
    text=re.sub(r'minSdkVersion\s+[^\n]+','minSdkVersion 31',text)
    text=text.replace("jvmTarget = '1.8'","jvmTarget = '17'")
    text=re.sub(r'(id\("com.android.application"\) version )"[^"]+"',r'\1"8.9.2"',text)
    text=re.sub(r'(id \"com.android.application\" version )\"[^\"]+\"',r'\1"8.9.2"',text)
    path.write_text(text)
wrapper=android/'gradle/wrapper/gradle-wrapper.properties'
wrapper.write_text(re.sub(r'gradle-[0-9.]+-(all|bin)\.zip','gradle-8.11.1-bin.zip',wrapper.read_text()))
podfile=target/'ios/Podfile'
if podfile.exists():podfile.write_text(re.sub(r"#?\s*platform :ios, '[^']+'","platform :ios, '15.0'",podfile.read_text()))
project=target/'ios/Runner.xcodeproj/project.pbxproj'
project.write_text(re.sub(r'IPHONEOS_DEPLOYMENT_TARGET = [0-9.]+;', 'IPHONEOS_DEPLOYMENT_TARGET = 15.0;',project.read_text()))
info=target/'ios/Runner/Info.plist'
metadata=plistlib.loads(info.read_bytes());metadata['NSFaceIDUsageDescription']='Permite comprobar tus documentos cifrados con la protección del dispositivo.'
info.write_bytes(plistlib.dumps(metadata))
print('Isolated native compilation host prepared. No key provisioning or document import executed.')
