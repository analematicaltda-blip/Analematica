from langchain_core.tools import tool

# --- Escuadra: GuionStoryboardSargento (PreproduccionLieutenant / ProduccionVideoCaptain) ---
@tool
def tool_redactar_guion_vertical(instruccion: str) -> str:
    """Soldado especialista de la escuadra GuionStoryboardSargento: tool_redactar_guion_vertical"""
    return f"[GuionStoryboardSargento] tool_redactar_guion_vertical ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_crear_storyboard_escenas(instruccion: str) -> str:
    """Soldado especialista de la escuadra GuionStoryboardSargento: tool_crear_storyboard_escenas"""
    return f"[GuionStoryboardSargento] tool_crear_storyboard_escenas ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_extraer_gancho_viral(instruccion: str) -> str:
    """Soldado especialista de la escuadra GuionStoryboardSargento: tool_extraer_gancho_viral"""
    return f"[GuionStoryboardSargento] tool_extraer_gancho_viral ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_estructurar_cta_final(instruccion: str) -> str:
    """Soldado especialista de la escuadra GuionStoryboardSargento: tool_estructurar_cta_final"""
    return f"[GuionStoryboardSargento] tool_estructurar_cta_final ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_calcular_tiempos_ritmo(instruccion: str) -> str:
    """Soldado especialista de la escuadra GuionStoryboardSargento: tool_calcular_tiempos_ritmo"""
    return f"[GuionStoryboardSargento] tool_calcular_tiempos_ritmo ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: OptimizacionTextoSargento (PreproduccionLieutenant / ProduccionVideoCaptain) ---
@tool
def tool_titulos_alta_retencion(instruccion: str) -> str:
    """Soldado especialista de la escuadra OptimizacionTextoSargento: tool_titulos_alta_retencion"""
    return f"[OptimizacionTextoSargento] tool_titulos_alta_retencion ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_copy_descripcion_post(instruccion: str) -> str:
    """Soldado especialista de la escuadra OptimizacionTextoSargento: tool_copy_descripcion_post"""
    return f"[OptimizacionTextoSargento] tool_copy_descripcion_post ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_hashtags_estrategicos(instruccion: str) -> str:
    """Soldado especialista de la escuadra OptimizacionTextoSargento: tool_hashtags_estrategicos"""
    return f"[OptimizacionTextoSargento] tool_hashtags_estrategicos ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_texto_portada_hook(instruccion: str) -> str:
    """Soldado especialista de la escuadra OptimizacionTextoSargento: tool_texto_portada_hook"""
    return f"[OptimizacionTextoSargento] tool_texto_portada_hook ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_validar_limites_caracteres(instruccion: str) -> str:
    """Soldado especialista de la escuadra OptimizacionTextoSargento: tool_validar_limites_caracteres"""
    return f"[OptimizacionTextoSargento] tool_validar_limites_caracteres ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: SintesisTtsSargento (LocucionAudioLieutenant / ProduccionVideoCaptain) ---
@tool
def tool_tts_voz_femenina(instruccion: str) -> str:
    """Soldado especialista de la escuadra SintesisTtsSargento: tool_tts_voz_femenina"""
    return f"[SintesisTtsSargento] tool_tts_voz_femenina ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_tts_voz_masculina(instruccion: str) -> str:
    """Soldado especialista de la escuadra SintesisTtsSargento: tool_tts_voz_masculina"""
    return f"[SintesisTtsSargento] tool_tts_voz_masculina ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_tts_ajustar_velocidad(instruccion: str) -> str:
    """Soldado especialista de la escuadra SintesisTtsSargento: tool_tts_ajustar_velocidad"""
    return f"[SintesisTtsSargento] tool_tts_ajustar_velocidad ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_tts_modular_tono(instruccion: str) -> str:
    """Soldado especialista de la escuadra SintesisTtsSargento: tool_tts_modular_tono"""
    return f"[SintesisTtsSargento] tool_tts_modular_tono ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_tts_limpiar_ruido(instruccion: str) -> str:
    """Soldado especialista de la escuadra SintesisTtsSargento: tool_tts_limpiar_ruido"""
    return f"[SintesisTtsSargento] tool_tts_limpiar_ruido ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: MezclaSonidoSargento (LocucionAudioLieutenant / ProduccionVideoCaptain) ---
@tool
def tool_seleccionar_musica_fondo(instruccion: str) -> str:
    """Soldado especialista de la escuadra MezclaSonidoSargento: tool_seleccionar_musica_fondo"""
    return f"[MezclaSonidoSargento] tool_seleccionar_musica_fondo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_mezclar_voz_musica(instruccion: str) -> str:
    """Soldado especialista de la escuadra MezclaSonidoSargento: tool_mezclar_voz_musica"""
    return f"[MezclaSonidoSargento] tool_mezclar_voz_musica ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_normalizar_lufs(instruccion: str) -> str:
    """Soldado especialista de la escuadra MezclaSonidoSargento: tool_normalizar_lufs"""
    return f"[MezclaSonidoSargento] tool_normalizar_lufs ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_agregar_efectos_sfx(instruccion: str) -> str:
    """Soldado especialista de la escuadra MezclaSonidoSargento: tool_agregar_efectos_sfx"""
    return f"[MezclaSonidoSargento] tool_agregar_efectos_sfx ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_audio_fade_in_out(instruccion: str) -> str:
    """Soldado especialista de la escuadra MezclaSonidoSargento: tool_audio_fade_in_out"""
    return f"[MezclaSonidoSargento] tool_audio_fade_in_out ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: SubtitulosDinamicosSargento (PostproduccionFfmpegLieutenant / ProduccionVideoCaptain) ---
@tool
def tool_generar_srt_sincronizado(instruccion: str) -> str:
    """Soldado especialista de la escuadra SubtitulosDinamicosSargento: tool_generar_srt_sincronizado"""
    return f"[SubtitulosDinamicosSargento] tool_generar_srt_sincronizado ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_quemar_subtitulos_video(instruccion: str) -> str:
    """Soldado especialista de la escuadra SubtitulosDinamicosSargento: tool_quemar_subtitulos_video"""
    return f"[SubtitulosDinamicosSargento] tool_quemar_subtitulos_video ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_resaltar_keywords_color(instruccion: str) -> str:
    """Soldado especialista de la escuadra SubtitulosDinamicosSargento: tool_resaltar_keywords_color"""
    return f"[SubtitulosDinamicosSargento] tool_resaltar_keywords_color ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_sincronizar_timing_subtitulos(instruccion: str) -> str:
    """Soldado especialista de la escuadra SubtitulosDinamicosSargento: tool_sincronizar_timing_subtitulos"""
    return f"[SubtitulosDinamicosSargento] tool_sincronizar_timing_subtitulos ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_zona_segura_subtitulos(instruccion: str) -> str:
    """Soldado especialista de la escuadra SubtitulosDinamicosSargento: tool_zona_segura_subtitulos"""
    return f"[SubtitulosDinamicosSargento] tool_zona_segura_subtitulos ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: RenderFfmpegSargento (PostproduccionFfmpegLieutenant / ProduccionVideoCaptain) ---
@tool
def tool_render_reel_1080x1920(instruccion: str) -> str:
    """Soldado especialista de la escuadra RenderFfmpegSargento: tool_render_reel_1080x1920"""
    return f"[RenderFfmpegSargento] tool_render_reel_1080x1920 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_render_video_1920x1080(instruccion: str) -> str:
    """Soldado especialista de la escuadra RenderFfmpegSargento: tool_render_video_1920x1080"""
    return f"[RenderFfmpegSargento] tool_render_video_1920x1080 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_colorimetria_institucional(instruccion: str) -> str:
    """Soldado especialista de la escuadra RenderFfmpegSargento: tool_colorimetria_institucional"""
    return f"[RenderFfmpegSargento] tool_colorimetria_institucional ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_optimizar_bitrate_h264(instruccion: str) -> str:
    """Soldado especialista de la escuadra RenderFfmpegSargento: tool_optimizar_bitrate_h264"""
    return f"[RenderFfmpegSargento] tool_optimizar_bitrate_h264 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_extraer_thumbnail_poster(instruccion: str) -> str:
    """Soldado especialista de la escuadra RenderFfmpegSargento: tool_extraer_thumbnail_poster"""
    return f"[RenderFfmpegSargento] tool_extraer_thumbnail_poster ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: PostCuadradoSargento (PostsBannersLieutenant / DisenoVisualCaptain) ---
@tool
def tool_canvas_post_1080x1080(instruccion: str) -> str:
    """Soldado especialista de la escuadra PostCuadradoSargento: tool_canvas_post_1080x1080"""
    return f"[PostCuadradoSargento] tool_canvas_post_1080x1080 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_titular_jerarquia_post(instruccion: str) -> str:
    """Soldado especialista de la escuadra PostCuadradoSargento: tool_titular_jerarquia_post"""
    return f"[PostCuadradoSargento] tool_titular_jerarquia_post ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_aislar_sujeto_png(instruccion: str) -> str:
    """Soldado especialista de la escuadra PostCuadradoSargento: tool_aislar_sujeto_png"""
    return f"[PostCuadradoSargento] tool_aislar_sujeto_png ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_degradado_institucional(instruccion: str) -> str:
    """Soldado especialista de la escuadra PostCuadradoSargento: tool_degradado_institucional"""
    return f"[PostCuadradoSargento] tool_degradado_institucional ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_insertar_logos_entidad(instruccion: str) -> str:
    """Soldado especialista de la escuadra PostCuadradoSargento: tool_insertar_logos_entidad"""
    return f"[PostCuadradoSargento] tool_insertar_logos_entidad ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: BannerHorizontalSargento (PostsBannersLieutenant / DisenoVisualCaptain) ---
@tool
def tool_crear_banner_1920x1080(instruccion: str) -> str:
    """Soldado especialista de la escuadra BannerHorizontalSargento: tool_crear_banner_1920x1080"""
    return f"[BannerHorizontalSargento] tool_crear_banner_1920x1080 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_adaptar_hero_web(instruccion: str) -> str:
    """Soldado especialista de la escuadra BannerHorizontalSargento: tool_adaptar_hero_web"""
    return f"[BannerHorizontalSargento] tool_adaptar_hero_web ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_integrar_datos_evento(instruccion: str) -> str:
    """Soldado especialista de la escuadra BannerHorizontalSargento: tool_integrar_datos_evento"""
    return f"[BannerHorizontalSargento] tool_integrar_datos_evento ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_banner_email_header(instruccion: str) -> str:
    """Soldado especialista de la escuadra BannerHorizontalSargento: tool_banner_email_header"""
    return f"[BannerHorizontalSargento] tool_banner_email_header ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_exportar_webp(instruccion: str) -> str:
    """Soldado especialista de la escuadra BannerHorizontalSargento: tool_exportar_webp"""
    return f"[BannerHorizontalSargento] tool_exportar_webp ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: NarrativaCarruselSargento (CarruselesSecuenciasLieutenant / DisenoVisualCaptain) ---
@tool
def tool_definir_slides_carrusel(instruccion: str) -> str:
    """Soldado especialista de la escuadra NarrativaCarruselSargento: tool_definir_slides_carrusel"""
    return f"[NarrativaCarruselSargento] tool_definir_slides_carrusel ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_slide_portada_hook(instruccion: str) -> str:
    """Soldado especialista de la escuadra NarrativaCarruselSargento: tool_slide_portada_hook"""
    return f"[NarrativaCarruselSargento] tool_slide_portada_hook ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_slides_cuerpo_educativo(instruccion: str) -> str:
    """Soldado especialista de la escuadra NarrativaCarruselSargento: tool_slides_cuerpo_educativo"""
    return f"[NarrativaCarruselSargento] tool_slides_cuerpo_educativo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_slide_cierre_cta(instruccion: str) -> str:
    """Soldado especialista de la escuadra NarrativaCarruselSargento: tool_slide_cierre_cta"""
    return f"[NarrativaCarruselSargento] tool_slide_cierre_cta ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_continuidad_visual_flechas(instruccion: str) -> str:
    """Soldado especialista de la escuadra NarrativaCarruselSargento: tool_continuidad_visual_flechas"""
    return f"[NarrativaCarruselSargento] tool_continuidad_visual_flechas ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: EmpaquetadoCarruselSargento (CarruselesSecuenciasLieutenant / DisenoVisualCaptain) ---
@tool
def tool_render_slides_secuencia(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmpaquetadoCarruselSargento: tool_render_slides_secuencia"""
    return f"[EmpaquetadoCarruselSargento] tool_render_slides_secuencia ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_paginacion_badge(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmpaquetadoCarruselSargento: tool_paginacion_badge"""
    return f"[EmpaquetadoCarruselSargento] tool_paginacion_badge ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_empaquetar_directorio(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmpaquetadoCarruselSargento: tool_empaquetar_directorio"""
    return f"[EmpaquetadoCarruselSargento] tool_empaquetar_directorio ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_generar_pdf_carrusel(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmpaquetadoCarruselSargento: tool_generar_pdf_carrusel"""
    return f"[EmpaquetadoCarruselSargento] tool_generar_pdf_carrusel ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_verificar_resolucion_slides(instruccion: str) -> str:
    """Soldado especialista de la escuadra EmpaquetadoCarruselSargento: tool_verificar_resolucion_slides"""
    return f"[EmpaquetadoCarruselSargento] tool_verificar_resolucion_slides ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: PaletaTipografiaSargento (BrandingIdentidadLieutenant / DisenoVisualCaptain) ---
@tool
def tool_aplicar_paleta_colores(instruccion: str) -> str:
    """Soldado especialista de la escuadra PaletaTipografiaSargento: tool_aplicar_paleta_colores"""
    return f"[PaletaTipografiaSargento] tool_aplicar_paleta_colores ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_aplicar_fuente_titulos(instruccion: str) -> str:
    """Soldado especialista de la escuadra PaletaTipografiaSargento: tool_aplicar_fuente_titulos"""
    return f"[PaletaTipografiaSargento] tool_aplicar_fuente_titulos ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_aplicar_fuente_cuerpo(instruccion: str) -> str:
    """Soldado especialista de la escuadra PaletaTipografiaSargento: tool_aplicar_fuente_cuerpo"""
    return f"[PaletaTipografiaSargento] tool_aplicar_fuente_cuerpo ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_verificar_contraste_wcag(instruccion: str) -> str:
    """Soldado especialista de la escuadra PaletaTipografiaSargento: tool_verificar_contraste_wcag"""
    return f"[PaletaTipografiaSargento] tool_verificar_contraste_wcag ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_insertar_marca_agua(instruccion: str) -> str:
    """Soldado especialista de la escuadra PaletaTipografiaSargento: tool_insertar_marca_agua"""
    return f"[PaletaTipografiaSargento] tool_insertar_marca_agua ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: CalidadGraficaSargento (BrandingIdentidadLieutenant / DisenoVisualCaptain) ---
@tool
def tool_optimizar_peso_imagen(instruccion: str) -> str:
    """Soldado especialista de la escuadra CalidadGraficaSargento: tool_optimizar_peso_imagen"""
    return f"[CalidadGraficaSargento] tool_optimizar_peso_imagen ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_convertir_png_jpg_webp(instruccion: str) -> str:
    """Soldado especialista de la escuadra CalidadGraficaSargento: tool_convertir_png_jpg_webp"""
    return f"[CalidadGraficaSargento] tool_convertir_png_jpg_webp ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_verificar_dpi(instruccion: str) -> str:
    """Soldado especialista de la escuadra CalidadGraficaSargento: tool_verificar_dpi"""
    return f"[CalidadGraficaSargento] tool_verificar_dpi ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_variacion_modo_oscuro(instruccion: str) -> str:
    """Soldado especialista de la escuadra CalidadGraficaSargento: tool_variacion_modo_oscuro"""
    return f"[CalidadGraficaSargento] tool_variacion_modo_oscuro ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_archivar_master_grafico(instruccion: str) -> str:
    """Soldado especialista de la escuadra CalidadGraficaSargento: tool_archivar_master_grafico"""
    return f"[CalidadGraficaSargento] tool_archivar_master_grafico ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: ClasificacionTagsSargento (IngestaTagsLieutenant / AlmacenAssetsCaptain) ---
@tool
def tool_asignar_uuid_asset(instruccion: str) -> str:
    """Soldado especialista de la escuadra ClasificacionTagsSargento: tool_asignar_uuid_asset"""
    return f"[ClasificacionTagsSargento] tool_asignar_uuid_asset ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_categorizar_medio_deporte(instruccion: str) -> str:
    """Soldado especialista de la escuadra ClasificacionTagsSargento: tool_categorizar_medio_deporte"""
    return f"[ClasificacionTagsSargento] tool_categorizar_medio_deporte ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_extraer_exif_metadata(instruccion: str) -> str:
    """Soldado especialista de la escuadra ClasificacionTagsSargento: tool_extraer_exif_metadata"""
    return f"[ClasificacionTagsSargento] tool_extraer_exif_metadata ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_asignar_tags_busqueda(instruccion: str) -> str:
    """Soldado especialista de la escuadra ClasificacionTagsSargento: tool_asignar_tags_busqueda"""
    return f"[ClasificacionTagsSargento] tool_asignar_tags_busqueda ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_registrar_inquilino_propietario(instruccion: str) -> str:
    """Soldado especialista de la escuadra ClasificacionTagsSargento: tool_registrar_inquilino_propietario"""
    return f"[ClasificacionTagsSargento] tool_registrar_inquilino_propietario ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: IntegridadStorageSargento (IngestaTagsLieutenant / AlmacenAssetsCaptain) ---
@tool
def tool_calcular_sha256_media(instruccion: str) -> str:
    """Soldado especialista de la escuadra IntegridadStorageSargento: tool_calcular_sha256_media"""
    return f"[IntegridadStorageSargento] tool_calcular_sha256_media ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_verificar_integridad_bitstream(instruccion: str) -> str:
    """Soldado especialista de la escuadra IntegridadStorageSargento: tool_verificar_integridad_bitstream"""
    return f"[IntegridadStorageSargento] tool_verificar_integridad_bitstream ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_detectar_duplicados_storage(instruccion: str) -> str:
    """Soldado especialista de la escuadra IntegridadStorageSargento: tool_detectar_duplicados_storage"""
    return f"[IntegridadStorageSargento] tool_detectar_duplicados_storage ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_reparar_moov_atom_mp4(instruccion: str) -> str:
    """Soldado especialista de la escuadra IntegridadStorageSargento: tool_reparar_moov_atom_mp4"""
    return f"[IntegridadStorageSargento] tool_reparar_moov_atom_mp4 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_cuarentena_corruptos(instruccion: str) -> str:
    """Soldado especialista de la escuadra IntegridadStorageSargento: tool_cuarentena_corruptos"""
    return f"[IntegridadStorageSargento] tool_cuarentena_corruptos ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: PublicacionWebSargento (EntregaNginxLieutenant / AlmacenAssetsCaptain) ---
@tool
def tool_mover_a_assets_generated(instruccion: str) -> str:
    """Soldado especialista de la escuadra PublicacionWebSargento: tool_mover_a_assets_generated"""
    return f"[PublicacionWebSargento] tool_mover_a_assets_generated ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_permisos_lectura_nginx(instruccion: str) -> str:
    """Soldado especialista de la escuadra PublicacionWebSargento: tool_permisos_lectura_nginx"""
    return f"[PublicacionWebSargento] tool_permisos_lectura_nginx ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_enlace_publico_http(instruccion: str) -> str:
    """Soldado especialista de la escuadra PublicacionWebSargento: tool_enlace_publico_http"""
    return f"[PublicacionWebSargento] tool_enlace_publico_http ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_codigo_qr_recurso(instruccion: str) -> str:
    """Soldado especialista de la escuadra PublicacionWebSargento: tool_codigo_qr_recurso"""
    return f"[PublicacionWebSargento] tool_codigo_qr_recurso ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_headers_cache_control(instruccion: str) -> str:
    """Soldado especialista de la escuadra PublicacionWebSargento: tool_headers_cache_control"""
    return f"[PublicacionWebSargento] tool_headers_cache_control ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: PurgaRetencionSargento (EntregaNginxLieutenant / AlmacenAssetsCaptain) ---
@tool
def tool_limpiar_temporales_render(instruccion: str) -> str:
    """Soldado especialista de la escuadra PurgaRetencionSargento: tool_limpiar_temporales_render"""
    return f"[PurgaRetencionSargento] tool_limpiar_temporales_render ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_purgar_archivos_antiguos(instruccion: str) -> str:
    """Soldado especialista de la escuadra PurgaRetencionSargento: tool_purgar_archivos_antiguos"""
    return f"[PurgaRetencionSargento] tool_purgar_archivos_antiguos ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_calcular_espacio_disco(instruccion: str) -> str:
    """Soldado especialista de la escuadra PurgaRetencionSargento: tool_calcular_espacio_disco"""
    return f"[PurgaRetencionSargento] tool_calcular_espacio_disco ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_alerta_umbral_storage_90(instruccion: str) -> str:
    """Soldado especialista de la escuadra PurgaRetencionSargento: tool_alerta_umbral_storage_90"""
    return f"[PurgaRetencionSargento] tool_alerta_umbral_storage_90 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_comprimir_historicos_tar(instruccion: str) -> str:
    """Soldado especialista de la escuadra PurgaRetencionSargento: tool_comprimir_historicos_tar"""
    return f"[PurgaRetencionSargento] tool_comprimir_historicos_tar ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: TranscodificacionSargento (AdaptacionFormatosLieutenant / AlmacenAssetsCaptain) ---
@tool
def tool_variante_video_720p(instruccion: str) -> str:
    """Soldado especialista de la escuadra TranscodificacionSargento: tool_variante_video_720p"""
    return f"[TranscodificacionSargento] tool_variante_video_720p ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_variante_video_480p(instruccion: str) -> str:
    """Soldado especialista de la escuadra TranscodificacionSargento: tool_variante_video_480p"""
    return f"[TranscodificacionSargento] tool_variante_video_480p ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_preview_gif_3seg(instruccion: str) -> str:
    """Soldado especialista de la escuadra TranscodificacionSargento: tool_preview_gif_3seg"""
    return f"[TranscodificacionSargento] tool_preview_gif_3seg ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_extraer_audio_mp3(instruccion: str) -> str:
    """Soldado especialista de la escuadra TranscodificacionSargento: tool_extraer_audio_mp3"""
    return f"[TranscodificacionSargento] tool_extraer_audio_mp3 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_ajustar_rotacion_metadata(instruccion: str) -> str:
    """Soldado especialista de la escuadra TranscodificacionSargento: tool_ajustar_rotacion_metadata"""
    return f"[TranscodificacionSargento] tool_ajustar_rotacion_metadata ejecutada con éxito para: {instruccion[:50]}"

# --- Escuadra: CompatibilidadSoSargento (AdaptacionFormatosLieutenant / AlmacenAssetsCaptain) ---
@tool
def tool_soporte_reproductor_android(instruccion: str) -> str:
    """Soldado especialista de la escuadra CompatibilidadSoSargento: tool_soporte_reproductor_android"""
    return f"[CompatibilidadSoSargento] tool_soporte_reproductor_android ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_soporte_reproductor_ios(instruccion: str) -> str:
    """Soldado especialista de la escuadra CompatibilidadSoSargento: tool_soporte_reproductor_ios"""
    return f"[CompatibilidadSoSargento] tool_soporte_reproductor_ios ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_pixel_format_yuv420p(instruccion: str) -> str:
    """Soldado especialista de la escuadra CompatibilidadSoSargento: tool_pixel_format_yuv420p"""
    return f"[CompatibilidadSoSargento] tool_pixel_format_yuv420p ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_fragmentar_hls_m3u8(instruccion: str) -> str:
    """Soldado especialista de la escuadra CompatibilidadSoSargento: tool_fragmentar_hls_m3u8"""
    return f"[CompatibilidadSoSargento] tool_fragmentar_hls_m3u8 ejecutada con éxito para: {instruccion[:50]}"

@tool
def tool_validar_reproduccion_sin_cortes(instruccion: str) -> str:
    """Soldado especialista de la escuadra CompatibilidadSoSargento: tool_validar_reproduccion_sin_cortes"""
    return f"[CompatibilidadSoSargento] tool_validar_reproduccion_sin_cortes ejecutada con éxito para: {instruccion[:50]}"

