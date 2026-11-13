"""Strict offline Android Key Attestation verification; no client trust booleans.

Roots, package/signers and revocation feed are trusted SERVER configuration.
No default root, test CA, network fetch or software-key fallback is shipped.
"""
from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
import hashlib
import hmac
import re
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec,rsa
from cryptography.x509.oid import ExtensionOID,ObjectIdentifier

ATTESTATION_OID=ObjectIdentifier('1.3.6.1.4.1.11129.2.1.17')

class AttestationRejected(ValueError):
    """Stable code only. Never include certificate, identity or raw claims."""

@dataclass(frozen=True)
class Node:
    cls: int
    constructed: bool
    tag: int
    value: bytes


def nodes(data):
    """Bounded, canonical definite-length DER; disallows trailing/indefinite data."""
    if not isinstance(data,bytes) or len(data)>16384:raise AttestationRejected('DER_SIZE')
    result=[];offset=0
    while offset<len(data):
        if len(result)>=128:raise AttestationRejected('DER_ELEMENTS')
        first=data[offset];offset+=1;tag=first&31
        if tag==31:
            tag=0;count=0
            while True:
                if offset>=len(data) or count>=4:raise AttestationRejected('DER_TAG')
                item=data[offset];offset+=1
                if count==0 and item&127==0:raise AttestationRejected('DER_TAG')
                tag=(tag<<7)|(item&127);count+=1
                if not item&128:break
            if tag<31:raise AttestationRejected('DER_TAG')
        if offset>=len(data):raise AttestationRejected('DER_LENGTH')
        size=data[offset];offset+=1
        if size&128:
            count=size&127
            if not 1<=count<=3 or offset+count>len(data) or data[offset]==0:raise AttestationRejected('DER_LENGTH')
            size=int.from_bytes(data[offset:offset+count],'big');offset+=count
            if size<128:raise AttestationRejected('DER_LENGTH')
        if offset+size>len(data):raise AttestationRejected('DER_TRUNCATED')
        result.append(Node(first>>6,bool(first&32),tag,data[offset:offset+size]));offset+=size
    return result


def expect(node,tag,constructed=False):
    if node.cls!=0 or node.tag!=tag or node.constructed!=constructed:raise AttestationRejected('DER_TYPE')
    return node.value


def integer(node,tag=2):
    value=expect(node,tag)
    if not value or len(value)>9 or value[0]&128 or (len(value)>1 and value[0]==0 and not value[1]&128):raise AttestationRejected('DER_INTEGER')
    return int.from_bytes(value,'big')


def sequence(node):return nodes(expect(node,16,True))


def integer_set(node):
    values=[integer(value) for value in nodes(expect(node,17,True))]
    if not values or len(set(values))!=len(values):raise AttestationRejected('DER_SET')
    return set(values)


def authorizations(node):
    result={}
    for item in sequence(node):
        if item.cls!=2 or not item.constructed or item.tag in result:raise AttestationRejected('AUTHORIZATION_TAG')
        value=nodes(item.value)
        if len(value)!=1:raise AttestationRejected('AUTHORIZATION_VALUE')
        result[item.tag]=value[0]
    return result


@dataclass(frozen=True)
class RevocationSnapshot:
    observed_at: datetime
    valid_until: datetime
    revoked_serials: frozenset
    def require_fresh(self,now):
        if self.observed_at.tzinfo is None or self.valid_until.tzinfo is None or not self.observed_at<=now<self.valid_until<=self.observed_at+timedelta(hours=24):raise AttestationRejected('REVOCATIONS_STALE')
        if not isinstance(self.revoked_serials,frozenset) or any(type(value)is not int or value<=0 for value in self.revoked_serials):raise AttestationRejected('REVOCATIONS_INVALID')


@dataclass(frozen=True)
class AndroidAttestationPolicy:
    trusted_roots: tuple
    package_name: str
    signer_sha256: frozenset
    minimum_package_version: int
    minimum_os_version: int
    minimum_patch_level: int
    require_strongbox: bool=True
    maximum_patch_age_days: int=90
    def __post_init__(self):
        if not isinstance(self.package_name,str) or re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+',self.package_name) is None:raise AttestationRejected('POLICY_PACKAGE')
        if not isinstance(self.trusted_roots,tuple) or not 1<=len(self.trusted_roots)<=4 or any(not isinstance(root,bytes) or len(root)>16384 for root in self.trusted_roots):raise AttestationRejected('POLICY_ROOTS')
        try:
            if len(set(self.trusted_roots))!=len(self.trusted_roots):raise ValueError()
            for raw in self.trusted_roots:
                root=x509.load_der_x509_certificate(raw)
                if not root.extensions.get_extension_for_class(x509.BasicConstraints).value.ca or not root.extensions.get_extension_for_class(x509.KeyUsage).value.key_cert_sign:raise ValueError()
                root.verify_directly_issued_by(root)
        except Exception:raise AttestationRejected('POLICY_ROOT_CERTIFICATE_INVALID') from None
        if not isinstance(self.signer_sha256,frozenset) or not 1<=len(self.signer_sha256)<=4 or any(not isinstance(pin,str) or re.fullmatch('[0-9a-f]{64}',pin) is None for pin in self.signer_sha256):raise AttestationRejected('POLICY_SIGNERS')
        if type(self.minimum_package_version)is not int or self.minimum_package_version<1 or type(self.minimum_os_version)is not int or self.minimum_os_version<120000 or type(self.maximum_patch_age_days)is not int or not 1<=self.maximum_patch_age_days<=90 or type(self.require_strongbox)is not bool:raise AttestationRejected('POLICY_LIMITS')
        if type(self.minimum_patch_level)is not int or re.fullmatch('[0-9]{6}',str(self.minimum_patch_level)) is None:raise AttestationRejected('POLICY_PATCH')
        try:datetime.strptime(str(self.minimum_patch_level),'%Y%m')
        except ValueError:raise AttestationRejected('POLICY_PATCH')
    @property
    def digest(self):
        import json
        value={'roots':sorted(hashlib.sha256(root).hexdigest() for root in self.trusted_roots),'package':self.package_name,'signers':sorted(self.signer_sha256),'version':self.minimum_package_version,'os':self.minimum_os_version,'patch':self.minimum_patch_level,'strongbox':self.require_strongbox,'patch_age':self.maximum_patch_age_days}
        return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


class AndroidAttestationVerifier:
    def __init__(self,policy,revocations):
        if type(policy)is not AndroidAttestationPolicy or not callable(revocations):raise AttestationRejected('SERVER_CONFIGURATION_REQUIRED')
        self.policy=policy;self.revocations=revocations
    def snapshot(self,now):
        result=self.revocations()
        if type(result)is not RevocationSnapshot:raise AttestationRejected('REVOCATIONS_INVALID')
        result.require_fresh(now);return result
    def check_registered(self,credential):
        now=datetime.now(timezone.utc);snapshot=self.snapshot(now)
        serials=credential.attestation_serials
        if credential.attestation_platform!='ANDROID_KEY_ATTESTATION' or credential.attestation_policy_digest!=self.policy.digest or not isinstance(serials,list) or not 2<=len(serials)<=8 or any(not isinstance(value,str) or re.fullmatch('[1-9a-f][0-9a-f]{0,39}',value) is None for value in serials):raise AttestationRejected('REGISTERED_TRUST_MISMATCH')
        if any(int(value,16) in snapshot.revoked_serials for value in serials):raise AttestationRejected('CERTIFICATE_REVOKED')
    def __call__(self,credential,public_key,certificates):
        from .device_approvals import VerifiedAttestation
        now=datetime.now(timezone.utc);policy=self.policy;snapshot=self.snapshot(now)
        if not isinstance(certificates,tuple) or not 2<=len(certificates)<=8 or any(not isinstance(value,bytes) or not value or len(value)>16384 for value in certificates):raise AttestationRejected('CERTIFICATE_CHAIN_SIZE')
        try:
            chain=[x509.load_der_x509_certificate(value) for value in certificates]
            if len(set(certificates))!=len(chain) or certificates[-1] not in policy.trusted_roots:raise AttestationRejected('UNTRUSTED_ROOT')
            for index,cert in enumerate(chain):
                if cert.serial_number in snapshot.revoked_serials:raise AttestationRejected('CERTIFICATE_REVOKED')
                if not cert.not_valid_before_utc<=now<cert.not_valid_after_utc:raise AttestationRejected('CERTIFICATE_EXPIRED')
                key=cert.public_key()
                if isinstance(key,rsa.RSAPublicKey):
                    if key.key_size<2048:raise AttestationRejected('WEAK_CERTIFICATE_KEY')
                elif not isinstance(key,ec.EllipticCurvePublicKey) or key.key_size<256:raise AttestationRejected('UNSUPPORTED_CERTIFICATE_KEY')
                if cert.signature_hash_algorithm.name not in {'sha256','sha384','sha512'}:raise AttestationRejected('WEAK_CERTIFICATE_SIGNATURE')
                for extension in cert.extensions:
                    if extension.critical and extension.oid not in {ExtensionOID.BASIC_CONSTRAINTS,ExtensionOID.KEY_USAGE,ATTESTATION_OID}:raise AttestationRejected('UNSUPPORTED_CRITICAL_EXTENSION')
                if index>0:
                    constraints=cert.extensions.get_extension_for_class(x509.BasicConstraints).value
                    if not constraints.ca or (constraints.path_length is not None and index-1>constraints.path_length):raise AttestationRejected('INVALID_CA_CONSTRAINTS')
                    usage=cert.extensions.get_extension_for_class(x509.KeyUsage).value
                    if not usage.key_cert_sign:raise AttestationRejected('INVALID_CA_USAGE')
                    try:cert.extensions.get_extension_for_oid(ATTESTATION_OID)
                    except x509.ExtensionNotFound:pass
                    else:raise AttestationRejected('ATTESTATION_NOT_LEAF')
                else:
                    try:
                        if cert.extensions.get_extension_for_class(x509.BasicConstraints).value.ca:raise AttestationRejected('LEAF_IS_CA')
                    except x509.ExtensionNotFound:pass
                    try:
                        usage=cert.extensions.get_extension_for_class(x509.KeyUsage).value
                        if not usage.digital_signature or usage.key_cert_sign:raise AttestationRejected('INVALID_LEAF_USAGE')
                    except x509.ExtensionNotFound:pass
                cert.verify_directly_issued_by(chain[index+1] if index+1<len(chain) else cert)
            leaf=chain[0].public_key()
            if not isinstance(leaf,ec.EllipticCurvePublicKey) or not isinstance(leaf.curve,ec.SECP256R1) or leaf.public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)!=public_key:raise AttestationRejected('ATTESTED_KEY_MISMATCH')
            encoded=chain[0].extensions.get_extension_for_oid(ATTESTATION_OID).value.value
            outer=nodes(encoded)
            if len(outer)!=1:raise AttestationRejected('ATTESTATION_STRUCTURE')
            fields=sequence(outer[0])
            if len(fields)!=8 or integer(fields[0])<3 or integer(fields[2])<4:raise AttestationRejected('ATTESTATION_VERSION')
            levels={2} if policy.require_strongbox else {1,2}
            if integer(fields[1],10) not in levels or integer(fields[3],10) not in levels:raise AttestationRejected('HARDWARE_SECURITY_LEVEL')
            nonce=expect(fields[4],4)
            if len(nonce)!=32 or not hmac.compare_digest(hashlib.sha256(nonce).hexdigest(),credential.enrollment_nonce_hash):raise AttestationRejected('ENROLLMENT_NONCE_MISMATCH')
            expect(fields[5],4)
            software,hardware=authorizations(fields[6]),authorizations(fields[7])
            security={1,2,3,5,10,503,504,505,506,600,702,704,705,706,718,719}
            if security.intersection(software) or 503 in hardware or 506 in hardware or 600 in hardware:raise AttestationRejected('SOFTWARE_OR_UNRESTRICTED_AUTHORIZATION')
            if integer_set(hardware[1])!={2,3} or integer(hardware[2])!=3 or integer(hardware[3])!=256 or integer_set(hardware[5])!={4} or integer(hardware[10])!=1 or integer(hardware[702])!=0:raise AttestationRejected('KEY_PURPOSE_MISMATCH')
            if integer(hardware[504])!=2 or (505 in hardware and integer(hardware[505])!=0):raise AttestationRejected('PER_OPERATION_BIOMETRICS_REQUIRED')
            unlocked=hardware.get(509,software.get(509))
            if unlocked is None or expect(unlocked,5)!=b'':raise AttestationRejected('UNLOCKED_DEVICE_REQUIRED')
            root=sequence(hardware[704])
            if len(root)!=4 or len(expect(root[0],4))!=32 or expect(root[1],1)!=b'\xff' or integer(root[2],10)!=0 or len(expect(root[3],4))!=32:raise AttestationRejected('VERIFIED_BOOT_REQUIRED')
            if integer(hardware[705])<policy.minimum_os_version:raise AttestationRejected('OS_VERSION_TOO_OLD')
            patch=integer(hardware[706])
            if re.fullmatch('[0-9]{6}',str(patch)) is None or patch<policy.minimum_patch_level:raise AttestationRejected('OS_PATCH_TOO_OLD')
            patch_date=datetime.strptime(str(patch),'%Y%m').replace(tzinfo=timezone.utc)
            if patch_date>now or now-patch_date>timedelta(days=policy.maximum_patch_age_days):raise AttestationRejected('OS_PATCH_STALE')
            for tag in [718,719]:
                raw_date=str(integer(hardware[tag]))
                if re.fullmatch('[0-9]{8}',raw_date) is None:raise AttestationRejected('PATCH_FORMAT')
                date=datetime.strptime(raw_date,'%Y%m%d').replace(tzinfo=timezone.utc)
                if date>now or now-date>timedelta(days=policy.maximum_patch_age_days) or int(date.strftime('%Y%m'))<policy.minimum_patch_level:raise AttestationRejected('BOOT_OR_VENDOR_PATCH_STALE')
            app=nodes(expect(software[709],4))
            if len(app)!=1:raise AttestationRejected('APPLICATION_BINDING')
            app=sequence(app[0])
            if len(app)!=2:raise AttestationRejected('APPLICATION_BINDING')
            packages=nodes(expect(app[0],17,True));signers=nodes(expect(app[1],17,True))
            if len(packages)!=1 or not 1<=len(signers)<=4:raise AttestationRejected('APPLICATION_BINDING')
            package=sequence(packages[0])
            if len(package)!=2 or expect(package[0],4)!=policy.package_name.encode() or integer(package[1])<policy.minimum_package_version:raise AttestationRejected('APPLICATION_ID_OR_VERSION')
            if any(len(expect(signer,4))!=32 or expect(signer,4).hex() not in policy.signer_sha256 for signer in signers):raise AttestationRejected('APPLICATION_SIGNER')
            if 709 in hardware:raise AttestationRejected('APPLICATION_BINDING_LOCATION')
            expiry=min(now+timedelta(days=7,seconds=-60),*(cert.not_valid_after_utc for cert in chain))
            return VerifiedAttestation(credential.pk,credential.user_id,credential.audience,public_key,hashlib.sha256(nonce).hexdigest(),expiry,True,'ANDROID_KEY_ATTESTATION',policy.digest,tuple(format(cert.serial_number,'x') for cert in chain))
        except AttestationRejected:raise
        except Exception as error:raise AttestationRejected('MALFORMED_OR_INVALID_ATTESTATION') from error
