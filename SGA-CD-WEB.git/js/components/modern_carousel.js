/**
 * Modern Carousel Component - SGA-CD
 * Carrusel de 10 diapositivas con letras y párrafos flotantes
 * Animado a 60 FPS con GSAP GPU hardware compositing (transform: translate3d y opacity)
 * Incluye listener de visibilitychange para pausar en blur y evitar leaks.
 */
window.SGAModernCarousel = (function() {
    const defaultSlidesData = [
        {
            title: "Gestión Institucional de Cobertura Nacional",
            subtitle: "Disciplinas Deportivas y Modalidades Culturales en un solo ecosistema.",
            tag: "ENTIDADES PÚBLICAS Y PRIVADAS",
            bgGradient: "linear-gradient(135deg, #070B14 0%, #0D1424 100%)",
            imageUrl: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Taekwondo, Fútbol y Baloncesto",
            subtitle: "Seguimiento atlético, métricas de rendimiento y expedientes de deportistas.",
            tag: "DISCIPLINAS DEPORTIVAS",
            bgGradient: "linear-gradient(135deg, #0B172E 0%, #070B14 100%)",
            imageUrl: "https://images.unsplash.com/photo-1555597673-b21d5c935865?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Danza: Joropo, Salsa y Vallenato",
            subtitle: "Preservación del patrimonio cultural con escuelas de formación estructuradas.",
            tag: "MODALIDADES CULTURALES",
            bgGradient: "linear-gradient(135deg, #0D1424 0%, #0F2042 100%)",
            imageUrl: "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Instrumentos: Guitarra y Arpa",
            subtitle: "Talleres especializados de música con control de asistencia offline PWA.",
            tag: "TALLERES DE FORMACIÓN",
            bgGradient: "linear-gradient(135deg, #081121 0%, #070B14 100%)",
            imageUrl: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Plataforma para Profesores e Instructores",
            subtitle: "Carga de notas, Roster de alumnos e informes de cumplimiento en tiempo real.",
            tag: "DOCENTES / INSTRUCTORES",
            bgGradient: "linear-gradient(135deg, #0D1424 0%, #0A1931 100%)",
            imageUrl: "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Suscripción Estudiantil Costo 0",
            subtitle: "Inscripción en línea, carnet digital y medallería para alumnos y acudientes.",
            tag: "ESTUDIANTES Y PADRES DE FAMILIA",
            bgGradient: "linear-gradient(135deg, #050D1A 0%, #0D1424 100%)",
            imageUrl: "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Fiscalización Presupuestal y Convenios",
            subtitle: "Auditoría en tiempo real para Ministerios, Gobernaciones y Alcaldías.",
            tag: "CONTROL GUBERNAMENTAL",
            bgGradient: "linear-gradient(135deg, #0D1424 0%, #081B38 100%)",
            imageUrl: "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Sincronización PWA Offline Sync",
            subtitle: "Registro de asistencia sin conexión a internet en escenarios remotos.",
            tag: "TECNOLOGÍA ROBUSTA",
            bgGradient: "linear-gradient(135deg, #070B14 0%, #0D1E3A 100%)",
            imageUrl: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Análisis Predictivo e Inteligencia Artificial",
            subtitle: "Generación automatizada de planes anuales de trabajo y proyectos.",
            tag: "IA Y TELEMETRÍA",
            bgGradient: "linear-gradient(135deg, #09152B 0%, #070B14 100%)",
            imageUrl: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80"
        },
        {
            title: "Seguridad y Hardening Criptográfico",
            subtitle: "Aislamiento multi-tenant, sanitización XSS y protección AgentShield ECC.",
            tag: "SEGURIDAD DE ALTO NIVEL",
            bgGradient: "linear-gradient(135deg, #0D1424 0%, #070B14 100%)",
            imageUrl: "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80"
        }
    ];

    let activeSlidesData = [...defaultSlidesData];
    let currentIndex = 0;
    let autoPlayTimer = null;

    function sanitizeAttr(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function setCustomImages(urlsArray) {
        if (Array.isArray(urlsArray) && urlsArray.length > 0) {
            urlsArray.forEach((url, i) => {
                if (i < activeSlidesData.length && url && (url.trim().startsWith('http') || url.trim().startsWith('assets/'))) {
                    activeSlidesData[i].imageUrl = url.trim();
                }
            });
        }
    }

    function setCustomSlides(slidesArray) {
        if (Array.isArray(slidesArray) && slidesArray.length > 0) {
            slidesArray.forEach((slide, i) => {
                if (i < activeSlidesData.length && slide && typeof slide === 'object') {
                    if (slide.title) activeSlidesData[i].title = String(slide.title);
                    if (slide.subtitle) activeSlidesData[i].subtitle = String(slide.subtitle);
                    if (slide.tag) activeSlidesData[i].tag = String(slide.tag);
                    if (slide.imageUrl && (slide.imageUrl.startsWith('http') || slide.imageUrl.startsWith('assets/'))) {
                        activeSlidesData[i].imageUrl = slide.imageUrl;
                    }
                }
            });
        }
    }

    function renderCarousel(containerId, customData = null) {
        if (Array.isArray(customData)) {
            if (customData.length > 0 && typeof customData[0] === 'object') {
                setCustomSlides(customData);
            } else if (customData.length > 0 && typeof customData[0] === 'string') {
                setCustomImages(customData);
            }
        }
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="sga-modern-carousel-wrapper" style="position:relative; width:100%; min-height:480px; background:#070B14; border:1px solid rgba(56,189,248,0.25); border-radius:20px; overflow:hidden; padding:1.5rem; box-sizing:border-box;">
                <div class="sga-carousel-track" style="position:relative; width:100%; min-height:440px; display:flex; align-items:center;">
                    ${activeSlidesData.map((slide, index) => `
                        <div class="sga-carousel-slide ${index === 0 ? 'active' : ''}" data-index="${index}" style="position:absolute; inset:0; opacity:${index === 0 ? 1 : 0}; transform:translate3d(${index === 0 ? '0px' : '100px'}, 0, 0); transition:opacity 0.6s ease, transform 0.6s ease; display:flex; flex-direction:column; justify-content:flex-start; padding:2.5rem 2rem 2rem 2rem; background:${slide.bgGradient}; border-radius:16px; box-sizing:border-box; overflow:hidden;">
                            <!-- Dynamic Background Image Layer with Contrast Overlay -->
                            <div class="sga-slide-image-layer" style="position:absolute; inset:0; z-index:1; overflow:hidden;">
                                <img src="${sanitizeAttr(slide.imageUrl)}" alt="${sanitizeAttr(slide.title)}" loading="lazy" style="width:100%; height:100%; object-fit:cover; opacity:0.38; transition:transform 0.8s ease;" onerror="this.style.display='none';">
                                <div style="position:absolute; inset:0; background:linear-gradient(180deg, rgba(7,11,20,0.7) 0%, rgba(7,11,20,0.92) 100%);"></div>
                            </div>

                            <div style="position:relative; z-index:2; display:flex; flex-direction:column; justify-content:flex-start; height:100%;">
                                <span class="slide-tag" style="display:inline-block; align-self:flex-start; background:rgba(56,189,248,0.18); color:#38BDF8; font-size:0.8rem; font-weight:800; padding:0.4rem 1rem; border-radius:20px; border:1px solid rgba(56,189,248,0.35); margin-bottom:1.2rem; letter-spacing:1px; flex-shrink:0;">
                                    ${slide.tag}
                                </span>
                                <h2 class="slide-floating-title" style="color:#F8FAFC; font-size:clamp(1.5rem, 3vw, 2.5rem); font-weight:800; margin:0 0 1rem 0; line-height:1.2; text-shadow:0 2px 8px rgba(0,0,0,0.8);">
                                    ${slide.title}
                                </h2>
                                <p class="slide-floating-desc" style="color:#CBD5E1; font-size:clamp(0.95rem, 1.5vw, 1.25rem); margin:0; max-width:700px; line-height:1.6; text-shadow:0 1px 4px rgba(0,0,0,0.8);">
                                    ${slide.subtitle}
                                </p>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <!-- Navigation Controls -->
                <div style="position:absolute; bottom:1.5rem; right:2rem; display:flex; gap:0.75rem; align-items:center; z-index:10;">
                    <button id="sga-carousel-prev" class="btn-secondary" style="width:44px; height:44px; border-radius:50%; min-height:44px; padding:0; display:flex; align-items:center; justify-content:center;">
                        <i class="fas fa-chevron-left" style="color:#38BDF8;"></i>
                    </button>
                    <span id="sga-carousel-indicator" style="color:#38BDF8; font-size:0.85rem; font-weight:700; min-width:50px; text-align:center;">1 / 10</span>
                    <button id="sga-carousel-next" class="btn-secondary" style="width:44px; height:44px; border-radius:50%; min-height:44px; padding:0; display:flex; align-items:center; justify-content:center;">
                        <i class="fas fa-chevron-right" style="color:#38BDF8;"></i>
                    </button>
                </div>
            </div>
        `;

        setupEvents(container);
        startAutoPlay();
    }

    function goToSlide(newIndex) {
        const slides = document.querySelectorAll('.sga-carousel-slide');
        if (!slides.length) return;

        slides[currentIndex].style.opacity = '0';
        slides[currentIndex].style.transform = 'translate3d(-100px, 0, 0)';
        slides[currentIndex].classList.remove('active');

        currentIndex = (newIndex + slides.length) % slides.length;

        slides[currentIndex].style.opacity = '1';
        slides[currentIndex].style.transform = 'translate3d(0, 0, 0)';
        slides[currentIndex].classList.add('active');

        const indicator = document.getElementById('sga-carousel-indicator');
        if (indicator) {
            indicator.textContent = `${currentIndex + 1} / ${slides.length}`;
        }

        // Animación GSAP flotante de letras y párrafos
        if (window.gsap) {
            const activeSlide = slides[currentIndex];
            gsap.fromTo(activeSlide.querySelector('.slide-floating-title'),
                { y: 15, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.6, ease: 'power2.out' }
            );
            gsap.fromTo(activeSlide.querySelector('.slide-floating-desc'),
                { y: 10, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8, delay: 0.1, ease: 'power2.out' }
            );
        }
    }

    function startAutoPlay() {
        stopAutoPlay();
        autoPlayTimer = setInterval(() => {
            goToSlide(currentIndex + 1);
        }, 5000);
    }

    function stopAutoPlay() {
        if (autoPlayTimer) clearInterval(autoPlayTimer);
    }

    function setupEvents(container) {
        const prevBtn = document.getElementById('sga-carousel-prev');
        const nextBtn = document.getElementById('sga-carousel-next');

        if (prevBtn) prevBtn.addEventListener('click', () => { goToSlide(currentIndex - 1); startAutoPlay(); });
        if (nextBtn) nextBtn.addEventListener('click', () => { goToSlide(currentIndex + 1); startAutoPlay(); });

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopAutoPlay();
            } else {
                startAutoPlay();
            }
        });
    }

    return {
        init: renderCarousel,
        goToSlide: goToSlide
    };
})();
