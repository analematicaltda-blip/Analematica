"""Canonical company role contracts; owner is independent of commercial plans.
Sources: ROLES_Y_PERMISOS.md, endpoints/admin.py, and the owner's 2026-11-04 instructions.
Coordinator retains operational duties and belongs to the explicitly named Full admin team.
"""
ADMIN_TEAM={'jefe_area','coordinador','profesional_area','tecnico_area'}
MANAGEMENT={'admin_empresa'}|ADMIN_TEAM
OPERATIONS={'profesor','jefe_almacen','almacenista','jefe_escenarios'}
CLIENTS={'alumno','padre_acudiente'}
NAMES={'admin_empresa':'Administrador de empresa','jefe_area':'Jefe de área','profesional_area':'Profesional de área','tecnico_area':'Técnico de área','coordinador':'Coordinador','profesor':'Profesor / Instructor','jefe_almacen':'Jefe de almacén','almacenista':'Almacenista','jefe_escenarios':'Jefe de escenarios','alumno':'Alumno','padre_acudiente':'Madre, padre o acudiente'}
CREATE={'admin_empresa':list(NAMES.keys())[1:],'jefe_area':['coordinador','profesor','jefe_almacen','almacenista','jefe_escenarios'],'profesional_area':['profesor','almacenista','jefe_escenarios'],'tecnico_area':['profesor','almacenista','jefe_escenarios']}
DUTIES={
'admin_empresa':['Gestionar la entidad, sus áreas y su personal','Seleccionar disciplinas y modalidades del catálogo maestro','Consultar indicadores y auditoría de su empresa'],
'jefe_area':['Supervisar su área y su personal','Gestionar y aprobar disciplinas, eventos y programación','Consultar indicadores de su área'],
'profesional_area':['Crear y editar actividades sin atribuirse eliminación','Apoyar supervisión y gestión autorizada de personal','Consultar reportes de su área'],
 'tecnico_area':['Brindar soporte operativo autorizado','Preparar y editar disciplinas y eventos','Consultar indicadores operativos de su área'],
 'coordinador':['Coordinar profesores y comprobar programación','Aprobar propuestas de su competencia','Consultar indicadores de su área y usar las funciones Full heredadas'],
 'profesor':['Gestionar sus clases, plan de trabajo y currículo','Registrar asistencia e inscripciones de sus alumnos','Solicitar recursos y autorizaciones'],
 'jefe_almacen':['Gestionar stock, movimientos y hojas de vida','Autorizar entrega de materiales y consultar reportes'],
 'almacenista':['Registrar préstamos, devoluciones y movimientos autorizados'],
 'jefe_escenarios':['Gestionar reservas, asignaciones y mantenimiento'],
 'alumno':['Consultar sus cursos, horarios, progreso y asistencia'],
 'padre_acudiente':['Consultar únicamente sus acudidos','Inscribir y otorgar autorizaciones de su competencia']}

def contract(role,plan):
    if role not in NAMES:raise ValueError('Rol no reconocido')
    group='administrativo' if role in MANAGEMENT else 'operativo' if role in OPERATIONS else 'clientes'
    return {'role':role,'name':NAMES[role],'group':group,'organization_plan':plan,'commercial_eligible':role in MANAGEMENT and plan=='full','analytics':role in MANAGEMENT,'scope':'empresa' if role=='admin_empresa' else 'area' if role in ADMIN_TEAM else 'propio','creates':CREATE.get(role,[]),'duties':DUTIES[role],'sources':['SGA-CD-BACKEND/ROLES_Y_PERMISOS.md','SGA-CD-BACKEND/app/api/v1/endpoints/admin.py','Instrucciones del propietario 2026-11-04']}
