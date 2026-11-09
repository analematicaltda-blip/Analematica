"""Local test-only XSD validation; not DIAN acceptance or a server intake route."""
import hashlib,json,sys
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[2]/'shared/accounting/vendor/ubl21-reference'
manifest=json.loads((ROOT/'PROVENANCE.json').read_text())
for filename,digest in manifest['files'].items():
 path=(ROOT/filename).resolve()
 if not path.is_relative_to(ROOT.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Reference schema integrity mismatch')
parser=etree.XMLParser(resolve_entities=False,load_dtd=False,no_network=True)
# Dependencies are namespace-only imports in the mirrored Java resources.
# An explicit local catalog loads their unmodified schemas first; no remote fetch.
catalog=etree.Element('{http://www.w3.org/2001/XMLSchema}schema',nsmap={'xs':'http://www.w3.org/2001/XMLSchema'})
for filename in manifest['validation_import_order']:
 target=etree.parse(str(ROOT/filename),parser).getroot().get('targetNamespace')
 etree.SubElement(catalog,'{http://www.w3.org/2001/XMLSchema}import',namespace=target,schemaLocation=filename)
schema=etree.XMLSchema(etree.fromstring(etree.tostring(catalog),parser,base_url=(ROOT/'local-reference-catalog.xsd').resolve().as_uri()))
documents=json.load(sys.stdin)
if not isinstance(documents,list) or not 1<=len(documents)<=20:raise ValueError('Bounded synthetic document list required')
for text in documents:
 if not isinstance(text,str) or len(text.encode())>200000 or '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():raise ValueError('External declarations or oversized document rejected')
 schema.assertValid(etree.fromstring(text.encode(),parser))
# Ensure the reference actually rejects missing mandatory content.
try:schema.assertValid(etree.fromstring(b'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"/>',parser))
except etree.DocumentInvalid:pass
else:raise AssertionError('Reference failed to enforce mandatory structure')
print(json.dumps({'xsd_reference_validated_documents':len(documents),'schema_files_verified':len(manifest['files']),'schema_reference':manifest['schema_header'],'dian_profile_validated':False,'fiscal_accepted':False}))
