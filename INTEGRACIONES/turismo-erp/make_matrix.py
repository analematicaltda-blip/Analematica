"""Requirements traceability: conservative statuses until end-to-end evidence exists."""
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GROUPS=[
('INS','Usuarios y entidades','Crear usuarios institucionales;Entidades nacionales departamentales y municipales;Roles jefe profesional técnico asistencial;Dependencias y jerarquías;Jurisdicción municipal y departamental;Asignación de tareas;Aprobación de publicaciones','BACKEND/SGA-TUR-BAKEND/api/models.py'),
('INS','Panel institucional','Dashboard institucional;Indicadores de dependencia;Pendientes y alertas;Seguimiento de tareas y metas','FRONTEND/SGA-TUR-FRONTEND/src/app/dashboard'),
('INS','Directorio PST','Registrar prestadores;Categorías y subcategorías extensibles;Identificación NIT y RNT;Verificación institucional;Accesibilidad y sostenibilidad;Integración autorizada ERP;Detección de duplicados','BACKEND/SGA-TUR-BAKEND/apps/turismo/models/provider_models.py'),
('INS','Atractivos','Caracterización de atractivos;Georreferenciación;Fotografías y evidencias;Categorías y estado;Escrituras autorizadas por jurisdicción','BACKEND/SGA-TUR-BAKEND/api/views.py'),
('INS','Ferias y fiestas','Directorio de eventos;Calendario turístico;Programación y promoción;Aprobación de eventos','BACKEND/SGA-TUR-BAKEND/api/models.py'),
('INS','Artesanos','Registro institucional de artesanos;Productos y técnicas;Territorios y comunidades;Promoción comercial consentida','BACKEND/SGA-TUR-BAKEND/api/models.py'),
('INS','Gestión y planificación','Planes de turismo;Proyectos institucionales;Metas y actividades;Compromisos e informes;Evidencias de ejecución','BACKEND/SGA-TUR-BAKEND/apps'),
('INS','Analítica','Consolidación municipal;Consolidación departamental;Consolidación nacional;Exportación de reportes;Trazabilidad de indicadores','BACKEND/SGA-TUR-BAKEND/apps/tourism_intelligence'),
('INS','Documental','Expedientes y documentos;Actas y certificados;Versionamiento;Permisos de archivos privados;Retención y evidencias','BACKEND/SGA-TUR-BAKEND/api'),
('INS','Portal público','Buscador nacional;Mapas y directorios;Contenido promocional separado del registro;Consulta accesible y responsive','FRONTEND/SGA-TUR-FRONTEND/src/app'),
('INS','Transversal','Aprobación multinivel cuando aplique;Historial de cambios;Notificaciones por vencimiento;Formularios dinámicos;Importación Excel y CSV;Exportación Excel PDF CSV;Auditoría administrativa;Modo offline y sincronización;Integración con fuentes oficiales autorizadas;No modificar otro municipio sin autorización','BACKEND/SGA-TUR-BAKEND/api/permissions.py'),
('ERP','Portal del cliente','Registro e inicio de sesión;Perfil personal;Historial de compras y reservas;Consulta de disponibilidad;Solicitud de cotizaciones;Reservas en línea;Compra de servicios y experiencias;Pagos y estado de pagos;Descarga de comprobantes;Cancelaciones y modificaciones;Confirmaciones y recordatorios;Chat WhatsApp y canales;Calificaciones y reseñas;Fidelización;Promociones y descuentos;Solicitudes quejas y reclamaciones','FRONTEND/SGA-TUR-FRONTEND/src/app'),
('ERP','Experiencia comercial','Catálogo digital;Tarifas temporadas y condiciones;Calendario de servicios;Cotizador;Carrito multservicio;Checkout;Confirmación idempotente;Voucher factura o comprobante;Recomendaciones;Seguimiento de reserva','BACKEND/SGA-TUR-BAKEND/apps/tourism_marketplace'),
('ERP','Hoteles','Habitaciones fechas y huéspedes;Tarifas y disponibilidad;Servicios adicionales;Check-in y check-out','BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/modulos_especializados'),
('ERP','Restaurantes','Reserva de mesas;Menú digital;Pedidos y consumo;Eventos gastronómicos','BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/modulos_especializados'),
('ERP','Agencias y operadores','Paquetes e itinerarios;Circuitos y pasajeros;Tarifas vouchers y experiencias','BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/modulos_especializados'),
('ERP','Guías y experiencias','Calendario y cupos;Puntos de encuentro;Reserva y asignación de guía','BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/modulos_especializados'),
('ERP','Transporte','Solicitudes de traslado;Rutas vehículos y pasajeros;Horarios tarifas y confirmaciones','BACKEND/SGA-ERP-TUR-BAKEND/gestion_operativa/modulos_especializados'),
('ERP','Comercial y pauta','Clientes y CRM;Ventas y cotizaciones;Micrositio empresarial;Dominio personalizado y SEO;Redes sociales;WhatsApp Business;Campañas de correo;Cupones y códigos;Embudo y cotizaciones no aceptadas;Canales y marketplaces;Comisiones de intermediarios;Conversiones y ventas','BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial'),
('ERP','Cinco módulos','Gestión comercial;Gestión archivística;Gestión operacional;Gestión contable;Gestión financiera','BACKEND/SGA-ERP-TUR-BAKEND'),
('ERP','Administración','Panel del propietario y rentabilidad;Panel del administrador y configuración;Panel profesional y procesos asignados;Panel técnico y ejecución;Panel asistencial y apoyo;Permisos funcionales sin equivalencia automática de nombres','FRONTEND/SGA-ERP-TUR-FRONTEND'),
('ERP','Transversal','Recursos humanos y turnos;Proveedores y compras;Inventario y almacén;Mantenimiento preventivo;Gestión de calidad;Riesgos y controles;Seguridad y sesiones;Contratos y obligaciones;Inteligencia empresarial;Multempresa sedes y sucursales;Multidivisa;Tareas y aprobaciones;Aplicación móvil;Modo offline;Facturación electrónica e integración DIAN;Flujo de caja;Cuentas por cobrar y pagar;Presupuesto y proyecciones;Conciliaciones contables','BACKEND/SGA-ERP-TUR-BAKEND'),
('INT','Interoperabilidad','Identificador único de negocio;Registro institucional independiente de pauta;Consentimiento de publicación;Contrato y vigencia comercial;Validación de publicación;Retirada comercial sin borrar el registro;Verificación oficial RNT independiente;Reconciliación y deduplicación;Intercambio autorizado por campos;Auditoría de sincronización','BACKEND/SGA-TUR-BAKEND/apps/turismo/models/provider_models.py')]

def generate():
 rows=[];counters={}
 for platform,module,features,evidence in GROUPS:
  for feature in features.split(';'):
   counters[platform]=counters.get(platform,0)+1;identifier=platform+'-'+str(counters[platform]).zfill(3)
   priority='ALTA';status='NO VERIFICADA';finding='Hay fuentes o componentes candidatos; no hay evidencia end-to-end suficiente para certificar la función.'
   acceptance='Flujo completo con datos de prueba identificados, autorización positiva y negativa, integridad y evidencia reproducible; sin afectar funciones previas.'
   if 'jurisdicción' in feature or 'otro municipio' in feature:priority='CRITICA';acceptance='Municipio A no crea ni modifica datos de B; departamento consolida lo permitido; cada excepción requiere autorización explícita.'
   if module=='Atractivos' and feature=='Escrituras autorizadas por jurisdicción':status='PARCIAL';priority='CRITICA';finding='Permiso funcional, asignación institucional activa y territorio comprobados en atractivos sobre SQLite temporal. No equivale a jurisdicción validada en todos los módulos o en producción.'
   if platform=='ERP' and feature=='Calificaciones y reseñas':status='PARCIAL';finding='Gestión privada de reseñas ligada al cliente y verificación de compra controlada por servidor; pruebas HTTP/ORM. Moderación y prueba real de compra pendientes.'
   if feature in ['Presupuesto y proyecciones','Proveedores y compras','Flujo de caja','Cuentas por cobrar y pagar','Conciliaciones contables']:priority='CRITICA';acceptance='Aislamiento de negocio, idempotencia, conciliación de saldos, auditoría y comprobantes; ningún pago externo durante auditoría.'
   if platform=='INT':acceptance='Contrato y consentimiento válidos publican solo campos autorizados; al vencer la pauta se retira promoción sin borrar ni validar automáticamente registro institucional/RNT.'
   rows.append({'id':identifier,'plataforma':platform,'modulo':module,'funcionalidad':feature,'ruta_o_componente':evidence,'estado':status,'evidencia':finding,'riesgo':'Permisos, integridad o publicación incorrectos si se confunde presencia de código con funcionamiento.','prioridad':priority,'accion':'Auditar dependencias y ejecutar caso de aceptación antes de desarrollar.','criterio_aceptacion':acceptance,'prueba_ejecutada':status=='PARCIAL'})
 return rows

def main():
 rows=generate();(HERE/'matriz-funcional.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 with (HERE/'matriz-funcional.csv').open('w',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
 print('Requirements tracked:',len(rows),{p:sum(r['plataforma']==p for r in rows) for p in ['INS','ERP','INT']})
if __name__=='__main__':main()
