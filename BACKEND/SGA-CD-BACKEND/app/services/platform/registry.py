SYSTEMS=[
 {'id':'analematica','name':'Analemática','deployment_state':'not_checked_by_this_endpoint'},
 {'id':'erp','name':'ERP de empresas turísticas','deployment_state':'not_checked_by_this_endpoint'},
 {'id':'turismo','name':'Gestión turística institucional','deployment_state':'not_checked_by_this_endpoint'},
]
MODULES=[{'id':'control','name':'Control autorizado','path':'/control.html'},{'id':'assistance','name':'Guías de asistencia','path':'/assistance.html'},{'id':'resources','name':'Seguridad y recursos IA','path':'/resources.html'}]

def describe(who):
 # New containers avoid sharing viewer state between users or tenants.
 return {'schema':'sgacd-platform-v1','viewer':{'user_id':who.user_id,'tenant_id':who.tenant_id},'systems':[dict(s) for s in SYSTEMS],'shared_modules':[dict(m) for m in MODULES],'identity':{'domain_sso_enabled':False,'automatic_role_mapping':False,'tenant_source':'authenticated_server_identity'},'control':{'minimum_authorizations':2,'requesting_administrator_only':True,'mutation_authorizations':3},'pending_modules':['erp.compras','erp.proyectos','erp.presupuesto','erp.reportes'],'production_ready':False,'audit_order':['institutional','erp_customer_flows'],'notice':'El catálogo común no concede acceso a otro dominio ni certifica sus procesos.'}
