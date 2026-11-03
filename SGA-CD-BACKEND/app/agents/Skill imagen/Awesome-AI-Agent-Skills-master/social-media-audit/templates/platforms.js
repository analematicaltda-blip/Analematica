/* ═══════════════════════════════════════════
   Platforms Configuration — All 11 Networks
   ═══════════════════════════════════════════ */

const PLATFORMS = {
    instagram: {
        id: 'instagram', name: 'Instagram', icon: '📸',
        color: '#E1306C', desc: 'Posts, Stories, Reels, IG Live',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'ig_url', label: 'URL / @usuario', type: 'text', placeholder: '@tu_marca', required: true },
                { id: 'ig_objetivo', label: 'Objetivo principal', type: 'select', options: ['Branding','Ventas','Leads','Engagement','Comunidad'] },
                { id: 'ig_nicho', label: 'Nicho / Industria', type: 'text', placeholder: 'Ej: Moda, Fitness, Gastronomía' },
                { id: 'ig_publico', label: 'Público objetivo', type: 'text', placeholder: 'Ej: Mujeres 25-35, Lima' },
                { id: 'ig_seguidores', label: 'Seguidores actuales', type: 'number', placeholder: '10000' },
            ]},
            { section: '📊 Métricas y Contenido', fields: [
                { id: 'ig_frecuencia', label: 'Frecuencia de posts/semana', type: 'number', placeholder: '5' },
                { id: 'ig_stories', label: 'Stories/semana', type: 'number', placeholder: '10' },
                { id: 'ig_reels', label: 'Reels/semana', type: 'number', placeholder: '3' },
                { id: 'ig_engagement', label: 'Engagement promedio (%)', type: 'number', placeholder: '3.5', step: '0.1' },
                { id: 'ig_reach', label: 'Alcance promedio por post', type: 'number', placeholder: '5000' },
                { id: 'ig_hashtags', label: 'Hashtags principales', type: 'textarea', placeholder: '#tumarca #nicho #tendencia' },
            ]},
            { section: '🎥 IG Live', fields: [
                { id: 'ig_live_freq', label: 'Frecuencia de Lives', type: 'select', options: ['No hago','Semanal','Quincenal','Mensual','Esporádico'] },
                { id: 'ig_live_duracion', label: 'Duración promedio (min)', type: 'number', placeholder: '30' },
                { id: 'ig_live_viewers', label: 'Viewers promedio', type: 'number', placeholder: '50' },
            ]},
            { section: '💰 Campañas', fields: [
                { id: 'ig_ads', label: '¿Campañas pagadas?', type: 'select', options: ['No','Sí, actualmente','Sí, en el pasado'] },
                { id: 'ig_ads_budget', label: 'Presupuesto mensual (USD)', type: 'number', placeholder: '500', optional: true },
                { id: 'ig_bio', label: 'Bio actual', type: 'textarea', placeholder: 'Copia tu bio aquí', optional: true },
            ]},
        ]
    },
    tiktok: {
        id: 'tiktok', name: 'TikTok', icon: '🎵',
        color: '#00F2EA', desc: 'Videos, TikTok Live',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'tt_url', label: 'URL / @usuario', type: 'text', placeholder: '@tu_marca', required: true },
                { id: 'tt_objetivo', label: 'Objetivo principal', type: 'select', options: ['Branding','Ventas','Leads','Engagement','Comunidad','Viralidad'] },
                { id: 'tt_nicho', label: 'Nicho / Industria', type: 'text', placeholder: 'Ej: Entretenimiento, Educación' },
                { id: 'tt_publico', label: 'Público objetivo', type: 'text', placeholder: 'Ej: Gen Z 18-24' },
                { id: 'tt_seguidores', label: 'Seguidores actuales', type: 'number', placeholder: '50000' },
            ]},
            { section: '📊 Métricas y Contenido', fields: [
                { id: 'tt_frecuencia', label: 'Videos/semana', type: 'number', placeholder: '7' },
                { id: 'tt_engagement', label: 'Engagement promedio (%)', type: 'number', placeholder: '5', step: '0.1' },
                { id: 'tt_views', label: 'Views promedio por video', type: 'number', placeholder: '10000' },
                { id: 'tt_hashtags', label: 'Hashtags principales', type: 'textarea', placeholder: '#fyp #trend #nicho' },
                { id: 'tt_tendencias', label: '¿Sigues tendencias?', type: 'select', options: ['Siempre','A veces','Rara vez','Nunca'] },
            ]},
            { section: '🔴 TikTok Live', fields: [
                { id: 'tt_live_freq', label: 'Frecuencia de Lives', type: 'select', options: ['No hago','Diario','Semanal','Quincenal','Mensual'] },
                { id: 'tt_live_duracion', label: 'Duración promedio (min)', type: 'number', placeholder: '60' },
                { id: 'tt_live_viewers', label: 'Viewers concurrentes promedio', type: 'number', placeholder: '100' },
                { id: 'tt_live_interaccion', label: 'Nivel de interacción en Live', type: 'select', options: ['Alto','Medio','Bajo'] },
                { id: 'tt_live_regalos', label: '¿Recibes regalos/coins?', type: 'select', options: ['Sí, frecuentemente','A veces','No'] },
            ]},
        ]
    },
    facebook: {
        id: 'facebook', name: 'Facebook', icon: '👤',
        color: '#1877F2', desc: 'Posts, Stories, Reels, Grupos',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'fb_url', label: 'URL de página/perfil', type: 'text', placeholder: 'facebook.com/tupagina', required: true },
                { id: 'fb_tipo', label: 'Tipo de cuenta', type: 'select', options: ['Página de negocio','Perfil personal','Grupo'] },
                { id: 'fb_objetivo', label: 'Objetivo principal', type: 'select', options: ['Branding','Ventas','Leads','Comunidad','Tráfico web'] },
                { id: 'fb_seguidores', label: 'Seguidores/Miembros', type: 'number', placeholder: '5000' },
            ]},
            { section: '📊 Métricas y Contenido', fields: [
                { id: 'fb_frecuencia', label: 'Posts/semana', type: 'number', placeholder: '5' },
                { id: 'fb_engagement', label: 'Engagement promedio (%)', type: 'number', placeholder: '2', step: '0.1' },
                { id: 'fb_reach', label: 'Alcance promedio', type: 'number', placeholder: '3000' },
                { id: 'fb_stories', label: '¿Usas Stories?', type: 'select', options: ['Sí, diario','A veces','No'] },
                { id: 'fb_reels', label: '¿Usas Reels?', type: 'select', options: ['Sí, frecuente','A veces','No'] },
                { id: 'fb_cta', label: 'CTA principal en posts', type: 'text', placeholder: 'Ej: Link en bio, Compra ahora' },
                { id: 'fb_ads', label: '¿Campañas pagadas?', type: 'select', options: ['No','Sí, actualmente','Sí, en el pasado'] },
            ]},
        ]
    },
    youtube: {
        id: 'youtube', name: 'YouTube', icon: '▶️',
        color: '#FF0000', desc: 'Videos largos + Shorts',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'yt_url', label: 'URL del canal', type: 'text', placeholder: 'youtube.com/@tucanal', required: true },
                { id: 'yt_objetivo', label: 'Objetivo principal', type: 'select', options: ['Monetización','Branding','Educación','Entretenimiento','Leads'] },
                { id: 'yt_nicho', label: 'Nicho', type: 'text', placeholder: 'Ej: Tech, Cocina, Gaming' },
                { id: 'yt_suscriptores', label: 'Suscriptores', type: 'number', placeholder: '10000' },
            ]},
            { section: '📊 Videos Largos', fields: [
                { id: 'yt_frecuencia', label: 'Videos/mes', type: 'number', placeholder: '4' },
                { id: 'yt_duracion', label: 'Duración promedio (min)', type: 'number', placeholder: '15' },
                { id: 'yt_views', label: 'Views promedio por video', type: 'number', placeholder: '5000' },
                { id: 'yt_engagement', label: 'Engagement (likes+comments/views %)', type: 'number', placeholder: '4', step: '0.1' },
                { id: 'yt_miniaturas', label: 'Calidad de miniaturas', type: 'select', options: ['Profesionales','Aceptables','Básicas','Sin personalizar'] },
                { id: 'yt_seo', label: '¿Optimizas títulos/descripciones?', type: 'select', options: ['Sí, siempre','A veces','No'] },
            ]},
            { section: '📱 Shorts', fields: [
                { id: 'yt_shorts', label: '¿Publicas Shorts?', type: 'select', options: ['Sí, frecuente','A veces','No'] },
                { id: 'yt_shorts_freq', label: 'Shorts/semana', type: 'number', placeholder: '3' },
                { id: 'yt_shorts_views', label: 'Views promedio Shorts', type: 'number', placeholder: '10000' },
            ]},
        ]
    },
    linkedin: {
        id: 'linkedin', name: 'LinkedIn', icon: '💼',
        color: '#0A66C2', desc: 'Publicaciones B2B, Networking',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'li_url', label: 'URL de perfil/empresa', type: 'text', placeholder: 'linkedin.com/in/tuusuario', required: true },
                { id: 'li_tipo', label: 'Tipo', type: 'select', options: ['Perfil personal','Página de empresa','Ambos'] },
                { id: 'li_objetivo', label: 'Objetivo', type: 'select', options: ['Networking','Leads B2B','Employer branding','Thought leadership','Ventas'] },
                { id: 'li_conexiones', label: 'Conexiones/Seguidores', type: 'number', placeholder: '2000' },
            ]},
            { section: '📊 Contenido y Engagement', fields: [
                { id: 'li_frecuencia', label: 'Posts/semana', type: 'number', placeholder: '3' },
                { id: 'li_engagement', label: 'Engagement promedio (%)', type: 'number', placeholder: '3', step: '0.1' },
                { id: 'li_tipo_contenido', label: 'Tipo de contenido principal', type: 'select', options: ['Texto','Carruseles','Videos','Artículos','Mix'] },
                { id: 'li_cta', label: 'CTA habitual', type: 'text', placeholder: 'Ej: Agenda una reunión, Descarga el PDF' },
                { id: 'li_branding', label: 'Coherencia de branding', type: 'select', options: ['Alta','Media','Baja'] },
            ]},
        ]
    },
    twitter: {
        id: 'twitter', name: 'X (Twitter)', icon: '𝕏',
        color: '#1DA1F2', desc: 'Tweets, Hilos, Spaces',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'tw_url', label: 'URL / @usuario', type: 'text', placeholder: '@tumarca', required: true },
                { id: 'tw_objetivo', label: 'Objetivo', type: 'select', options: ['Branding','Comunidad','Atención al cliente','Thought leadership','Tráfico'] },
                { id: 'tw_seguidores', label: 'Seguidores', type: 'number', placeholder: '5000' },
            ]},
            { section: '📊 Contenido y Engagement', fields: [
                { id: 'tw_frecuencia', label: 'Tweets/día', type: 'number', placeholder: '3' },
                { id: 'tw_engagement', label: 'Engagement promedio (%)', type: 'number', placeholder: '2', step: '0.1' },
                { id: 'tw_hilos', label: '¿Publicas hilos?', type: 'select', options: ['Sí, frecuente','A veces','No'] },
                { id: 'tw_hashtags', label: 'Hashtags principales', type: 'textarea', placeholder: '#tumarca #tendencia' },
                { id: 'tw_retweets', label: 'Retweets promedio', type: 'number', placeholder: '20' },
                { id: 'tw_cta', label: 'CTA habitual', type: 'text', placeholder: 'Ej: Link en perfil' },
            ]},
        ]
    },
    pinterest: {
        id: 'pinterest', name: 'Pinterest', icon: '📌',
        color: '#E60023', desc: 'Pins, Tableros, SEO visual',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'pi_url', label: 'URL / usuario', type: 'text', placeholder: 'pinterest.com/tumarca', required: true },
                { id: 'pi_objetivo', label: 'Objetivo', type: 'select', options: ['Tráfico web','Ventas','Branding','Inspiración'] },
                { id: 'pi_seguidores', label: 'Seguidores', type: 'number', placeholder: '1000' },
            ]},
            { section: '📊 Contenido', fields: [
                { id: 'pi_tableros', label: 'Número de tableros', type: 'number', placeholder: '15' },
                { id: 'pi_pins_mes', label: 'Pins nuevos/mes', type: 'number', placeholder: '30' },
                { id: 'pi_engagement', label: 'Engagement promedio (%)', type: 'number', placeholder: '1.5', step: '0.1' },
                { id: 'pi_seo', label: '¿Optimizas SEO en pins?', type: 'select', options: ['Sí','A veces','No'] },
                { id: 'pi_calidad', label: 'Calidad visual de pins', type: 'select', options: ['Profesional','Aceptable','Básica'] },
            ]},
        ]
    },
    twitch: {
        id: 'twitch', name: 'Twitch', icon: '🟣',
        color: '#9146FF', desc: 'Streaming, Clips, Comunidad',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'twi_url', label: 'URL / usuario', type: 'text', placeholder: 'twitch.tv/tucanal', required: true },
                { id: 'twi_categoria', label: 'Categoría principal', type: 'text', placeholder: 'Ej: Just Chatting, Gaming, IRL' },
                { id: 'twi_seguidores', label: 'Seguidores', type: 'number', placeholder: '500' },
                { id: 'twi_subs', label: 'Suscriptores', type: 'number', placeholder: '50' },
            ]},
            { section: '🎮 Streaming', fields: [
                { id: 'twi_horario', label: 'Horario de streaming', type: 'text', placeholder: 'Ej: Lun-Vie 8pm-11pm' },
                { id: 'twi_frecuencia', label: 'Streams/semana', type: 'number', placeholder: '4' },
                { id: 'twi_duracion', label: 'Duración promedio (horas)', type: 'number', placeholder: '3' },
                { id: 'twi_viewers', label: 'Viewers concurrentes promedio', type: 'number', placeholder: '30' },
                { id: 'twi_chat', label: 'Interacción de chat', type: 'select', options: ['Muy activo','Activo','Moderado','Bajo'] },
                { id: 'twi_clips', label: 'Clips destacados/mes', type: 'number', placeholder: '5' },
                { id: 'twi_alertas', label: '¿Usas alertas/overlays?', type: 'select', options: ['Sí, profesionales','Sí, básicos','No'] },
            ]},
        ]
    },
    kick: {
        id: 'kick', name: 'Kick', icon: '🟢',
        color: '#53FC18', desc: 'Streaming alternativo',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'ki_url', label: 'URL / usuario', type: 'text', placeholder: 'kick.com/tucanal', required: true },
                { id: 'ki_categoria', label: 'Categoría principal', type: 'text', placeholder: 'Ej: Just Chatting, Gaming' },
                { id: 'ki_seguidores', label: 'Seguidores', type: 'number', placeholder: '200' },
                { id: 'ki_subs', label: 'Suscriptores', type: 'number', placeholder: '20' },
            ]},
            { section: '🎮 Streaming', fields: [
                { id: 'ki_horario', label: 'Horario de streaming', type: 'text', placeholder: 'Ej: Fines de semana 9pm' },
                { id: 'ki_frecuencia', label: 'Streams/semana', type: 'number', placeholder: '3' },
                { id: 'ki_duracion', label: 'Duración promedio (horas)', type: 'number', placeholder: '3' },
                { id: 'ki_viewers', label: 'Viewers concurrentes', type: 'number', placeholder: '15' },
                { id: 'ki_chat', label: 'Interacción de chat', type: 'select', options: ['Muy activo','Activo','Moderado','Bajo'] },
            ]},
        ]
    },
    whatsapp: {
        id: 'whatsapp', name: 'WhatsApp Business', icon: '💬',
        color: '#25D366', desc: 'Catálogo, Mensajes automáticos',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'wa_numero', label: 'Número / Nombre de perfil', type: 'text', placeholder: '+51 999 999 999', required: true },
                { id: 'wa_objetivo', label: 'Objetivo', type: 'select', options: ['Ventas directas','Atención al cliente','Catálogo','Comunidad','Soporte'] },
            ]},
            { section: '⚙️ Configuración', fields: [
                { id: 'wa_perfil', label: 'Perfil completo', type: 'select', options: ['Sí, con foto y descripción','Parcial','No configurado'] },
                { id: 'wa_catalogo', label: '¿Catálogo activo?', type: 'select', options: ['Sí, actualizado','Sí, desactualizado','No'] },
                { id: 'wa_auto', label: 'Mensajes automáticos', type: 'select', options: ['Sí, bienvenida + ausencia','Solo bienvenida','No'] },
                { id: 'wa_respuestas', label: 'Respuestas rápidas configuradas', type: 'select', options: ['Sí, varias','Pocas','No'] },
                { id: 'wa_etiquetas', label: '¿Usas etiquetas?', type: 'select', options: ['Sí','No'] },
                { id: 'wa_enlaces', label: 'Link en redes sociales', type: 'select', options: ['Sí, en todas','En algunas','No'] },
            ]},
        ]
    },
    telegram: {
        id: 'telegram', name: 'Telegram', icon: '✈️',
        color: '#0088CC', desc: 'Canal, Grupo, Bot',
        fields: [
            { section: '📋 Información General', fields: [
                { id: 'tg_url', label: 'URL / @canal', type: 'text', placeholder: '@tucanal o t.me/tucanal', required: true },
                { id: 'tg_tipo', label: 'Tipo', type: 'select', options: ['Canal','Grupo','Ambos','Bot'] },
                { id: 'tg_objetivo', label: 'Objetivo', type: 'select', options: ['Comunidad','Noticias','Ventas','Soporte','Contenido exclusivo'] },
                { id: 'tg_miembros', label: 'Miembros/Suscriptores', type: 'number', placeholder: '500' },
            ]},
            { section: '📊 Contenido', fields: [
                { id: 'tg_frecuencia', label: 'Mensajes/semana', type: 'number', placeholder: '10' },
                { id: 'tg_engagement', label: 'Views promedio por mensaje', type: 'number', placeholder: '200' },
                { id: 'tg_tipo_contenido', label: 'Tipo de contenido', type: 'select', options: ['Texto','Multimedia','Links','Mix'] },
                { id: 'tg_bot', label: '¿Usas bot?', type: 'select', options: ['Sí','No'] },
                { id: 'tg_promocion', label: '¿Promocionas en otras redes?', type: 'select', options: ['Sí','A veces','No'] },
            ]},
        ]
    },
};
