"""Read-only PostgreSQL role-boundary audit for guarded accounting tables and account identity.

Not a complete database/application authorization audit. Membership is evaluated
conservatively, including roles reachable from both current_user and session_user.
"""
from .sql_guards import TABLES


def inspect_privileges(connection):
    issues=set();scope='guarded_accounting_objects_and_reachable_roles'
    if connection.vendor!='postgresql':
        return {'ready':False,'checks':['accounting_db_privileges_unsupported'],'read_only':True,'scope':scope,'production_ready':False}
    with connection.cursor() as cursor:
        cursor.execute('''WITH RECURSIVE reachable(oid) AS (
            SELECT oid FROM pg_catalog.pg_roles WHERE rolname IN (current_user,session_user)
            UNION SELECT m.roleid FROM pg_catalog.pg_auth_members m JOIN reachable r ON r.oid=m.member)
            SELECT r.oid,r.rolsuper,r.rolcreaterole,r.rolcreatedb,r.rolbypassrls,r.rolreplication,r.rolname
            FROM pg_catalog.pg_roles r JOIN reachable s ON s.oid=r.oid''')
        roles=cursor.fetchall();role_ids=[row[0] for row in roles]
        for index,code in [(1,'superuser'),(2,'role_admin'),(3,'database_creator'),(4,'rls_bypass'),(5,'replication')]:
            if any(row[index] for row in roles):issues.add('accounting_db_'+code)
        if any(row[6] in {'pg_read_server_files','pg_write_server_files','pg_execute_server_program'} for row in roles):issues.add('accounting_db_server_files')
        cursor.execute('SELECT datdba FROM pg_catalog.pg_database WHERE datname=current_database()')
        if cursor.fetchone()[0] in role_ids:issues.add('accounting_db_database_owner')
        cursor.execute("SELECT bool_or(pg_catalog.has_database_privilege(oid,current_database(),'CREATE')),bool_or(pg_catalog.has_database_privilege(oid,current_database(),'TEMP')) FROM pg_catalog.pg_roles WHERE oid=ANY(%s)",[role_ids])
        create,temp=cursor.fetchone()
        if create:issues.add('accounting_db_database_create')
        if temp:issues.add('accounting_db_temporary_objects')
        cursor.execute('''SELECT c.oid,c.relname,c.relowner,n.oid,n.nspowner
            FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
            WHERE c.oid IN (pg_catalog.to_regclass(%s),pg_catalog.to_regclass(%s),pg_catalog.to_regclass(%s),pg_catalog.to_regclass(%s))''',list(TABLES.values())+['core_erp_account'])
        objects=cursor.fetchall()
        if len(objects)!=4:issues.add('accounting_db_guarded_objects_missing')
        schemas=set()
        for oid,name,owner,schema,schema_owner in objects:
            schemas.add(schema)
            if owner in role_ids:issues.add('accounting_db_table_owner')
            if schema_owner in role_ids:issues.add('accounting_db_schema_owner')
            cursor.execute("SELECT bool_or(pg_catalog.has_schema_privilege(oid,%s,'CREATE')) FROM pg_catalog.pg_roles WHERE oid=ANY(%s)",[schema,role_ids])
            if cursor.fetchone()[0]:issues.add('accounting_db_schema_create')
            required=['SELECT'] if name=='core_erp_account' else ['SELECT','INSERT']+(['UPDATE'] if name!=TABLES['policy'] else [])
            for privilege in required:
                cursor.execute('SELECT pg_catalog.has_table_privilege(current_user,%s,%s)',[oid,privilege])
                if not cursor.fetchone()[0]:issues.add('accounting_db_required_dml_missing')
            forbidden='DELETE,TRUNCATE,TRIGGER'+(',UPDATE' if name==TABLES['policy'] else '')
            if name=='core_erp_account':forbidden+=',INSERT,UPDATE'
            cursor.execute('SELECT bool_or(pg_catalog.has_table_privilege(oid,%s,%s)) FROM pg_catalog.pg_roles WHERE oid=ANY(%s)',[oid,forbidden,role_ids])
            if cursor.fetchone()[0]:issues.add('accounting_db_excessive_table_privilege')
        if schemas:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_proc WHERE pronamespace=ANY(%s) AND proname LIKE 'core_accounting_%%' AND proowner=ANY(%s))",[list(schemas),role_ids])
            if cursor.fetchone()[0]:issues.add('accounting_db_guard_function_owner')
    return {'ready':not issues,'checks':sorted(issues),'read_only':True,'scope':scope,
            'reachable_roles_checked':len(role_ids),'guarded_tables_checked':len(objects),'production_ready':False}
