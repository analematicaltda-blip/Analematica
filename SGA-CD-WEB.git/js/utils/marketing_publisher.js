/**
 * Marketing Publisher Utility - SGA-CD Social Media & Messaging Integration
 * SGA-CD Architecture - Dark Metallic Blue System (60-30-10)
 *
 * Integración con WhatsApp Cloud API / service.py, Instagram (Publora API) y TikTok
 * automatizando la conversión de planes por roles y la difusión de la oferta cultural y deportiva.
 */
(function() {
    if (window.SGAMarketingPublisher) return;

    class MarketingPublisher {
        constructor() {
            this.config = {
                whatsappWebhookUrl: '/api/v1/webhooks/whatsapp',
                marketingDraftsUrl: '/api/v1/marketing/drafts',
                defaultHashtags: ['#SGACD', '#DeporteColombia', '#CulturaColombia', '#FormacionIntegral']
            };
        }

        /**
         * Despacha plantillas de alertas de WhatsApp según el nivel del plan de suscripción seleccionado
         * @param {string} planRole - 'entidades', 'profesores' o 'alumnos_padres'
         * @param {object} details - Información de contexto del usuario o entidad
         */
        async dispatchPlanWhatsAppAlert(planRole, details = {}) {
            let templateName = "";
            let messageBody = "";

            if (planRole === 'entidades') {
                templateName = "conversion_nivel1_entidades";
                messageBody = `🏛️ *SGA-CD — Notificación de Alcance Corporativo*\n` +
                              `Hola. Se ha registrado una solicitud de interés para Entidades Públicas/Privadas (Nacional, Departamental o Municipal).\n` +
                              `📌 *Beneficios Activos:* Telemetría analítica territorial masiva, auditoría presupuestal en tiempo real e indicadores de metas gubernamentales.`;
            } else if (planRole === 'profesores') {
                templateName = "soporte_nivel2_profesores";
                messageBody = `🎓 *SGA-CD — Plan Profesional Instructores*\n` +
                              `Hola Instructor/Profesor. Tu plan incluye accesos rápidos para la gestión de Roster y control de asistencia offline PWA en tus Talleres Culturales y Disciplinas Deportivas.`;
            } else if (planRole === 'alumnos_padres') {
                templateName = "bienvenida_nivel3_alumnos_gratis";
                messageBody = `✨ *SGA-CD — Bienvenida a la Suscripción Estudiantil Costo 0*\n` +
                              `¡Felicidades! Tu acceso como Alumno o Acudiente es 100% GRATUITO. Ya puedes inscribirte a Disciplinas Deportivas y Talleres Culturales, consultar tu carnet digital y dar seguimiento a tu medallería.`;
            } else {
                templateName = "consulta_general_planes";
                messageBody = `SGA-CD — Consulta de Planes de Suscripción para la Plataforma Cultural y Deportiva.`;
            }

            const payload = {
                event: 'plan_interaction',
                planRole: planRole,
                templateName: templateName,
                data: {
                    messageBody: messageBody,
                    timestamp: new Date().toISOString(),
                    entityLevel: details.entityLevel || 'municipal_departamental',
                    taxonomy: {
                        deportes: "Disciplinas Deportivas",
                        cultura: "Talleres / Modalidades (Danza: Joropo/Llanera, Salsa, Vallenato | Instrumentos: Guitarra, Arpa)"
                    }
                }
            };

            try {
                const response = await fetch(this.config.whatsappWebhookUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Silent-Error': 'true'
                    },
                    silent: true,
                    body: JSON.stringify(payload)
                });

                if (!response.ok && (response.status === 403 || response.status === 429)) {
                    if (window.SGAErrorHandler && typeof window.SGAErrorHandler.handleSecurityBreach === 'function') {
                        window.SGAErrorHandler.handleSecurityBreach(response.status);
                    }
                }

                console.log(`[SGAMarketingPublisher] WhatsApp alert dispatched successfully for [${planRole}]`);
                return response.ok;
            } catch (err) {
                console.warn(`[SGAMarketingPublisher] Error dispatching WhatsApp alert [STD-ERR-SECURITY-BREACH]:`, err.message);
                if (window.SGAErrorHandler && typeof window.SGAErrorHandler.handleSecurityBreach === 'function') {
                    window.SGAErrorHandler.handleSecurityBreach(503);
                }
                return false;
            }
        }

        /**
         * Procesa solicitudes de conversión para Entidades Públicas o Privadas (Nacional, Departamental o Municipal)
         * en segundo plano sin bloquear la interfaz de usuario.
         * @param {object} entityDetails - Detalles de la entidad solicitante
         */
        async processPartnerConversion(entityDetails = {}) {
            setTimeout(async () => {
                try {
                    await this.dispatchPlanWhatsAppAlert('entidades', entityDetails);
                    await this.captureAndDraftHook({
                        type: 'instagram',
                        title: entityDetails.entityName || 'Solicitud Entidad Aliada',
                        planType: 'Nivel 1 Corporativo Entidades',
                        targetRegion: entityDetails.entityLevel || 'Nacional / Departamental / Municipal'
                    });
                    console.log('[SGAMarketingPublisher] Conversión de aliado procesada exitosamente en segundo plano.');
                } catch (err) {
                    console.warn('[SGAMarketingPublisher] Excepción en segundo plano [STD-ERR-SECURITY-BREACH]:', err.message);
                }
            }, 0);
        }

        /**
         * Captura eventos y genera borradores de ganchos para Instagram (Publora) y TikTok
         */
        async captureAndDraftHook(options = {}) {
            const {
                type = 'instagram',
                title = 'Plan Institucional SGA-CD',
                disciplineOrTaller = 'Disciplinas Deportivas y Talleres Culturales',
                planType = 'Suscripción Estudiantil Costo 0',
                targetRegion = 'Nacional / Departamental / Municipal'
            } = options;

            const hashtags = [...this.config.defaultHashtags, `#${disciplineOrTaller.replace(/\s+/g, '')}`];

            const igCaption = `🚀 *TRANSFORMACIÓN DIGITAL EN DEPORTES Y CULTURA*\n\n` +
                `Presentamos el plan ${planType} de la suite SGA-CD en ${targetRegion}.\n\n` +
                `🏆 Optimización de presupuestos gubernamentales, control de asistencia offline PWA y fichas atléticas/artísticas en tiempo real.\n\n` +
                `📌 Inscríbete o solicita tu acreditación hoy mismo en la plataforma oficial.\n\n` +
                `${hashtags.join(' ')}`;

            const ttHookScript = {
                spokenHook: `¡Atención ${targetRegion}! Descubre el plan ${planType} para escuelas deportivas y talleres culturales.`,
                onScreenText: `🔥 PLAN ${planType.toUpperCase()}: REGISTRO ABIERTO`,
                durationSeconds: 3,
                recommendedSound: 'Trending Upbeat Metallic Blue 2026',
                cta: 'Accede GRATIS a la Suscripción Estudiantil'
            };

            const payload = {
                platform: type === 'tiktok' ? 'tiktok' : 'instagram',
                draft: {
                    title: title,
                    igCaption: igCaption,
                    ttHookScript: ttHookScript,
                    status: 'draft_created',
                    timestamp: new Date().toISOString()
                }
            };

            try {
                if (window.fetch) {
                    await window.fetch(this.config.marketingDraftsUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Silent-Error': 'true'
                        },
                        silent: true,
                        body: JSON.stringify(payload)
                    });
                }
            } catch (e) {
                console.warn('[SGAMarketingPublisher] Draft submission handled gracefully [STD-ERR-SECURITY-BREACH]:', e.message);
            }

            return payload;
        }
    }

    window.SGAMarketingPublisher = new MarketingPublisher();

    document.addEventListener('DOMContentLoaded', () => {
        // Escuchar clics en botones de acción o planes para activar la difusión
        document.querySelectorAll('.plan-button, .btn-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const planCard = btn.closest('.plan-card');
                const planTitle = planCard ? planCard.querySelector('h3')?.innerText : 'Plan General SGA-CD';
                let role = 'alumnos_padres';
                if (planTitle.includes('Corporativo') || planTitle.includes('Gubernamental')) role = 'entidades';
                else if (planTitle.includes('Instructores') || planTitle.includes('Profesional')) role = 'profesores';

                window.SGAMarketingPublisher.dispatchPlanWhatsAppAlert(role, { planTitle });
                window.SGAMarketingPublisher.captureAndDraftHook({
                    type: 'instagram',
                    title: planTitle,
                    planType: planTitle
                });
            });
        });
    });
})();
