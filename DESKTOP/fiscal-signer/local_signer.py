"""Restricted local XAdES laboratory signer, never a fiscal submission route.

Only explicitly pinned two-certificate RSA laboratory chains are supported.
No intermediates, revocation, full PKIX, hardware custody or DIAN qualification.
"""
import base64,copy,hashlib,hmac,json,re
from datetime import datetime,timezone
from uuid import UUID
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.x509.oid import NameOID,ExtensionOID,ExtendedKeyUsageOID,SignatureAlgorithmOID
from lxml import etree
from signxml import SignatureMethod,DigestAlgorithm,CanonicalizationMethod,methods
from signxml.xades import XAdESSigner,XAdESVerifier,XAdESSignaturePolicy,XAdESDataObjectFormat,XAdESSignatureConfiguration
from package_crypto import open_package,seal_package,MAX
NS={'inv':'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2','cbc':'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2','cac':'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2','ext':'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2','ds':'http://www.w3.org/2000/09/xmldsig#','xades':'http://uri.etsi.org/01903/v1.3.2#'}
LOCATION='./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature'
FIELDS={'mode','company_id','document_id','supplier_nit','source_sha256','leaf_sha256','root_sha256','certificate_subject_serial','policy_id','policy_sha256'}

class LaboratorySigningError(ValueError):pass

def profile_checked(profile):
    if not isinstance(profile,dict) or set(profile)!=FIELDS or any(not isinstance(v,str) for v in profile.values()) or profile['mode']!='LABORATORY_ONLY':raise LaboratorySigningError('Only an explicit laboratory profile is supported.')
    if any(not isinstance(profile[k],str) or str(UUID(profile[k]))!=profile[k] for k in ('company_id','document_id')):raise LaboratorySigningError('Canonical document/company IDs required.')
    if not re.fullmatch('[0-9]{6,15}',profile['supplier_nit']) or not profile['policy_id'].startswith('urn:sgacd:lab-policy:') or not 1<=len(profile['certificate_subject_serial'])<=100:raise LaboratorySigningError('Explicit laboratory identity and policy required.')
    if any(not isinstance(profile[k],str) or not re.fullmatch('[0-9a-f]{64}',profile[k]) for k in ('source_sha256','leaf_sha256','root_sha256','policy_sha256')):raise LaboratorySigningError('Pinned digests required.')
    return copy.deepcopy(profile)

def parse_invoice(raw,profile):
    if not isinstance(raw,bytes) or not 0<len(raw)<=MAX:raise LaboratorySigningError('Bounded UTF-8 document required.')
    text=raw.decode('utf-8')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper() or '\x00' in text:raise LaboratorySigningError('External declarations are forbidden.')
    root=etree.fromstring(raw,etree.XMLParser(resolve_entities=False,load_dtd=False,no_network=True,remove_blank_text=False))
    if root.tag!='{'+NS['inv']+'}Invoice':raise LaboratorySigningError('One UBL invoice root required.')
    def field(path):
        found=root.xpath(path,namespaces=NS)
        if len(found)!=1 or not found[0].text:return None
        return found[0].text
    if field('./cbc:UUID')!=profile['document_id'] or field('./cbc:CustomizationID')!='SGACD-STRUCTURAL-DRAFT' or field('./cbc:ProfileID')!='LOCAL-UNSIGNED-DRAFT' or field('./cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:CompanyID')!=profile['supplier_nit'] or not any('BORRADOR' in (n.text or '') for n in root.findall('cbc:Note',NS)):raise LaboratorySigningError('Only reviewed local, non-fiscal UBL drafts are supported.')
    return root

def certificates(leaf_pem,root_pem,profile,now):
    if now.tzinfo is None:raise LaboratorySigningError('Timezone-aware verification time required.')
    if len(leaf_pem)>16384 or len(root_pem)>16384:raise LaboratorySigningError('Certificate size bound exceeded.')
    leaf=x509.load_pem_x509_certificate(leaf_pem);root=x509.load_pem_x509_certificate(root_pem)
    for cert,key in [(leaf,'leaf_sha256'),(root,'root_sha256')]:
        if cert.fingerprint(hashes.SHA256()).hex()!=profile[key] or not cert.not_valid_before_utc<=now<=cert.not_valid_after_utc:raise LaboratorySigningError('Pinned laboratory certificate not current.')
        if 'SGACD LABORATORY ONLY' not in [v.value for v in cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)]:raise LaboratorySigningError('Real/unknown certificate profiles cannot be used in this laboratory signer.')
        if not isinstance(cert.public_key(),rsa.RSAPublicKey) or not 2048<=cert.public_key().key_size<=8192 or cert.signature_algorithm_oid!=SignatureAlgorithmOID.RSA_WITH_SHA256:raise LaboratorySigningError('Bounded RSA-SHA256 laboratory chain required.')
        if any(ext.critical and ext.oid not in {ExtensionOID.BASIC_CONSTRAINTS,ExtensionOID.KEY_USAGE} for ext in cert.extensions):raise LaboratorySigningError('Unsupported critical certificate extension.')
    if leaf.issuer!=root.subject or root.issuer!=root.subject or leaf.subject==root.subject:raise LaboratorySigningError('Exactly one laboratory leaf and self-signed root required.')
    root.public_key().verify(root.signature,root.tbs_certificate_bytes,padding.PKCS1v15(),root.signature_hash_algorithm);root.public_key().verify(leaf.signature,leaf.tbs_certificate_bytes,padding.PKCS1v15(),leaf.signature_hash_algorithm)
    ca=root.extensions.get_extension_for_class(x509.BasicConstraints).value;end=leaf.extensions.get_extension_for_class(x509.BasicConstraints).value;usage=leaf.extensions.get_extension_for_class(x509.KeyUsage).value;ca_usage=root.extensions.get_extension_for_class(x509.KeyUsage).value
    serials=leaf.subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
    if not ca.ca or ca.path_length!=0 or end.ca or not ca_usage.key_cert_sign or not usage.digital_signature or usage.key_cert_sign or ExtendedKeyUsageOID.CODE_SIGNING not in leaf.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value or len(serials)!=1 or serials[0].value!=profile['certificate_subject_serial']:raise LaboratorySigningError('Laboratory chain purpose/identity incompatible.')
    return leaf,root

def policy_checked(policy,profile):
    if not isinstance(policy,bytes) or not 0<len(policy)<=MAX or hashlib.sha256(policy).hexdigest()!=profile['policy_sha256']:raise LaboratorySigningError('Local policy bytes do not match reviewed digest.')
    return XAdESSignaturePolicy(Identifier=profile['policy_id'],Description='SGACD LABORATORY ONLY - NOT DIAN QUALIFIED',DigestMethod=DigestAlgorithm.SHA256,DigestValue=base64.b64encode(hashlib.sha256(policy).digest()).decode())

def verify_lab_xml(raw,*,profile,leaf_pem,root_pem,policy,reviewed_source,now=None):
    profile=profile_checked(profile);now=now or datetime.now(timezone.utc);leaf,_=certificates(leaf_pem,root_pem,profile,now);expected_policy=policy_checked(policy,profile);root=parse_invoice(raw,profile)
    signatures=root.xpath('.//ds:Signature',namespaces=NS);placed=root.xpath(LOCATION,namespaces=NS)
    if len(signatures)!=1 or signatures!=placed:raise LaboratorySigningError('Exactly one signature in the UBL extension is required.')
    refs=signatures[0].xpath('./ds:SignedInfo/ds:Reference',namespaces=NS)
    if len(refs)!=3 or any(n.get('URI') is None or n.get('URI')!='' and not n.get('URI').startswith('#') for n in refs):raise LaboratorySigningError('Only three local signature references are permitted.')
    config=XAdESSignatureConfiguration(require_x509=True,expect_references=3,signature_methods=frozenset({SignatureMethod.RSA_SHA256}),digest_algorithms=frozenset({DigestAlgorithm.SHA256}),default_reference_c14n_method=CanonicalizationMethod.CANONICAL_XML_1_0)
    results=XAdESVerifier().verify(root,x509_cert=leaf_pem,expect_signature_policy=expected_policy,expect_config=config)
    documents=[r.signed_xml for r in results if r.signed_xml is not None and r.signed_xml.tag=='{'+NS['inv']+'}Invoice']
    if len(documents)!=1:raise LaboratorySigningError('Verified reference is not the invoice root.')
    parse_invoice(etree.tostring(documents[0]),profile)
    if hashlib.sha256(reviewed_source).hexdigest()!=profile['source_sha256']:raise LaboratorySigningError('Reviewed source digest mismatch.')
    source=parse_invoice(reviewed_source,profile)
    if source.find('ext:UBLExtensions',NS) is not None or source.xpath('.//ds:Signature',namespaces=NS):raise LaboratorySigningError('Reviewed source must be unsigned.')
    verified=copy.deepcopy(documents[0]);extensions=verified.findall('ext:UBLExtensions',NS)
    if len(extensions)!=1:raise LaboratorySigningError('Unexpected extension set.')
    verified.remove(extensions[0])
    if etree.tostring(verified,method='c14n',exclusive=True)!=etree.tostring(source,method='c14n',exclusive=True):raise LaboratorySigningError('Verified invoice differs from reviewed source.')
    descriptions=root.xpath('.//xades:DataObjectFormat/xades:Description/text()',namespaces=NS)
    if descriptions!=['SGACD reviewed input SHA256 '+profile['source_sha256']]:raise LaboratorySigningError('Reviewed-input digest is not bound in signed properties.')
    return {'xml_signature_verified':True,'reviewed_source_verified':True,'trusted_timestamp_verified':False,'laboratory_chain_verified':True,'local_policy_digest_verified':True,'certificate_revocation_checked':False,'full_pkix_qualified':False,'hardware_custody_verified':False,'fiscal_accepted':False,'dian_profile_validated':False,'network_called':False,'ledger_written':False,'mode':'LABORATORY_ONLY'}

def sign_package(value,*,package_password,key_pem,key_password,leaf_pem,root_pem,policy,profile,source_confirmation,sign_confirmation,now=None):
    profile=profile_checked(profile);expected={'company_id':profile['company_id'],'document_id':profile['document_id']};plain,original=open_package(value,package_password,expected)
    if source_confirmation!='REVISADO '+original['package_digest'][:12] or sign_confirmation!='FIRMAR LAB '+profile['document_id']:raise LaboratorySigningError('Two separate owner confirmations required.')
    if hashlib.sha256(plain).hexdigest()!=profile['source_sha256']:raise LaboratorySigningError('Document differs from the reviewed source.')
    root=parse_invoice(plain,profile)
    if root.xpath('.//ds:Signature',namespaces=NS) or root.find('ext:UBLExtensions',NS) is not None:raise LaboratorySigningError('An existing extension/signature requires a separate reviewed workflow.')
    now=now or datetime.now(timezone.utc);leaf,anchor=certificates(leaf_pem,root_pem,profile,now);signature_policy=policy_checked(policy,profile)
    if not isinstance(key_pem,bytes) or len(key_pem)>32768 or not key_pem.startswith(b'-----BEGIN ENCRYPTED PRIVATE KEY-----') or not isinstance(key_password,bytes) or not 16<=len(key_password)<=1024:raise LaboratorySigningError('Encrypted PKCS8 and explicit long local password required.')
    private=serialization.load_pem_private_key(key_pem,key_password)
    if not isinstance(private,rsa.RSAPrivateKey) or private.public_key().public_numbers()!=leaf.public_key().public_numbers():raise LaboratorySigningError('Private key does not match the pinned leaf certificate.')
    extensions=etree.Element('{'+NS['ext']+'}UBLExtensions',nsmap={'ext':NS['ext']});extension=etree.SubElement(extensions,'{'+NS['ext']+'}UBLExtension');content=etree.SubElement(extension,'{'+NS['ext']+'}ExtensionContent');etree.SubElement(content,'{'+NS['ds']+'}Signature',Id='placeholder');root.insert(0,extensions)
    signer=XAdESSigner(signature_policy=signature_policy,data_object_format=XAdESDataObjectFormat(Description='SGACD reviewed input SHA256 '+profile['source_sha256'],MimeType='text/xml'),method=methods.enveloped,signature_algorithm=SignatureMethod.RSA_SHA256,digest_algorithm=DigestAlgorithm.SHA256,c14n_algorithm=CanonicalizationMethod.CANONICAL_XML_1_0)
    signed=signer.sign(root,key=private,cert=[leaf]);raw=etree.tostring(signed,encoding='UTF-8',xml_declaration=True);report=verify_lab_xml(raw,profile=profile,leaf_pem=leaf_pem,root_pem=root_pem,policy=policy,reviewed_source=plain,now=now)
    if len(raw)>MAX or original['revision']>=1000000:raise LaboratorySigningError('Signed package outside supported version/size.')
    output=seal_package(raw,package_password,expected,original['revision']+1,original['package_digest']);return {'package':output,'report':report}
