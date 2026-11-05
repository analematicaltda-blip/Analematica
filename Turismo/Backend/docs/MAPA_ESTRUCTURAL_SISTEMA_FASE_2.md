# MAPA ESTRUCTURAL DEL SISTEMA — SARITA ERP (FASE 2)

## 1. Definición de Macro-Módulos
1. **Gestión Comercial:** CRM, Leads, Facturación Electrónica DIAN, CUFE, Firma Digital, Embudos de Venta.
2. **Gestión Archivística:** Expediente digital, Hashing SHA-256, Notarización Blockchain, Taxonomía ISO.
3. **Gestión Contable:** Libro Mayor Inmutable, Partida Doble Automática, Motor Ledger, NIIF.
4. **Gestión Financiera:** Tesorería Central, Control de Liquidez, Presupuestos, Flujo de Caja.
5. **Gestión Operativa:**
   - *Genérica:* Órdenes, Tareas, Incidentes, Bitácora.
   - *Especializada:* Hoteles (Housekeeping), Restaurantes (Cocina), Agencias (Paquetes), Transporte (Flota).
6. **Experiencia del Turista:** Explorador, Directorio, Reservas, Delivery, Monedero.

## 2. Relaciones e Interoperabilidad
El sistema opera mediante un **Event Bus** central.
- **Ejemplo Venta:** Venta -> Factura -> Asiento Contable -> Actualización Liquidez -> Orden Operativa -> Contrato Archivístico.

## 3. Flujo de Información
`Capa Cliente (Web/App/Desktop) -> Shared SDK -> API Backend -> Capa Servicios (Agentes IA) -> Capa Dominio (Modelos/Reglas) -> Persistencia (PostgreSQL)`.

## 4. Arquitectura Funcional de 5 Capas
1. **Capa de Clientes:** Interfaz de usuario multiplataforma.
2. **Capa de Comunicación:** SDK compartido, JWT, Multi-tenant headers.
3. **Capa de Servicios:** Lógica de negocio, Orquestadores, Agentes IA.
4. **Capa de Dominio:** Modelos Django, Reglas NIIF/DIAN.
5. **Capa de Persistencia:** PostgreSQL, S3, Hashing de integridad.

## 5. Diagrama de Módulos
Sincronización total entre el core administrativo y los servicios de cara al turista, garantizando que cada transacción financiera tenga un reflejo operativo y contable inmediato.
