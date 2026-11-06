# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/coronel.py

from .....coronel_template import CoronelTemplate

# --- GESTION COMERCIAL ---
from .capitanes.gestion_comercial.capitan_marketing import CapitanMarketing
from .capitanes.gestion_comercial.capitan_publicidad_y_adquisicion_de_trafico_ads import CapitanPublicidadYAdquisicionDeTraficoADS
from .capitanes.gestion_comercial.capitan_gestion_operativa_de_contenidos_comerciales import CapitanGestionOperativaDeContenidosComerciales
from .capitanes.gestion_comercial.capitan_produccion_y_automatizacion_audiovisual import CapitanProduccionYAutomatizacionAudiovisual
from .capitanes.gestion_comercial.capitan_seo_turistico import CapitanSEOTuristico
from .capitanes.gestion_comercial.capitan_recomendaciones_sadi import CapitanRecomendacionesSADI
from .capitanes.gestion_comercial.capitan_alianzas_comerciales import CapitanAlianzasComerciales
from .capitanes.gestion_comercial.capitan_conversion import CapitanConversion
from .capitanes.gestion_comercial.capitan_embudos_conversion import CapitanEmbudosConversion
from .capitanes.gestion_comercial.capitan_implementacion_tecnica_de_embudos_y_crm import CapitanImplementacionTecnicaDeEmbudosYCRM
from .capitanes.gestion_comercial.capitan_pasarela_pagos import CapitanPasarelaPagos
from .capitanes.gestion_comercial.capitan_cotizaciones_dinamicas import CapitanCotizacionesDinamicas
from .capitanes.gestion_comercial.capitan_venta_conversacional import CapitanVentaConversacional
from .capitanes.gestion_comercial.capitan_contratacion import CapitanContratacion
from .capitanes.gestion_comercial.capitan_firma_digital import CapitanFirmaDigital
from .capitanes.gestion_comercial.capitan_kyc_verificacion import CapitanKYCVerificacion
from .capitanes.gestion_comercial.capitan_legalidad_y_privacidad import CapitanLegalidadYPrivacidad
from .capitanes.gestion_comercial.capitan_relacion_clientes import CapitanRelacionClientes
from .capitanes.gestion_comercial.capitan_mensajeria_y_envios_masivos import CapitanMensajeriaYEnviosMasivos
from .capitanes.gestion_comercial.capitan_fidelizacion_lealtad import CapitanFidelizacionLealtad
from .capitanes.gestion_comercial.capitan_soporte_viajero import CapitanSoporteViajero
from .capitanes.gestion_comercial.capitan_postventa_feedback import CapitanPostventaFeedback
from .capitanes.gestion_comercial.capitan_cumplimiento_comercial import CapitanCumplimientoComercial
from .capitanes.gestion_comercial.capitan_inteligencia_analitica_y_optimizacion import CapitanInteligenciaAnaliticaYOptimizacion
from .capitanes.gestion_comercial.capitan_auditoria_ventas import CapitanAuditoriaVentas
from .capitanes.gestion_comercial.capitan_prevencion_fraude import CapitanPrevencionFraude
from .capitanes.gestion_comercial.capitan_comercial_estrategico import CapitanComercialEstrategico
from .capitanes.gestion_comercial.capitan_gestion_comercial_general import CapitanGestionComercialGeneral
from .capitanes.gestion_comercial.capitan_comercial_hotelero import CapitanComercialHotelero
from .capitanes.gestion_comercial.capitan_comercial_gastronomico import CapitanComercialGastronomico
from .capitanes.gestion_comercial.capitan_comercial_turistico_tours import CapitanComercialTuristicoTours
from .capitanes.gestion_comercial.capitan_comercial_transporte import CapitanComercialTransporte

# --- OTROS DOMINIOS ---
from .capitanes.onboarding_prestador_capitan import CapitanOnboardingPrestador
from .capitanes.gestion_archivistica.capitan_archivistico import CapitanArchivistico
from .capitanes.gestion_archivistica.capitan_integridad_documental import CapitanIntegridadDocumental
from .capitanes.gestion_archivistica.capitan_retencion_normativa import CapitanRetencionNormativa
from .capitanes.gestion_archivistica.capitan_auditoria_documental import CapitanAuditoriaDocumental
from .capitanes.gestion_archivistica.capitan_busqueda_documental import CapitanBusquedaDocumental
from .capitanes.gestion_archivistica.capitan_captura_y_creacion_documental import CapitanCapturaYCreacionDocumental
from .capitanes.gestion_archivistica.capitan_cumplimiento_normativo import CapitanCumplimientoNormativo
from .capitanes.gestion_archivistica.capitan_gestion_documental_general import CapitanGestionDocumentalGeneral
from .capitanes.gestion_archivistica.capitan_politicas_retencion import CapitanPoliticasRetencion
from .capitanes.gestion_archivistica.capitan_seguridad_documental import CapitanSeguridadDocumental
from .capitanes.gestion_archivistica.capitan_trazabilidad_documental import CapitanTrazabilidadDocumental
from .capitanes.gestion_archivistica.capitan_documentos_legales import CapitanDocumentosLegales
from .capitanes.gestion_archivistica.capitan_documentos_contables import CapitanDocumentosContables
from .capitanes.gestion_archivistica.capitan_documentos_operativos import CapitanDocumentosOperativos
from .capitanes.gestion_archivistica.capitan_documentos_sst import CapitanDocumentosSST
from .capitanes.gestion_archivistica.capitan_documentos_nomina import CapitanDocumentosNomina
from .capitanes.gestion_archivistica.capitan_documentos_publicos import CapitanDocumentosPublicos
from .capitanes.gestion_archivistica.capitan_documentos_confidenciales import CapitanDocumentosConfidenciales
from .capitanes.gestion_archivistica.capitan_conservacion_historica import CapitanConservacionHistorica
from .capitanes.gestion_archivistica.capitan_disposicion_final import CapitanDisposicionFinal
from .capitanes.gestion_archivistica.capitan_notarizacion_blockchain import CapitanNotarizacionBlockchain
from .capitanes.gestion_operativa.capitan_gestion_operativa_general import CapitanGestionOperativaGeneral
from .capitanes.gestion_operativa.capitan_control_operativo import CapitanControlOperativo
from .capitanes.gestion_operativa.capitan_incidentes_operativos import CapitanIncidentesOperativos
from .capitanes.gestion_operativa.capitan_calidad_y_cumplimiento import CapitanCalidadYCumplimiento
from .capitanes.gestion_operativa.capitan_flujos_secuenciales import CapitanFlujosSecuenciales
from .capitanes.gestion_operativa.capitan_flujos_paralelos import CapitanFlujosParalelos
from .capitanes.gestion_operativa.capitan_validacion_ordenes import CapitanValidacionOrdenes
from .capitanes.gestion_operativa.capitan_enrutamiento_ordenes import CapitanEnrutamientoOrdenes
from .capitanes.gestion_operativa.capitan_priorizacion_tareas import CapitanPriorizacionTareas
from .capitanes.gestion_operativa.capitan_asignacion_tareas import CapitanAsignacionTareas
from .capitanes.gestion_operativa.capitan_transiciones_estado import CapitanTransicionesEstado
from .capitanes.gestion_operativa.capitan_bloqueos_operativos import CapitanBloqueosOperativos
from .capitanes.gestion_operativa.capitan_gestion_reintentos import CapitanGestionReintentos
from .capitanes.gestion_operativa.capitan_fallback_operativo import CapitanFallbackOperativo
from .capitanes.gestion_operativa.capitan_escalamiento_excepciones import CapitanEscalamientoExcepciones
from .capitanes.gestion_contable.capitan_contabilidad_general import CapitanContabilidadGeneral
from .capitanes.gestion_contable.capitan_asientos_automaticos import CapitanAsientosAutomaticos
from .capitanes.gestion_contable.capitan_cierre_contable import CapitanCierreContable
from .capitanes.gestion_contable.capitan_auditoria_contable import CapitanAuditoriaContable
from .capitanes.gestion_contable.capitan_reconocimiento_ingresos import CapitanReconocimientoIngresos
from .capitanes.gestion_contable.capitan_impuestos_iva import CapitanImpuestosIVA
from .capitanes.gestion_contable.capitan_provisiones_contables import CapitanProvisionesContables
from .capitanes.gestion_contable.capitan_conciliacion_automatica import CapitanConciliacionAutomatica
from .capitanes.gestion_contable.capitan_reportes_normativos import CapitanReportesNormativos
from .capitanes.gestion_financiera.capitan_base import CapitanFinancieraBase # Use base if specific missing
from .capitanes.gestion_financiera.capitan_gestion_financiera import CapitanGestionFinanciera
from .capitanes.gestion_financiera.capitan_flujo_caja import CapitanFlujoCaja
from .capitanes.gestion_financiera.capitan_riesgo_financiero import CapitanRiesgoFinanciero
from .capitanes.gestion_financiera.capitan_ratios_y_formulas_financieras import CapitanRatiosYFormulasFinancieras
from .capitanes.gestion_financiera.capitanes_especializados import (
    CapitanTesoreria, CapitanCustodiaFondos, CapitanLiquidez, CapitanPagos,
    CapitanDistribucion, CapitanReservas, CapitanProyecciones, CapitanCumplimientoFinanciero,
    CapitanEstadoResultados, CapitanBalanceGeneral, CapitanFlujoEfectivo,
    CapitanCambiosPatrimonio, CapitanConciliacionBancaria, CapitanProvisionesFinancieras
)
from .capitanes.gestion_operativa.sg_sst.capitan_sst import CapitanSST
from .capitanes.gestion_operativa.sg_sst.capitan_incidentes_sst import CapitanIncidentesSST
from .capitanes.gestion_operativa.sg_sst.capitan_normativo_sst import CapitanNormativoSST
from .capitanes.gestion_operativa.sg_sst.capitanes_sst_especializados import (
    CapitanIdentificacionPeligros, CapitanEvaluacionRiesgos, CapitanSaludOcupacional,
    CapitanRiesgoPsicosocial, CapitanEmergencias, CapitanCapacitacionSST, CapitanVigilanciaSST
)
from .capitanes.gestion_contable.nomina.capitan_nomina import CapitanNomina
from .capitanes.gestion_contable.nomina.capitan_liquidacion_contratos import CapitanLiquidacionContratos
from .capitanes.gestion_contable.nomina.capitan_legal_laboral import CapitanLegalLaboral

class PrestadoresCoronel(CoronelTemplate):
    def __init__(self, general):
        super().__init__(general=general, domain="prestadores")

    def _get_capitanes(self) -> dict:
        return {
            # Comercial
            "marketing": CapitanMarketing(coronel=self),
            "ads": CapitanPublicidadYAdquisicionDeTraficoADS(coronel=self),
            "contenidos": CapitanGestionOperativaDeContenidosComerciales(coronel=self),
            "audiovisual": CapitanProduccionYAutomatizacionAudiovisual(coronel=self),
            "seo": CapitanSEOTuristico(coronel=self),
            "sadi_matching": CapitanRecomendacionesSADI(coronel=self),
            "alianzas": CapitanAlianzasComerciales(coronel=self),
            "conversion": CapitanConversion(coronel=self),
            "embudos": CapitanEmbudosConversion(coronel=self),
            "crm_tech": CapitanImplementacionTecnicaDeEmbudosYCRM(coronel=self),
            "pagos": CapitanPasarelaPagos(coronel=self),
            "cotizaciones": CapitanCotizacionesDinamicas(coronel=self),
            "venta_conversacional": CapitanVentaConversacional(coronel=self),
            "contratacion": CapitanContratacion(coronel=self),
            "firma_digital": CapitanFirmaDigital(coronel=self),
            "kyc": CapitanKYCVerificacion(coronel=self),
            "legal_privacidad": CapitanLegalidadYPrivacidad(coronel=self),
            "crm_relacion": CapitanRelacionClientes(coronel=self),
            "mensajeria_masiva": CapitanMensajeriaYEnviosMasivos(coronel=self),
            "lealtad": CapitanFidelizacionLealtad(coronel=self),
            "soporte_viajero": CapitanSoporteViajero(coronel=self),
            "postventa": CapitanPostventaFeedback(coronel=self),
            "cumplimiento_comercial": CapitanCumplimientoComercial(coronel=self),
            "inteligencia_comercial": CapitanInteligenciaAnaliticaYOptimizacion(coronel=self),
            "auditoria_ventas": CapitanAuditoriaVentas(coronel=self),
            "prevencion_fraude": CapitanPrevencionFraude(coronel=self),
            "comercial_estrategico": CapitanComercialEstrategico(coronel=self),
            "comercial_general": CapitanGestionComercialGeneral(coronel=self),
            "comercial_hotel": CapitanComercialHotelero(coronel=self),
            "comercial_gastronomia": CapitanComercialGastronomico(coronel=self),
            "comercial_tours": CapitanComercialTuristicoTours(coronel=self),
            "comercial_transporte": CapitanComercialTransporte(coronel=self),

            # Otros
            "onboarding": CapitanOnboardingPrestador(coronel=self),
            "archivistico": CapitanArchivistico(coronel=self),
            "integridad_documental": CapitanIntegridadDocumental(coronel=self),
            "retencion_normativa": CapitanRetencionNormativa(coronel=self),
            "auditoria_documental": CapitanAuditoriaDocumental(coronel=self),
            "busqueda_documental": CapitanBusquedaDocumental(coronel=self),
            "captura_documental": CapitanCapturaYCreacionDocumental(coronel=self),
            "cumplimiento_archivistico": CapitanCumplimientoNormativo(coronel=self),
            "gestion_documental_general": CapitanGestionDocumentalGeneral(coronel=self),
            "politicas_retencion": CapitanPoliticasRetencion(coronel=self),
            "seguridad_documental": CapitanSeguridadDocumental(coronel=self),
            "trazabilidad_documental": CapitanTrazabilidadDocumental(coronel=self),
            "documentos_legales": CapitanDocumentosLegales(coronel=self),
            "documentos_contables": CapitanDocumentosContables(coronel=self),
            "documentos_operativos": CapitanDocumentosOperativos(coronel=self),
            "documentos_sst": CapitanDocumentosSST(coronel=self),
            "documentos_nomina": CapitanDocumentosNomina(coronel=self),
            "documentos_publicos": CapitanDocumentosPublicos(coronel=self),
            "documentos_confidenciales": CapitanDocumentosConfidenciales(coronel=self),
            "conservacion_historica": CapitanConservacionHistorica(coronel=self),
            "disposicion_final": CapitanDisposicionFinal(coronel=self),
            "notarizacion_blockchain": CapitanNotarizacionBlockchain(coronel=self),
            "operativo_general": CapitanGestionOperativaGeneral(coronel=self),
            "seguimiento_operativo": CapitanControlOperativo(coronel=self),
            "incidentes_operativos": CapitanIncidentesOperativos(coronel=self),
            "cierre_operativo": CapitanCalidadYCumplimiento(coronel=self),
            "flujos_secuenciales": CapitanFlujosSecuenciales(coronel=self),
            "flujos_paralelos": CapitanFlujosParalelos(coronel=self),
            "validacion_ordenes": CapitanValidacionOrdenes(coronel=self),
            "enrutamiento_ordenes": CapitanEnrutamientoOrdenes(coronel=self),
            "priorizacion_tareas": CapitanPriorizacionTareas(coronel=self),
            "asignacion_tareas": CapitanAsignacionTareas(coronel=self),
            "transiciones_estado": CapitanTransicionesEstado(coronel=self),
            "bloqueos_operativos": CapitanBloqueosOperativos(coronel=self),
            "gestion_reintentos": CapitanGestionReintentos(coronel=self),
            "fallback_operativo": CapitanFallbackOperativo(coronel=self),
            "escalamiento_excepciones": CapitanEscalamientoExcepciones(coronel=self),
            "contabilidad_general": CapitanContabilidadGeneral(coronel=self),
            "asientos_automaticos": CapitanAsientosAutomaticos(coronel=self),
            "cierre_contable": CapitanCierreContable(coronel=self),
            "auditoria_contable": CapitanAuditoriaContable(coronel=self),
            "reconocimiento_ingresos": CapitanReconocimientoIngresos(coronel=self),
            "impuestos_iva": CapitanImpuestosIVA(coronel=self),
            "provisiones_contables": CapitanProvisionesContables(coronel=self),
            "conciliacion_automatica": CapitanConciliacionAutomatica(coronel=self),
            "reportes_normativos": CapitanReportesNormativos(coronel=self),
            "gestion_financiera": CapitanGestionFinanciera(coronel=self),
            "flujo_caja": CapitanFlujoCaja(coronel=self),
            "riesgo_financiero": CapitanRiesgoFinanciero(coronel=self),
            "indicadores_financieros": CapitanRatiosYFormulasFinancieras(coronel=self),
            "tesoreria": CapitanTesoreria(coronel=self),
            "custodia_fondos": CapitanCustodiaFondos(coronel=self),
            "liquidez": CapitanLiquidez(coronel=self),
            "pagos_financieros": CapitanPagos(coronel=self),
            "distribucion_fondos": CapitanDistribucion(coronel=self),
            "reservas": CapitanReservas(coronel=self),
            "proyecciones": CapitanProyecciones(coronel=self),
            "cumplimiento_financiero": CapitanCumplimientoFinanciero(coronel=self),
            "estado_resultados": CapitanEstadoResultados(coronel=self),
            "balance_general": CapitanBalanceGeneral(coronel=self),
            "flujo_efectivo": CapitanFlujoEfectivo(coronel=self),
            "cambios_patrimonio": CapitanCambiosPatrimonio(coronel=self),
            "conciliacion_bancaria": CapitanConciliacionBancaria(coronel=self),
            "provisiones_financieras": CapitanProvisionesFinancieras(coronel=self),
            "sst_general": CapitanSST(coronel=self),
            "sst_incidentes": CapitanIncidentesSST(coronel=self),
            "sst_normativo": CapitanNormativoSST(coronel=self),
            "sst_peligros": CapitanIdentificacionPeligros(coronel=self),
            "sst_evaluacion": CapitanEvaluacionRiesgos(coronel=self),
            "sst_salud": CapitanSaludOcupacional(coronel=self),
            "sst_psicosocial": CapitanRiesgoPsicosocial(coronel=self),
            "sst_emergencias": CapitanEmergencias(coronel=self),
            "sst_capacitacion": CapitanCapacitacionSST(coronel=self),
            "sst_vigilancia": CapitanVigilanciaSST(coronel=self),
            "nomina_general": CapitanNomina(coronel=self),
            "nomina_liquidacion": CapitanLiquidacionContratos(coronel=self),
            "nomina_legal": CapitanLegalLaboral(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        m_type = directiva.get("mission", {}).get("type")

        # Mapeo de tipos de misión a llaves del roster
        mapping = {
            "MARKETING_CAMP": "marketing",
            "ADS_CAMPAIGN": "ads",
            "SEO_AUDIT": "seo",
            "SADI_MATCH": "sadi_matching",
            "PROCESS_PAYMENT": "pagos",
            "GENERATE_QUOTE": "cotizaciones",
            "SALES_CHAT": "venta_conversacional",
            "SIGN_CONTRACT": "firma_digital",
            "KYC_CHECK": "kyc",
            "AUDIT_SALES": "auditoria_ventas",
            "FRAUD_CHECK": "prevencion_fraude",
            # ... (se pueden agregar todos los nuevos tipos aquí)
            "ONBOARDING_PRESTADOR": "onboarding",
            "CERRAR_CONTRATO": "contratacion",
            "VALIDAR_CUMPLIMIENTO_COMERCIAL": "cumplimiento_comercial",
            "AVANZAR_LEAD": "conversion",
            "ISSUE_INVOICE": "facturacion_general",
            "ANALISIS_ESTRATEGICO_COMERCIAL": "comercial_estrategico",
            # Archivístico
            "ARCHIVE_LEAL_DOC": "documentos_legales",
            "ARCHIVE_ACCOUNTING_DOC": "documentos_contables",
            "ARCHIVE_OPERATIONAL_DOC": "documentos_operativos",
            "ARCHIVE_SST_DOC": "documentos_sst",
            "ARCHIVE_PAYROLL_DOC": "documentos_nomina",
            "NOTARIZE_DOC": "notarizacion_blockchain",
            "RETENTION_AUDIT": "politicas_retencion",
            "DOCUMENT_SEARCH": "busqueda_documental",
            # Operativo Genérico
            "EXECUTE_OPERATIONAL_FLOW": "operativo_general",
            "UPDATE_OPERATIONAL_STATE": "transiciones_estado",
            "ASSIGN_TASK": "asignacion_tareas",
            "RETRY_OPERATION": "gestion_reintentos",
            # Operativo Especializado (Delegado a CoronelOperativaTuristica vía Orchestrator)
            # Contable
            "RECOGNIZE_REVENUE": "reconocimiento_ingresos",
            "CALCULATE_TAX": "gestion_impuestos_general",
            "MONTHLY_CLOSE": "cierre_contable",
            "GENERATE_FINANCIAL_REPORT": "reportes_normativos",
            "AUDIT_TREASURY": "tesoreria",
            "MANAGE_CUSTODY": "custodia_fondos",
            "CHECK_LIQUIDITY": "liquidez",
            "EXECUTE_PAYMENT": "pagos_financieros",
            "DISTRIBUTE_FUNDS": "distribucion_fondos",
            "MANAGE_RESERVES": "reservas",
            "FORECAST_FINANCE": "proyecciones",
            "GENERATE_P_L": "estado_resultados",
            "GENERATE_BALANCE": "balance_general",
            "GENERATE_CASH_FLOW": "flujo_efectivo",
            "MANAGE_RECEIVABLES": "cartera_general",
            "GENERATE_EQUITY_CHANGE": "cambios_patrimonio",
            "IDENTIFY_HAZARDS": "sst_peligros",
            "EVALUATE_SST_RISK": "sst_evaluacion",
            "REGISTER_SST_INCIDENT": "sst_incidentes",
            "MANAGE_SST_EMERGENCY": "sst_emergencias",
            "AUDIT_SST_COMPLIANCE": "sst_normativo",
            "ADJUST_INVENTORY": "control_inventario_general", # Reusing or mapping to specialized
        }

        cap_key = mapping.get(m_type)
        if cap_key:
            return self.capitanes.get(cap_key)

        # Fallback por prefijo si no hay match exacto
        if m_type and m_type.startswith("COMERCIAL_"):
            return self.capitanes.get("comercial_general")

        return None
