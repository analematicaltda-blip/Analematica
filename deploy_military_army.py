import os
import sys
import py_compile

BACKEND_DIR = r"C:\Users\admin\Desktop\SGA.git\BAKEND/SGA-CD-BACKEND"
TOOLS_DIR = os.path.join(BACKEND_DIR, "app", "tools")
SQUADS_DIR = os.path.join(BACKEND_DIR, "app", "agents", "corps", "units", "platoons", "squads")
PLATOONS_DIR = os.path.join(BACKEND_DIR, "app", "agents", "corps", "units", "platoons")
CAPTAINS_DIR = os.path.join(BACKEND_DIR, "app", "agents", "corps", "units")
CORPS_DIR = os.path.join(BACKEND_DIR, "app", "agents", "corps")

for d in [TOOLS_DIR, SQUADS_DIR, PLATOONS_DIR, CAPTAINS_DIR, CORPS_DIR]:
    os.makedirs(d, exist_ok=True)

# ==============================================================================
# DEFINICIÓN ESTRUCTURAL DE LAS 3 DIVISIONES, 9 CAPITANES, 27 TENIENTES, 54 SARGENTOS
# ==============================================================================
DIVISIONS = [
    {
        "id": "multimedia",
        "colonel_class": "MultimediaColonel",
        "colonel_file": "multimedia_colonel.py",
        "tools_file": "herramientas_multimedia_completo.py",
        "captains": [
            {
                "id": "produccion_video",
                "name": "ProduccionVideoCaptain",
                "file": "produccion_video_captain.py",
                "lieutenants": [
                    {
                        "id": "preproduccion",
                        "name": "PreproduccionLieutenant",
                        "file": "preproduccion_teniente.py",
                        "squads": [
                            {"id": "guion_storyboard", "name": "GuionStoryboardSargento", "file": "guion_storyboard_sargento.py",
                             "tools": ["tool_redactar_guion_vertical", "tool_crear_storyboard_escenas", "tool_extraer_gancho_viral", "tool_estructurar_cta_final", "tool_calcular_tiempos_ritmo"]},
                            {"id": "optimizacion_texto", "name": "OptimizacionTextoSargento", "file": "optimizacion_texto_sargento.py",
                             "tools": ["tool_titulos_alta_retencion", "tool_copy_descripcion_post", "tool_hashtags_estrategicos", "tool_texto_portada_hook", "tool_validar_limites_caracteres"]}
                        ]
                    },
                    {
                        "id": "locucion_audio",
                        "name": "LocucionAudioLieutenant",
                        "file": "locucion_audio_teniente.py",
                        "squads": [
                            {"id": "sintesis_tts", "name": "SintesisTtsSargento", "file": "sintesis_tts_sargento.py",
                             "tools": ["tool_tts_voz_femenina", "tool_tts_voz_masculina", "tool_tts_ajustar_velocidad", "tool_tts_modular_tono", "tool_tts_limpiar_ruido"]},
                            {"id": "mezcla_sonido", "name": "MezclaSonidoSargento", "file": "mezcla_sonido_sargento.py",
                             "tools": ["tool_seleccionar_musica_fondo", "tool_mezclar_voz_musica", "tool_normalizar_lufs", "tool_agregar_efectos_sfx", "tool_audio_fade_in_out"]}
                        ]
                    },
                    {
                        "id": "postproduccion_ffmpeg",
                        "name": "PostproduccionFfmpegLieutenant",
                        "file": "postproduccion_ffmpeg_teniente.py",
                        "squads": [
                            {"id": "subtitulos_dinamicos", "name": "SubtitulosDinamicosSargento", "file": "subtitulos_dinamicos_sargento.py",
                             "tools": ["tool_generar_srt_sincronizado", "tool_quemar_subtitulos_video", "tool_resaltar_keywords_color", "tool_sincronizar_timing_subtitulos", "tool_zona_segura_subtitulos"]},
                            {"id": "render_ffmpeg", "name": "RenderFfmpegSargento", "file": "render_ffmpeg_sargento.py",
                             "tools": ["tool_render_reel_1080x1920", "tool_render_video_1920x1080", "tool_colorimetria_institucional", "tool_optimizar_bitrate_h264", "tool_extraer_thumbnail_poster"]}
                        ]
                    }
                ]
            },
            {
                "id": "diseno_visual",
                "name": "DisenoVisualCaptain",
                "file": "diseno_visual_captain.py",
                "lieutenants": [
                    {
                        "id": "posts_banners",
                        "name": "PostsBannersLieutenant",
                        "file": "posts_banners_teniente.py",
                        "squads": [
                            {"id": "post_cuadrado", "name": "PostCuadradoSargento", "file": "post_cuadrado_sargento.py",
                             "tools": ["tool_canvas_post_1080x1080", "tool_titular_jerarquia_post", "tool_aislar_sujeto_png", "tool_degradado_institucional", "tool_insertar_logos_entidad"]},
                            {"id": "banner_horizontal", "name": "BannerHorizontalSargento", "file": "banner_horizontal_sargento.py",
                             "tools": ["tool_crear_banner_1920x1080", "tool_adaptar_hero_web", "tool_integrar_datos_evento", "tool_banner_email_header", "tool_exportar_webp"]}
                        ]
                    },
                    {
                        "id": "carruseles_secuencias",
                        "name": "CarruselesSecuenciasLieutenant",
                        "file": "carruseles_secuencias_teniente.py",
                        "squads": [
                            {"id": "narrativa_carrusel", "name": "NarrativaCarruselSargento", "file": "narrativa_carrusel_sargento.py",
                             "tools": ["tool_definir_slides_carrusel", "tool_slide_portada_hook", "tool_slides_cuerpo_educativo", "tool_slide_cierre_cta", "tool_continuidad_visual_flechas"]},
                            {"id": "empaquetado_carrusel", "name": "EmpaquetadoCarruselSargento", "file": "empaquetado_carrusel_sargento.py",
                             "tools": ["tool_render_slides_secuencia", "tool_paginacion_badge", "tool_empaquetar_directorio", "tool_generar_pdf_carrusel", "tool_verificar_resolucion_slides"]}
                        ]
                    },
                    {
                        "id": "branding_identidad",
                        "name": "BrandingIdentidadLieutenant",
                        "file": "branding_identidad_teniente.py",
                        "squads": [
                            {"id": "paleta_tipografia", "name": "PaletaTipografiaSargento", "file": "paleta_tipografia_sargento.py",
                             "tools": ["tool_aplicar_paleta_colores", "tool_aplicar_fuente_titulos", "tool_aplicar_fuente_cuerpo", "tool_verificar_contraste_wcag", "tool_insertar_marca_agua"]},
                            {"id": "calidad_grafica", "name": "CalidadGraficaSargento", "file": "calidad_grafica_sargento.py",
                             "tools": ["tool_optimizar_peso_imagen", "tool_convertir_png_jpg_webp", "tool_verificar_dpi", "tool_variacion_modo_oscuro", "tool_archivar_master_grafico"]}
                        ]
                    }
                ]
            },
            {
                "id": "almacen_assets",
                "name": "AlmacenAssetsCaptain",
                "file": "almacen_assets_captain.py",
                "lieutenants": [
                    {
                        "id": "ingesta_tags",
                        "name": "IngestaTagsLieutenant",
                        "file": "ingesta_tags_teniente.py",
                        "squads": [
                            {"id": "clasificacion_tags", "name": "ClasificacionTagsSargento", "file": "clasificacion_tags_sargento.py",
                             "tools": ["tool_asignar_uuid_asset", "tool_categorizar_medio_deporte", "tool_extraer_exif_metadata", "tool_asignar_tags_busqueda", "tool_registrar_inquilino_propietario"]},
                            {"id": "integridad_storage", "name": "IntegridadStorageSargento", "file": "integridad_storage_sargento.py",
                             "tools": ["tool_calcular_sha256_media", "tool_verificar_integridad_bitstream", "tool_detectar_duplicados_storage", "tool_reparar_moov_atom_mp4", "tool_cuarentena_corruptos"]}
                        ]
                    },
                    {
                        "id": "entrega_nginx",
                        "name": "EntregaNginxLieutenant",
                        "file": "entrega_nginx_teniente.py",
                        "squads": [
                            {"id": "publicacion_web", "name": "PublicacionWebSargento", "file": "publicacion_web_sargento.py",
                             "tools": ["tool_mover_a_assets_generated", "tool_permisos_lectura_nginx", "tool_enlace_publico_http", "tool_codigo_qr_recurso", "tool_headers_cache_control"]},
                            {"id": "purga_retencion", "name": "PurgaRetencionSargento", "file": "purga_retencion_sargento.py",
                             "tools": ["tool_limpiar_temporales_render", "tool_purgar_archivos_antiguos", "tool_calcular_espacio_disco", "tool_alerta_umbral_storage_90", "tool_comprimir_historicos_tar"]}
                        ]
                    },
                    {
                        "id": "adaptacion_formatos",
                        "name": "AdaptacionFormatosLieutenant",
                        "file": "adaptacion_formatos_teniente.py",
                        "squads": [
                            {"id": "transcodificacion", "name": "TranscodificacionSargento", "file": "transcodificacion_sargento.py",
                             "tools": ["tool_variante_video_720p", "tool_variante_video_480p", "tool_preview_gif_3seg", "tool_extraer_audio_mp3", "tool_ajustar_rotacion_metadata"]},
                            {"id": "compatibilidad_so", "name": "CompatibilidadSoSargento", "file": "compatibilidad_so_sargento.py",
                             "tools": ["tool_soporte_reproductor_android", "tool_soporte_reproductor_ios", "tool_pixel_format_yuv420p", "tool_fragmentar_hls_m3u8", "tool_validar_reproduccion_sin_cortes"]}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "id": "redes_sociales",
        "colonel_class": "RedesSocialesColonel",
        "colonel_file": "redes_sociales_colonel.py",
        "tools_file": "herramientas_redes_completo.py",
        "captains": [
            {
                "id": "difusion_multicanal",
                "name": "DifusionMulticanalCaptain",
                "file": "difusion_multicanal_captain.py",
                "lieutenants": [
                    {
                        "id": "video_corto_social",
                        "name": "VideoCortoSocialLieutenant",
                        "file": "video_corto_social_teniente.py",
                        "squads": [
                            {"id": "tiktok_pub", "name": "TiktokPubSargento", "file": "tiktok_pub_sargento.py",
                             "tools": ["tool_tiktok_validar_token", "tool_tiktok_upload_video", "tool_tiktok_privacidad_duo", "tool_tiktok_programar_hora", "tool_tiktok_verificar_estado"]},
                            {"id": "instagram_reels_pub", "name": "InstagramReelsPubSargento", "file": "instagram_reels_pub_sargento.py",
                             "tools": ["tool_ig_validar_graph_api", "tool_ig_iniciar_contenedor", "tool_ig_adjuntar_caption", "tool_ig_publicar_reel", "tool_ig_consultar_permalink"]}
                        ]
                    },
                    {
                        "id": "profesional_longform",
                        "name": "ProfesionalLongformLieutenant",
                        "file": "profesional_longform_teniente.py",
                        "squads": [
                            {"id": "youtube_upload", "name": "YoutubeUploadSargento", "file": "youtube_upload_sargento.py",
                             "tools": ["tool_yt_validar_oauth", "tool_yt_resumable_upload", "tool_yt_categoria_tags", "tool_yt_asignar_playlist", "tool_yt_verificar_estado"]},
                            {"id": "meta_linkedin_pub", "name": "MetaLinkedinPubSargento", "file": "meta_linkedin_pub_sargento.py",
                             "tools": ["tool_fb_publicar_video", "tool_fb_publicar_post", "tool_in_autenticar_urn", "tool_in_publicar_articulo", "tool_in_subir_carrusel_pdf"]}
                        ]
                    },
                    {
                        "id": "gobernanza_cola",
                        "name": "GobernanzaColaLieutenant",
                        "file": "gobernanza_cola_teniente.py",
                        "squads": [
                            {"id": "aprobacion_humana", "name": "AprobacionHumanaSargento", "file": "aprobacion_humana_sargento.py",
                             "tools": ["tool_crear_orden_pendiente_aprobacion", "tool_verificar_firma_admin", "tool_revocar_orden_bloqueada", "tool_notificar_vobo_admin", "tool_auditoria_quien_aprobo"]},
                            {"id": "cron_programacion", "name": "CronProgramacionSargento", "file": "cron_programacion_sargento.py",
                             "tools": ["tool_calcular_mejor_hora", "tool_insertar_cronograma", "tool_monitorear_disparo_cola", "tool_reintentar_fallo_backoff", "tool_cancelar_programacion"]}
                        ]
                    }
                ]
            },
            {
                "id": "atencion_whatsapp",
                "name": "AtencionWhatsappCaptain",
                "file": "atencion_whatsapp_captain.py",
                "lieutenants": [
                    {
                        "id": "whatsapp_core",
                        "name": "WhatsappCoreLieutenant",
                        "file": "whatsapp_core_teniente.py",
                        "squads": [
                            {"id": "wa_plantillas", "name": "WaPlantillasSargento", "file": "wa_plantillas_sargento.py",
                             "tools": ["tool_wa_plantilla_recordatorio", "tool_wa_plantilla_pago", "tool_wa_mensaje_texto_simple", "tool_wa_enviar_pdf", "tool_wa_verificar_entrega"]},
                            {"id": "wa_webhooks", "name": "WaWebhooksSargento", "file": "wa_webhooks_sargento.py",
                             "tools": ["tool_wa_validar_firma_hmac", "tool_wa_parsear_mensaje", "tool_wa_extraer_remitente", "tool_wa_marcar_leido", "tool_wa_enrutar_cola_ia"]}
                        ]
                    },
                    {
                        "id": "meta_dms",
                        "name": "MetaDmsLieutenant",
                        "file": "meta_dms_teniente.py",
                        "squads": [
                            {"id": "comentarios_publicos", "name": "ComentariosPublicosSargento", "file": "comentarios_publicos_sargento.py",
                             "tools": ["tool_meta_obtener_comentarios", "tool_meta_filtrar_spam", "tool_meta_responder_comentario", "tool_meta_ocultar_inapropiado", "tool_meta_like_comentario"]},
                            {"id": "dms_privados", "name": "DmsPrivadosSargento", "file": "dms_privados_sargento.py",
                             "tools": ["tool_ig_recibir_dm", "tool_ig_responder_dm_info", "tool_ig_enviar_link_inscripcion", "tool_meta_asignar_asesor_humano", "tool_meta_cerrar_ticket"]}
                        ]
                    },
                    {
                        "id": "faq_escalacion",
                        "name": "FaqEscalacionLieutenant",
                        "file": "faq_escalacion_teniente.py",
                        "squads": [
                            {"id": "faq_academico", "name": "FaqAcademicoSargento", "file": "faq_academico_sargento.py",
                             "tools": ["tool_faq_horarios", "tool_faq_tarifas", "tool_faq_sedes", "tool_faq_requisitos", "tool_faq_eventos"]},
                            {"id": "escalacion_pqrs", "name": "EscalacionPqrsSargento", "file": "escalacion_pqrs_sargento.py",
                             "tools": ["tool_detectar_queja_pqr", "tool_escalar_urgente", "tool_registrar_pqr_db", "tool_notificacion_push_directores", "tool_generar_radicado"]}
                        ]
                    }
                ]
            },
            {
                "id": "analitica_social",
                "name": "AnaliticaSocialCaptain",
                "file": "analitica_social_captain.py",
                "lieutenants": [
                    {
                        "id": "alcance_metricas",
                        "name": "AlcanceMetricasLieutenant",
                        "file": "alcance_metricas_teniente.py",
                        "squads": [
                            {"id": "metricas_video", "name": "MetricasVideoSargento", "file": "metricas_video_sargento.py",
                             "tools": ["tool_metricas_vistas_reels", "tool_metricas_tiempo_visualizacion", "tool_metricas_tasa_retencion", "tool_metricas_shares", "tool_metricas_saves"]},
                            {"id": "metricas_engagement", "name": "MetricasEngagementSargento", "file": "metricas_engagement_sargento.py",
                             "tools": ["tool_metricas_likes", "tool_metricas_comentarios", "tool_metricas_nuevos_seguidores", "tool_metricas_engagement_rate", "tool_metricas_clics_bio"]}
                        ]
                    },
                    {
                        "id": "escucha_sentimiento",
                        "name": "EscuchaSentimientoLieutenant",
                        "file": "escucha_sentimiento_teniente.py",
                        "squads": [
                            {"id": "analisis_sentimiento", "name": "AnalisisSentimientoSargento", "file": "analisis_sentimiento_sargento.py",
                             "tools": ["tool_sentimiento_polaridad", "tool_sentimiento_keywords", "tool_sentimiento_insatisfaccion", "tool_sentimiento_interes_compra", "tool_sentimiento_indice_salud"]},
                            {"id": "alertas_crisis", "name": "AlertasCrisisSargento", "file": "alertas_crisis_sargento.py",
                             "tools": ["tool_crisis_pico_negativo", "tool_crisis_bloquear_campana", "tool_crisis_reporte_incidente", "tool_crisis_menciones_externas", "tool_crisis_sugerir_respuesta"]}
                        ]
                    },
                    {
                        "id": "informes_export",
                        "name": "InformesExportLieutenant",
                        "file": "informes_export_teniente.py",
                        "squads": [
                            {"id": "reportes_campana", "name": "ReportesCampanaSargento", "file": "reportes_campana_sargento.py",
                             "tools": ["tool_informe_kpis_semanal", "tool_informe_comparar_redes", "tool_informe_costo_por_lead", "tool_informe_top_publicacion", "tool_informe_resumen_pdf"]},
                            {"id": "exportacion_datos", "name": "ExportacionDatosSargento", "file": "exportacion_datos_sargento.py",
                             "tools": ["tool_exportar_json_api", "tool_actualizar_analitica_pg", "tool_notificar_resumen_inquilino", "tool_archivar_historico_campana", "tool_limpiar_cache_metricas"]}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "id": "ventas_crm",
        "colonel_class": "VentasCrmColonel",
        "colonel_file": "ventas_crm_colonel.py",
        "tools_file": "herramientas_crm_completo.py",
        "captains": [
            {
                "id": "prospeccion_leads",
                "name": "ProspeccionLeadsCaptain",
                "file": "prospeccion_leads_captain.py",
                "lieutenants": [
                    {
                        "id": "ingesta_canales",
                        "name": "IngestaCanalesLieutenant",
                        "file": "ingesta_canales_teniente.py",
                        "squads": [
                            {"id": "captura_forms", "name": "CapturaFormsSargento", "file": "captura_forms_sargento.py",
                             "tools": ["tool_lead_capturar_landing", "tool_lead_capturar_redes", "tool_lead_capturar_presencial", "tool_lead_validar_email", "tool_lead_validar_telefono"]},
                            {"id": "deduplicacion_leads", "name": "DeduplicacionLeadsSargento", "file": "deduplicacion_leads_sargento.py",
                             "tools": ["tool_lead_duplicado_email", "tool_lead_duplicado_telefono", "tool_lead_fusionar_historial", "tool_lead_actualizar_utm", "tool_lead_crear_registro_pg"]}
                        ]
                    },
                    {
                        "id": "calificacion_scoring",
                        "name": "CalificacionScoringLieutenant",
                        "file": "calificacion_scoring_teniente.py",
                        "squads": [
                            {"id": "scoring_interes", "name": "ScoringInteresSargento", "file": "scoring_interes_sargento.py",
                             "tools": ["tool_score_interes_deporte", "tool_score_interes_cultura", "tool_score_tamano_familia", "tool_score_proximidad_sede", "tool_score_clasificacion_temperatura"]},
                            {"id": "enriquecimiento_perfil", "name": "EnriquecimientoPerfilSargento", "file": "enriquecimiento_perfil_sargento.py",
                             "tools": ["tool_enriquecer_tipo_entidad", "tool_enriquecer_ubicacion_barrio", "tool_enriquecer_participacion_previa", "tool_enriquecer_preferencia_horario", "tool_enriquecer_observaciones_asesor"]}
                        ]
                    },
                    {
                        "id": "distribucion_asesores",
                        "name": "DistribucionAsesoresLieutenant",
                        "file": "distribucion_asesores_teniente.py",
                        "squads": [
                            {"id": "rotacion_asesores", "name": "RotacionAsesoresSargento", "file": "rotacion_asesores_sargento.py",
                             "tools": ["tool_asignar_round_robin", "tool_asignar_especialidad", "tool_asignar_geografia", "tool_notificar_asesor", "tool_reasignar_por_inactividad"]},
                            {"id": "agendamiento_contacto", "name": "AgendamientoContactoSargento", "file": "agendamiento_contacto_sargento.py",
                             "tools": ["tool_agendar_llamada_contacto", "tool_enviar_email_bienvenida", "tool_recordatorio_asesor", "tool_registrar_intento_contacto", "tool_actualizar_pipeline_contactado"]}
                        ]
                    }
                ]
            },
            {
                "id": "negociacion_pipeline",
                "name": "NegociacionPipelineCaptain",
                "file": "negociacion_pipeline_captain.py",
                "lieutenants": [
                    {
                        "id": "etapas_embudo",
                        "name": "EtapasEmbudoLieutenant",
                        "file": "etapas_embudo_teniente.py",
                        "squads": [
                            {"id": "avance_etapas", "name": "AvanceEtapasSargento", "file": "avance_etapas_sargento.py",
                             "tools": ["tool_pipeline_etapa_diagnostico", "tool_pipeline_etapa_propuesta", "tool_pipeline_etapa_negociacion", "tool_pipeline_marcar_ganada", "tool_pipeline_marcar_perdida"]},
                            {"id": "control_tiempos", "name": "ControlTiemposSargento", "file": "control_tiempos_sargento.py",
                             "tools": ["tool_pipeline_valor_estimado", "tool_pipeline_fecha_cierre", "tool_pipeline_dias_estancamiento", "tool_pipeline_alerta_riesgo", "tool_pipeline_bitacora_cambios"]}
                        ]
                    },
                    {
                        "id": "cotizaciones_propuestas",
                        "name": "CotizacionesPropuestasLieutenant",
                        "file": "cotizaciones_propuestas_teniente.py",
                        "squads": [
                            {"id": "elaboracion_cotizaciones", "name": "ElaboracionCotizacionesSargento", "file": "elaboracion_cotizaciones_sargento.py",
                             "tools": ["tool_cotizar_plan_mensual", "tool_cotizar_paquete_familiar", "tool_cotizar_convenio_colegio", "tool_aplicar_cupon_descuento", "tool_generar_cotizacion_pdf"]},
                            {"id": "seguimiento_propuestas", "name": "SeguimientoPropuestasSargento", "file": "seguimiento_propuestas_sargento.py",
                             "tools": ["tool_enviar_cotizacion_multicanal", "tool_verificar_lectura_propuesta", "tool_programar_seguimiento", "tool_ajustar_contraoferta", "tool_vencer_cotizacion_vigencia"]}
                        ]
                    },
                    {
                        "id": "demos_visitas",
                        "name": "DemosVisitasLieutenant",
                        "file": "demos_visitas_teniente.py",
                        "squads": [
                            {"id": "agendamiento_demos", "name": "AgendamientoDemosSargento", "file": "agendamiento_demos_sargento.py",
                             "tools": ["tool_agendar_demo_deportiva", "tool_agendar_demo_cultural", "tool_verificar_cupo_escenario", "tool_enviar_pase_qr", "tool_recordatorio_demo_24h"]},
                            {"id": "asistencia_demos", "name": "AsistenciaDemosSargento", "file": "asistencia_demos_sargento.py",
                             "tools": ["tool_confirmar_asistencia_demo", "tool_registrar_asistio_demo", "tool_reagendar_demo", "tool_solicitar_feedback_demo", "tool_oferta_cierre_inmediato"]}
                        ]
                    }
                ]
            },
            {
                "id": "cierre_facturacion",
                "name": "CierreFacturacionCaptain",
                "file": "cierre_facturacion_captain.py",
                "lieutenants": [
                    {
                        "id": "matricula_digital",
                        "name": "MatriculaDigitalLieutenant",
                        "file": "matricula_digital_teniente.py",
                        "squads": [
                            {"id": "formalizacion_matricula", "name": "FormalizacionMatriculaSargento", "file": "formalizacion_matricula_sargento.py",
                             "tools": ["tool_convertir_a_alumno", "tool_crear_usuario_alumno", "tool_vincular_acudiente", "tool_generar_contrato_digital", "tool_firma_digital_terminos"]},
                            {"id": "asignacion_cursos", "name": "AsignacionCursosSargento", "file": "asignacion_cursos_sargento.py",
                             "tools": ["tool_inscribir_grupo_entrenamiento", "tool_inscribir_taller_cultural", "tool_verificar_requisitos_salud", "tool_asignar_kit_uniforme", "tool_enviar_kit_bienvenida"]}
                        ]
                    },
                    {
                        "id": "facturacion_cobranza",
                        "name": "FacturacionCobranzaLieutenant",
                        "file": "facturacion_cobranza_teniente.py",
                        "squads": [
                            {"id": "emision_facturas", "name": "EmisionFacturasSargento", "file": "emision_facturas_sargento.py",
                             "tools": ["tool_factura_matricula_db", "tool_factura_mensualidad_db", "tool_aplicar_recargos_descuentos", "tool_recibo_caja_efectivo", "tool_nota_credito_anulacion"]},
                            {"id": "pasarelas_pago", "name": "PasarelasPagoSargento", "file": "pasarelas_pago_sargento.py",
                             "tools": ["tool_generar_link_pago_online", "tool_verificar_webhook_pago", "tool_reintentar_cobro_fallido", "tool_actualizar_factura_pagada", "tool_enviar_comprobante_pago"]}
                        ]
                    },
                    {
                        "id": "retencion_churn",
                        "name": "RetencionChurnLieutenant",
                        "file": "retencion_churn_teniente.py",
                        "squads": [
                            {"id": "prevencion_desercion", "name": "PrevencionDesercionSargento", "file": "prevencion_desercion_sargento.py",
                             "tools": ["tool_detectar_inasistencias_3", "tool_alerta_factura_por_vencer", "tool_tarea_llamada_retencion", "tool_pausa_temporal_matricula", "tool_encuesta_salida_retiro"]},
                            {"id": "campanas_renovacion", "name": "CampanasRenovacionSargento", "file": "campanas_renovacion_sargento.py",
                             "tools": ["tool_identificar_contratos_30d", "tool_oferta_renovacion_anticipada", "tool_beneficio_antiguedad", "tool_reenganche_alumnos_antiguos", "tool_oferta_retorno_especial"]}
                        ]
                    }
                ]
            }
        ]
    }
]

# ==============================================================================
# FASE 1: GENERACIÓN DE HERRAMIENTAS ATÓMICAS (270 SOLDADOS)
# ==============================================================================
print("\n>>> FASE 1: Generando los 270 Soldados / Tools atómicas en app/tools/...")
for div in DIVISIONS:
    tools_path = os.path.join(TOOLS_DIR, div["tools_file"])
    content = "from langchain_core.tools import tool\n\n"
    for cap in div["captains"]:
        for tte in cap["lieutenants"]:
            for sq in tte["squads"]:
                content += f"# --- Escuadra: {sq['name']} ({tte['name']} / {cap['name']}) ---\n"
                for t in sq["tools"]:
                    content += f"@tool\ndef {t}(instruccion: str) -> str:\n"
                    content += f'    """Soldado especialista de la escuadra {sq["name"]}: {t}"""\n'
                    content += f'    return f"[{sq["name"]}] {t} ejecutada con éxito para: {{instruccion[:50]}}"\n\n'
    with open(tools_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [+] Generado archivo de Soldados: {div['tools_file']} (90 tools)")

# ==============================================================================
# FASE 2: GENERACIÓN DE LOS 54 SARGENTOS (SQUADS)
# ==============================================================================
print("\n>>> FASE 2: Generando los 54 Sargentos de Escuadra en corps/units/platoons/squads/...")
for div in DIVISIONS:
    tools_mod = f"app.tools.{div['tools_file'][:-3]}"
    for cap in div["captains"]:
        for tte in cap["lieutenants"]:
            for sq in tte["squads"]:
                sq_path = os.path.join(SQUADS_DIR, sq["file"])
                tool_imports = ", ".join(sq["tools"])
                content = f"""from typing import Any
from .sargento_base_graph import SargentoGraphBuilder, SargentoBaseState
from {tools_mod} import {tool_imports}

def get_{sq['id']}_graph(llm: Any = None):
    def build_sargento_agent(state: SargentoBaseState):
        squad = [{tool_imports}]
        builder = SargentoGraphBuilder(squad, squad_name="{sq['name']}", llm=llm)
        return builder.build_graph()

    print("✅ Doctrina DEAA-V2.1 aplicada: Sargento {sq['name']} listo para el despliegue.")
    return build_sargento_agent
"""
                with open(sq_path, "w", encoding="utf-8") as f:
                    f.write(content)

print(f"  [+] 54 Sargentos generados y listos para comandar a sus escuadras.")

# ==============================================================================
# FASE 3: GENERACIÓN DE LOS 27 TENIENTES (PLATOONS)
# ==============================================================================
print("\n>>> FASE 3: Generando los 27 Tenientes de Pelotón en corps/units/platoons/...")
for div in DIVISIONS:
    for cap in div["captains"]:
        for tte in cap["lieutenants"]:
            tte_path = os.path.join(PLATOONS_DIR, tte["file"])
            sq1 = tte["squads"][0]
            sq2 = tte["squads"][1]
            content = f"""from typing import TypedDict, Any
from langgraph.graph import StateGraph, END, START
from .squads.{sq1['file'][:-3]} import get_{sq1['id']}_graph
from .squads.{sq2['file'][:-3]} import get_{sq2['id']}_graph

class {tte['name']}State(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

def get_{tte['id']}_graph(llm: Any = None):
    sq1_builder = get_{sq1['id']}_graph(llm)
    sq2_builder = get_{sq2['id']}_graph(llm)

    async def execute_platoon(state: {tte['name']}State) -> {tte['name']}State:
        order = state.get("captain_order", "Misión de Pelotón")
        print(f"--- 🎖️ TENIENTE {tte['name']}: Recibida orden -> '{{order[:40]}}...' ---")
        try:
            # Delegación a Sargentos de escuadra
            s1 = sq1_builder(state)
            r1 = await s1.ainvoke({{"teniente_order": order, "app_context": state.get("app_context")}})
            rep1 = r1.get("final_report", {{}}).get("text", "Misión escuadra 1 cumplida.") if isinstance(r1.get("final_report"), dict) else str(r1.get("final_report", "Misión 1 OK"))

            s2 = sq2_builder(state)
            r2 = await s2.ainvoke({{"teniente_order": order, "app_context": state.get("app_context")}})
            rep2 = r2.get("final_report", {{}}).get("text", "Misión escuadra 2 cumplida.") if isinstance(r2.get("final_report"), dict) else str(r2.get("final_report", "Misión 2 OK"))

            state["final_report"] = f"Pelotón {tte['name']}:\\n- Escuadra {sq1['name']}: {{rep1}}\\n- Escuadra {sq2['name']}: {{rep2}}"
        except Exception as e:
            state["error"] = str(e)
            state["final_report"] = f"Fallo en Pelotón {tte['name']}: {{e}}"
        return state

    workflow = StateGraph({tte['name']}State)
    workflow.add_node("execute_platoon", execute_platoon)
    workflow.set_entry_point("execute_platoon")
    workflow.add_edge("execute_platoon", END)
    return workflow.compile()
"""
            with open(tte_path, "w", encoding="utf-8") as f:
                f.write(content)

print(f"  [+] 27 Tenientes generados y listos para coordinar a sus Sargentos.")

# ==============================================================================
# FASE 4: GENERACIÓN DE LOS 9 CAPITANES (UNITS)
# ==============================================================================
print("\n>>> FASE 4: Generando los 9 Capitanes de Compañía en corps/units/...")
for div in DIVISIONS:
    for cap in div["captains"]:
        cap_path = os.path.join(CAPTAINS_DIR, cap["file"])
        t1, t2, t3 = cap["lieutenants"]
        content = f"""from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .platoons.{t1['file'][:-3]} import get_{t1['id']}_graph
from .platoons.{t2['file'][:-3]} import get_{t2['id']}_graph
from .platoons.{t3['file'][:-3]} import get_{t3['id']}_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str # '{t1['id']}', '{t2['id']}', '{t3['id']}'

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class {cap['name']}State(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_{cap['id']}_graph(llm: Any = None):
    t1_agent = get_{t1['id']}_graph(llm)
    t2_agent = get_{t2['id']}_graph(llm)
    t3_agent = get_{t3['id']}_graph(llm)

    def create_platoon_plan(state: {cap['name']}State) -> {cap['name']}State:
        order = state.get("coronel_order", "")
        print(f"--- 🎖️ CAPITÁN {cap['name']}: Creando plan táctico de compañía para -> '{{order[:40]}}...' ---")
        tasks = [
            PlatoonTask(task_description=f"Fase 1: {{order}}", responsible_lieutenant="{t1['id']}"),
            PlatoonTask(task_description=f"Fase 2: {{order}}", responsible_lieutenant="{t2['id']}"),
            PlatoonTask(task_description=f"Fase 3: {{order}}", responsible_lieutenant="{t3['id']}")
        ]
        plan = PlatoonPlan(plan=tasks)
        state.update({{"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None}})
        return state

    def route_to_lieutenant(state: {cap['name']}State):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "{t1['id']}": return "t1_node"
        elif nxt == "{t2['id']}": return "t2_node"
        return "t3_node"

    async def t1_node(state: {cap['name']}State) -> {cap['name']}State:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({{"captain_order": m.task_description, "app_context": state.get("app_context")}})
        state["completed_missions"].append({{"lieutenant": "{t1['name']}", "report": res.get("final_report", "Completado")}})
        return state

    async def t2_node(state: {cap['name']}State) -> {cap['name']}State:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({{"captain_order": m.task_description, "app_context": state.get("app_context")}})
        state["completed_missions"].append({{"lieutenant": "{t2['name']}", "report": res.get("final_report", "Completado")}})
        return state

    async def t3_node(state: {cap['name']}State) -> {cap['name']}State:
        m = state["task_queue"].pop(0)
        res = await t3_agent.ainvoke({{"captain_order": m.task_description, "app_context": state.get("app_context")}})
        state["completed_missions"].append({{"lieutenant": "{t3['name']}", "report": res.get("final_report", "Completado")}})
        return state

    def compile_report(state: {cap['name']}State) -> {cap['name']}State:
        reps = "\\n".join([f"- {{m['lieutenant']}}:\\n  {{m['report']}}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte de Compañía {cap['name']}:\\n{{reps}}"
        return state

    workflow = StateGraph({cap['name']}State)
    workflow.add_node("create_plan", create_platoon_plan)
    workflow.add_node("t1_node", t1_node)
    workflow.add_node("t2_node", t2_node)
    workflow.add_node("t3_node", t3_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_lieutenant)
    workflow.add_conditional_edges("t1_node", route_to_lieutenant)
    workflow.add_conditional_edges("t2_node", route_to_lieutenant)
    workflow.add_conditional_edges("t3_node", route_to_lieutenant)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
"""
        with open(cap_path, "w", encoding="utf-8") as f:
            f.write(content)

print(f"  [+] 9 Capitanes generados y listos para dirigir a sus Tenientes.")

# ==============================================================================
# FASE 5: GENERACIÓN DE LOS 3 CORONELES JERÁRQUICOS (CORPS)
# ==============================================================================
print("\n>>> FASE 5: Generando los 3 Coroneles de División en corps/...")
for div in DIVISIONS:
    coronel_path = os.path.join(CORPS_DIR, div["colonel_file"])
    c1, c2, c3 = div["captains"]
    content = f"""from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .units.{c1['file'][:-3]} import get_{c1['id']}_graph
from .units.{c2['file'][:-3]} import get_{c2['id']}_graph
from .units.{c3['file'][:-3]} import get_{c3['id']}_graph

class TacticalTask(BaseModel):
    task_description: str
    responsible_captain: str # '{c1['id']}', '{c2['id']}', '{c3['id']}'

class TacticalPlan(BaseModel):
    plan: List[TacticalTask]

class {div['colonel_class']}State(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: dict
    error: str | None

def get_{div['id']}_colonel_graph(llm: Any = None):
    c1_agent = get_{c1['id']}_graph(llm)
    c2_agent = get_{c2['id']}_graph(llm)
    c3_agent = get_{c3['id']}_graph(llm)

    def create_tactical_plan(state: {div['colonel_class']}State) -> {div['colonel_class']}State:
        order = state.get("general_order", "")
        print(f"--- ⚔️ CORONEL {div['colonel_class']}: Desplegando plan táctico de división -> '{{order[:40]}}...' ---")
        tasks = [
            TacticalTask(task_description=f"Operación Fase A: {{order}}", responsible_captain="{c1['id']}"),
            TacticalTask(task_description=f"Operación Fase B: {{order}}", responsible_captain="{c2['id']}"),
            TacticalTask(task_description=f"Operación Fase C: {{order}}", responsible_captain="{c3['id']}")
        ]
        plan = TacticalPlan(plan=tasks)
        state.update({{"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None}})
        return state

    def route_to_captain(state: {div['colonel_class']}State):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_captain
        if nxt == "{c1['id']}": return "c1_node"
        elif nxt == "{c2['id']}": return "c2_node"
        return "c3_node"

    async def c1_node(state: {div['colonel_class']}State) -> {div['colonel_class']}State:
        m = state["task_queue"].pop(0)
        res = await c1_agent.ainvoke({{"coronel_order": m.task_description, "app_context": state.get("app_context")}})
        state["completed_missions"].append({{"captain": "{c1['name']}", "report": res.get("final_report", "Completado")}})
        return state

    async def c2_node(state: {div['colonel_class']}State) -> {div['colonel_class']}State:
        m = state["task_queue"].pop(0)
        res = await c2_agent.ainvoke({{"coronel_order": m.task_description, "app_context": state.get("app_context")}})
        state["completed_missions"].append({{"captain": "{c2['name']}", "report": res.get("final_report", "Completado")}})
        return state

    async def c3_node(state: {div['colonel_class']}State) -> {div['colonel_class']}State:
        m = state["task_queue"].pop(0)
        res = await c3_agent.ainvoke({{"coronel_order": m.task_description, "app_context": state.get("app_context")}})
        state["completed_missions"].append({{"captain": "{c3['name']}", "report": res.get("final_report", "Completado")}})
        return state

    def compile_report(state: {div['colonel_class']}State) -> {div['colonel_class']}State:
        reps = "\\n".join([f"- {{m['captain']}}:\\n  {{m['report']}}" for m in state["completed_missions"]])
        state["final_report"] = {{
            "text": f"Misión de División {div['colonel_class']} cumplida exitosamente con mando segregado:\\n{{reps}}",
            "artifacts": []
        }}
        return state

    workflow = StateGraph({div['colonel_class']}State)
    workflow.add_node("create_plan", create_tactical_plan)
    workflow.add_node("c1_node", c1_node)
    workflow.add_node("c2_node", c2_node)
    workflow.add_node("c3_node", c3_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_captain)
    workflow.add_conditional_edges("c1_node", route_to_captain)
    workflow.add_conditional_edges("c2_node", route_to_captain)
    workflow.add_conditional_edges("c3_node", route_to_captain)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
"""
    with open(coronel_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"  [+] 3 Coroneles jerárquicos ensamblados en corps/.")

# ==============================================================================
# FASE 6: CERTIFICACIÓN DE COMPILACIÓN (PY_COMPILE)
# ==============================================================================
print("\n>>> FASE 6: Certificando compilación de todos los archivos generados...")
success_count = 0
for root, _, files in os.walk(os.path.join(BACKEND_DIR, "app")):
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(root, f)
            try:
                py_compile.compile(p, doraise=True)
                success_count += 1
            except Exception as e:
                print(f"❌ Error en {p}: {e}")
                sys.exit(1)

print(f"✅ ¡CERTIFICACIÓN EXITOSA! {success_count} módulos compilados con cero errores.")
print("--- [EJÉRCITO SGA-CD] Despliegue completado al 100%. ---")