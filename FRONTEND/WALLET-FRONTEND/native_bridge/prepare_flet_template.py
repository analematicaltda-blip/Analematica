"""Create a separate, pinned Flet template with the native vault's build minimums."""
import argparse
from pathlib import Path
import shutil
import subprocess

PIN='9782991a5c20744354a7177d3f15f5c145d03864'
parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,type=Path);parser.add_argument('--destination',required=True,type=Path);args=parser.parse_args()
source=args.source.resolve();destination=args.destination.resolve()
head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
status=subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip()
if head!=PIN or status:raise SystemExit('Expected a clean official flet-build-template 0.28.3 checkout')
if destination.exists():raise SystemExit('Refusing to replace an existing template')
shutil.copytree(source,destination,ignore=shutil.ignore_patterns('.git','__pycache__'))
root=destination/'{{cookiecutter.out_dir}}'
changes={
 root/'android/settings.gradle': [('version "8.3.1"','version "8.9.2"')],
 root/'android/gradle/wrapper/gradle-wrapper.properties':[('gradle-8.7-bin.zip','gradle-8.11.1-bin.zip')],
 root/'android/app/build.gradle':[('compileSdkVersion flutter.compileSdkVersion','compileSdkVersion 35'),('JavaVersion.VERSION_1_8','JavaVersion.VERSION_17'),("jvmTarget = '1.8'","jvmTarget = '17'")],
 root/'ios/Podfile':[("platform :ios, '13.0'","platform :ios, '15.0'")],
 root/'ios/Runner.xcodeproj/project.pbxproj':[('IPHONEOS_DEPLOYMENT_TARGET = 13.0;','IPHONEOS_DEPLOYMENT_TARGET = 15.0;')],
}
for path,replacements in changes.items():
    text=path.read_text()
    for before,after in replacements:
        if before not in text:raise SystemExit('Unexpected template structure: '+path.name)
        text=text.replace(before,after)
    path.write_text(text)
print('Separate Flet template prepared; original checkout and user app unchanged. License preserved.')
