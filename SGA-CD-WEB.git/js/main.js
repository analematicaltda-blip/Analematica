document.addEventListener('DOMContentLoaded', () => {

    // --- XSS Escaping Helper ---
    function sanitizeHTML(str) {
        if (!str) return '';
        const temp = document.createElement('div');
        temp.textContent = String(str);
        return temp.innerHTML;
    }

    // --- 1. Load Dynamic Content from API ---
    async function loadAndRenderContent() {
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/public/landing`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const settings = await response.json();

            // Inject Admin General Dynamic Settings to Landing Page
            if (settings.hero_title) {
                const titleEl = document.querySelector('#hero h1');
                if (titleEl) titleEl.textContent = settings.hero_title;
            }
            if (settings.hero_subtitle) {
                const subEl = document.querySelector('#hero p.lead');
                if (subEl) subEl.textContent = settings.hero_subtitle;
            }
            if (settings.hero_video_url) {
                const videoSource = document.querySelector('#hero-video-container video source');
                if (videoSource && settings.hero_video_url) {
                    videoSource.src = settings.hero_video_url;
                    const videoEl = document.querySelector('#hero-video-container video');
                    if (videoEl) videoEl.load();
                }
            }
            if (settings.carousel_slides_json && window.SGAModernCarousel) {
                try {
                    const parsedSlides = JSON.parse(settings.carousel_slides_json);
                    if (Array.isArray(parsedSlides) && parsedSlides.length > 0) {
                        window.SGAModernCarousel.init('modern-carousel-container', parsedSlides);
                    }
                } catch(e) {
                    console.warn('[Carousel Settings] Error parseando JSON de diapositivas:', e);
                }
            } else if (settings.carousel_urls && window.SGAModernCarousel) {
                const customUrls = settings.carousel_urls.split(',').map(u => u.trim()).filter(u => u.startsWith('http') || u.startsWith('assets/'));
                if (customUrls.length > 0) {
                    window.SGAModernCarousel.init('modern-carousel-container', customUrls);
                }
            }
            if (settings.plan_tier1_price) {
                const p1 = document.querySelector('#plan-tier1-price-display');
                if (p1) p1.textContent = `$${settings.plan_tier1_price}`;
            }

            renderFallbackContent();
            initializeGSAPAnimations();

        } catch (error) {
            console.warn("Using default fallback content for marketing page due to API offline state:", error);
            renderFallbackContent();
            initializeGSAPAnimations();
        }
    }

    function renderFallbackContent() {
        const defaultFeatures = [
            { titulo: "Gestión Roster Deportivo", descripcion: "Inscripciones a escuelas de formación, plantillas de torneos y acreditaciones digitales.", icono: "fa-solid fa-running" },
            { titulo: "Talleres Culturales", descripcion: "Inscripción a música, danza, teatro y control de asistencia para instructores y estudiantes.", icono: "fa-solid fa-masks-theater" },
            { titulo: "Diagnóstico Biométrico", descripcion: "Evaluación antropométrica, rendimiento físico y alertas preventivas de lesiones.", icono: "fa-solid fa-heart-pulse" },
            { titulo: "Reserva de Escenarios", descripcion: "Programación de canchas, coliseos y auditorios con control de aforo e inventario.", icono: "fa-solid fa-building-columns" },
            { titulo: "Gamificación & Logros", descripcion: "Insignias, cuadro de medallería y clasificaciones por rendimiento académico-deportivo.", icono: "fa-solid fa-award" },
            { titulo: "Multi-Inquilino Seguro", descripcion: "Aislamiento estricto de datos por empresa, seguridad JWT y derechos ARCO.", icono: "fa-solid fa-shield-halved" }
        ];

        // --- MATRIZ OFICIAL DE PLANES Y PRECIOS POR ROLES SGA-CD ---
        const defaultPlans = [
            {
                nombre: "Suscripción Estudiantil Costo 0",
                role_target: "alumnos_padres",
                precio_mensual: "0",
                precio_anual: "0",
                gratis_badge: true,
                descripcion: "Plan COMPLETAMENTE GRATUITO para Alumnos, Padres y Madres de Alumnos.",
                caracteristicas: '["Inscripción a Disciplinas Deportivas y Talleres", "Control de Asistencia Offline PWA", "Carnet Digital Estudiantil", "Seguimiento de Logros y Medallería", "Acceso Total Sin Costo"]',
                recomendado: false
            },
            {
                nombre: "Plan Profesional Instructores",
                role_target: "profesores",
                precio_mensual: "29",
                precio_anual: "290",
                gratis_badge: false,
                descripcion: "Plan intermedio optimizado para Profesores, Instructores y Entrenadores.",
                caracteristicas: '["Gestión de Roster y Plantillas", "Toma de Asistencia Georreferenciada", "Reportes de Desempeño y Rendimiento", "Sincronización Offline Instantánea", "Soporte Técnico Directo"]',
                recomendado: false
            },
            {
                nombre: "Plan Corporativo Gubernamental & Institucional",
                role_target: "entidades",
                precio_mensual: "299",
                precio_anual: "2990",
                gratis_badge: false,
                descripcion: "Para Entidades Públicas y Privadas (Nacional, Departamental y Municipal).",
                caracteristicas: '["Telemetría Analítica Territorial Masiva", "Auditoría Presupuestal en Tiempo Real", "Gestión de Metas de Convenios Institucionales", "Multi-Inquilino Dedicado con SLA 99.9%", "Integración de API & Certificación ARCO"]',
                recomendado: true
            }
        ];

        renderFeatures(defaultFeatures);
        renderPlans(defaultPlans);
        renderFaq([]);
        renderVideo("https://www.youtube.com/watch?v=dQw4w9WgXcQ");
        renderLaunchOffer("¡Invita a 10 instituciones o empresas y recibe 6 meses de licenciamiento completamente gratis!");
        renderFooter({
            nombre_empresa: "SGA-CD Inc.",
            mission: "Democratizar la gestión deportiva y cultural mediante soluciones tecnológicas de alto rendimiento.",
            vision: "Ser la plataforma estándar de administración atlética y artística en Latinoamérica.",
            email_contacto: "contacto@sga-cd.org",
            telefono_contacto: "+57 (601) 800-7422",
            direccion: "Calle 100 #11B-27, Bogotá, Colombia"
        });
    }

    // --- RENDER FUNCTIONS WITH SANITIZATION ---
    function renderFeatures(features) {
        const grid = document.getElementById('features-grid');
        if (!grid) return;
        grid.innerHTML = '';

        features.forEach((feature, index) => {
            const card = document.createElement('div');
            card.className = `feature-card ${index === 0 ? 'bento-highlight' : ''}`;
            const iconClass = feature.icono ? sanitizeHTML(feature.icono) : 'fa-solid fa-star';

            card.innerHTML = `
                <i class="${iconClass}"></i>
                <h3>${sanitizeHTML(feature.titulo)}</h3>
                <p>${sanitizeHTML(feature.descripcion)}</p>
            `;
            grid.appendChild(card);
        });
    }

    function renderVideo(videoUrl) {
        const container = document.getElementById('video-container');
        if (!container || !videoUrl) return;

        let videoId = '';
        if (videoUrl.includes('youtube.com/watch?v=')) {
            videoId = videoUrl.split('v=')[1].split('&')[0];
        } else if (videoUrl.includes('youtu.be/')) {
            videoId = videoUrl.split('youtu.be/')[1].split('?')[0];
        }

        if (videoId) {
            const cleanVideoId = sanitizeHTML(videoId);
            container.innerHTML = `
                <iframe
                    src="https://www.youtube-nocookie.com/embed/${cleanVideoId}"
                    title="Video Institucional SGA-CD"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen>
                </iframe>`;
        }
    }

    function renderPartners(partners) {
        const clientsGrid = document.getElementById('clients-grid');
        const testersGrid = document.getElementById('testers-grid');
        if (!clientsGrid || !testersGrid) return;

        clientsGrid.innerHTML = '';
        testersGrid.innerHTML = '';

        if (!partners || partners.length === 0) {
            clientsGrid.innerHTML = '<p style="color: var(--color-text-muted);">Academia Central de Deportes, Instituto de Cultura Municipal, Universidad del Deporte</p>';
            return;
        }

        partners.forEach(partner => {
            const partnerLogo = document.createElement('div');
            partnerLogo.className = 'partner-logo';
            const cleanName = sanitizeHTML(partner.nombre);
            const cleanLogo = sanitizeHTML(partner.logo_url);

            let innerHTML = `<img src="${cleanLogo}" alt="${cleanName}">`;
            if (partner.website_url) {
                innerHTML = `<a href="${sanitizeHTML(partner.website_url)}" target="_blank" rel="noopener noreferrer">${innerHTML}</a>`;
            }
            if (partner.es_autentico_verificado !== false) {
                innerHTML += `<div style="font-size:0.75rem; color: var(--color-accent-cyan); font-weight:bold; margin-top:0.25rem;"><i class="fa-solid fa-circle-check"></i> Verificado</div>`;
            }
            partnerLogo.innerHTML = innerHTML;

            if (partner.tipo === 'cliente') {
                clientsGrid.appendChild(partnerLogo);
            } else {
                testersGrid.appendChild(partnerLogo);
            }
        });
    }

    function renderPlans(plans) {
        const grid = document.getElementById('pricing-grid');
        if (!grid) return;
        grid.innerHTML = '';

        plans.forEach(plan => {
            const card = document.createElement('div');
            card.className = 'plan-card' + (plan.recomendado ? ' recommended' : '');

            let featuresHtml = '';
            if (plan.caracteristicas) {
                try {
                    const features = typeof plan.caracteristicas === 'string' ? JSON.parse(plan.caracteristicas) : plan.caracteristicas;
                    featuresHtml = features.map(f => `<li><i class="fa-solid fa-check" style="color: var(--color-accent-cyan); margin-right: 0.5rem;"></i>${sanitizeHTML(f)}</li>`).join('');
                } catch (e) {
                    console.error("Could not parse plan features JSON:", e);
                }
            }

            const cleanNombre = sanitizeHTML(plan.nombre);
            const isGratis = plan.gratis_badge || plan.precio_mensual === "0" || plan.precio_mensual === 0;
            const cleanPrecio = isGratis ? 'Gratis / Costo 0' : `$${sanitizeHTML(plan.precio_mensual)}/mes`;
            const cleanDescripcion = sanitizeHTML(plan.descripcion);

            card.innerHTML = `
                ${plan.recomendado ? '<div class="recommended-badge" style="background:#38BDF8; color:#070B14; font-weight:800; font-size:0.75rem; padding:4px 10px; border-radius:12px; position:absolute; top:12px; right:12px;">RECOMENDADO</div>' : ''}
                ${isGratis ? '<div class="free-badge" style="background:#38BDF8; color:#070B14; font-weight:800; font-size:0.75rem; padding:4px 10px; border-radius:12px; position:absolute; top:12px; right:12px;">GRATIS — COSTO 0</div>' : ''}
                <h3 style="color:#38BDF8; font-size:1.3rem; font-weight:800; margin-top:0.5rem;">${cleanNombre}</h3>
                <p class="price" style="font-size:1.8rem; font-weight:800; color:#E2E8F0; margin:0.5rem 0;">${cleanPrecio}</p>
                ${(plan.precio_anual && !isGratis) ? `<p style="font-size:0.85rem; color:var(--color-text-muted);">o $${sanitizeHTML(plan.precio_anual)}/año</p>` : ''}
                <p style="margin-top: 1rem; font-size:0.95rem; color:#94A3B8;">${cleanDescripcion}</p>
                <ul>${featuresHtml}</ul>
                <a href="register.html" class="plan-button" style="width: 100%; text-align:center; display:inline-block; padding:0.75rem 0; min-height:44px; margin-top:1rem; font-weight:700;">
                    ${isGratis ? 'Acceder Gratis' : 'Seleccionar Plan'}
                </a>
            `;
            grid.appendChild(card);
        });

        // GSAP Hover Animations para las tarjetas de precios con resalte Cyan Metálico
        if (typeof gsap !== 'undefined') {
            document.querySelectorAll('.plan-card').forEach(c => {
                c.addEventListener('mouseenter', () => {
                    gsap.to(c, { scale: 1.03, borderColor: '#38BDF8', boxShadow: '0 8px 30px rgba(56, 189, 248, 0.3)', duration: 0.3 });
                });
                c.addEventListener('mouseleave', () => {
                    gsap.to(c, { scale: 1.0, borderColor: 'rgba(26, 38, 66, 0.8)', boxShadow: 'none', duration: 0.3 });
                });
            });
        }
    }

    function renderLaunchOffer(offerText) {
        const container = document.getElementById('launch-offer-container');
        if (!container || !offerText) return;
        container.innerHTML = `<p style="font-size: 1.1rem; color: var(--color-text-primary); margin: 0;">${sanitizeHTML(offerText)}</p>`;
    }

    function renderFaq(faqs) {
        const container = document.getElementById('faq-container');
        if (!container) return;
        container.innerHTML = '';

        const faqData = (faqs && faqs.length > 0) ? faqs : [
            { pregunta: "¿Qué es la suite SGA-CD?", respuesta: "Es la plataforma integrada para la gestión de inscripciones deportivas, escuelas culturales, evaluación biológica y control de escenarios." },
            { pregunta: "¿Cómo funciona el aislamiento multi-inquilino?", respuesta: "Cada institución opera sobre una partición aislada garantizando privacidad de datos de menores y cumplimiento normativo ARCO." },
            { pregunta: "¿Qué metodos de pago y facturación soporta?", respuesta: "Integración con Stripe, PSE y pasarelas bancarias locales con facturación recurrente automatizada." },
            { pregunta: "¿Soporta uso en dispositivos móviles?", respuesta: "Sí, la plataforma cuenta con soporte PWA responsivo optimizado para tabletas y smartphones en campo." }
        ];

        faqData.forEach(faq => {
            const faqItem = document.createElement('div');
            faqItem.className = 'faq-item';
            faqItem.innerHTML = `
                <button class="faq-question">
                    <span>${sanitizeHTML(faq.pregunta)}</span>
                    <i class="fa-solid fa-chevron-down" style="font-size: 0.85rem;"></i>
                </button>
                <div class="faq-answer">
                    <p>${sanitizeHTML(faq.respuesta)}</p>
                </div>
            `;
            container.appendChild(faqItem);
        });

        container.querySelectorAll('.faq-question').forEach(button => {
            button.addEventListener('click', () => {
                const answer = button.nextElementSibling;
                const icon = button.querySelector('i');
                const isOpen = answer.style.maxHeight;

                if (isOpen) {
                    answer.style.maxHeight = null;
                    if (icon) icon.style.transform = 'rotate(0deg)';
                } else {
                    answer.style.maxHeight = answer.scrollHeight + "px";
                    if (icon) icon.style.transform = 'rotate(180deg)';
                }
            });
        });
    }

    function renderFooter(contact) {
        const companyContainer = document.getElementById('company-info');
        const contactContainer = document.getElementById('contact-info');
        const socialContainer = document.getElementById('social-media');
        const footer = document.getElementById('main-footer');

        if (companyContainer) {
            companyContainer.innerHTML = `
                <h4>${sanitizeHTML(contact.nombre_empresa || 'SGA-CD')}</h4>
                <h5>Misión</h5>
                <p>${sanitizeHTML(contact.mission || '')}</p>
                <h5>Visión</h5>
                <p>${sanitizeHTML(contact.vision || '')}</p>
            `;
        }
        if (contactContainer) {
            contactContainer.innerHTML = `
                <h4>Contacto Institucional</h4>
                <p>${sanitizeHTML(contact.direccion || '')}</p>
                <p>Email: <a href="mailto:${sanitizeHTML(contact.email_contacto)}">${sanitizeHTML(contact.email_contacto || '')}</a></p>
                <p>Teléfono: ${sanitizeHTML(contact.telefono_contacto || '')}</p>
            `;
        }
        if (socialContainer) {
            socialContainer.innerHTML = `
                <h4>Redes & Canales</h4>
                <div style="display:flex; gap:1rem; margin-top:0.5rem; font-size:1.2rem;">
                    <a href="#" aria-label="Facebook"><i class="fa-brands fa-facebook"></i></a>
                    <a href="#" aria-label="Twitter"><i class="fa-brands fa-x-twitter"></i></a>
                    <a href="#" aria-label="Instagram"><i class="fa-brands fa-instagram"></i></a>
                    <a href="#" aria-label="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
                </div>
            `;
        }
        if (footer) {
            const year = new Date().getFullYear();
            let copy = footer.querySelector('.footer-copy');
            if (!copy) {
                copy = document.createElement('p');
                copy.className = 'footer-copy';
                footer.appendChild(copy);
            }
            copy.innerHTML = `&copy; ${year} ${sanitizeHTML(contact.nombre_empresa || 'SGA-CD')}. Todos los derechos reservados.`;
        }
    }

    // --- 2. GSAP & ScrollTrigger Animations ---
    function initializeGSAPAnimations() {
        if (typeof gsap === 'undefined') return;

        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
        }

        // Hero title & CTA entrance
        gsap.from('#hero .hero-title, #hero .hero-tagline, #hero .cta-button', {
            duration: 1,
            y: 30,
            opacity: 0,
            stagger: 0.15,
            ease: 'power3.out'
        });

        // 3D Parallax Scrolling on Sports Disciplines & Cultural Workshops
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.to('#hero-video-container', {
                scrollTrigger: {
                    trigger: '#hero',
                    start: 'top top',
                    end: 'bottom top',
                    scrub: true
                },
                yPercent: 25,
                ease: 'none'
            });

            gsap.to('#monitor-vivo', {
                scrollTrigger: {
                    trigger: '#monitor-vivo',
                    start: 'top bottom',
                    end: 'bottom top',
                    scrub: 1
                },
                y: -30,
                ease: 'power1.out'
            });
        }

        // Animated Statistics Counter with ScrollTrigger
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-target') || '0', 10);

            if (typeof ScrollTrigger !== 'undefined') {
                gsap.to(stat, {
                    scrollTrigger: {
                        trigger: stat,
                        start: 'top 85%'
                    },
                    duration: 2,
                    innerText: target,
                    snap: { innerText: 1 },
                    ease: 'power2.out',
                    onUpdate: function() {
                        const val = Math.ceil(this.targets()[0].innerText);
                        stat.innerText = val.toLocaleString() + (target >= 1000 ? '+' : '');
                    }
                });
            } else {
                stat.innerText = target.toLocaleString() + '+';
            }
        });

        // Feature & Plan Cards Reveal
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.from('.feature-card, .plan-card', {
                scrollTrigger: {
                    trigger: '#funcionalidades',
                    start: 'top 80%'
                },
                duration: 0.8,
                y: 40,
                opacity: 0,
                stagger: 0.1,
                ease: 'power2.out'
            });
        }
    }

    // --- 3. AI Sales Agent Chat Handler ---
    function initializeAIAgent() {
        const toggleButton = document.getElementById('ai-agent-toggle');
        const chatbox = document.getElementById('ai-agent-chatbox');
        const messagesContainer = document.getElementById('chatbox-messages');
        const sendButton = document.getElementById('chatbox-send');
        const inputField = document.getElementById('chatbox-input');

        if (!toggleButton || !chatbox) return;

        toggleButton.addEventListener('click', () => {
            const isHidden = chatbox.classList.contains('hidden');
            if (isHidden) {
                chatbox.classList.remove('hidden');
                toggleButton.setAttribute('aria-expanded', 'true');
                if (messagesContainer.children.length === 0) {
                    addMessage('agent-message', '¡Hola! Soy el asistente virtual de SGA-CD. ¿Deseas conocer más sobre nuestras escuelas deportivas, talleres o planes institucionales?');
                }
            } else {
                chatbox.classList.add('hidden');
                toggleButton.setAttribute('aria-expanded', 'false');
            }
        });

        sendButton?.addEventListener('click', sendMessage);
        inputField?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        function sendMessage() {
            const rawText = inputField.value.trim();
            if (!rawText) return;

            const sanitizedMsg = sanitizeHTML(rawText);
            addMessage('user-message', sanitizedMsg);
            inputField.value = '';

            sendMessageToAgent(rawText);
        }

        function addMessage(typeClass, text) {
            const msgEl = document.createElement('div');
            msgEl.className = `chat-message ${typeClass}`;
            msgEl.textContent = text;
            messagesContainer.appendChild(msgEl);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            return msgEl;
        }

        async function sendMessageToAgent(message) {
            const API_ENDPOINT = `${config.apiBaseUrl}/api/v1/sales_agent`;
            const thinkingMsg = addMessage('agent-message', 'Procesando consulta...');

            try {
                const response = await fetch(API_ENDPOINT, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: message })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                thinkingMsg.textContent = data.reply || 'SGA-CD ofrece soporte integral para gestión de deportes y cultura.';

            } catch (error) {
                console.warn('Fallback response for agent:', error);
                thinkingMsg.textContent = 'Ofrecemos planes desde $0 USD con soporte multi-inquilino, diagnósticos biométricos y control de escenarios.';
            }
        }
    }

    function initializeServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js')
            .then(reg => console.log('Service Worker registrado correctamente.', reg))
            .catch(err => console.log('Registro de Service Worker fallido:', err));
        }
    }

    // --- 4. Live Monitor & Telemetry Engine (Agent-Reach Integration) ---
    let liveMonitorEvents = [];

    async function loadLiveMonitor() {
        const monitorGrid = document.getElementById('monitor-grid');
        if (!monitorGrid) return;

        try {
            const response = await fetch(`${config.apiBaseUrl}/api/v1/public/events`);
            if (response.ok) {
                liveMonitorEvents = await response.json();
            } else {
                throw new Error('API offline');
            }
        } catch (e) {
        // Default high-performance fallback feed with 5 photos gallery per activity card
            liveMonitorEvents = [
            {
                id: 1,
                categoria: 'deporte',
                titulo: 'Disciplina Deportiva: Copa Intercolegial de Taekwondo 2025',
                detalle: 'Fase eliminatoria regional - 48 atletas acreditados.',
                estado: 'En Vivo',
                icono: 'fa-solid fa-trophy',
                fotos: [
                    'https://images.unsplash.com/photo-1555597673-b21d5c935865?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1517649763962-0c623266ddc0?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1526676037777-05a232554f77?auto=format&fit=crop&w=600&q=80'
                ]
            },
            {
                id: 2,
                categoria: 'cultura',
                titulo: 'Taller Cultural - Instrumentos: Guitarra & Arpa Llanera',
                detalle: 'Modalidad de música tradicional y cuerdas en auditorio central.',
                estado: 'Programado',
                icono: 'fa-solid fa-music',
                fotos: [
                    'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1525201548942-d8732f6617a0?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=600&q=80'
                ]
            },
            {
                id: 3,
                categoria: 'deporte',
                titulo: 'Disciplina Deportiva: Torneo de Natación Infantil & Juvenil',
                detalle: 'Pruebas de 100m libres y relevos mixtos.',
                estado: 'En Vivo',
                icono: 'fa-solid fa-person-swimming',
                fotos: [
                    'https://images.unsplash.com/photo-1530549387789-4c1017266635?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1519315901367-f34ff9154487?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1560090995-01632a28895b?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1438029071396-1e831a7fa6d8?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1519315901367-f34ff9154487?auto=format&fit=crop&w=600&q=80'
                ]
            },
            {
                id: 4,
                categoria: 'cultura',
                titulo: 'Taller Cultural - Danza: Joropo/Llanera, Salsa & Vallenato',
                detalle: 'Gala folclórica y muestra de ritmos tradicionales.',
                estado: 'Próximo',
                icono: 'fa-solid fa-masks-theater',
                fotos: [
                    'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1518834107882-77d19d5c5c62?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?auto=format&fit=crop&w=600&q=80'
                ]
            }
            ];
        }

        renderLiveMonitor('all');
        setupFilterTabs();
    }

    function renderLiveMonitor(filterCategory) {
        const monitorGrid = document.getElementById('monitor-grid');
        if (!monitorGrid) return;

        const filtered = filterCategory === 'all'
            ? liveMonitorEvents
            : liveMonitorEvents.filter(ev => ev.categoria === filterCategory);

        monitorGrid.innerHTML = '';

        if (filtered.length === 0) {
            monitorGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--color-text-muted);">No hay eventos disponibles en esta categoría.</p>';
            return;
        }

        filtered.forEach(ev => {
            const card = document.createElement('div');
            card.className = 'feature-card monitor-card multi-photo-card';
            card.setAttribute('data-category', ev.categoria);

            const cleanTitle = sanitizeHTML(ev.titulo);
            const cleanDetalle = sanitizeHTML(ev.detalle);
            const cleanEstado = sanitizeHTML(ev.estado);
            const cleanIcon = sanitizeHTML(ev.icono || 'fa-solid fa-star');
            const fotos = (ev.fotos && ev.fotos.length === 5) ? ev.fotos : [
                'https://images.unsplash.com/photo-1555597673-b21d5c935865?auto=format&fit=crop&w=600&q=80',
                'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80',
                'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=600&q=80',
                'https://images.unsplash.com/photo-1517649763962-0c623266ddc0?auto=format&fit=crop&w=600&q=80',
                'https://images.unsplash.com/photo-1526676037777-05a232554f77?auto=format&fit=crop&w=600&q=80'
            ];

            const galleryImgsHtml = fotos.map((fUrl, imgIdx) => `
                <img src="${sanitizeHTML(fUrl)}" alt="Foto ${imgIdx + 1} - ${cleanTitle}" class="card-gallery-img" loading="${imgIdx === 0 ? 'eager' : 'lazy'}" width="300" height="180">
            `).join('');

            card.innerHTML = `
                <!-- Micro-Carrusel Multifoto (5 Fotos GPU Hardware Composited) -->
                <div class="card-gallery-wrapper" data-card-id="${ev.id}">
                    <div class="card-gallery-strip" style="transform: translate3d(0%, 0, 0);">
                        ${galleryImgsHtml}
                    </div>
                    <button class="gallery-arrow-btn prev" aria-label="Foto Anterior"><i class="fa-solid fa-chevron-left"></i></button>
                    <button class="gallery-arrow-btn next" aria-label="Foto Siguiente"><i class="fa-solid fa-chevron-right"></i></button>
                    <div class="gallery-nav-dots">
                        <span class="gallery-dot active" data-dot="0"></span>
                        <span class="gallery-dot" data-dot="1"></span>
                        <span class="gallery-dot" data-dot="2"></span>
                        <span class="gallery-dot" data-dot="3"></span>
                        <span class="gallery-dot" data-dot="4"></span>
                    </div>
                </div>

                <div style="padding: 1.25rem; display:flex; flex-direction:column; flex:1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                        <i class="${cleanIcon}" style="font-size:1.5rem; margin-bottom:0; color:#38BDF8;"></i>
                        <span style="font-size:0.75rem; font-weight:700; padding:0.25rem 0.65rem; border-radius:12px; background:rgba(56,189,248,0.15); color:var(--color-accent-cyan); border:1px solid var(--color-border-specular);">
                            ${cleanEstado}
                        </span>
                    </div>
                    <h3>${cleanTitle}</h3>
                    <p style="font-size:0.88rem; margin-bottom:1rem; flex:1; color:#94A3B8;">${cleanDetalle}</p>

                    <!-- Vector UI Icons Action Group -->
                    <div class="card-actions-group">
                        <button class="ui-icon-btn bookmark-btn" aria-label="Guardar / Bookmark actividad" title="Guardar Actividad">
                            <svg class="ui-icon-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"></path></svg>
                        </button>
                        <button class="ui-icon-btn details-btn" aria-label="Ver cupos y detalles de actividad" title="Ver Cupos y Detalles" onclick="window.trackEvent('event_interest_click', { event_id: ${ev.id}, event_title: '${cleanTitle}' })">
                            <svg class="ui-icon-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                        </button>
                        <a href="register.html" class="ui-icon-btn register-arrow-btn" aria-label="Inscripción / Registro rápido" title="Registro Rápido" style="margin-left:auto;">
                            <svg class="ui-icon-svg" viewBox="0 0 24 24" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                        </a>
                    </div>
                </div>
            `;
            monitorGrid.appendChild(card);

            // Bind Micro-Carrusel 5 Photos Event Listeners
            setupMicroGallery(card);
        });

        // Attach GSAP Timeline 60 FPS transitions for Vector UI Icons
        document.querySelectorAll('.ui-icon-btn').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                const svg = btn.querySelector('.ui-icon-svg');
                if (typeof gsap !== 'undefined' && svg) {
                    gsap.to(svg, { scale: 1.15, stroke: '#38BDF8', duration: 0.2, ease: 'power2.out' });
                }
            });
            btn.addEventListener('mouseleave', () => {
                const svg = btn.querySelector('.ui-icon-svg');
                if (typeof gsap !== 'undefined' && svg && !btn.classList.contains('active')) {
                    gsap.to(svg, { scale: 1.0, stroke: '#94A3B8', duration: 0.2, ease: 'power2.out' });
                }
            });
            btn.addEventListener('click', () => {
                if (btn.classList.contains('bookmark-btn')) {
                    btn.classList.toggle('active');
                    if (btn.classList.contains('active')) {
                        window.trackEvent('bookmark_activity', { status: 'saved' });
                    }
                }
            });
        });

        // GSAP smooth transition for filtered items
        if (typeof gsap !== 'undefined') {
            gsap.fromTo('.monitor-card',
                { opacity: 0, y: 20, scale: 0.95 },
                { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.08, ease: 'power2.out' }
            );
        }
    }

    function setupFilterTabs() {
        const tabs = document.querySelectorAll('.filter-tabs .filter-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => {
                    t.classList.remove('active');
                    t.setAttribute('aria-selected', 'false');
                });
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');

                const category = tab.getAttribute('data-filter');
                window.trackEvent('filter_monitor_category', { category });
                renderLiveMonitor(category);
            });
        });
    }

    // Agent-Reach Telemetry Analytics Tracker
    window.trackEvent = function(eventName, payload = {}) {
        const telemetryData = {
            event: eventName,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            payload: {
                ...payload,
                taxonomy_domain: {
                    cultura: "Talleres / Modalidades (Danza: Joropo/Llanera, Salsa, Vallenato | Instrumentos Culturales: Guitarra, Arpa)",
                    deportes: "Disciplinas Deportivas"
                }
            }
        };
        console.log('[Agent-Reach Telemetry]:', telemetryData);

        // Dispatch async telemetry beacon if endpoint is configured
        if (navigator.sendBeacon) {
            navigator.sendBeacon(`${config.apiBaseUrl}/api/v1/telemetry`, JSON.stringify(telemetryData));
        }
    };

    // Attach telemetry tracking to public CTA buttons
    document.querySelectorAll('.cta-button, .plan-button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const btnText = e.currentTarget.textContent.trim();
            window.trackEvent('cta_click', { button_text: btnText, target_href: e.currentTarget.getAttribute('href') });
        });
    });

    // --- Micro-Gallery 5 Photos Controller ---
    function setupMicroGallery(cardEl) {
        const strip = cardEl.querySelector('.card-gallery-strip');
        const prevBtn = cardEl.querySelector('.gallery-arrow-btn.prev');
        const nextBtn = cardEl.querySelector('.gallery-arrow-btn.next');
        const dots = cardEl.querySelectorAll('.gallery-dot');

        if (!strip || !dots.length) return;

        let activeImgIndex = 0;

        function updateGalleryIndex(newIdx) {
            activeImgIndex = (newIdx + 5) % 5;
            const offset = activeImgIndex * 20; // 20% per image in 500% strip width
            strip.style.transform = `translate3d(-${offset}%, 0, 0)`;

            dots.forEach((dot, dIdx) => {
                if (dIdx === activeImgIndex) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        }

        prevBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            updateGalleryIndex(activeImgIndex - 1);
        });

        nextBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            updateGalleryIndex(activeImgIndex + 1);
        });

        dots.forEach((dot, dIdx) => {
            dot.addEventListener('click', (e) => {
                e.stopPropagation();
                updateGalleryIndex(dIdx);
            });
        });

        // Touch swipe gesture support for micro-carousel
        let touchStartX = 0;
        cardEl.querySelector('.card-gallery-wrapper')?.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        cardEl.querySelector('.card-gallery-wrapper')?.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].screenX;
            if (touchStartX - touchEndX > 40) {
                updateGalleryIndex(activeImgIndex + 1);
            } else if (touchEndX - touchStartX > 40) {
                updateGalleryIndex(activeImgIndex - 1);
            }
        }, { passive: true });
    }

    // --- Corporate Allies Matrix Generator ---
    function renderCorporateAllies() {
        const grid = document.getElementById('corporate-allies-grid');
        if (!grid) return;

        const allies = [
            {
                nombre: "Ecopetrol Energía & Regiones",
                categoria: "Co-Patrocinador Departamental",
                icono: "fa-solid fa-bolt-lightning",
                descripcion: "Financiación de escuelas deportivas y dotación de auditorios culturales en comunidades de influencia."
            },
            {
                nombre: "Bancolombia Social & Cultura",
                categoria: "Aliado Financiero",
                icono: "fa-solid fa-building-columns",
                descripcion: "Plataforma de becas estudiantiles y apoyo a certámenes folclóricos regionales."
            },
            {
                nombre: "Servientrega Logística Nacional",
                categoria: "Sponsor Deportivo",
                icono: "fa-solid fa-truck-fast",
                descripcion: "Suministro y distribución de implementos deportivos para escuelas de formación municipal."
            },
            {
                nombre: "Postobón Talentos Deportivos",
                categoria: "Patrocinador Oficial",
                icono: "fa-solid fa-glass-water",
                descripcion: "Respaldo al rendimiento atlético infantil en torneos intercolegiales de taekwondo y natación."
            }
        ];

        grid.innerHTML = allies.map(ally => `
            <div class="ally-card">
                <span class="ally-card-badge">${sanitizeHTML(ally.categoria)}</span>
                <div class="ally-logo-container">
                    <i class="${sanitizeHTML(ally.icono)}"></i>
                </div>
                <h3>${sanitizeHTML(ally.nombre)}</h3>
                <p>${sanitizeHTML(ally.descripcion)}</p>
                <div style="display:flex; align-items:center; justify-content:center; gap:0.4rem; color:#38BDF8; font-size:0.8rem; font-weight:700;">
                    <i class="fa-solid fa-circle-check"></i> Convenio Vigente 2025
                </div>
            </div>
        `).join('');
    }

    // --- Admin Territorial Asset Submit Handler ---
    window.handleAdminAssetSubmit = function() {
        const jurisdiction = document.getElementById('admin-jurisdiction')?.value || 'municipal';
        const activity = document.getElementById('admin-activity-target')?.value || 'taekwondo';
        const statusEl = document.getElementById('admin-shield-status');

        if (window.SGASEOOptimizer && window.SGASEOOptimizer.updateActivityMetadata) {
            const cat = (activity === 'taekwondo') ? 'deportes' : 'cultura';
            window.SGASEOOptimizer.updateActivityMetadata(cat, activity);
        }

        if (window.SGADynamicIsland) {
            window.SGADynamicIsland.showNotification(`Assets de ${activity.toUpperCase()} (${jurisdiction.toUpperCase()}) Sincronizados OK`, 'success');
        }

        if (statusEl) {
            statusEl.innerHTML = `<i class="fa-solid fa-check-double" style="color:#38BDF8;"></i> Sincronizado Exitosamente (Nivel ${jurisdiction.toUpperCase()})`;
            setTimeout(() => {
                statusEl.innerHTML = `<i class="fa-solid fa-shield-halved"></i> AgentShield ECC Protegido`;
            }, 3000);
        }
    };

    // --- 5. GPU-Bound GSAP Carousel Component ---
    function initializeGPUCarousel() {
        const track = document.getElementById('carousel-track');
        const prevBtn = document.getElementById('carousel-prev');
        const nextBtn = document.getElementById('carousel-next');

        if (!track || !prevBtn || !nextBtn) return;

        const slidesData = [
            { titulo: 'Acreditación Atlética Nacional', cita: 'SGA-CD nos permitió gestionar el perfil biométrico de más de 1,200 atletas sin fallas de concurrencia.', autor: 'Dra. María Fernanda López — Dir. Deportes Campus' },
            { titulo: 'Gala Anual de Danza y Teatro', cita: 'El control de aforo y asistencia de talleres culturales se automatizó por completo desde el primer mes.', autor: 'Prof. Jorge Restrepo — Coordinador Cultural' },
            { titulo: 'Torneo Intercolegial 2025', cita: 'La programación de escenarios y el medallero en tiempo real mantuvieron informadas a 45 instituciones.', autor: 'Lic. Claudia Morales — Secretaría de Deportes' }
        ];

        track.innerHTML = '';
        slidesData.forEach((slide) => {
            const slideEl = document.createElement('div');
            slideEl.className = 'carousel-slide';
            slideEl.innerHTML = `
                <h3 style="color:var(--color-accent-cyan); margin-top:0;"><i class="fa-solid fa-quote-left" style="font-size:1.5rem; margin-right:0.5rem;"></i>${sanitizeHTML(slide.titulo)}</h3>
                <p style="font-style:italic; font-size:1rem; margin-bottom:1.5rem;">"${sanitizeHTML(slide.cita)}"</p>
                <p style="font-size:0.85rem; font-weight:700; color:var(--color-text-primary); margin:0;">— ${sanitizeHTML(slide.autor)}</p>
            `;
            track.appendChild(slideEl);
        });

        let currentIndex = 0;
        let autoLoopTimer = null;
        const totalSlides = slidesData.length;

        function updateSlide(index) {
            currentIndex = (index + totalSlides) % totalSlides;
            const slideWidth = window.innerWidth >= 768 ? 50 : 100;
            const offset = currentIndex * slideWidth;

            if (typeof gsap !== 'undefined') {
                gsap.to(track, {
                    xPercent: -offset,
                    duration: 0.7,
                    ease: 'power2.out'
                });
            } else {
                track.style.transform = `translate3d(-${offset}%, 0, 0)`;
            }
        }

        function startAutoLoop() {
            stopAutoLoop();
            autoLoopTimer = setInterval(() => {
                updateSlide(currentIndex + 1);
            }, 5000);
        }

        function stopAutoLoop() {
            if (autoLoopTimer) {
                clearInterval(autoLoopTimer);
                autoLoopTimer = null;
            }
        }

        prevBtn.addEventListener('click', () => {
            updateSlide(currentIndex - 1);
            startAutoLoop();
        });

        nextBtn.addEventListener('click', () => {
            updateSlide(currentIndex + 1);
            startAutoLoop();
        });

        // Tab visibility listener to prevent memory leaks and unnecessary GPU cycles
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopAutoLoop();
            } else {
                startAutoLoop();
            }
        });

        startAutoLoop();
    }

    // --- App Init ---
    loadAndRenderContent();
    loadLiveMonitor();
    renderCorporateAllies();
    initializeGPUCarousel();
    if (window.SGAModernCarousel) {
        window.SGAModernCarousel.init('modern-carousel-container');
    }
    initializeAIAgent();
    initializeServiceWorker();
});
