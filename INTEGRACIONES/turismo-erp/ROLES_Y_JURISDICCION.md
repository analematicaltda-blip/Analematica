# Matriz objetivo de roles, nivel y jurisdicción

Regla de autorización: principal autenticado + institución/empresa asignada + nivel + jurisdicción + permiso funcional + estado del registro. Un nombre de rol o encabezado no basta. Esta matriz es un requisito objetivo, no un permiso ya concedido.

| Ámbito | Jefe/director o propietario | Profesional | Técnico | Asistencial |
|---|---|---|---|---|
| Municipal | Asigna tareas y aprueba dentro de su entidad/municipio según delegación. | Gestiona contenidos y expedientes asignados en ese municipio. | Actualiza registros y evidencias autorizados. | Captura y apoya tareas expresamente permitidas. |
| Departamental | Consulta/consolida municipios de su departamento; aprueba lo delegado. | Análisis/gestión asignados en el departamento. | Soporte y actualización de su dependencia. | Registro y apoyo según permisos. |
| Nacional | Consulta consolidación nacional y gestiona funciones nacionales expresas. | Análisis y expedientes nacionales asignados. | Soporte funcional autorizado. | Apoyo administrativo asignado. |
| Empresa ERP | Propietario consulta resultados, aprueba decisiones y configura delegaciones. Administrador configura y supervisa lo delegado. | Comercial, documental y operaciones de su área. | Ejecución operativa, inventario y evidencias asignados. | Captura, reservas y atención; registrar una solicitud no autoriza pagar. |

Prohibiciones: municipio A no modifica municipio B; empleado A no opera empresa B; consolidar no implica editar; una jerarquía no concede acceso a documentos privados de manera indiscriminada; un plan comercial no valida RNT. Aprobaciones multinivel se aplican solo a procesos definidos, conservando actor, fecha, alcance y versión.

La fuente ya declara roles territoriales y empresariales en `api/models.py:CustomUser.Role`, roles globales, relaciones a entidades y permisos especializados. Parte de las vistas usa permisos excesivamente amplios. Falta demostrar que consulta, creación, actualización, aprobación y exportación usan la misma jurisdicción.

Pruebas obligatorias: A/B municipios del mismo departamento; A/B departamentos; lectura consolidada nacional; usuarios no asignados; cambio de jurisdicción; baja de funcionario; edición de campo territorial; descarga privada; intento de alterar rol/empresa mediante cuerpo, query o headers. Las identidades SGA-CD y Django siguen separadas; no se heredan privilegios entre tokens.
