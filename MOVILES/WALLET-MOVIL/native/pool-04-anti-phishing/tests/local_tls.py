"""Actual loopback TLS tests with temporary CA/keys. Needs local port 443 free.
No external endpoint, production certificate or user credential is used.
"""
import base64
from datetime import datetime,timedelta,timezone
import hashlib
import http.server
import ipaddress
from pathlib import Path
import shutil
import ssl
import subprocess
import tempfile
import threading
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID,ExtendedKeyUsageOID
ROOT=Path(__file__).resolve().parents[2]
NOW=datetime.now(timezone.utc)

def key():return ec.generate_private_key(ec.SECP256R1())
def pin(public):return 'sha256/'+base64.b64encode(hashlib.sha256(public.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).digest()).decode()
def cert(subject,private,issuer,signer,ca=False,correct_host=True):
    builder=x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,subject)])).issuer_name(issuer).public_key(private.public_key()).serial_number(x509.random_serial_number()).not_valid_before(NOW-timedelta(minutes=1)).not_valid_after(NOW+timedelta(days=1)).add_extension(x509.BasicConstraints(ca=ca,path_length=None),True)
    if not ca:
        names=[x509.IPAddress(ipaddress.ip_address('127.0.0.1'))] if correct_host else [x509.DNSName('other.example.test')]
        builder=builder.add_extension(x509.SubjectAlternativeName(names),False).add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),False)
    return builder.sign(signer,hashes.SHA256())

class Server(http.server.HTTPServer):
    allow_reuse_address=True
    def handle_error(self,*args):pass
class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.seen.append(self.path)
        self.rfile.read(int(self.headers.get('Content-Length','0')))
        if self.path=='/redirect':
            self.send_response(302);self.send_header('Location','https://127.0.0.1/leak');self.send_header('Content-Length','0');self.end_headers();return
        body=b'verified';self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,*args):pass

compiler=[shutil.which('javac')] if shutil.which('javac') else ['java','-m','jdk.compiler/com.sun.tools.javac.Main']
with tempfile.TemporaryDirectory(prefix='sgacd-loopback-tls-') as temp:
    folder=Path(temp);ca_key=key();ca_name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'public fixture CA')]);ca=cert('public fixture CA',ca_key,ca_name,ca_key,ca=True)
    ca_file=folder/'ca.pem';ca_file.write_bytes(ca.public_bytes(serialization.Encoding.PEM));store=folder/'fixture.p12'
    source=ROOT/'pool-04-anti-phishing/android/src/main/java/co/analematica/protection'
    subprocess.run([*compiler,'-source','17','-target','17','-Xlint:all,-options','-d',str(folder),str(source/'OriginPinPolicy.java'),str(source/'PinnedHttpsClient.java'),str(ROOT/'pool-04-anti-phishing/tests/java/co/analematica/protection/LocalTLSCheck.java')],check=True,timeout=60)
    java=['java','-cp',str(folder),'co.analematica.protection.LocalTLSCheck']
    subprocess.run([*java,'store',str(ca_file),str(store)],check=True,timeout=30)
    java=['java',f'-Djavax.net.ssl.trustStore={store}','-Djavax.net.ssl.trustStorePassword=fixture-only','-cp',str(folder),'co.analematica.protection.LocalTLSCheck','request']
    backup=pin(key().public_key())
    for scenario in ['trusted','untrusted-ca','wrong-host']:
        private=key();signer=key() if scenario=='untrusted-ca' else ca_key
        issuer=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'untrusted fixture')]) if scenario=='untrusted-ca' else ca_name
        leaf=cert('public fixture server',private,issuer,signer,correct_host=scenario!='wrong-host')
        pem=folder/'server.pem';pem.write_bytes(leaf.public_bytes(serialization.Encoding.PEM));secret=folder/'key.pem';secret.write_bytes(private.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));secret.chmod(0o600)
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(pem,secret)
        server=Server(('127.0.0.1',443),Handler);server.seen=[];server.socket=context.wrap_socket(server.socket,server_side=True)
        thread=threading.Thread(target=lambda:server.serve_forever(poll_interval=0.05),daemon=True);thread.start()
        try:
            leaf_pin=pin(private.public_key())
            if scenario=='trusted':
                subprocess.run([*java,'pass',leaf_pin,backup,'/ok','valid-pin'],check=True,timeout=20)
                subprocess.run([*java,'reject',pin(key().public_key()),backup,'/should-never-arrive','wrong-pin'],check=True,timeout=20)
                subprocess.run([*java,'reject',leaf_pin,backup,'/redirect','redirect'],check=True,timeout=20)
                assert server.seen==['/ok','/redirect'],server.seen
            else:
                subprocess.run([*java,'reject',leaf_pin,backup,'/should-never-arrive',scenario],check=True,timeout=20)
                assert server.seen==[],server.seen
        finally:server.shutdown();server.server_close();thread.join(timeout=2)
print('Loopback TLS passed: valid PKI+pin; wrong pin; untrusted CA despite matching pin; wrong hostname despite matching pin; redirect refusal. No external calls.')
