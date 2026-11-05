/**
 * SEO & Marketing Engine - SGA-CD Multi-Entity & Role-Segmented Analytics
 * SGA-CD Architecture - Dark Metallic Blue System
 *
 * Inyección dinámica de metadatos SEO y JSON-LD estructurados para:
 * - Entidades B2B vs Profesores/Estudiantes B2C.
 * - Rutas e interfaces internas de Disciplinas Deportivas y Modalidades Culturales / Talleres.
 */
window.SGASEOOptimizer = (function() {
    const SCHEMAS = {
        organization: {
            "@context": "https://schema.org",
            "@type": "EducationalOrganization",
            "name": "SGA-CD — Sistema de Gestión Cultural y Deportiva",
            "alternateName": "Plataforma de Formación e Impacto Social SGA-CD",
            "url": "https://sga-cd.gov.co",
            "logo": "https://sga-cd.gov.co/assets/logo-sga.png",
            "description": "Plataforma oficial para la administración, fiscalización y seguimiento de convenios institucionales en Disciplinas Deportivas, Modalidades Culturales y Talleres de formación.",
            "areaServed": [
                {
                    "@type": "AdministrativeArea",
                    "name": "Nivel Nacional (Ministerios de Cultura y Deporte)"
                },
                {
                    "@type": "AdministrativeArea",
                    "name": "Nivel Departamental (Gobernaciones e Institutos)"
                },
                {
                    "@type": "AdministrativeArea",
                    "name": "Nivel Municipal (Alcaldías y Entes Descentralizados)"
                }
            ],
            "offers": [
                {
                    "@type": "Offer",
                    "category": "Disciplinas Deportivas",
                    "description": "Gestión de torneos, entrenamientos y fichas atléticas de rendimiento en Taekwondo, Fútbol, Baloncesto, Natación y más."
                },
                {
                    "@type": "Offer",
                    "category": "Modalidades Culturales y Talleres",
                    "description": "Formación en Danza (Joropo/Llanera, Salsa, Vallenato) e Instrumentos (Guitarra, Arpa)."
                }
            ]
        },
        governmentService: {
            "@context": "https://schema.org",
            "@type": "GovernmentService",
            "name": "Gestión e Impacto Social Cultural y Deportivo SGA-CD",
            "serviceType": "Administración de Convenios e Inscripciones Institucionales",
            "provider": {
                "@type": "Organization",
                "name": "SGA-CD Colombia"
            },
            "areaServed": "Colombia",
            "audience": {
                "@type": "Audience",
                "audienceType": "Entidades Públicas, Gobernaciones, Alcaldías, Instructores y Estudiantes"
            }
        }
    };

    function injectJSONLD(customSchemas) {
        let scriptTag = document.getElementById('sga-jsonld-schema');
        if (!scriptTag) {
            scriptTag = document.createElement('script');
            scriptTag.id = 'sga-jsonld-schema';
            scriptTag.type = 'application/ld+json';
            document.head.appendChild(scriptTag);
        }

        const schemasToInject = customSchemas || [SCHEMAS.organization, SCHEMAS.governmentService];
        scriptTag.textContent = JSON.stringify(schemasToInject, null, 2);
    }

    function updateRoleMetadata(role) {
        const metaTitle = document.querySelector('meta[property="og:title"]') || createMeta('og:title', 'property');
        const metaDesc = document.querySelector('meta[property="og:description"]') || createMeta('og:description', 'property');
        const metaTwTitle = document.querySelector('meta[name="twitter:title"]') || createMeta('twitter:title', 'name');
        const metaTwDesc = document.querySelector('meta[name="twitter:description"]') || createMeta('twitter:description', 'name');

        let title = "SGA-CD — Plataforma de Gestión Cultural y Deportiva";
        let desc = "Sistema unificado para el seguimiento de presupuestos institucionales, asistencia y formación en disciplinas deportivas y modalidades culturales.";

        if (role === 'entidad') {
            title = "SGA-CD B2B — Control Presupuestal e Impacto Social para Entidades";
            desc = "Auditoría en tiempo real, gestión de metas gubernamentales e indicadores de convenios para Ministerios, Gobernaciones y Alcaldías.";
        } else if (role === 'profesor_estudiante') {
            title = "SGA-CD — Portal de Formación en Deportes y Talleres Culturales";
            desc = "Inscripción en línea, control de asistencia offline PWA y seguimiento académico en danza (joropo, salsa, vallenato) e instrumentos.";
        }

        metaTitle.setAttribute('content', title);
        metaDesc.setAttribute('content', desc);
        metaTwTitle.setAttribute('content', title);
        metaTwDesc.setAttribute('content', desc);
        document.title = title;
    }

    /**
     * Inyección Dinámica de SEO para Páginas/Vistas Internas de Actividades
     * @param {string} category - 'deportes' o 'cultura'
     * @param {string} activityName - Nombre de la Disciplina o Taller (ej. Taekwondo, Joropo, Guitarra)
     */
    function updateActivityMetadata(category, activityName) {
        if (!activityName) return;

        const isDeporte = category === 'deportes' || category === 'deporte';
        const cleanName = activityName.trim();

        let title = "";
        let desc = "";
        let activitySchema = {};

        if (isDeporte) {
            title = `Disciplina Deportiva: ${cleanName} — Formación e Impacto Social SGA-CD`;
            desc = `Inscripciones abiertas, entrenamiento especializado y ficha técnica atlética en ${cleanName}. Programa oficial avalado para convenios municipales y departamentales.`;

            activitySchema = {
                "@context": "https://schema.org",
                "@type": "SportsEvent",
                "name": `Programa de Formación en Disciplina Deportiva: ${cleanName}`,
                "description": desc,
                "organizer": SCHEMAS.organization,
                "sport": cleanName,
                "location": {
                    "@type": "Place",
                    "name": "Escenario Deportivo Municipal / Departamental SGA-CD",
                    "address": {
                        "@type": "PostalAddress",
                        "addressCountry": "CO"
                    }
                }
            };
        } else {
            title = `Taller Cultural / Modalidad: ${cleanName} — Escuela de Formación SGA-CD`;
            desc = `Aprende y perfecciona ${cleanName} en la Escuela de Formación Cultural SGA-CD. Cupos disponibles para niños, jóvenes y adultos.`;

            activitySchema = {
                "@context": "https://schema.org",
                "@type": "Course",
                "name": `Taller Cultural de ${cleanName}`,
                "description": desc,
                "provider": SCHEMAS.organization,
                "hasCourseInstance": {
                    "@type": "CourseInstance",
                    "courseMode": "Blended / Presencial Offline Sync",
                    "instructor": "Instructor Calificado SGA-CD"
                }
            };
        }

        // Actualizar Meta Tags
        const metaOgTitle = document.querySelector('meta[property="og:title"]') || createMeta('og:title', 'property');
        const metaOgDesc = document.querySelector('meta[property="og:description"]') || createMeta('og:description', 'property');
        const metaTwTitle = document.querySelector('meta[name="twitter:title"]') || createMeta('twitter:title', 'name');
        const metaTwDesc = document.querySelector('meta[name="twitter:description"]') || createMeta('twitter:description', 'name');

        metaOgTitle.setAttribute('content', title);
        metaOgDesc.setAttribute('content', desc);
        metaTwTitle.setAttribute('content', title);
        metaTwDesc.setAttribute('content', desc);
        document.title = title;

        // Inyectar esquema estructurado específico de la actividad
        injectJSONLD([SCHEMAS.organization, SCHEMAS.governmentService, activitySchema]);

        console.log(`[SEO Optimizer] Metadata e Inyección JSON-LD actualizada para [${isDeporte ? 'Deporte' : 'Cultura'}]: ${cleanName}`);
    }

    function createMeta(attrValue, attrType = 'name') {
        const meta = document.createElement('meta');
        meta.setAttribute(attrType, attrValue);
        document.head.appendChild(meta);
        return meta;
    }

    function setupTelemetry() {
        window.trackConversionEvent = function(eventName, category, metadata = {}) {
            const safeData = {
                event: String(eventName),
                category: String(category),
                timestamp: new Date().toISOString(),
                referrer: document.referrer ? 'external_partner' : 'direct',
                entityLevel: metadata.entityLevel || 'municipal_departamental'
            };

            const payload = JSON.stringify(safeData);
            if (navigator.sendBeacon && window.location.protocol.startsWith('http')) {
                try {
                    navigator.sendBeacon('/api/v1/telemetry/event', payload);
                } catch (e) {
                    // Fallback
                }
            } else {
                fetch('/api/v1/telemetry/event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payload,
                    keepalive: true
                }).catch(() => {});
            }
            console.log('[SGA Telemetry Event Captured]:', safeData);
        };
    }

    /**
     * Aplica la política de privacidad de indexación basada en la ruta actual o vista.
     * Rutas privadas (app.html, paneles internos y paneles de los 12 roles) reciben noindex, nofollow.
     */
    function applyPrivacyRobotsPolicy() {
        let metaRobots = document.querySelector('meta[name="robots"]');
        if (!metaRobots) {
            metaRobots = createMeta('robots', 'name');
        }

        const path = window.location.pathname.toLowerCase();
        const hash = window.location.hash.toLowerCase();
        const search = window.location.search.toLowerCase();

        const privateKeywords = [
            'app.html', '/admin', '/dashboard', 'admin_general', 'admin_empresa',
            'jefe_area', 'profesional_area', 'tecnico_area', 'coordinador',
            'profesor', 'alumno', 'padre_acudiente', 'jefe_escenarios',
            'jefe_almacen', 'almacenista'
        ];

        const isPrivateArea = privateKeywords.some(kw => path.includes(kw) || hash.includes(kw) || search.includes(kw)) ||
                              document.getElementById('app-content') !== null ||
                              document.querySelector('.app-layout') !== null;

        if (isPrivateArea) {
            metaRobots.setAttribute('content', 'noindex, nofollow');
            console.log('[SEO Optimizer] Límite de Privacidad Aplicado: <meta name="robots" content="noindex, nofollow">');
        } else {
            metaRobots.setAttribute('content', 'index, follow');
        }
    }

    return {
        init: function() {
            injectJSONLD();
            setupTelemetry();
            applyPrivacyRobotsPolicy();

            const params = new URLSearchParams(window.location.search);
            const role = params.get('role') || 'general';
            updateRoleMetadata(role);

            // Detectar si la URL incluye parámetros dinámicos de actividad (?deporte=Taekwondo o ?taller=Joropo)
            const deporte = params.get('deporte') || params.get('disciplina');
            const taller = params.get('taller') || params.get('modalidad');

            if (deporte) {
                updateActivityMetadata('deportes', deporte);
            } else if (taller) {
                updateActivityMetadata('cultura', taller);
            }
        },
        updateRoleMetadata: updateRoleMetadata,
        updateActivityMetadata: updateActivityMetadata,
        applyPrivacyRobotsPolicy: applyPrivacyRobotsPolicy
    };
})();

document.addEventListener('DOMContentLoaded', function() {
    window.SGASEOOptimizer.init();
});
