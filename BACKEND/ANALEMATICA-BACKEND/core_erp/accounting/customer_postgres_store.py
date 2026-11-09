"""Explicit customer-DB connector for opaque envelopes. Never uses default connection.
Ownership and deployment authorization remain external; no network configuration is inferred.
"""
import hashlib,json
from uuid import UUID
from .fiscal_envelope import inspect_envelope,MAX_WIRE_BYTES

class StorageConflict(ValueError):pass


def customer_destination(connection):
    if connection.vendor!='postgresql':raise ValueError('Customer PostgreSQL connection required.')
    with connection.cursor() as cursor:
        cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace WHERE c.relname='core_erp_journalentry' AND n.nspname NOT IN ('pg_catalog','information_schema'))")
        if cursor.fetchone()[0]:raise ValueError('Provider ledger databases cannot be customer document destinations.')


def initialize_customer_store(connection,company_id):
    """Explicit customer migration/bootstrap operation. Never called by put/get."""
    customer_destination(connection);company=str(UUID(str(company_id)))
    with connection.cursor() as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS public.customer_fiscal_binding (
            singleton smallint PRIMARY KEY CHECK(singleton=1),company_id uuid UNIQUE NOT NULL,
            schema_version integer NOT NULL CHECK(schema_version=1))''')
        cursor.execute('SELECT company_id,schema_version FROM public.customer_fiscal_binding WHERE singleton=1')
        row=cursor.fetchone()
        if row is not None and (str(row[0])!=company or row[1]!=1):raise ValueError('Customer storage binding mismatch.')
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS public.customer_fiscal_envelopes (
            document_id uuid PRIMARY KEY,company_id uuid NOT NULL REFERENCES public.customer_fiscal_binding(company_id),
            envelope_digest varchar(64) NOT NULL CHECK(envelope_digest ~ '^[0-9a-f]{{64}}$'),
            envelope_bytes bytea NOT NULL CHECK(octet_length(envelope_bytes)<={MAX_WIRE_BYTES}),
            created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute('''CREATE OR REPLACE FUNCTION public.customer_fiscal_no_rewrite_v1() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN RAISE EXCEPTION 'CUSTOMER_FISCAL_IMMUTABLE'; END $$''')
        for table in ('customer_fiscal_binding','customer_fiscal_envelopes'):
            cursor.execute(f'DROP TRIGGER IF EXISTS customer_fiscal_row_guard ON public.{table}')
            cursor.execute(f'CREATE TRIGGER customer_fiscal_row_guard BEFORE UPDATE OR DELETE ON public.{table} FOR EACH ROW EXECUTE FUNCTION public.customer_fiscal_no_rewrite_v1()')
            cursor.execute(f'DROP TRIGGER IF EXISTS customer_fiscal_truncate_guard ON public.{table}')
            cursor.execute(f'CREATE TRIGGER customer_fiscal_truncate_guard BEFORE TRUNCATE ON public.{table} FOR EACH STATEMENT EXECUTE FUNCTION public.customer_fiscal_no_rewrite_v1()')
        cursor.execute('INSERT INTO public.customer_fiscal_binding VALUES (1,%s,1) ON CONFLICT(singleton) DO NOTHING',[company])
        cursor.execute('SELECT company_id,schema_version FROM public.customer_fiscal_binding WHERE singleton=1')
        row=cursor.fetchone()
        if row is None or str(row[0])!=company or row[1]!=1:raise ValueError('Customer storage binding mismatch.')


class CustomerPostgresStore:
    def __init__(self,connection,company_id):
        self.connection=connection;self.company_id=str(UUID(str(company_id)))
        self.check_destination()

    def check_destination(self):
        customer_destination(self.connection)
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT company_id,schema_version FROM public.customer_fiscal_binding WHERE singleton=1')
            row=cursor.fetchone()
            if row is None or str(row[0])!=self.company_id or row[1]!=1:raise ValueError('Customer storage binding mismatch.')
            cursor.execute("""SELECT c.relname,t.tgname,t.tgenabled,t.tgtype,p.proname,t.tgqual IS NULL,t.tgnargs,t.tgattr::text=''
                FROM pg_catalog.pg_trigger t JOIN pg_catalog.pg_class c ON c.oid=t.tgrelid
                JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_proc p ON p.oid=t.tgfoid
                WHERE n.nspname='public' AND c.relname IN ('customer_fiscal_binding','customer_fiscal_envelopes') AND NOT t.tgisinternal""")
            guards={(table,name):(enabled,kind,function,no_when,args,all_columns) for table,name,enabled,kind,function,no_when,args,all_columns in cursor.fetchall()}
            for table in ('customer_fiscal_binding','customer_fiscal_envelopes'):
                for name,kind in [('customer_fiscal_row_guard',27),('customer_fiscal_truncate_guard',34)]:
                    guard=guards.get((table,name))
                    if guard is None or guard[0] not in {'O','A'} or guard[1:]!=(kind,'customer_fiscal_no_rewrite_v1',True,0,True):
                        raise ValueError('Customer storage guards are unavailable; no automatic repair.')

    def put(self,envelope):
        self.check_destination()
        if not self.connection.get_autocommit() or self.connection.in_atomic_block:raise ValueError('Customer writes require a dedicated autocommit connection.')
        report=inspect_envelope(envelope,self.company_id)
        encoded=json.dumps(envelope,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
        if len(encoded)>MAX_WIRE_BYTES:raise ValueError('Envelope exceeds customer storage bound.')
        with self.connection.cursor() as cursor:
            cursor.execute('''INSERT INTO public.customer_fiscal_envelopes(document_id,company_id,envelope_digest,envelope_bytes)
                VALUES (%s,%s,%s,%s) ON CONFLICT(document_id) DO NOTHING RETURNING envelope_digest''',
                [report['document_id'],self.company_id,report['envelope_digest'],encoded])
            inserted=cursor.fetchone() is not None
            cursor.execute('SELECT envelope_digest,envelope_bytes FROM public.customer_fiscal_envelopes WHERE document_id=%s AND company_id=%s',[report['document_id'],self.company_id])
            found=cursor.fetchone()
        if found is None or found[0]!=report['envelope_digest'] or bytes(found[1])!=encoded:raise StorageConflict('Document version already contains different encrypted bytes; no overwrite performed.')
        return {'document_id':report['document_id'],'company_id':self.company_id,'envelope_digest':found[0],
                'stored':True,'replayed':not inserted,'destination':'explicit_customer_postgresql',
                'authenticated_ciphertext_verified':False,'ownership_independently_verified':False}

    def get(self,document_id):
        self.check_destination();document=str(UUID(str(document_id)))
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT envelope_digest,envelope_bytes FROM public.customer_fiscal_envelopes WHERE document_id=%s AND company_id=%s',[document,self.company_id])
            found=cursor.fetchone()
        if found is None:raise ValueError('Customer document unavailable.')
        raw=bytes(found[1])
        if len(raw)>MAX_WIRE_BYTES:raise ValueError('Stored envelope outside supported bounds.')
        envelope=json.loads(raw)
        report=inspect_envelope(envelope,self.company_id)
        if report['document_id']!=document or report['envelope_digest']!=found[0] or hashlib.sha256(raw).hexdigest()!=found[0]:
            raise ValueError('Stored envelope digest mismatch.')
        return envelope
