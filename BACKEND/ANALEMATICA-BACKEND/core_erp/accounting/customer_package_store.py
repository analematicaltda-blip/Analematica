"""Explicit customer PostgreSQL version store. Opaque packages, never passwords.

Digest/shape checks are not HMAC verification: only the client has its KEK.
Service locking orders versions; privileged writers require separate qualification.
"""
import hashlib,json,re
from uuid import UUID
from .fiscal_envelope import inspect_envelope,decode,MAX_WIRE_BYTES
from .customer_postgres_store import CustomerPostgresStore,StorageConflict,initialize_customer_store

def inspect_package(value,company_id):
    keys={'schema','revision','previous_digest','key_descriptor','envelope','auth_tag','package_digest'}
    if not isinstance(value,dict) or set(value)!=keys or value['schema']!='sgacd-fiscal-package-v1':raise ValueError('Invalid customer package.')
    revision=value['revision'];previous=value['previous_digest']
    if type(revision) is not int or not 1<=revision<=1000000 or (revision==1 and previous is not None) or (revision>1 and (not isinstance(previous,str) or not re.fullmatch('[0-9a-f]{64}',previous))):raise ValueError('Invalid customer version.')
    descriptor=value['key_descriptor']
    if not isinstance(descriptor,dict) or set(descriptor)!={'kdf','iterations','salt'} or descriptor['kdf']!='PBKDF2-SHA256' or type(descriptor['iterations']) is not int or descriptor['iterations']!=600000:raise ValueError('Invalid customer key descriptor.')
    decode(descriptor['salt'],16,16);decode(value['auth_tag'],32,32)
    report=inspect_envelope(value['envelope'],company_id)
    body={k:v for k,v in value.items() if k!='package_digest'}
    encoded_body=json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    digest=hashlib.sha256(encoded_body).hexdigest()
    if value['package_digest']!=digest:raise ValueError('Package digest mismatch.')
    encoded=json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    if len(encoded)>MAX_WIRE_BYTES:raise ValueError('Package exceeds customer storage bound.')
    return {'company_id':report['company_id'],'document_id':report['document_id'],'revision':revision,'previous_digest':previous,'package_digest':digest},encoded

def initialize_customer_packages(connection,company_id):
    initialize_customer_store(connection,company_id)
    with connection.cursor() as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS public.customer_fiscal_packages (
            company_id uuid NOT NULL REFERENCES public.customer_fiscal_binding(company_id),document_id uuid NOT NULL,
            revision integer NOT NULL CHECK(revision BETWEEN 1 AND 1000000),
            package_digest varchar(64) NOT NULL UNIQUE CHECK(package_digest ~ '^[0-9a-f]{64}$'),
            previous_digest varchar(64),package_bytes bytea NOT NULL CHECK(octet_length(package_bytes)<=1500000),
            created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(document_id,revision),
            CHECK((revision=1 AND previous_digest IS NULL) OR (revision>1 AND previous_digest IS NOT NULL AND previous_digest ~ '^[0-9a-f]{64}$')))''')
        cursor.execute('DROP TRIGGER IF EXISTS customer_package_row_guard ON public.customer_fiscal_packages')
        cursor.execute('CREATE TRIGGER customer_package_row_guard BEFORE UPDATE OR DELETE ON public.customer_fiscal_packages FOR EACH ROW EXECUTE FUNCTION public.customer_fiscal_no_rewrite_v1()')
        cursor.execute('DROP TRIGGER IF EXISTS customer_package_truncate_guard ON public.customer_fiscal_packages')
        cursor.execute('CREATE TRIGGER customer_package_truncate_guard BEFORE TRUNCATE ON public.customer_fiscal_packages FOR EACH STATEMENT EXECUTE FUNCTION public.customer_fiscal_no_rewrite_v1()')

class CustomerPackageStore:
    def __init__(self,connection,company_id):
        self.connection=connection;self.company_id=str(UUID(str(company_id)));self.check()
    def check(self):
        CustomerPostgresStore(self.connection,self.company_id)
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT t.tgname,t.tgenabled,t.tgtype,p.proname,t.tgqual IS NULL,t.tgnargs,t.tgattr::text=''
                FROM pg_catalog.pg_trigger t JOIN pg_catalog.pg_class c ON c.oid=t.tgrelid
                JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_proc p ON p.oid=t.tgfoid
                WHERE n.nspname='public' AND c.relname='customer_fiscal_packages' AND NOT t.tgisinternal""")
            guards={name:(enabled,kind,function,no_when,args,columns) for name,enabled,kind,function,no_when,args,columns in cursor.fetchall()}
            for name,kind in [('customer_package_row_guard',27),('customer_package_truncate_guard',34)]:
                found=guards.get(name)
                if not found or found[0] not in {'O','A'} or found[1:]!=(kind,'customer_fiscal_no_rewrite_v1',True,0,True):raise ValueError('Customer package guards unavailable; explicit migration required.')
    def put(self,value):
        self.check();connection=self.connection
        if not connection.get_autocommit() or connection.in_atomic_block:raise ValueError('Dedicated customer autocommit connection required.')
        report,encoded=inspect_package(value,self.company_id);connection.set_autocommit(False)
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT pg_advisory_xact_lock(%s)',[int.from_bytes(hashlib.sha256(self.company_id.encode()).digest()[:8],'big',signed=True)])
                cursor.execute('SELECT company_id FROM public.customer_fiscal_binding WHERE singleton=1')
                binding=cursor.fetchone()
                if not binding or str(binding[0])!=self.company_id:raise ValueError('Customer binding changed.')
                cursor.execute('SELECT package_digest,package_bytes FROM public.customer_fiscal_packages WHERE company_id=%s AND document_id=%s AND revision=%s',[self.company_id,report['document_id'],report['revision']]);old=cursor.fetchone()
                if old:
                    if old[0]!=report['package_digest'] or bytes(old[1])!=encoded:raise StorageConflict('Another package already occupies this document version.')
                    replayed=True
                else:
                    cursor.execute('SELECT revision,package_digest FROM public.customer_fiscal_packages WHERE company_id=%s AND document_id=%s ORDER BY revision DESC LIMIT 1',[self.company_id,report['document_id']]);head=cursor.fetchone()
                    if (head is None and report['revision']!=1) or (head and (report['revision']!=head[0]+1 or report['previous_digest']!=head[1])):raise StorageConflict('Parent/head mismatch; retrieve the customer version before appending.')
                    cursor.execute('INSERT INTO public.customer_fiscal_packages(company_id,document_id,revision,package_digest,previous_digest,package_bytes) VALUES (%s,%s,%s,%s,%s,%s)',[self.company_id,report['document_id'],report['revision'],report['package_digest'],report['previous_digest'],encoded]);replayed=False
                    cursor.execute('SELECT package_digest,package_bytes FROM public.customer_fiscal_packages WHERE company_id=%s AND document_id=%s AND revision=%s',[self.company_id,report['document_id'],report['revision']]);written=cursor.fetchone()
                    if not written or written[0]!=report['package_digest'] or bytes(written[1])!=encoded:raise ValueError('Customer write did not preserve opaque package bytes.')
            connection.commit()
        except BaseException:
            connection.rollback();raise
        finally:connection.set_autocommit(True)
        return {**report,'stored':True,'replayed':replayed,'destination':'explicit_customer_postgresql','authenticated_ciphertext_verified':False,'ownership_independently_verified':False,'fiscal_accepted':False,'ledger_written':False}
    def get(self,document_id,revision=None):
        self.check();document=str(UUID(str(document_id)))
        if revision is not None and (type(revision) is not int or not 1<=revision<=1000000):raise ValueError('Invalid requested version.')
        with self.connection.cursor() as cursor:
            query='SELECT revision,package_digest,package_bytes FROM public.customer_fiscal_packages WHERE company_id=%s AND document_id=%s';args=[self.company_id,document]
            if revision is not None:query+=' AND revision=%s';args.append(revision)
            cursor.execute(query+' ORDER BY revision DESC LIMIT 1',args);found=cursor.fetchone()
        if not found:raise LookupError('Customer package unavailable.')
        raw=bytes(found[2])
        if len(raw)>MAX_WIRE_BYTES:raise ValueError('Stored package exceeds supported bound.')
        value=json.loads(raw);report,encoded=inspect_package(value,self.company_id)
        if encoded!=raw or report['document_id']!=document or report['revision']!=found[0] or report['package_digest']!=found[1]:raise ValueError('Stored customer package changed.')
        return value
