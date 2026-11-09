"""Customer-host signed UBL ApplicationResponse verifier, LABORATORY ONLY.

Not a DIAN parser qualified against the current annex, official trust policy,
transport, or fiscal acceptance. Signed synthetic states cannot authorize posting.
"""
from datetime import datetime, timezone
import hashlib,json,re
from uuid import UUID
from lxml import etree
from signxml import XMLVerifier,SignatureConfiguration,SignatureMethod,DigestAlgorithm,CanonicalizationMethod
from local_signer import certificates,NS,LOCATION,LaboratorySigningError

APPLICATION='urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2'
FIELDS={'mode','company_id','document_id','invoice_number','invoice_fingerprint',
        'sender_id','recipient_id','environment','leaf_sha256','root_sha256','certificate_subject_serial'}
STATES={'LAB_ACCEPTED':'ACCEPTED_LAB_ONLY','LAB_REJECTED':'REJECTED_LAB_ONLY','LAB_PENDING':'PENDING_LAB_ONLY'}
MAX=1024*1024

def checked_profile(profile):
    if not isinstance(profile,dict) or set(profile)!=FIELDS or any(not isinstance(v,str) for v in profile.values()) or profile['mode']!='LABORATORY_ONLY':
        raise LaboratorySigningError('Explicit laboratory receipt profile required.')
    for key in ('company_id','document_id'):
        if str(UUID(profile[key]))!=profile[key]:raise LaboratorySigningError('Canonical scoped receipt identifiers required.')
    if (not re.fullmatch('[A-Z0-9-]{1,30}',profile['invoice_number'])
            or not re.fullmatch('[0-9a-f]{96}',profile['invoice_fingerprint'])
            or any(not re.fullmatch('[0-9]{6,15}',profile[k]) for k in ('sender_id','recipient_id'))
            or profile['environment']!='HABILITACION-LAB'
            or not 1<=len(profile['certificate_subject_serial'])<=100
            or any(not re.fullmatch('[0-9a-f]{64}',profile[k]) for k in ('leaf_sha256','root_sha256'))):
        raise LaboratorySigningError('Pinned identities and explicit laboratory environment required.')
    return dict(profile)

def parse(raw):
    if not isinstance(raw,bytes) or not 0<len(raw)<=MAX:
        raise LaboratorySigningError('Bounded UTF-8 response required.')
    text=raw.decode('utf-8')
    if '\x00' in text or '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise LaboratorySigningError('External declarations forbidden.')
    root=etree.fromstring(raw,etree.XMLParser(resolve_entities=False,load_dtd=False,no_network=True,remove_blank_text=False))
    if root.tag!='{'+APPLICATION+'}ApplicationResponse':
        raise LaboratorySigningError('Exactly one UBL ApplicationResponse root required.')
    return root

def semantic(root,profile):
    def one(path):
        values=root.xpath(path,namespaces=NS)
        if len(values)!=1 or values[0].text is None or len(values[0])!=0:
            raise LaboratorySigningError('Unambiguous scalar receipt identity required.')
        return values[0].text
    if one('./cbc:CustomizationID')!='SGACD-LAB-RECEIPT' or one('./cbc:ProfileID')!='LABORATORY-ONLY' or one('./cbc:ProfileExecutionID')!=profile['environment']:
        raise LaboratorySigningError('Real or mismatched fiscal profiles cannot use the laboratory verifier.')
    receipt_id=one('./cbc:UUID')
    if str(UUID(receipt_id))!=receipt_id:raise LaboratorySigningError('Canonical laboratory response UUID required.')
    for name in ('SenderParty','ReceiverParty'):
        parties=root.findall('cac:'+name,NS)
        if len(parties)!=1 or len(parties[0].findall('cac:PartyTaxScheme',NS))!=1:
            raise LaboratorySigningError('One unambiguous sender and receiver required.')
    responses=root.findall('cac:DocumentResponse',NS)
    if len(responses)!=1 or len(responses[0].findall('cac:Response',NS))!=1 or len(responses[0].findall('cac:DocumentReference',NS))!=1:
        raise LaboratorySigningError('One explicit document response/reference required.')
    expected={
        './cac:SenderParty/cac:PartyTaxScheme/cbc:CompanyID':profile['sender_id'],
        './cac:ReceiverParty/cac:PartyTaxScheme/cbc:CompanyID':profile['recipient_id'],
        './cac:DocumentResponse/cac:DocumentReference/cbc:ID':profile['invoice_number'],
        './cac:DocumentResponse/cac:DocumentReference/cbc:UUID':profile['invoice_fingerprint'],
    }
    if any(one(path)!=value for path,value in expected.items()):
        raise LaboratorySigningError('Response does not correspond to the reviewed issuer, recipient or document.')
    code=one('./cac:DocumentResponse/cac:Response/cbc:ResponseCode')
    if code not in STATES:raise LaboratorySigningError('Only explicitly synthetic laboratory response codes supported.')
    return receipt_id,STATES[code]

def verify_receipt(raw,*,profile,leaf_pem,root_pem,now=None):
    """Cryptographic verification first; semantic extraction only from signed root.

    No caller-supplied `signature_valid` boolean or verifier callback can authorize
    acceptance. No network, revocation lookup, XML retrieval or database writes.
    """
    profile=checked_profile(profile);now=now or datetime.now(timezone.utc)
    certificates(leaf_pem,root_pem,profile,now)
    root=parse(raw)
    signatures=root.xpath('.//ds:Signature',namespaces=NS)
    if len(signatures)!=1 or signatures!=root.xpath(LOCATION,namespaces=NS):
        raise LaboratorySigningError('One signature in the UBL extension required.')
    refs=signatures[0].xpath('./ds:SignedInfo/ds:Reference',namespaces=NS)
    if len(refs)!=1 or refs[0].get('URI')!='':
        raise LaboratorySigningError('Only the complete receipt root may be signed; no external references.')
    config=SignatureConfiguration(require_x509=True,expect_references=1,
        signature_methods=frozenset({SignatureMethod.RSA_SHA256}),
        digest_algorithms=frozenset({DigestAlgorithm.SHA256}),
        default_reference_c14n_method=CanonicalizationMethod.CANONICAL_XML_1_0)
    verified=XMLVerifier().verify(root,x509_cert=leaf_pem,expect_config=config).signed_xml
    if verified is None or verified.tag!='{'+APPLICATION+'}ApplicationResponse':
        raise LaboratorySigningError('Signature must cover the complete ApplicationResponse.')
    receipt_id,state=semantic(verified,profile)
    return {'schema':'sgacd-laboratory-receipt-verification-v1','mode':'LABORATORY_ONLY',
        'company_id':profile['company_id'],'document_id':profile['document_id'],
        'receipt_id':receipt_id,'response_sha256':hashlib.sha256(raw).hexdigest(),
        'reviewed_profile_sha256':hashlib.sha256(json.dumps(profile,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'laboratory_response_state':state,'xml_signature_verified':True,'laboratory_chain_verified':True,
        'document_identity_matched':True,'fiscal_accepted':False,'dian_origin_verified':False,
        'dian_profile_validated':False,'certificate_revocation_checked':False,'full_pkix_qualified':False,
        'trusted_timestamp_verified':False,'network_called':False,'ledger_written':False,
        'number_allocated':False,'usable_as_fiscal_acceptance':False}
