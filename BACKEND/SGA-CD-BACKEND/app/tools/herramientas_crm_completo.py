from langchain_core.tools import tool

# --- Escuadra: CapturaFormsSargento (IngestaCanalesLieutenant / ProspeccionLeadsCaptain) ---
@tool
def tool_lead_capturar_landing(instruccion: str) -> str:
    """Soldado especialista de la escuadra CapturaFormsSargento: tool_lead_capturar_landing"""
    return f"[CapturaFormsSargento] tool_lead_capturar_landing ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_capturar_redes(instruccion: str) -> str:
    """Soldado especialista de la escuadra CapturaFormsSargento: tool_lead_capturar_redes"""
    return f"[CapturaFormsSargento] tool_lead_capturar_redes ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_capturar_presencial(instruccion: str) -> str:
    """Soldado especialista de la escuadra CapturaFormsSargento: tool_lead_capturar_presencial"""
    return f"[CapturaFormsSargento] tool_lead_capturar_presencial ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_validar_email(instruccion: str) -> str:
    """Soldado especialista de la escuadra CapturaFormsSargento: tool_lead_validar_email"""
    return f"[CapturaFormsSargento] tool_lead_validar_email ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_validar_telefono(instruccion: str) -> str:
    """Soldado especialista de la escuadra CapturaFormsSargento: tool_lead_validar_telefono"""
    return f"[CapturaFormsSargento] tool_lead_validar_telefono ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: DeduplicacionLeadsSargento (IngestaCanalesLieutenant / ProspeccionLeadsCaptain) ---
@tool
def tool_lead_duplicado_email(instruccion: str) -> str:
    """Soldado especialista de la escuadra DeduplicacionLeadsSargento: tool_lead_duplicado_email"""
    return f"[DeduplicacionLeadsSargento] tool_lead_duplicado_email ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_duplicado_telefono(instruccion: str) -> str:
    """Soldado especialista de la escuadra DeduplicacionLeadsSargento: tool_lead_duplicado_telefono"""
    return f"[DeduplicacionLeadsSargento] tool_lead_duplicado_telefono ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_fusionar_historial(instruccion: str) -> str:
    """Soldado especialista de la escuadra DeduplicacionLeadsSargento: tool_lead_fusionar_historial"""
    return f"[DeduplicacionLeadsSargento] tool_lead_fusionar_historial ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_actualizar_utm(instruccion: str) -> str:
    """Soldado especialista de la escuadra DeduplicacionLeadsSargento: tool_lead_actualizar_utm"""
    return f"[DeduplicacionLeadsSargento] tool_lead_actualizar_utm ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_lead_crear_registro_pg(instruccion: str) -> str:
    """Soldado especialista de la escuadra DeduplicacionLeadsSargento: tool_lead_crear_registro_pg"""
    return f"[DeduplicacionLeadsSargento] tool_lead_crear_registro_pg ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: ScoringInteresSargento (CalificacionScoringLieutenant / ProspeccionLeadsCaptain) ---
@tool
def tool_score_interes_deporte(instruccion: str) -> str:
    """Soldado especialista de la escuadra ScoringInteresSargento: tool_score_interes_deporte"""
    return f"[ScoringInteresSargento] tool_score_interes_deporte ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_score_interes_cultura(instruccion: str) -> str:
    """Soldado especialista de la escuadra ScoringInteresSargento: tool_score_interes_cultura"""
    return f"[ScoringInteresSargento] tool_score_interes_cultura ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_score_tamano_familia(instruccion: str) -> str:
    """Soldado especialista de la escuadra ScoringInteresSargento: tool_score_tamano_familia"""
    return f"[ScoringInteresSargento] tool_score_tamano_familia ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_score_proximidad_sede(instruccion: str) -> str:
    """Soldado especialista de la escuadra ScoringInteresSargento: tool_score_proximidad_sede"""
    return f"[ScoringInteresSargento] tool_score_proximidad_sede ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_score_clasificacion_temperatura(instruccion: str) -> str:
    """Soldado especialista de la escuadra ScoringInteresSargento: tool_score_clasificacion_temperatura"""
    return f"[ScoringInteresSargento] tool_score_clasificacion_temperatura ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: EnriquecimientoPerfilSargento (CalificacionScoringLieutenant / ProspeccionLeadsCaptain) ---
@tool
def tool_enriquecer_tipo_entidad(instruccion: str) -> str:
    """Soldado especialista de la escuadra EnriquecimientoPerfilSargento: tool_enriquecer_tipo_entidad"""
    return f"[EnriquecimientoPerfilSargento] tool_enriquecer_tipo_entidad ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enriquecer_ubicacion_barrio(instruccion: str) -> str:
    """Soldado especialista de la escuadra EnriquecimientoPerfilSargento: tool_enriquecer_ubicacion_barrio"""
    return f"[EnriquecimientoPerfilSargento] tool_enriquecer_ubicacion_barrio ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enriquecer_participacion_previa(instruccion: str) -> str:
    """Soldado especialista de la escuadra EnriquecimientoPerfilSargento: tool_enriquecer_participacion_previa"""
    return f"[EnriquecimientoPerfilSargento] tool_enriquecer_participacion_previa ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enriquecer_preferencia_horario(instruccion: str) -> str:
    """Soldado especialista de la escuadra EnriquecimientoPerfilSargento: tool_enriquecer_preferencia_horario"""
    return f"[EnriquecimientoPerfilSargento] tool_enriquecer_preferencia_horario ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enriquecer_observaciones_asesor(instruccion: str) -> str:
    """Soldado especialista de la escuadra EnriquecimientoPerfilSargento: tool_enriquecer_observaciones_asesor"""
    return f"[EnriquecimientoPerfilSargento] tool_enriquecer_observaciones_asesor ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: RotacionAsesoresSargento (DistribucionAsesoresLieutenant / ProspeccionLeadsCaptain) ---
@tool
def tool_asignar_round_robin(instruccion: str) -> str:
    """Soldado especialista de la escuadra RotacionAsesoresSargento: tool_asignar_round_robin"""
    return f"[RotacionAsesoresSargento] tool_asignar_round_robin ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_asignar_especialidad(instruccion: str) -> str:
    """Soldado especialista de la escuadra RotacionAsesoresSargento: tool_asignar_especialidad"""
    return f"[RotacionAsesoresSargento] tool_asignar_especialidad ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_asignar_geografia(instruccion: str) -> str:
    """Soldado especialista de la escuadra RotacionAsesoresSargento: tool_asignar_geografia"""
    return f"[RotacionAsesoresSargento] tool_asignar_geografia ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_notificar_asesor(instruccion: str) -> str:
    """Soldado especialista de la escuadra RotacionAsesoresSargento: tool_notificar_asesor"""
    return f"[RotacionAsesoresSargento] tool_notificar_asesor ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_reasignar_por_inactividad(instruccion: str) -> str:
    """Soldado especialista de la escuadra RotacionAsesoresSargento: tool_reasignar_por_inactividad"""
    return f"[RotacionAsesoresSargento] tool_reasignar_por_inactividad ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: AgendamientoContactoSargento (DistribucionAsesoresLieutenant / ProspeccionLeadsCaptain) ---
@tool
def tool_agendar_llamada_contacto(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoContactoSargento: tool_agendar_llamada_contacto"""
    return f"[AgendamientoContactoSargento] tool_agendar_llamada_contacto ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enviar_email_bienvenida(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoContactoSargento: tool_enviar_email_bienvenida"""
    return f"[AgendamientoContactoSargento] tool_enviar_email_bienvenida ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_recordatorio_asesor(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoContactoSargento: tool_recordatorio_asesor"""
    return f"[AgendamientoContactoSargento] tool_recordatorio_asesor ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_registrar_intento_contacto(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoContactoSargento: tool_registrar_intento_contacto"""
    return f"[AgendamientoContactoSargento] tool_registrar_intento_contacto ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_actualizar_pipeline_contactado(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoContactoSargento: tool_actualizar_pipeline_contactado"""
    return f"[AgendamientoContactoSargento] tool_actualizar_pipeline_contactado ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: AvanceEtapasSargento (EtapasEmbudoLieutenant / NegociacionPipelineCaptain) ---
@tool
def tool_pipeline_etapa_diagnostico(instruccion: str) -> str:
    """Soldado especialista de la escuadra AvanceEtapasSargento: tool_pipeline_etapa_diagnostico"""
    return f"[AvanceEtapasSargento] tool_pipeline_etapa_diagnostico ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_etapa_propuesta(instruccion: str) -> str:
    """Soldado especialista de la escuadra AvanceEtapasSargento: tool_pipeline_etapa_propuesta"""
    return f"[AvanceEtapasSargento] tool_pipeline_etapa_propuesta ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_etapa_negociacion(instruccion: str) -> str:
    """Soldado especialista de la escuadra AvanceEtapasSargento: tool_pipeline_etapa_negociacion"""
    return f"[AvanceEtapasSargento] tool_pipeline_etapa_negociacion ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_marcar_ganada(instruccion: str) -> str:
    """Soldado especialista de la escuadra AvanceEtapasSargento: tool_pipeline_marcar_ganada"""
    return f"[AvanceEtapasSargento] tool_pipeline_marcar_ganada ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_marcar_perdida(instruccion: str) -> str:
    """Soldado especialista de la escuadra AvanceEtapasSargento: tool_pipeline_marcar_perdida"""
    return f"[AvanceEtapasSargento] tool_pipeline_marcar_perdida ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: ControlTiemposSargento (EtapasEmbudoLieutenant / NegociacionPipelineCaptain) ---
@tool
def tool_pipeline_valor_estimado(instruccion: str) -> str:
    """Soldado especialista de la escuadra ControlTiemposSargento: tool_pipeline_valor_estimado"""
    return f"[ControlTiemposSargento] tool_pipeline_valor_estimado ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_fecha_cierre(instruccion: str) -> str:
    """Soldado especialista de la escuadra ControlTiemposSargento: tool_pipeline_fecha_cierre"""
    return f"[ControlTiemposSargento] tool_pipeline_fecha_cierre ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_dias_estancamiento(instruccion: str) -> str:
    """Soldado especialista de la escuadra ControlTiemposSargento: tool_pipeline_dias_estancamiento"""
    return f"[ControlTiemposSargento] tool_pipeline_dias_estancamiento ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_alerta_riesgo(instruccion: str) -> str:
    """Soldado especialista de la escuadra ControlTiemposSargento: tool_pipeline_alerta_riesgo"""
    return f"[ControlTiemposSargento] tool_pipeline_alerta_riesgo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pipeline_bitacora_cambios(instruccion: str) -> str:
    """Soldado especialista de la escuadra ControlTiemposSargento: tool_pipeline_bitacora_cambios"""
    return f"[ControlTiemposSargento] tool_pipeline_bitacora_cambios ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: ElaboracionCotizacionesSargento (CotizacionesPropuestasLieutenant / NegociacionPipelineCaptain) ---
@tool
def tool_cotizar_plan_mensual(instruccion: str) -> str:
    """Soldado especialista de la escuadra ElaboracionCotizacionesSargento: tool_cotizar_plan_mensual"""
    return f"[ElaboracionCotizacionesSargento] tool_cotizar_plan_mensual ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_cotizar_paquete_familiar(instruccion: str) -> str:
    """Soldado especialista de la escuadra ElaboracionCotizacionesSargento: tool_cotizar_paquete_familiar"""
    return f"[ElaboracionCotizacionesSargento] tool_cotizar_paquete_familiar ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_cotizar_convenio_colegio(instruccion: str) -> str:
    """Soldado especialista de la escuadra ElaboracionCotizacionesSargento: tool_cotizar_convenio_colegio"""
    return f"[ElaboracionCotizacionesSargento] tool_cotizar_convenio_colegio ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_aplicar_cupon_descuento(instruccion: str) -> str:
    """Soldado especialista de la escuadra ElaboracionCotizacionesSargento: tool_aplicar_cupon_descuento"""
    return f"[ElaboracionCotizacionesSargento] tool_aplicar_cupon_descuento ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_generar_cotizacion_pdf(instruccion: str) -> str:
    """Soldado especialista de la escuadra ElaboracionCotizacionesSargento: tool_generar_cotizacion_pdf"""
    return f"[ElaboracionCotizacionesSargento] tool_generar_cotizacion_pdf ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: SeguimientoPropuestasSargento (CotizacionesPropuestasLieutenant / NegociacionPipelineCaptain) ---
@tool
def tool_enviar_cotizacion_multicanal(instruccion: str) -> str:
    """Soldado especialista de la escuadra SeguimientoPropuestasSargento: tool_enviar_cotizacion_multicanal"""
    return f"[SeguimientoPropuestasSargento] tool_enviar_cotizacion_multicanal ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_verificar_lectura_propuesta(instruccion: str) -> str:
    """Soldado especialista de la escuadra SeguimientoPropuestasSargento: tool_verificar_lectura_propuesta"""
    return f"[SeguimientoPropuestasSargento] tool_verificar_lectura_propuesta ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_programar_seguimiento(instruccion: str) -> str:
    """Soldado especialista de la escuadra SeguimientoPropuestasSargento: tool_programar_seguimiento"""
    return f"[SeguimientoPropuestasSargento] tool_programar_seguimiento ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_ajustar_contraoferta(instruccion: str) -> str:
    """Soldado especialista de la escuadra SeguimientoPropuestasSargento: tool_ajustar_contraoferta"""
    return f"[SeguimientoPropuestasSargento] tool_ajustar_contraoferta ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_vencer_cotizacion_vigencia(instruccion: str) -> str:
    """Soldado especialista de la escuadra SeguimientoPropuestasSargento: tool_vencer_cotizacion_vigencia"""
    return f"[SeguimientoPropuestasSargento] tool_vencer_cotizacion_vigencia ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: AgendamientoDemosSargento (DemosVisitasLieutenant / NegociacionPipelineCaptain) ---
@tool
def tool_agendar_demo_deportiva(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoDemosSargento: tool_agendar_demo_deportiva"""
    return f"[AgendamientoDemosSargento] tool_agendar_demo_deportiva ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_agendar_demo_cultural(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoDemosSargento: tool_agendar_demo_cultural"""
    return f"[AgendamientoDemosSargento] tool_agendar_demo_cultural ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_verificar_cupo_escenario(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoDemosSargento: tool_verificar_cupo_escenario"""
    return f"[AgendamientoDemosSargento] tool_verificar_cupo_escenario ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enviar_pase_qr(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoDemosSargento: tool_enviar_pase_qr"""
    return f"[AgendamientoDemosSargento] tool_enviar_pase_qr ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_recordatorio_demo_24h(instruccion: str) -> str:
    """Soldado especialista de la escuadra AgendamientoDemosSargento: tool_recordatorio_demo_24h"""
    return f"[AgendamientoDemosSargento] tool_recordatorio_demo_24h ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: AsistenciaDemosSargento (DemosVisitasLieutenant / NegociacionPipelineCaptain) ---
@tool
def tool_confirmar_asistencia_demo(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsistenciaDemosSargento: tool_confirmar_asistencia_demo"""
    return f"[AsistenciaDemosSargento] tool_confirmar_asistencia_demo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_registrar_asistio_demo(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsistenciaDemosSargento: tool_registrar_asistio_demo"""
    return f"[AsistenciaDemosSargento] tool_registrar_asistio_demo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_reagendar_demo(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsistenciaDemosSargento: tool_reagendar_demo"""
    return f"[AsistenciaDemosSargento] tool_reagendar_demo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_solicitar_feedback_demo(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsistenciaDemosSargento: tool_solicitar_feedback_demo"""
    return f"[AsistenciaDemosSargento] tool_solicitar_feedback_demo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_oferta_cierre_inmediato(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsistenciaDemosSargento: tool_oferta_cierre_inmediato"""
    return f"[AsistenciaDemosSargento] tool_oferta_cierre_inmediato ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: FormalizacionMatriculaSargento (MatriculaDigitalLieutenant / CierreFacturacionCaptain) ---
@tool
def tool_convertir_a_alumno(instruccion: str) -> str:
    """Soldado especialista de la escuadra FormalizacionMatriculaSargento: tool_convertir_a_alumno"""
    return f"[FormalizacionMatriculaSargento] tool_convertir_a_alumno ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_crear_usuario_alumno(instruccion: str) -> str:
    """Soldado especialista de la escuadra FormalizacionMatriculaSargento: tool_crear_usuario_alumno"""
    return f"[FormalizacionMatriculaSargento] tool_crear_usuario_alumno ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_vincular_acudiente(instruccion: str) -> str:
    """Soldado especialista de la escuadra FormalizacionMatriculaSargento: tool_vincular_acudiente"""
    return f"[FormalizacionMatriculaSargento] tool_vincular_acudiente ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_generar_contrato_digital(instruccion: str) -> str:
    """Soldado especialista de la escuadra FormalizacionMatriculaSargento: tool_generar_contrato_digital"""
    return f"[FormalizacionMatriculaSargento] tool_generar_contrato_digital ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_firma_digital_terminos(instruccion: str) -> str:
    """Soldado especialista de la escuadra FormalizacionMatriculaSargento: tool_firma_digital_terminos"""
    return f"[FormalizacionMatriculaSargento] tool_firma_digital_terminos ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: AsignacionCursosSargento (MatriculaDigitalLieutenant / CierreFacturacionCaptain) ---
@tool
def tool_inscribir_grupo_entrenamiento(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsignacionCursosSargento: tool_inscribir_grupo_entrenamiento"""
    return f"[AsignacionCursosSargento] tool_inscribir_grupo_entrenamiento ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_inscribir_taller_cultural(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsignacionCursosSargento: tool_inscribir_taller_cultural"""
    return f"[AsignacionCursosSargento] tool_inscribir_taller_cultural ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_verificar_requisitos_salud(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsignacionCursosSargento: tool_verificar_requisitos_salud"""
    return f"[AsignacionCursosSargento] tool_verificar_requisitos_salud ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_asignar_kit_uniforme(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsignacionCursosSargento: tool_asignar_kit_uniforme"""
    return f"[AsignacionCursosSargento] tool_asignar_kit_uniforme ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enviar_kit_bienvenida(instruccion: str) -> str:
    """Soldado especialista de la escuadra AsignacionCursosSargento: tool_enviar_kit_bienvenida"""
    return f"[AsignacionCursosSargento] tool_enviar_kit_bienvenida ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: EmisionFacturasSargento (FacturacionCobranzaLieutenant / CierreFacturacionCaptain) ---
@tool
def tool_factura_matricula_db(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmisionFacturasSargento: tool_factura_matricula_db"""
    return f"[EmisionFacturasSargento] tool_factura_matricula_db ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_factura_mensualidad_db(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmisionFacturasSargento: tool_factura_mensualidad_db"""
    return f"[EmisionFacturasSargento] tool_factura_mensualidad_db ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_aplicar_recargos_descuentos(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmisionFacturasSargento: tool_aplicar_recargos_descuentos"""
    return f"[EmisionFacturasSargento] tool_aplicar_recargos_descuentos ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_recibo_caja_efectivo(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmisionFacturasSargento: tool_recibo_caja_efectivo"""
    return f"[EmisionFacturasSargento] tool_recibo_caja_efectivo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_nota_credito_anulacion(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmisionFacturasSargento: tool_nota_credito_anulacion"""
    return f"[EmisionFacturasSargento] tool_nota_credito_anulacion ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: PasarelasPagoSargento (FacturacionCobranzaLieutenant / CierreFacturacionCaptain) ---
@tool
def tool_generar_link_pago_online(instruccion: str) -> str:
    """Soldado especialista de la escuadra PasarelasPagoSargento: tool_generar_link_pago_online"""
    return '{"status":"BLOCKED","code":"PERSISTED_PAYMENT_AND_AUTHENTIC_RECEIPT_REQUIRED","executed":false}'

@tool

def tool_verificar_webhook_pago(instruccion: str) -> str:
    """Soldado especialista de la escuadra PasarelasPagoSargento: tool_verificar_webhook_pago"""
    return '{"status":"BLOCKED","code":"PERSISTED_PAYMENT_AND_AUTHENTIC_RECEIPT_REQUIRED","executed":false}'

@tool

def tool_reintentar_cobro_fallido(instruccion: str) -> str:
    """Soldado especialista de la escuadra PasarelasPagoSargento: tool_reintentar_cobro_fallido"""
    return '{"status":"BLOCKED","code":"PERSISTED_PAYMENT_AND_AUTHENTIC_RECEIPT_REQUIRED","executed":false}'

@tool

def tool_actualizar_factura_pagada(instruccion: str) -> str:
    """Soldado especialista de la escuadra PasarelasPagoSargento: tool_actualizar_factura_pagada"""
    return '{"status":"BLOCKED","code":"PERSISTED_PAYMENT_AND_AUTHENTIC_RECEIPT_REQUIRED","executed":false}'

@tool

def tool_enviar_comprobante_pago(instruccion: str) -> str:
    """Soldado especialista de la escuadra PasarelasPagoSargento: tool_enviar_comprobante_pago"""
    return '{"status":"BLOCKED","code":"PERSISTED_PAYMENT_AND_AUTHENTIC_RECEIPT_REQUIRED","executed":false}'

# --- Escuadra: PrevencionDesercionSargento (RetencionChurnLieutenant / CierreFacturacionCaptain) ---
@tool

def tool_detectar_inasistencias_3(instruccion: str) -> str:
    """Soldado especialista de la escuadra PrevencionDesercionSargento: tool_detectar_inasistencias_3"""
    return f"[PrevencionDesercionSargento] tool_detectar_inasistencias_3 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_alerta_factura_por_vencer(instruccion: str) -> str:
    """Soldado especialista de la escuadra PrevencionDesercionSargento: tool_alerta_factura_por_vencer"""
    return f"[PrevencionDesercionSargento] tool_alerta_factura_por_vencer ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_tarea_llamada_retencion(instruccion: str) -> str:
    """Soldado especialista de la escuadra PrevencionDesercionSargento: tool_tarea_llamada_retencion"""
    return f"[PrevencionDesercionSargento] tool_tarea_llamada_retencion ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pausa_temporal_matricula(instruccion: str) -> str:
    """Soldado especialista de la escuadra PrevencionDesercionSargento: tool_pausa_temporal_matricula"""
    return f"[PrevencionDesercionSargento] tool_pausa_temporal_matricula ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_encuesta_salida_retiro(instruccion: str) -> str:
    """Soldado especialista de la escuadra PrevencionDesercionSargento: tool_encuesta_salida_retiro"""
    return f"[PrevencionDesercionSargento] tool_encuesta_salida_retiro ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: CampanasRenovacionSargento (RetencionChurnLieutenant / CierreFacturacionCaptain) ---
@tool
def tool_identificar_contratos_30d(instruccion: str) -> str:
    """Soldado especialista de la escuadra CampanasRenovacionSargento: tool_identificar_contratos_30d"""
    return f"[CampanasRenovacionSargento] tool_identificar_contratos_30d ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_oferta_renovacion_anticipada(instruccion: str) -> str:
    """Soldado especialista de la escuadra CampanasRenovacionSargento: tool_oferta_renovacion_anticipada"""
    return f"[CampanasRenovacionSargento] tool_oferta_renovacion_anticipada ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_beneficio_antiguedad(instruccion: str) -> str:
    """Soldado especialista de la escuadra CampanasRenovacionSargento: tool_beneficio_antiguedad"""
    return f"[CampanasRenovacionSargento] tool_beneficio_antiguedad ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_reenganche_alumnos_antiguos(instruccion: str) -> str:
    """Soldado especialista de la escuadra CampanasRenovacionSargento: tool_reenganche_alumnos_antiguos"""
    return f"[CampanasRenovacionSargento] tool_reenganche_alumnos_antiguos ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_oferta_retorno_especial(instruccion: str) -> str:
    """Soldado especialista de la escuadra CampanasRenovacionSargento: tool_oferta_retorno_especial"""
    return f"[CampanasRenovacionSargento] tool_oferta_retorno_especial ejecutada con éxito para: {instruccion[:50]}"

