"""Database append-only guards for the new normalized worker evidence tables."""
TABLES=['sg_sst_professionalauthorization','sg_sst_ppeassignment','sg_sst_workperiod','sg_sst_workperiodend','sg_sst_restperiod','sg_sst_safetyrevocation']

def install(connection):
    quote=connection.ops.quote_name
    with connection.cursor() as cur:
        for table in TABLES:
            if connection.vendor=='sqlite':
                for operation in ('UPDATE','DELETE'):
                    name='safety_'+operation.lower()+'_'+table
                    cur.execute(f"CREATE TRIGGER {quote(name)} BEFORE {operation} ON {quote(table)} BEGIN SELECT RAISE(ABORT,'worker safety evidence is append only'); END")
            elif connection.vendor=='postgresql':
                function='safety_guard_'+table
                cur.execute(f"CREATE FUNCTION {quote(function)}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'worker safety evidence is append only'; END; $$")
                cur.execute(f"CREATE TRIGGER {quote('safety_immutable_'+table)} BEFORE UPDATE OR DELETE ON {quote(table)} FOR EACH ROW EXECUTE FUNCTION {quote(function)}()")
            else:raise RuntimeError('Worker safety guards require qualified SQLite/PostgreSQL storage.')

def require(connection):
    from rest_framework.exceptions import ValidationError
    quote=connection.ops.quote_name
    with connection.cursor() as cur:
        if connection.vendor=='sqlite':
            cur.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger' AND tbl_name IN ("+','.join(['%s']*len(TABLES))+")",TABLES)
            actual=dict(cur.fetchall())
            for table in TABLES:
                for operation in ('UPDATE','DELETE'):
                    name='safety_'+operation.lower()+'_'+table
                    expected=f"CREATE TRIGGER {quote(name)} BEFORE {operation} ON {quote(table)} BEGIN SELECT RAISE(ABORT,'worker safety evidence is append only'); END"
                    if actual.get(name)!=expected:raise ValidationError('Faltan guardas verificables de evidencia laboral; aplica la migración revisada, sin reparación automática.')
        elif connection.vendor=='postgresql':
            for table in TABLES:
                cur.execute("SELECT t.tgenabled,t.tgtype,p.prosrc,p.prosecdef FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid WHERE n.nspname=current_schema() AND c.relname=%s AND t.tgname=%s AND NOT t.tgisinternal",[table,'safety_immutable_'+table])
                row=cur.fetchone()
                if row is None or row[0] not in ('O','A') or row[1]!=27 or row[2]!=" BEGIN RAISE EXCEPTION 'worker safety evidence is append only'; END; " or row[3]:raise ValidationError('Guardas de evidencia laboral no cualificadas.')
        else:raise ValidationError('Motor de almacenamiento no cualificado para evidencia laboral.')
