"""Use the actual backend payload writer and verify native-format ECDSA with Python."""
import argparse,base64,runpy,shutil,subprocess,sys,tempfile,uuid
from pathlib import Path
from types import SimpleNamespace
from datetime import timedelta
from decimal import Decimal
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT/'BACKEND/deployment/tests/tourism_runtime_check.py'),run_name='fixture_setup')
from django.utils import timezone
from apps.wallet.services.device_approvals import payload
from apps.wallet.services.internal_transfer import fingerprint
parser=argparse.ArgumentParser();parser.add_argument('--android-jar',type=Path);args=parser.parse_args()
intent=SimpleNamespace(requested_by_id=7,pk=uuid.uuid4(),digest='0'*64,source_id=uuid.uuid4(),destination_id=uuid.uuid4(),amount=Decimal('12.30'),currency='COP')
intent.digest=fingerprint(intent.source_id,intent.destination_id,intent.amount,intent.currency)
credential=SimpleNamespace(audience=uuid.uuid4());credential_id=uuid.uuid4()
challenge=SimpleNamespace(pk=uuid.uuid4(),credential=credential,credential_id=credential_id,phase='REVIEW',nonce=base64.b64encode(bytes(32)).decode(),expires_at=timezone.now()+timedelta(seconds=120))
compiler=[shutil.which('javac')] if shutil.which('javac') else ['java','-m','jdk.compiler/com.sun.tools.javac.Main']
source=ROOT/'pool-02-biometrics/android/src/main/java/co/analematica/approval'
with tempfile.TemporaryDirectory(prefix='sgacd-approval-check-') as temp:
    directory=Path(temp);message=payload(challenge,intent);(directory/'message').write_bytes(message)
    files=list(source.glob('*.java')) if args.android_jar else [source/'ApprovalMessage.java']
    if args.android_jar: files+=list((ROOT/'pool-03-integrity/android/src/main/java/co/analematica/integrity').glob('*.java'))
    flags=['-cp',str(args.android_jar)] if args.android_jar else []
    subprocess.run([*compiler,'-source','17','-target','17','-Xlint:all,-options',*flags,'-d',str(directory),*map(str,files),str(ROOT/'pool-02-biometrics/tests/java/co/analematica/approval/ApprovalCheck.java')],check=True,timeout=60)
    subprocess.run(['java','-cp',str(directory),'co.analematica.approval.ApprovalCheck',str(directory/'message'),str(directory/'public'),str(directory/'signature')],check=True,timeout=60)
    public=ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(),(directory/'public').read_bytes())
    public.verify((directory/'signature').read_bytes(),message,ec.ECDSA(hashes.SHA256()))
print('Backend payload / JCE signature / Python P-256 verification passed. Hardware not exercised.')
