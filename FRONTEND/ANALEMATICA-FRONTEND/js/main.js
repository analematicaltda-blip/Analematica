/**
 * Analemática - Interactividad, Validaciones y Renderizado Dinámico 100% Editable
 * Ecosistema de Presentación Institucional y Enrutamiento a SGA-CD
 */

const STORAGE_KEY = 'analematica_landing_config';
const LEADS_KEY = 'analematica_leads_data';
const safeTextHTML=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

// Función para aplicar dinámicamente cualquier personalización del panel de administrador
function applyDynamicLandingContent(config) {
    if (!config) return;

    // 1. Header & Brand
    if (config.header) {
        const brandNames = document.querySelectorAll('.brand-name');
        brandNames.forEach(el => el.textContent = config.header.brand_name || 'ANALEMÁTICA');

        const brandTags = document.querySelectorAll('.brand-tag');
        brandTags.forEach(el => el.textContent = config.header.brand_tag || 'INGENIERÍA MODULAR');

        const navCta = document.querySelector('.nav-cta');
        if (navCta && config.header.nav_cta_text) {
            navCta.textContent = config.header.nav_cta_text;
            if (config.header.nav_cta_href) navCta.setAttribute('href', config.header.nav_cta_href);
        }
    }

    // 2. Hero Section
    if (config.hero) {
        const heroBadge = document.querySelector('.hero-badge .badge-text');
        if (heroBadge && config.hero.badge) heroBadge.textContent = config.hero.badge;

        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle && config.hero.title) heroTitle.innerHTML = config.hero.title;

        const heroSubtitle = document.querySelector('.hero-subtitle');
        if (heroSubtitle && config.hero.subtitle) heroSubtitle.textContent = config.hero.subtitle;

        const heroBtnPrimary = document.getElementById('heroCtaBtn');
        if (heroBtnPrimary && config.hero.btn_primary) {
            heroBtnPrimary.innerHTML = `${safeTextHTML(config.hero.btn_primary)} <svg class="btn-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>`;
        }

        const heroMetrics = document.querySelectorAll('.hero-metrics .metric-item');
        if (heroMetrics.length && config.hero.metrics) {
            config.hero.metrics.forEach((m, idx) => {
                if (heroMetrics[idx]) {
                    const valEl = heroMetrics[idx].querySelector('.metric-value');
                    const lblEl = heroMetrics[idx].querySelector('.metric-label');
                    if (valEl && m.value) valEl.textContent = m.value;
                    if (lblEl && m.label) lblEl.textContent = m.label;
                }
            });
        }

        const cardBadge = document.querySelector('.badge-micro');
        if (cardBadge && config.hero.card_badge) cardBadge.textContent = config.hero.card_badge;

        const cardLegend = document.querySelector('.hero-card-legend');
        if (cardLegend && config.hero.card_legend) cardLegend.textContent = config.hero.card_legend;
    }

    // 3. El Desafío
    if (config.desafio) {
        const sec = document.getElementById('desafio');
        if (sec) {
            const tag = sec.querySelector('.section-tag');
            if (tag && config.desafio.tag) tag.textContent = config.desafio.tag;

            const title = sec.querySelector('.section-title');
            if (title && config.desafio.title) title.textContent = config.desafio.title;

            const desc = sec.querySelector('.section-description');
            if (desc && config.desafio.desc) desc.textContent = config.desafio.desc;

            const cards = sec.querySelectorAll('.pain-card');
            if (config.desafio.cards) {
                config.desafio.cards.forEach((c, idx) => {
                    if (cards[idx]) {
                        const ct = cards[idx].querySelector('.card-title');
                        const cd = cards[idx].querySelector('.card-text');
                        if (ct && c.title) ct.textContent = c.title;
                        if (cd && c.desc) cd.textContent = c.desc;
                    }
                });
            }
        }
    }

    // 4. Filosofía, Misión & Visión
    if (config.filosofia) {
        const filoSec = document.getElementById('filosofia');
        if (filoSec) {
            const tag = filoSec.querySelector('.section-tag');
            if (tag && config.filosofia.tag) tag.textContent = config.filosofia.tag;

            const title = filoSec.querySelector('.section-title');
            if (title && config.filosofia.title) title.textContent = config.filosofia.title;

            const desc = filoSec.querySelector('.section-description.lead');
            if (desc && config.filosofia.desc) desc.textContent = config.filosofia.desc;

            const pillars = filoSec.querySelectorAll('.pillar-item');
            if (config.filosofia.pillars) {
                config.filosofia.pillars.forEach((p, idx) => {
                    if (pillars[idx]) {
                        const pt = pillars[idx].querySelector('.pillar-title');
                        const pd = pillars[idx].querySelector('.pillar-desc');
                        if (pt && p.title) pt.textContent = p.title;
                        if (pd && p.desc) pd.textContent = p.desc;
                    }
                });
            }

            const caption = filoSec.querySelector('.diagram-caption');
            if (caption && config.filosofia.diagram_caption) caption.textContent = config.filosofia.diagram_caption;
        }
    }

    // Misión & Visión
    if (config.mision) {
        const mvGrid = document.getElementById('mision-vision');
        if (mvGrid) {
            const mvCards = mvGrid.querySelectorAll('.mv-card');
            if (mvCards[0]) {
                const mt = mvCards[0].querySelector('.mv-title');
                const md = mvCards[0].querySelector('.mv-text');
                if (mt && config.mision.title) mt.textContent = config.mision.title;
                if (md && config.mision.text) md.textContent = config.mision.text;
            }
            if (mvCards[1] && config.vision) {
                const vt = mvCards[1].querySelector('.mv-title');
                const vd = mvCards[1].querySelector('.mv-text');
                if (vt && config.vision.title) vt.textContent = config.vision.title;
                if (vd && config.vision.text) vd.textContent = config.vision.text;
            }
        }
    }

    // 5. Verticales & Módulo SGA-CD
    if (config.verticales) {
        const vertSec = document.getElementById('verticales');
        if (vertSec) {
            const tag = vertSec.querySelector('.section-tag');
            if (tag && config.verticales.tag) tag.textContent = config.verticales.tag;

            const title = vertSec.querySelector('.section-title');
            if (title && config.verticales.title) title.textContent = config.verticales.title;

            const desc = vertSec.querySelector('.section-description');
            if (desc && config.verticales.desc) desc.textContent = config.verticales.desc;

            const cards = vertSec.querySelectorAll('.vertical-card:not(.featured-sgacd)');
            if (config.verticales.cards) {
                config.verticales.cards.forEach((c, idx) => {
                    if (cards[idx]) {
                        const ct = cards[idx].querySelector('.card-title');
                        const cd = cards[idx].querySelector('.card-text');
                        if (ct && c.title) ct.textContent = c.title;
                        if (cd && c.desc) cd.textContent = c.desc;
                    }
                });
            }

            const sgaCard = vertSec.querySelector('.featured-sgacd');
            if (sgaCard && config.verticales.sgacd) {
                const st = sgaCard.querySelector('.featured-title');
                const sd = sgaCard.querySelector('.card-text');
                const sn = sgaCard.querySelector('.redirect-notice span');
                const sb = sgaCard.querySelector('#btnVisitarSgaCd');
                if (st && config.verticales.sgacd.title) st.textContent = config.verticales.sgacd.title;
                if (sd && config.verticales.sgacd.desc) sd.textContent = config.verticales.sgacd.desc;
                if (sn && config.verticales.sgacd.notice) sn.textContent = config.verticales.sgacd.notice;
                if (sb) {
                    if (config.verticales.sgacd.btn_text) sb.textContent = config.verticales.sgacd.btn_text;
                    if (config.verticales.sgacd.url) sb.setAttribute('href', config.verticales.sgacd.url);
                }
            }
        }
    }

    // 6. ADN Tecnológico
    if (config.adn) {
        const adnSec = document.getElementById('adn-tecnologico');
        if (adnSec) {
            const tag = adnSec.querySelector('.section-tag');
            if (tag && config.adn.tag) tag.textContent = config.adn.tag;

            const title = adnSec.querySelector('.section-title');
            if (title && config.adn.title) title.textContent = config.adn.title;

            const desc = adnSec.querySelector('.section-description');
            if (desc && config.adn.desc) desc.textContent = config.adn.desc;

            const cards = adnSec.querySelectorAll('.tech-card');
            if (config.adn.cards) {
                config.adn.cards.forEach((c, idx) => {
                    if (cards[idx]) {
                        const ct = cards[idx].querySelector('.card-title');
                        const cd = cards[idx].querySelector('.card-text');
                        if (ct && c.title) ct.textContent = c.title;
                        if (cd && c.desc) cd.textContent = c.desc;
                    }
                });
            }
        }
    }

    // 7. Impacto en el Ciudadano
    if (config.impacto) {
        const impSec = document.getElementById('impacto');
        if (impSec) {
            const tag = impSec.querySelector('.section-tag');
            if (tag && config.impacto.tag) tag.textContent = config.impacto.tag;

            const title = impSec.querySelector('.section-title');
            if (title && config.impacto.title) title.textContent = config.impacto.title;

            const desc = impSec.querySelector('.section-description');
            if (desc && config.impacto.desc) desc.textContent = config.impacto.desc;

            const cards = impSec.querySelectorAll('.impact-card');
            if (config.impacto.cards) {
                config.impacto.cards.forEach((c, idx) => {
                    if (cards[idx]) {
                        const cp = cards[idx].querySelector('.impact-metric-pill');
                        const ct = cards[idx].querySelector('.card-title');
                        const cd = cards[idx].querySelector('.card-text');
                        if (cp && c.pill) cp.textContent = c.pill;
                        if (ct && c.title) ct.textContent = c.title;
                        if (cd && c.desc) cd.textContent = c.desc;
                    }
                });
            }
        }
    }

    // 8. Contacto
    if (config.contacto) {
        const ctaSec = document.getElementById('contacto');
        if (ctaSec) {
            const tag = ctaSec.querySelector('.section-tag');
            if (tag && config.contacto.tag) tag.textContent = config.contacto.tag;

            const title = ctaSec.querySelector('.section-title');
            if (title && config.contacto.title) title.textContent = config.contacto.title;

            const desc = ctaSec.querySelector('.section-description');
            if (desc && config.contacto.desc) desc.textContent = config.contacto.desc;

            const btn = document.getElementById('submitFormBtn');
            if (btn && config.contacto.btn_text) {
                btn.innerHTML = `${safeTextHTML(config.contacto.btn_text)} <svg class="btn-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
            }

            const successText = document.querySelector('.feedback-text');
            if (successText && config.contacto.success_msg) successText.textContent = config.contacto.success_msg;
        }
    }

    // 9. Footer
    if (config.footer) {
        const bio = document.querySelector('.footer-bio');
        if (bio && config.footer.bio) bio.textContent = config.footer.bio;

        const copy = document.querySelector('.copyright-text');
        if (copy && config.footer.copyright) copy.textContent = config.footer.copyright;

        const statusEl = document.querySelector('.system-status');
        if (statusEl && config.footer.status) {
            statusEl.innerHTML = `<span class="status-indicator"></span> ${safeTextHTML(config.footer.status)}`;
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    // 0. Aplicar contenido dinámico desde el panel de administrador
    AnaleConnection.request('/config').then(published=>applyDynamicLandingContent(published.config)).catch(()=>console.warn('Se muestra el contenido institucional original; configuración no disponible.'));

    // 1. Menú móvil
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mainNav = document.querySelector('.main-nav');

    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', () => {
            mainNav.classList.toggle('active');
            mobileMenuBtn.setAttribute('aria-expanded',String(mainNav.classList.contains('active')));
        });

        // Cerrar menú al hacer clic en un enlace
        const navLinks = mainNav.querySelectorAll('.nav-link, .nav-cta');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                mainNav.classList.remove('active');
                mobileMenuBtn.setAttribute('aria-expanded','false');
            });
        });
    }

    // 2. Formulario de Captura de Leads (Diagnóstico Técnico)
    const leadForm = document.getElementById('leadCaptureForm');
    const successBox = document.getElementById('formSuccessMessage');

    if (leadForm) {
        let pendingRequestId=null;
        leadForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            let isValid = true;

            const fields = [
                { id: 'nombreCompleto', errorId: 'error-nombre', validator: val => val.trim().length >= 3 },
                { id: 'entidadOrganizacion', errorId: 'error-entidad', validator: val => val.trim().length >= 2 },
                { id: 'correoInstitucional', errorId: 'error-correo', validator: val => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim()) },
                { id: 'telefonoContacto', errorId: 'error-telefono', validator: val => val.trim().length >= 7 }
            ];

            fields.forEach(field => {
                const input = document.getElementById(field.id);
                const parent = input ? input.closest('.form-group') : null;

                if (!input || !field.validator(input.value)) {
                    isValid = false;
                    if (parent) parent.classList.add('input-error');
                } else {
                    if (parent) parent.classList.remove('input-error');
                }
            });

            if (isValid) {
                const submitBtn = document.getElementById('submitFormBtn');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Procesando Diagnóstico...';
                }

                const errorBox=document.getElementById('formErrorMessage');
                if(errorBox)errorBox.hidden=true;
                if(successBox)successBox.classList.add('hidden');
                pendingRequestId=pendingRequestId||crypto.randomUUID();
                try {
                    await AnaleConnection.request('/inquiries',{method:'POST',body:JSON.stringify({request_id:pendingRequestId,nombre:document.getElementById('nombreCompleto').value.trim(),entidad:document.getElementById('entidadOrganizacion').value.trim(),correo:document.getElementById('correoInstitucional').value.trim(),telefono:document.getElementById('telefonoContacto').value.trim(),consent:document.getElementById('contactConsent').checked,website:document.getElementById('contactWebsite').value})});
                    if(successBox){successBox.classList.remove('hidden');successBox.scrollIntoView({behavior:'smooth',block:'nearest'});}
                    leadForm.reset();pendingRequestId=null;
                } catch(error) {
                    if(errorBox){errorBox.hidden=false;errorBox.textContent=error.message;}
                } finally {if(submitBtn){submitBtn.disabled=false;submitBtn.textContent='Enviar Solicitud de Diagnóstico';}}

            }
        });

        // Limpieza de errores en tiempo real
        const inputs = leadForm.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                const parent = input.closest('.form-group');
                if (parent) parent.classList.remove('input-error');
            });
        });
    }

    // 3. Smooth scroll para anclas internas
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});
