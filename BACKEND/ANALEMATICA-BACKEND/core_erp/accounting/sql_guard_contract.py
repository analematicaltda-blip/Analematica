"""Derive expected guard definitions without running SQL or reading any data."""
import re
class Recorder:
    def __init__(self,connection):self.vendor=connection.vendor;self.ops=connection.ops;self.sql=[]
    def cursor(self):return self
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def execute(self,sql,*args):self.sql.append(sql)

def expected(connection):
    from . import sql_guards,sql_guard_hardening,sql_identity_guards
    recorder=Recorder(connection);sql_guards.install(recorder);sql_guard_hardening.install(recorder)
    recorder.sql+=sql_identity_guards.statements(connection)
    functions={};triggers={}
    for sql in recorder.sql:
        match=re.search(r'CREATE OR REPLACE FUNCTION (\w+)\(\).*?AS \$\$(.*?)\$\$',sql,re.S)
        if match:functions[match[1]]=match[2].strip()
        match=re.search(r'CREATE TRIGGER (?:IF NOT EXISTS )?(\w+)',sql)
        if match:triggers[match[1]]=sql.replace('CREATE TRIGGER IF NOT EXISTS','CREATE TRIGGER').strip().rstrip(';')
    return functions,triggers

def body_issues(connection):
    functions,triggers=expected(connection);issues=set()
    with connection.cursor() as cursor:
        if connection.vendor=='sqlite':
            cursor.execute("SELECT name,sql FROM sqlite_master WHERE type='trigger'");actual=dict(cursor.fetchall())
            for name,sql in triggers.items():
                if name not in actual:issues.add('accounting_sql_guards_missing')
                elif (actual[name] or '').strip().rstrip(';')!=sql:issues.add('accounting_sql_guard_body_changed')
        elif connection.vendor=='postgresql':
            # Resolve only the namespace containing the real ledger table.
            cursor.execute('''SELECT p.proname,p.prosrc,p.prosecdef,p.proconfig,p.pronargs,p.prorettype='pg_catalog.trigger'::pg_catalog.regtype
              FROM pg_catalog.pg_proc p WHERE p.pronamespace=(SELECT relnamespace FROM pg_catalog.pg_class WHERE oid=pg_catalog.to_regclass('core_erp_journalentry')) AND p.proname=ANY(%s)''',[list(functions)])
            actual={}
            for name,body,definer,config,args,trigger in cursor.fetchall():actual.setdefault(name,[]).append((body.strip(),definer,config,args,trigger))
            for name,body in functions.items():
                if name not in actual:issues.add('accounting_sql_guards_missing')
                elif actual[name]!=[(body,False,None,0,True)]:issues.add('accounting_sql_guard_body_changed')
    return issues
