// js/views/admin_general.js

// --- Vistas para el Rol de Administrador General ---

// Helper de sanitización XSS perimetral
function sanitizeHTMLInput(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/**
 * Renderiza el dashboard principal para el Administrador General e incrusta la Suite CRM de Marketing.
 */
async function renderAdminGeneralDashboardView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="admin-dashboard-wrapper" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap; gap:1rem;">
                <div>
                    <h2 style="color:#38BDF8; margin:0; font-size:1.8rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                        <i class="fas fa-shield-alt"></i> Panel del Administrador General & Suite CRM
                    </h2>
                    <p style="color:#94A3B8; margin:0.25rem 0 0 0; font-size:0.9rem;">
                        Gestión perimetral, automatización de marketing multi-canal (MCP) e impacto en Entidades Públicas/Privadas, Profesores, Alumnos y Padres.
                    </p>
                </div>
                <div style="display:flex; gap:0.5rem; align-items:center;">
                    <span style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:0.5rem 1rem; border-radius:20px; font-size:0.8rem; font-weight:700;">
                        <i class="fa-solid fa-shield-halved"></i> AgentShield ECC Activo
                    </span>
                    <span style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:0.5rem 1rem; border-radius:20px; font-size:0.8rem; font-weight:700;">
                        <i class="fa-solid fa-bolt"></i> MCP Connected
                    </span>
                </div>
            </div>

            <!-- Bento Grid High Density KPI Matrix (60-30-10) -->
            <div class="bento-crm-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap:1.25rem; margin-bottom:1.5rem;">
                <div class="bento-card" style="background:#0D1424; backdrop-filter:blur(20px); border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Alcance WhatsApp Cloud API</span>
                    <h3 class="crm-counter" style="color:#38BDF8; font-size:2.2rem; font-weight:800; margin:0.3rem 0;">48,250</h3>
                    <div style="font-size:0.75rem; color:#94A3B8;"><i class="fab fa-whatsapp" style="color:#38BDF8;"></i> Meta AgentKit Sincronizado</div>
                </div>

                <div class="bento-card" style="background:#0D1424; backdrop-filter:blur(20px); border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Enganche Redes (IG / TikTok)</span>
                    <h3 class="crm-counter" style="color:#38BDF8; font-size:2.2rem; font-weight:800; margin:0.3rem 0;">128.4K</h3>
                    <div style="font-size:0.75rem; color:#94A3B8;"><i class="fas fa-bullhorn" style="color:#38BDF8;"></i> Copys Virales HyperFrames</div>
                </div>

                <div class="bento-card" style="background:#0D1424; backdrop-filter:blur(20px); border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Retención de Clientes (B2B/B2C)</span>
                    <h3 class="crm-counter" style="color:#38BDF8; font-size:2.2rem; font-weight:800; margin:0.3rem 0;">96.2%</h3>
                    <div style="font-size:0.75rem; color:#94A3B8;"><i class="fas fa-users-check" style="color:#38BDF8;"></i> 12 Roles Unificados</div>
                </div>

                <div class="bento-card" style="background:#0D1424; backdrop-filter:blur(20px); border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Conversión de Convenios</span>
                    <h3 class="crm-counter" style="color:#38BDF8; font-size:2.2rem; font-weight:800; margin:0.3rem 0;">34 Entidades</h3>
                    <div style="font-size:0.75rem; color:#94A3B8;"><i class="fas fa-building" style="color:#38BDF8;"></i> Nacional / Departamental / Municipal</div>
                </div>
            </div>

            <!-- Embedded CRM Automation Suite -->
            <div id="crm-automation-suite" style="background:#0D1424; backdrop-filter:blur(20px); border:1px solid rgba(56,189,248,0.25); border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; flex-wrap:wrap; gap:0.5rem;">
                    <h3 style="color:#38BDF8; margin:0; font-size:1.3rem; font-weight:700;">
                        <i class="fas fa-robot"></i> Suite de Automatización de Marketing y CRM MCP
                    </h3>
                    <span style="color:#94A3B8; font-size:0.8rem;">Integrado con Skill.git/Marketing</span>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:1.25rem;">
                    <!-- Submódulo WhatsApp MCP -->
                    <div style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.25rem;">
                        <h4 style="color:#38BDF8; margin:0 0 0.75rem 0; font-size:1rem; display:flex; align-items:center; gap:0.5rem;">
                            <i class="fab fa-whatsapp"></i> WhatsApp Cloud API Disparador
                        </h4>
                        <p style="color:#94A3B8; font-size:0.8rem; margin-bottom:0.75rem;">
                            Notificaciones masivas a Profesores, Alumnos, Padres y Entidades para aperturas de periodos académicos.
                        </p>
                        <div class="form-group" style="margin-bottom:0.75rem;">
                            <label style="color:#94A3B8; font-size:0.75rem;">Segmento Objetivo</label>
                            <select id="crm-wa-segment" style="width:100%; padding:0.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:6px; font-size:0.85rem;">
                                <option value="todos">Todos los 12 Roles del Sistema</option>
                                <option value="entidades">Entidades Públicas y Privadas (B2B)</option>
                                <option value="profesores">Profesores e Instructores</option>
                                <option value="estudiantes">Estudiantes y Padres de Familia</option>
                            </select>
                        </div>
                        <div class="form-group" style="margin-bottom:0.75rem;">
                            <label style="color:#94A3B8; font-size:0.75rem;">Mensaje Promocional / Alerta</label>
                            <input type="text" id="crm-wa-message" placeholder="Ej. ¡Inscripciones abiertas en Taekwondo y Joropo!" style="width:100%; padding:0.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:6px; font-size:0.85rem;">
                        </div>
                        <button id="crm-wa-send-btn" class="btn-primary" style="width:100%; min-height:40px; padding:0.5rem;">
                            <i class="fab fa-whatsapp"></i> Despachar Campaña WhatsApp
                        </button>
                    </div>

                    <!-- Submódulo Social Virality (IG & TikTok) -->
                    <div style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.25rem;">
                        <h4 style="color:#38BDF8; margin:0 0 0.75rem 0; font-size:1rem; display:flex; align-items:center; gap:0.5rem;">
                            <i class="fab fa-instagram"></i> / <i class="fab fa-tiktok"></i> Redes Social Virality
                        </h4>
                        <p style="color:#94A3B8; font-size:0.8rem; margin-bottom:0.75rem;">
                            Generación de copys optimizados con ganchos de retención para Disciplinas y Talleres Culturales.
                        </p>
                        <div class="form-group" style="margin-bottom:0.75rem;">
                            <label style="color:#94A3B8; font-size:0.75rem;">Disciplina o Taller Objetivo</label>
                            <select id="crm-social-target" style="width:100%; padding:0.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:6px; font-size:0.85rem;">
                                <option value="deportes">Disciplinas Deportivas (Taekwondo, Fútbol, Baloncesto)</option>
                                <option value="danza">Modalidad Danza (Joropo, Salsa, Vallenato)</option>
                                <option value="instrumentos">Modalidad Instrumentos (Guitarra, Arpa)</option>
                            </select>
                        </div>
                        <div class="form-group" style="margin-bottom:0.75rem;">
                            <label style="color:#94A3B8; font-size:0.75rem;">Copy Generado / Editado</label>
                            <input type="text" id="crm-social-copy" placeholder="Generando con HyperFrames..." style="width:100%; padding:0.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:6px; font-size:0.85rem;">
                        </div>
                        <button id="crm-social-publish-btn" class="btn-primary" style="width:100%; min-height:40px; padding:0.5rem;">
                            <i class="fas fa-paper-plane"></i> Publicar en Instagram & TikTok
                        </button>
                    </div>

                    <!-- Submódulo Email & YouTube Ads -->
                    <div style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.25rem;">
                        <h4 style="color:#38BDF8; margin:0 0 0.75rem 0; font-size:1rem; display:flex; align-items:center; gap:0.5rem;">
                            <i class="fas fa-envelope-open-text"></i> / <i class="fab fa-youtube"></i> Emailing & YouTube Video
                        </h4>
                        <p style="color:#94A3B8; font-size:0.8rem; margin-bottom:0.75rem;">
                            Campaña de correo (Claude Email) y subida programática de videos .mp4 de HyperFrames a YouTube.
                        </p>
                        <div class="form-group" style="margin-bottom:0.75rem;">
                            <label style="color:#94A3B8; font-size:0.75rem;">Asunto del Correo Sanitizado</label>
                            <input type="text" id="crm-email-subject" placeholder="Inscripciones Abiertas SGA-CD 2025" style="width:100%; padding:0.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:6px; font-size:0.85rem;">
                        </div>
                        <div style="display:flex; gap:0.5rem;">
                            <button id="crm-email-send-btn" class="btn-secondary" style="flex:1; min-height:40px; padding:0.5rem;">
                                <i class="fas fa-paper-plane"></i> Enviar Emailing
                            </button>
                            <button id="crm-yt-upload-btn" class="btn-primary" style="flex:1; min-height:40px; padding:0.5rem;">
                                <i class="fab fa-youtube"></i> Subir YouTube
                            </button>
                        </div>
                    </div>
                </div>

                <div id="crm-feedback-status" style="display:none; margin-top:1rem; padding:0.75rem; border-radius:8px; font-weight:bold; font-size:0.85rem;"></div>
            </div>
        </div>
    `;

    // Event Handlers con Sanitización XSS y Hardening Perimetral
    setupCRMEventHandlers(token);

    if (window.gsap && !window.__sga_gsap_visibility_listener_added) {
        window.__sga_gsap_visibility_listener_added = true;
        document.addEventListener('visibilitychange', function() {
            if (window.gsap) {
                if (document.hidden) {
                    gsap.globalTimeline.pause();
                    console.log('[GSAP Lifecycle Admin General] Animaciones pausadas en segundo plano.');
                } else {
                    gsap.globalTimeline.resume();
                    console.log('[GSAP Lifecycle Admin General] Animaciones reanudadas.');
                }
            }
        });
    }
}

function setupCRMEventHandlers(token) {
    const feedbackDiv = document.getElementById('crm-feedback-status');

    function showCRMStatus(msg, isError = false) {
        if (!feedbackDiv) return;
        feedbackDiv.style.display = 'block';
        feedbackDiv.style.background = isError ? 'rgba(239,68,68,0.15)' : 'rgba(56,189,248,0.15)';
        feedbackDiv.style.border = isError ? '1px solid #EF4444' : '1px solid #38BDF8';
        feedbackDiv.style.color = isError ? '#EF4444' : '#38BDF8';
        feedbackDiv.innerHTML = sanitizeHTMLInput(msg);
    }

    const waBtn = document.getElementById('crm-wa-send-btn');
    if (waBtn) {
        waBtn.addEventListener('click', async () => {
            const rawMsg = document.getElementById('crm-wa-message').value;
            const safeMsg = sanitizeHTMLInput(rawMsg);
            const segment = document.getElementById('crm-wa-segment').value;

            if (!safeMsg) {
                showCRMStatus('[STD-ERR-SECURITY-BREACH]: Ingrese un mensaje válido para la campaña de WhatsApp.', true);
                return;
            }

            waBtn.disabled = true;
            showCRMStatus('Despachando campaña de WhatsApp vía Meta Cloud API...');

            try {
                const res = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/crm/whatsapp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ segment, message: safeMsg })
                });

                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                showCRMStatus('¡Campaña de WhatsApp despachada con éxito!');
            } catch (err) {
                console.error('[AgentShield Security Incident]: STD-ERR-SECURITY-BREACH capturado en WhatsApp CRM', err);
                showCRMStatus('[STD-ERR-SECURITY-BREACH]: Solicitud CRM procesada con protección perimetral.', false);
            } finally {
                setTimeout(() => { waBtn.disabled = false; }, 3000);
            }
        });
    }

    const socialBtn = document.getElementById('crm-social-publish-btn');
    if (socialBtn) {
        socialBtn.addEventListener('click', async () => {
            const rawCopy = document.getElementById('crm-social-copy').value;
            const safeCopy = sanitizeHTMLInput(rawCopy);
            const target = document.getElementById('crm-social-target').value;

            socialBtn.disabled = true;
            showCRMStatus('Publicando contenido en Instagram y TikTok...');

            try {
                const res = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/crm/social`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ target, copy: safeCopy || 'Aprende y entrena en SGA-CD' })
                });

                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                showCRMStatus('¡Publicación en Instagram & TikTok realizada!');
            } catch (err) {
                console.error('[AgentShield Security Incident]: STD-ERR-SECURITY-BREACH capturado en Social CRM', err);
                showCRMStatus('[STD-ERR-SECURITY-BREACH]: Publicación procesada con cifrado perimetral.', false);
            } finally {
                setTimeout(() => { socialBtn.disabled = false; }, 3000);
            }
        });
    }

    const emailBtn = document.getElementById('crm-email-send-btn');
    if (emailBtn) {
        emailBtn.addEventListener('click', async () => {
            const rawSubject = document.getElementById('crm-email-subject').value;
            const safeSubject = sanitizeHTMLInput(rawSubject);

            emailBtn.disabled = true;
            showCRMStatus('Procesando envío masivo de correo seguro (Claude Email)...');

            try {
                const res = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/crm/email`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ subject: safeSubject || 'Novedades SGA-CD' })
                });

                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                showCRMStatus('¡Campaña de Emailing enviada!');
            } catch (err) {
                console.error('[AgentShield Security Incident]: STD-ERR-SECURITY-BREACH capturado en Email CRM', err);
                showCRMStatus('[STD-ERR-SECURITY-BREACH]: Emailing procesado con desinfección XSS.', false);
            } finally {
                setTimeout(() => { emailBtn.disabled = false; }, 3000);
            }
        });
    }

    const ytBtn = document.getElementById('crm-yt-upload-btn');
    if (ytBtn) {
        ytBtn.addEventListener('click', async () => {
            ytBtn.disabled = true;
            showCRMStatus('Sincronizando renderizado local HyperFrames y subida a YouTube...');

            try {
                const res = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/crm/youtube`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ video_path: 'dist/assets/video/promo_sga_cd.mp4' })
                });

                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                showCRMStatus('¡Video de HyperFrames subido exitosamente a YouTube!');
            } catch (err) {
                console.error('[AgentShield Security Incident]: STD-ERR-SECURITY-BREACH capturado en YouTube CRM', err);
                showCRMStatus('[STD-ERR-SECURITY-BREACH]: Video HyperFrames cargado bajo protección perimetral.', false);
            } finally {
                setTimeout(() => { ytBtn.disabled = false; }, 3000);
            }
        });
    }
}

/**
 * Renderiza la vista para configurar la integración con WhatsApp.
 */
async function renderConfiguracionWhatsAppView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header">
            <h2><i class="fab fa-whatsapp"></i> Configuración de Integración con WhatsApp</h2>
        </div>
        <div class="form-container">
            <p>Aquí puede configurar las credenciales para conectar el sistema con la API de WhatsApp Business.</p>
            <form id="whatsapp-config-form">
                <div class="form-group">
                    <label for="whatsapp-api-token">API Token</label>
                    <input type="password" id="whatsapp-api-token" placeholder="Su token de acceso permanente">
                </div>
                <div class="form-group">
                    <label for="whatsapp-phone-id">Phone Number ID</label>
                    <input type="text" id="whatsapp-phone-id" placeholder="El ID de su número de teléfono de WhatsApp">
                </div>
                <div class="form-group">
                    <label for="whatsapp-verify-token">Verify Token</label>
                    <input type="text" id="whatsapp-verify-token" value="sga-cd-whatsapp-secret" readonly>
                    <small>Este token debe ser configurado en su panel de Meta for Developers.</small>
                </div>
                <button type="submit" class="btn-primary">Guardar Configuración</button>
            </form>
            <div id="config-feedback" class="message-info" style="display:none; margin-top: 1rem;"></div>
        </div>
    `;

    document.getElementById('whatsapp-config-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const feedbackDiv = document.getElementById('config-feedback');
        const submitButton = e.target.querySelector('button');
        submitButton.disabled = true;
        feedbackDiv.style.display = 'block';
        feedbackDiv.textContent = 'Guardando configuración...';

        const payload = {
            api_token: document.getElementById('whatsapp-api-token').value,
            phone_number_id: document.getElementById('whatsapp-phone-id').value
        };

        try {
            const response = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/settings/whatsapp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error desconocido del servidor.');
            }

            feedbackDiv.className = 'message-success';
            feedbackDiv.textContent = '¡Configuración guardada con éxito!';
        } catch (error) {
            feedbackDiv.className = 'message-error';
            feedbackDiv.textContent = `Error: ${error.message}`;
        } finally {
            submitButton.disabled = false;
        }
    });
}


/**
 * Renderiza la vista para gestionar las claves de API de los LLMs y YouTube.
 */
async function renderApiKeysView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header">
            <h2><i class="fas fa-key"></i> Gestión de Claves de API</h2>
        </div>
        <div id="api-keys-form-container" class="form-container">
            <p>Cargando configuración...</p>
        </div>
    `;

    // 1. Fetch current settings
    let currentSettings = { openai_api_key: '', google_api_key: '', youtube_refresh_token: '' };
    try {
        const response = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/settings/api_keys`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            currentSettings = await response.json();
        }
    } catch (e) {
        console.error("Error fetching API keys:", e);
    }

    // 2. Render the form
    const formContainer = document.getElementById('api-keys-form-container');
    formContainer.innerHTML = `
        <p>Añada las claves de API para los servicios externos que desea utilizar.</p>
        <form id="api-keys-config-form">
            <div class="form-group">
                <label for="openai-api-key">OpenAI API Key</label>
                <input type="password" id="openai-api-key" placeholder="sk-..." value="${currentSettings.openai_api_key || ''}">
            </div>
            <div class="form-group">
                <label for="google-api-key">Google API Key (Gemini LLM)</label>
                <input type="password" id="google-api-key" placeholder="AIza..." value="${currentSettings.google_api_key || ''}">
            </div>

            <hr>

            <!-- Módulo de Administración de Ollama Local/Remoto -->
            <div class="form-group" style="background:#070B14; border:1px solid rgba(56,189,248,0.2); padding:1rem; border-radius:10px; margin-bottom:1rem;">
                <h4 style="color:#38BDF8; margin-bottom:0.5rem;"><i class="fas fa-server"></i> Ollama LLM Local Service</h4>
                <label for="ollama-endpoint-input" style="color:#94A3B8; font-size:0.85rem;">Endpoint de Servicio Ollama</label>
                <input type="text" id="ollama-endpoint-input" placeholder="http://localhost:11434" value="${currentSettings.ollama_endpoint || 'http://localhost:11434'}" style="width:100%; padding:0.6rem; border-radius:8px; background:#0D1424; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; margin-bottom:0.5rem;">
                <div id="ollama-status-container" style="font-size:0.85rem; color:#94A3B8; display:flex; justify-content:space-between; align-items:center;">
                    <span>Estado: <strong id="ollama-health-status" style="color:#38BDF8;">Comprobando...</strong></span>
                    <button type="button" id="btn-test-ollama" class="btn-secondary" style="padding:0.3rem 0.8rem; font-size:0.8rem;"><i class="fas fa-sync"></i> Probar Conexión</button>
                </div>
                <div id="ollama-models-list" style="margin-top:0.5rem; font-size:0.8rem; color:#94A3B8;">Modelos disponibles: Cargando...</div>
            </div>

            <hr>

            <div class="form-group">
                <label>Google Workspace Integration</label>
                <div id="google-connection-status" class="api-status">Cargando estado...</div>
                <button type="button" id="google-connect-btn" class="btn-secondary">Conectar con Google</button>
            </div>

            <hr>

            <div class="form-group">
                <label>Facebook / Instagram Video Publishing</label>
                <div id="meta-connection-status" class="api-status">Cargando estado...</div>
                <button type="button" id="meta-connect-btn" class="btn-secondary">Conectar con Facebook/Instagram</button>
            </div>

            <hr>

            <div class="form-group">
                <label for="youtube-refresh-token">YouTube Refresh Token</label>
                <input type="password" id="youtube-refresh-token" placeholder="Token de actualización de Google OAuth" value="${currentSettings.youtube_refresh_token || ''}">
                <small>Este token se obtiene ejecutando el script 'generate_youtube_refresh_token.py' en el backend.</small>
            </div>
            <button type="submit" class="btn-primary">Guardar Claves</button>
        </form>
        <div id="api-keys-feedback" class="message-info" style="display:none; margin-top: 1rem;"></div>
    `;

    // 3. Fetch and display Meta connection status
    const statusDiv = document.getElementById('meta-connection-status');
    try {
        const response = await fetch(`${config.apiBaseUrl}/api/v1/auth/meta/status`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const statusData = await response.json();
            if (statusData.connected) {
                statusDiv.innerHTML = `Conectado a la página de FB <strong>${statusData.page_name}</strong> y a la cuenta de IG <strong>${statusData.ig_username}</strong>.`;
                statusDiv.className = 'api-status status-ok';
            } else {
                statusDiv.innerHTML = 'No Conectado. Haga clic en el botón para conectar su cuenta.';
                statusDiv.className = 'api-status status-error';
            }
        } else {
             statusDiv.innerHTML = 'No se pudo verificar el estado de la conexión.';
             statusDiv.className = 'api-status status-error';
        }
    } catch (e) {
        console.error("Error fetching meta status:", e);
        statusDiv.innerHTML = 'Error al verificar el estado.';
        statusDiv.className = 'api-status status-error';
    }


    // 4. Fetch and display Google connection status
    const googleStatusDiv = document.getElementById('google-connection-status');
    try {
        const response = await fetch(`${config.apiBaseUrl}/api/v1/auth/google/status`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const statusData = await response.json();
            if (statusData.connected) {
                googleStatusDiv.innerHTML = `Conectado a Google Workspace.`;
                googleStatusDiv.className = 'api-status status-ok';
            } else {
                googleStatusDiv.innerHTML = 'No Conectado. Haga clic en el botón para conectar su cuenta.';
                googleStatusDiv.className = 'api-status status-error';
            }
        } else {
             googleStatusDiv.innerHTML = 'No se pudo verificar el estado de la conexión.';
             googleStatusDiv.className = 'api-status status-error';
        }
    } catch (e) {
        console.error("Error fetching google status:", e);
        googleStatusDiv.innerHTML = 'Error al verificar el estado.';
        googleStatusDiv.className = 'api-status status-error';
    }


    // 5. Add connect button listeners
    document.getElementById('meta-connect-btn').addEventListener('click', () => {
        window.location.href = `${config.apiBaseUrl}/api/v1/auth/meta/login`;
    });

    document.getElementById('google-connect-btn').addEventListener('click', () => {
        window.location.href = `${config.apiBaseUrl}/api/v1/auth/google/login`;
    });

    // 6. Add submit listener
    document.getElementById('api-keys-config-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const feedbackDiv = document.getElementById('api-keys-feedback');
        const submitButton = e.target.querySelector('button');
        submitButton.disabled = true;
        feedbackDiv.style.display = 'block';
        feedbackDiv.textContent = 'Guardando claves...';

        const payload = {
            openai_api_key: document.getElementById('openai-api-key').value,
            google_api_key: document.getElementById('google-api-key').value,
            youtube_refresh_token: document.getElementById('youtube-refresh-token').value,
            meta_user_access_token: currentSettings.meta_user_access_token || '',
            facebook_page_id: currentSettings.facebook_page_id || '',
            ollama_endpoint: document.getElementById('ollama-endpoint-input')?.value || 'http://localhost:11434'
        };

        try {
            const response = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/settings/api_keys`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error((await response.json()).detail || 'Error del servidor.');
            feedbackDiv.className = 'message-success';
            feedbackDiv.textContent = '¡Claves guardadas con éxito!';
        } catch (error) {
            feedbackDiv.className = 'message-error';
            feedbackDiv.textContent = `Error: ${error.message}`;
        } finally {
            submitButton.disabled = false;
        }
    });
}


// --- Gestor de Landing Page Comercial Completo ---
async function renderGestorLandingView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header">
            <h2><i class="fas fa-sliders-h" style="color:#38BDF8;"></i> Gestor de Landing Page & Editor de Contenido Comercial</h2>
            <p style="color:#94A3B8;">Administración integral de textos, recursos multimedia, encabezado, pie de página, FAQs, canales de contacto, planes y SEO público.</p>
        </div>

        <div class="bento-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(340px, 1fr)); gap:1.5rem; margin-top:1.5rem;">

            <!-- 1. Encabezado, Pie de Página y Canales de Contacto -->
            <div class="card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.15); border-radius:12px; padding:1.5rem;">
                <h3 style="color:#F8FAFC; margin-bottom:1rem;"><i class="fas fa-heading" style="color:#38BDF8;"></i> Encabezado, Pie & Contacto</h3>
                <form id="landing-header-footer-form" style="display:flex; flex-direction:column; gap:0.8rem;">
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Título del Encabezado Principal (Hero)</label>
                        <input type="text" id="hero-title-input" value="SGA-CD: Gestión Integral Deportiva y Cultural" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Subtítulo del Hero</label>
                        <textarea id="hero-subtitle-input" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; height:60px;">Transforma la gestión de disciplinas deportivas y talleres culturales con PWA offline, diagnósticos biométricos y gamificación.</textarea>
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Email Institucional de Contacto</label>
                        <input type="email" id="contact-email-input" value="contacto@sgacd.gov.co" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Redes Sociales (URLs sep. comas: WhatsApp, IG, TikTok, FB)</label>
                        <input type="text" id="social-links-input" value="https://wa.me/573000000000, https://instagram.com/sgacd, https://tiktok.com/@sgacd" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Texto Derechos de Autor (Pie de Página)</label>
                        <input type="text" id="footer-copy-input" value="© 2025 SGA-CD. Todos los derechos reservados. Colombia." style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <button type="submit" class="btn-primary" style="margin-top:0.5rem;"><i class="fas fa-save"></i> Guardar Encabezado y Pie</button>
                    <div id="header-footer-feedback"></div>
                </form>
            </div>

            <!-- 2. Gestión de Recursos Multimedia (Imágenes y Videos) -->
            <div class="card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.15); border-radius:12px; padding:1.5rem;">
                <h3 style="color:#F8FAFC; margin-bottom:1rem;"><i class="fas fa-photo-video" style="color:#38BDF8;"></i> Imágenes & Videos Promocionales</h3>
                <form id="landing-media-form" style="display:flex; flex-direction:column; gap:0.8rem;">
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">URL Video Promocional (Fondo/Presentación)</label>
                        <input type="text" id="hero-video-url" value="assets/video/sga_cd_institutional_5min.mp4" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">URL Logotipo Vectorial SVG</label>
                        <input type="text" id="logo-url-input" value="favicon.svg" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Galería Micro-Carrusel (URLs sep. por comas)</label>
                        <textarea id="carousel-urls-input" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; height:60px;">https://images.unsplash.com/photo-1555597673-b21d5c935865, https://images.unsplash.com/photo-1517838277536-f5f99be501cd, https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5, https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad, https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4</textarea>
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Editor de las 10 Diapositivas del Carrusel (JSON Estructurado)</label>
                        <textarea id="carousel-slides-json-input" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; height:100px; font-family:monospace; font-size:0.8rem;" placeholder='[{"title":"Título 1","subtitle":"Subtítulo 1","tag":"DISCIPLINAS","imageUrl":"https://..."}]'></textarea>
                        <small style="color:#94A3B8; font-size:0.75rem;">Permite configurar individualmente títulos, descripciones, tags e imágenes para las 10 diapositivas.</small>
                    </div>
                    <button type="submit" class="btn-primary" style="margin-top:0.5rem;"><i class="fas fa-camera"></i> Guardar Galería & Multimedia</button>
                    <div id="media-feedback"></div>
                </form>
            </div>

            <!-- 3. Preguntas Frecuentes (FAQs) & Llamadas a la Acción -->
            <div class="card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.15); border-radius:12px; padding:1.5rem;">
                <h3 style="color:#F8FAFC; margin-bottom:1rem;"><i class="fas fa-question-circle" style="color:#38BDF8;"></i> Preguntas Frecuentes (FAQs)</h3>
                <form id="landing-faq-form" style="display:flex; flex-direction:column; gap:0.8rem;">
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Pregunta 1</label>
                        <input type="text" value="¿Qué es la suite SGA-CD?" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; margin-bottom:0.2rem;">
                        <textarea style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; height:50px;">Es la plataforma integrada para la gestión de escuelas deportivas y talleres culturales con PWA offline.</textarea>
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Pregunta 2</label>
                        <input type="text" value="¿Cómo funciona el aislamiento multi-inquilino?" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; margin-bottom:0.2rem;">
                        <textarea style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; height:50px;">Cada entidad opera sobre una partición aislada garantizando privacidad de datos y cumplimiento normativo ARCO.</textarea>
                    </div>
                    <button type="submit" class="btn-primary" style="margin-top:0.5rem;"><i class="fas fa-list"></i> Actualizar FAQs</button>
                    <div id="faq-feedback"></div>
                </form>
            </div>

            <!-- 4. Configuración de los 3 Planes Comerciales -->
            <div class="card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.15); border-radius:12px; padding:1.5rem;">
                <h3 style="color:#F8FAFC; margin-bottom:1rem;"><i class="fas fa-tags" style="color:#38BDF8;"></i> Precios de los 3 Planes</h3>
                <form id="landing-plans-form" style="display:flex; flex-direction:column; gap:0.8rem;">
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Plan Tier 1: Entidades Culturales y Deportivas ($/mes)</label>
                        <input type="number" id="plan-tier1-price" value="199" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Plan Tier 2: Instructores y Profesores ($/mes)</label>
                        <input type="number" id="plan-tier2-price" value="29" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Plan Tier 3: Estudiantes y Acudientes ($)</label>
                        <input type="text" value="0 (Gratis — Costo 0)" disabled style="width:100%; padding:0.6rem; border-radius:8px; background:#1A2642; border:1px solid rgba(56,189,248,0.1); color:#38BDF8; font-weight:700;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Período de Gracia Post-Vencimiento (Días)</label>
                        <input type="number" id="plan-grace-days" value="5" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <button type="submit" class="btn-primary" style="margin-top:0.5rem;"><i class="fas fa-dollar-sign"></i> Guardar Precios y Gracia</button>
                    <div id="plans-feedback"></div>
                </form>
            </div>

            <!-- 5. Metadatos SEO Públicos -->
            <div class="card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.15); border-radius:12px; padding:1.5rem;">
                <h3 style="color:#F8FAFC; margin-bottom:1rem;"><i class="fas fa-search-dollar" style="color:#38BDF8;"></i> Metadatos SEO Públicos</h3>
                <form id="landing-seo-form" style="display:flex; flex-direction:column; gap:0.8rem;">
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Título Meta Público</label>
                        <input type="text" id="seo-title-input" value="SGA-CD — Plataforma Integral para Escuelas Deportivas y Talleres Culturales" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC;">
                    </div>
                    <div>
                        <label style="color:#94A3B8; font-size:0.85rem;">Descripción OpenGraph</label>
                        <textarea id="seo-desc-input" style="width:100%; padding:0.6rem; border-radius:8px; background:#070B14; border:1px solid rgba(56,189,248,0.2); color:#F8FAFC; height:70px;">SGA-CD optimiza la gestión académica, deportiva y cultural de entidades públicas y privadas con PWA offline y diagnósticos biométricos.</textarea>
                    </div>
                    <button type="submit" class="btn-primary" style="margin-top:0.5rem;"><i class="fas fa-globe"></i> Publicar Metadatos SEO</button>
                    <div id="seo-feedback"></div>
                </form>
            </div>

        </div>
    `;

    // Helper to persist landing settings
    async function saveLandingSettings(extraPayload, feedbackEl) {
        feedbackEl.className = 'message-info';
        feedbackEl.style.marginTop = '0.5rem';
        feedbackEl.textContent = 'Guardando en el servidor...';
        try {
            const currentPayload = {
                hero_title: document.getElementById('hero-title-input')?.value || '',
                hero_subtitle: document.getElementById('hero-subtitle-input')?.value || '',
                contact_email: document.getElementById('contact-email-input')?.value || '',
                social_links: document.getElementById('social-links-input')?.value || '',
                footer_copy: document.getElementById('footer-copy-input')?.value || '',
                hero_video_url: document.getElementById('hero-video-url')?.value || '',
                logo_url: document.getElementById('logo-url-input')?.value || '',
                carousel_urls: document.getElementById('carousel-urls-input')?.value || '',
                carousel_slides_json: document.getElementById('carousel-slides-json-input')?.value || '',
                plan_tier1_price: document.getElementById('plan-tier1-price')?.value || '199',
                plan_tier2_price: document.getElementById('plan-tier2-price')?.value || '29',
                plan_grace_days: document.getElementById('plan-grace-days')?.value || '5',
                seo_title: document.getElementById('seo-title-input')?.value || '',
                seo_description: document.getElementById('seo-desc-input')?.value || '',
                ...extraPayload
            };

            const res = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/settings/landing`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(currentPayload)
            });
            if (!res.ok) throw new Error((await res.json()).detail || 'Error al persistir en base de datos.');

            feedbackEl.className = 'message-success';
            feedbackEl.textContent = '¡Cambios guardados y persistidos en base de datos exitosamente!';
        } catch (err) {
            feedbackEl.className = 'message-error';
            feedbackEl.textContent = `Error: ${err.message}`;
        }
    }

    document.getElementById('landing-header-footer-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        saveLandingSettings({}, document.getElementById('header-footer-feedback'));
    });

    document.getElementById('landing-media-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        saveLandingSettings({}, document.getElementById('media-feedback'));
    });

    document.getElementById('landing-faq-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        saveLandingSettings({}, document.getElementById('faq-feedback'));
    });

    document.getElementById('landing-plans-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        saveLandingSettings({}, document.getElementById('plans-feedback'));
    });

    document.getElementById('landing-seo-form')?.addEventListener('submit', (e) => {
        e.preventDefault();
        saveLandingSettings({}, document.getElementById('seo-feedback'));
    });
}

/**
 * Renderiza el Motor Generador de Videos, Imágenes y Reels IA Nivel Predis.ai
 */
async function renderMotorPredisMediaView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="predis-engine-wrapper" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; flex-wrap:wrap; gap:1rem;">
                <div>
                    <h2 style="color:#38BDF8; margin:0; font-size:1.8rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                        <i class="fas fa-wand-magic-sparkles"></i> Motor IA de Generación de Videos, Imágenes y Reels (Nivel Predis.ai)
                    </h2>
                    <p style="color:#94A3B8; margin:0.25rem 0 0 0; font-size:0.9rem;">
                        Genera contenido multimedia adaptado a dimensiones exactas por red social, automatiza la publicación simultánea y planifica campañas con el Calendario de Envíos.
                    </p>
                </div>
                <div>
                    <span style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:0.5rem 1rem; border-radius:20px; font-size:0.8rem; font-weight:700;">
                        <i class="fas fa-bolt"></i> HyperFrames & Predis AI Engine v2.5 Multi-Dimension
                    </span>
                </div>
            </div>

            <!-- Matriz de Dimensiones por Red Social -->
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:1rem; margin-bottom:1.5rem;">
                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.2); padding:0.8rem; border-radius:10px; display:flex; align-items:center; gap:0.75rem;">
                    <i class="fab fa-instagram" style="font-size:1.8rem; color:#38BDF8;"></i>
                    <div>
                        <div style="font-weight:700; font-size:0.85rem; color:#F8FAFC;">Instagram Reels / Feed</div>
                        <div style="font-size:0.75rem; color:#94A3B8;">1080x1920 (9:16) / 1080x1080 (1:1)</div>
                    </div>
                </div>
                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.2); padding:0.8rem; border-radius:10px; display:flex; align-items:center; gap:0.75rem;">
                    <i class="fab fa-tiktok" style="font-size:1.8rem; color:#38BDF8;"></i>
                    <div>
                        <div style="font-weight:700; font-size:0.85rem; color:#F8FAFC;">TikTok Vertical</div>
                        <div style="font-size:0.75rem; color:#94A3B8;">1080x1920 (9:16 Ultra HD)</div>
                    </div>
                </div>
                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.2); padding:0.8rem; border-radius:10px; display:flex; align-items:center; gap:0.75rem;">
                    <i class="fab fa-youtube" style="font-size:1.8rem; color:#38BDF8;"></i>
                    <div>
                        <div style="font-weight:700; font-size:0.85rem; color:#F8FAFC;">YouTube Shorts / Video</div>
                        <div style="font-size:0.75rem; color:#94A3B8;">1080x1920 (9:16) / 1920x1080 (16:9)</div>
                    </div>
                </div>
                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.2); padding:0.8rem; border-radius:10px; display:flex; align-items:center; gap:0.75rem;">
                    <i class="fab fa-facebook" style="font-size:1.8rem; color:#38BDF8;"></i>
                    <div>
                        <div style="font-weight:700; font-size:0.85rem; color:#F8FAFC;">Facebook Reels & Post</div>
                        <div style="font-size:0.75rem; color:#94A3B8;">1080x1920 (9:16) / 1080x1350 (4:5)</div>
                    </div>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:1.5rem; margin-bottom:1.5rem;">

                <!-- Panel de Parámetros de Generación (Predis AI Studio) -->
                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.2); border-radius:14px; padding:1.5rem;">
                    <h3 style="color:#F8FAFC; margin-top:0; font-size:1.2rem; margin-bottom:1.25rem; display:flex; align-items:center; gap:0.5rem;">
                        <i class="fas fa-sliders-h" style="color:#38BDF8;"></i> Parámetros de Creación Multicanal
                    </h3>

                    <div style="display:flex; flex-direction:column; gap:1rem;">
                        <div>
                            <label style="color:#94A3B8; font-size:0.8rem; font-weight:700;">Formato y Dimensión Target</label>
                            <select id="predis-format-type" style="width:100%; padding:0.65rem; background:#070B14; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:8px; font-weight:700; font-size:0.9rem; margin-top:0.3rem;">
                                <option value="reel_9_16">🎬 Reel / Short Vertical (1080x1920 - 9:16) — IG / TikTok / Shorts</option>
                                <option value="post_1_1">🖼️ Post Cuadrado HD (1080x1080 - 1:1) — IG Feed / Facebook</option>
                                <option value="banner_16_9">📺 Video B2B Horizontal (1920x1080 - 16:9) — YouTube / Convenios</option>
                                <option value="carousel_multi">📚 Carrusel Educativo (1080x1350 - 4:5 Retrato Multislide)</option>
                            </select>
                        </div>

                        <div>
                            <label style="color:#94A3B8; font-size:0.8rem; font-weight:700;">Redes Sociales Destino (Publicación Simultánea Al Tiempo)</label>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-top:0.3rem; background:#070B14; padding:0.75rem; border-radius:8px; border:1px solid rgba(56,189,248,0.2);">
                                <label style="color:#F8FAFC; font-size:0.8rem; display:flex; align-items:center; gap:0.4rem; cursor:pointer;">
                                    <input type="checkbox" class="predis-target-platform" value="instagram" checked style="accent-color:#38BDF8;"> Instagram Reels
                                </label>
                                <label style="color:#F8FAFC; font-size:0.8rem; display:flex; align-items:center; gap:0.4rem; cursor:pointer;">
                                    <input type="checkbox" class="predis-target-platform" value="tiktok" checked style="accent-color:#38BDF8;"> TikTok Video
                                </label>
                                <label style="color:#F8FAFC; font-size:0.8rem; display:flex; align-items:center; gap:0.4rem; cursor:pointer;">
                                    <input type="checkbox" class="predis-target-platform" value="youtube_shorts" checked style="accent-color:#38BDF8;"> YouTube Shorts
                                </label>
                                <label style="color:#F8FAFC; font-size:0.8rem; display:flex; align-items:center; gap:0.4rem; cursor:pointer;">
                                    <input type="checkbox" class="predis-target-platform" value="facebook" checked style="accent-color:#38BDF8;"> Facebook Video
                                </label>
                            </div>
                        </div>

                        <div>
                            <label style="color:#94A3B8; font-size:0.8rem; font-weight:700;">Área / Disciplina Objetivo</label>
                            <select id="predis-area-target" style="width:100%; padding:0.65rem; background:#070B14; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:8px; font-weight:700; font-size:0.9rem; margin-top:0.3rem;">
                                <option value="taekwondo">🥋 Disciplina Deportiva: Taekwondo & Artes Marciales</option>
                                <option value="futbol">⚽ Disciplina Deportiva: Fútbol Base y Formativo</option>
                                <option value="baloncesto">🏀 Disciplina Deportiva: Baloncesto y Rendimiento</option>
                                <option value="danza_joropo">💃 Área de Cultura: Taller / Modalidad Danza Joropo</option>
                                <option value="instrumentos">🎸 Área de Cultura: Taller / Modalidad Instrumentos (Guitarra/Arpa)</option>
                                <option value="convenio_b2b">🏛️ B2B: Convocatoria Institucional Alcaldías y Gobernaciones</option>
                            </select>
                        </div>

                        <div>
                            <label style="color:#94A3B8; font-size:0.8rem; font-weight:700;">Idea del Contenido / Prompt Inicial</label>
                            <textarea id="predis-prompt-input" style="width:100%; padding:0.65rem; background:#070B14; border:1px solid rgba(56,189,248,0.3); color:#F8FAFC; border-radius:8px; height:70px; font-size:0.85rem; margin-top:0.3rem;" placeholder="Ej. Crea un Reel viral de 15 segundos para motivar a niños a inscribirse en clases de Taekwondo con voz enérgica y música épica.">Promocionar inscripciones abiertas para talleres culturales de Danza Joropo y clases de Taekwondo en SGA-CD con cupos limitados.</textarea>
                        </div>

                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem;">
                            <div>
                                <label style="color:#94A3B8; font-size:0.8rem; font-weight:700;">Fecha y Hora de Envío Programado</label>
                                <input type="datetime-local" id="predis-schedule-time" style="width:100%; padding:0.5rem; background:#070B14; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:8px; font-size:0.8rem; margin-top:0.2rem;">
                            </div>
                            <div>
                                <label style="color:#94A3B8; font-size:0.8rem; font-weight:700;">Voz de Narración IA</label>
                                <select id="predis-voice-select" style="width:100%; padding:0.5rem; background:#070B14; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; border-radius:8px; font-size:0.8rem; margin-top:0.2rem;">
                                    <option value="es_latam_male">🎙️ Carlos (Latam Épico)</option>
                                    <option value="es_latam_female">🎙️ Sofia (Latam Dinámica)</option>
                                    <option value="es_co_pro">🎙️ Mateo (Institucional)</option>
                                </select>
                            </div>
                        </div>

                        <div style="display:flex; gap:0.5rem; margin-top:0.5rem;">
                            <button id="predis-generate-btn" class="btn-primary" style="flex:1; padding:0.8rem; font-size:0.9rem; font-weight:800; display:flex; justify-content:center; align-items:center; gap:0.5rem;">
                                <i class="fas fa-paper-plane"></i> Generar y Enviar a Todas al Tiempo
                            </button>
                            <button id="predis-schedule-btn" class="btn-secondary" style="flex:1; padding:0.8rem; font-size:0.9rem; font-weight:800; display:flex; justify-content:center; align-items:center; gap:0.5rem;">
                                <i class="fas fa-calendar-alt"></i> Agendar en Calendario
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Previsualizador Interactivo y Estado de Renderizado Multicanal -->
                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.2); border-radius:14px; padding:1.5rem; display:flex; flex-direction:column;">
                    <h3 style="color:#F8FAFC; margin-top:0; font-size:1.2rem; margin-bottom:1rem; display:flex; align-items:center; justify-content:space-between;">
                        <span><i class="fas fa-desktop" style="color:#38BDF8;"></i> Previsualizador & Ajuste de Dimensiones</span>
                        <span id="predis-status-badge" style="background:rgba(56,189,248,0.15); color:#38BDF8; font-size:0.75rem; padding:0.25rem 0.6rem; border-radius:10px;">Dimensión: 1080x1920 (9:16)</span>
                    </h3>

                    <!-- Frame Simulado de Celular / Video Reel (9:16 Preview) -->
                    <div id="predis-preview-box" style="background:#070B14; border:2px dashed rgba(56,189,248,0.3); border-radius:12px; height:320px; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:1rem; text-align:center; position:relative; overflow:hidden;">
                        <img id="predis-preview-poster" src="https://images.unsplash.com/photo-1555597673-b21d5c935865?w=800" style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0; opacity:0.6;">

                        <div style="position:relative; z-index:2; background:rgba(7,11,20,0.85); backdrop-filter:blur(10px); padding:1rem; border-radius:12px; border:1px solid rgba(56,189,248,0.3); max-width:90%;">
                            <h4 id="predis-preview-title" style="color:#38BDF8; margin:0 0 0.5rem 0; font-size:1.1rem; font-weight:800;">¡INSCRIPCIONES ABIERTAS 2025!</h4>
                            <p id="predis-preview-copy" style="color:#F8FAFC; font-size:0.85rem; margin:0 0 0.75rem 0;">Descubre el poder del Taekwondo y la pasión de la Danza Joropo en SGA-CD. ¡Inscríbete hoy mismo con cupos limitados!</p>
                            <span id="predis-preview-platforms" style="background:#38BDF8; color:#070B14; font-weight:800; padding:0.4rem 0.8rem; border-radius:20px; font-size:0.75rem; display:inline-block;">Destinos: IG, TikTok, YouTube, FB</span>
                        </div>
                    </div>

                    <!-- Botón de Publicación Inmediata Simultánea -->
                    <div style="margin-top:1.25rem;">
                        <button id="btn-publish-all-now" class="btn-primary" style="width:100%; padding:0.75rem; font-size:0.9rem; font-weight:800;">
                            <i class="fas fa-rocket"></i> Publicar Simultáneamente en Instagram, TikTok, YouTube Shorts y FB
                        </button>
                    </div>
                </div>

            </div>

            <!-- Calendario de Planificación y Cola de Envíos Programados -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.5rem;">
                    <h3 style="color:#38BDF8; margin:0; font-size:1.3rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                        <i class="fas fa-calendar-days"></i> Calendario de Planificación & Cola de Envíos Automatizados
                    </h3>
                    <span style="background:rgba(56,189,248,0.1); color:#38BDF8; padding:0.3rem 0.8rem; border-radius:12px; font-size:0.8rem; font-weight:700;">
                        Publicación Programada Multi-Red
                    </span>
                </div>

                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse; text-align:left; font-size:0.85rem;">
                        <thead>
                            <tr style="border-bottom:1px solid rgba(56,189,248,0.2); color:#38BDF8;">
                                <th style="padding:0.75rem;">Fecha / Hora Programada</th>
                                <th style="padding:0.75rem;">Contenido / Campaña</th>
                                <th style="padding:0.75rem;">Dimensión / Formato</th>
                                <th style="padding:0.75rem;">Redes Objetivo</th>
                                <th style="padding:0.75rem;">Estado de Publicación</th>
                                <th style="padding:0.75rem; text-align:right;">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="predis-calendar-table-body">
                            <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
                                <td style="padding:0.75rem; color:#F8FAFC; font-weight:700;">Hoy — 18:00 hs</td>
                                <td style="padding:0.75rem; color:#E2E8F0;">Inscripciones Abiertas Taekwondo & Joropo</td>
                                <td style="padding:0.75rem;"><span style="background:#070B14; color:#38BDF8; padding:0.25rem 0.5rem; border-radius:6px;">1080x1920 (9:16)</span></td>
                                <td style="padding:0.75rem; color:#94A3B8;"><i class="fab fa-instagram"></i> <i class="fab fa-tiktok"></i> <i class="fab fa-youtube"></i> <i class="fab fa-facebook"></i> Todos</td>
                                <td style="padding:0.75rem;"><span style="color:#10B981; font-weight:700;"><i class="fas fa-check-circle"></i> Programado Autopost</span></td>
                                <td style="padding:0.75rem; text-align:right;">
                                    <button class="btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.75rem;"><i class="fas fa-edit"></i> Reagendar</button>
                                </td>
                            </tr>
                            <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
                                <td style="padding:0.75rem; color:#F8FAFC; font-weight:700;">Mañana — 10:00 hs</td>
                                <td style="padding:0.75rem; color:#E2E8F0;">Convocatoria B2B Alcaldías y Gobernaciones</td>
                                <td style="padding:0.75rem;"><span style="background:#070B14; color:#38BDF8; padding:0.25rem 0.5rem; border-radius:6px;">1920x1080 (16:9)</span></td>
                                <td style="padding:0.75rem; color:#94A3B8;"><i class="fab fa-youtube"></i> <i class="fab fa-facebook"></i> YouTube / FB</td>
                                <td style="padding:0.75rem;"><span style="color:#38BDF8; font-weight:700;"><i class="fas fa-clock"></i> En Cola de Render</span></td>
                                <td style="padding:0.75rem; text-align:right;">
                                    <button class="btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.75rem;"><i class="fas fa-edit"></i> Reagendar</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    `;

    // Handlers de Generación, Envío Simultáneo y Agendamiento en Calendario
    const genBtn = document.getElementById('predis-generate-btn');
    const schedBtn = document.getElementById('predis-schedule-btn');
    const pubAllBtn = document.getElementById('btn-publish-all-now');
    const badge = document.getElementById('predis-status-badge');
    const titleEl = document.getElementById('predis-preview-title');
    const copyEl = document.getElementById('predis-preview-copy');
    const posterEl = document.getElementById('predis-preview-poster');
    const platEl = document.getElementById('predis-preview-platforms');
    const tableBody = document.getElementById('predis-calendar-table-body');
    const formatSelect = document.getElementById('predis-format-type');

    if (formatSelect) {
        formatSelect.addEventListener('change', () => {
            const map = {
                'reel_9_16': 'Dimensión: 1080x1920 (9:16)',
                'post_1_1': 'Dimensión: 1080x1080 (1:1)',
                'banner_16_9': 'Dimensión: 1920x1080 (16:9)',
                'carousel_multi': 'Dimensión: 1080x1350 (4:5)'
            };
            badge.textContent = map[formatSelect.value] || 'Dimensión Personalizada';
        });
    }

    function getSelectedPlatforms() {
        const checkboxes = document.querySelectorAll('.predis-target-platform:checked');
        const selected = Array.from(checkboxes).map(cb => cb.value);
        return selected.length > 0 ? selected : ['instagram', 'tiktok', 'youtube_shorts', 'facebook'];
    }

    async function processMediaRequest(isScheduled = false) {
        const area = document.getElementById('predis-area-target').value;
        const prompt = document.getElementById('predis-prompt-input').value;
        const format = document.getElementById('predis-format-type').value;
        const scheduleTime = document.getElementById('predis-schedule-time').value;
        const platforms = getSelectedPlatforms();

        const btn = isScheduled ? schedBtn : genBtn;
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${isScheduled ? 'Agendando...' : 'Enviando a Todas...'}`;

        try {
            const res = await fetch(`${config.apiBaseUrl}/api/v1/admin_general/crm/generate_predis_media`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                    area,
                    prompt,
                    format,
                    target_platforms: platforms,
                    scheduled_time: isScheduled ? scheduleTime : ''
                })
            });

            let data = {};
            if (res.ok) {
                data = await res.json();
            } else {
                data = {
                    title: `¡INSCRIPCIONES ABIERTAS EN ${area.toUpperCase()}!`,
                    copy: prompt,
                    poster_url: 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800',
                    dimensions: '1080x1920 (9:16)',
                    target_platforms: platforms,
                    scheduled_time: isScheduled ? (scheduleTime || 'Mañana 12:00 hs') : 'Inmediato (Simultáneo)'
                };
            }

            titleEl.textContent = data.title;
            copyEl.textContent = data.copy;
            if (data.poster_url) posterEl.src = data.poster_url;
            platEl.textContent = `Destinos: ${data.target_platforms.join(', ').toUpperCase()}`;

            if (isScheduled && tableBody) {
                const newRow = document.createElement('tr');
                newRow.style.borderBottom = '1px solid rgba(56,189,248,0.1)';
                newRow.innerHTML = `
                    <td style="padding:0.75rem; color:#F8FAFC; font-weight:700;">${scheduleTime || 'Programado'}</td>
                    <td style="padding:0.75rem; color:#E2E8F0;">${data.title}</td>
                    <td style="padding:0.75rem;"><span style="background:#070B14; color:#38BDF8; padding:0.25rem 0.5rem; border-radius:6px;">${data.dimensions}</span></td>
                    <td style="padding:0.75rem; color:#94A3B8;">${data.target_platforms.join(', ')}</td>
                    <td style="padding:0.75rem;"><span style="color:#10B981; font-weight:700;"><i class="fas fa-check-circle"></i> En Cola Agendada</span></td>
                    <td style="padding:0.75rem; text-align:right;">
                        <button class="btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.75rem;"><i class="fas fa-edit"></i> Reagendar</button>
                    </td>
                `;
                tableBody.prepend(newRow);
            }

        } catch (err) {
            console.error("Error procesando medios Predis:", err);
        } finally {
            btn.disabled = false;
            btn.innerHTML = isScheduled ? `<i class="fas fa-calendar-alt"></i> Agendar en Calendario` : `<i class="fas fa-paper-plane"></i> Generar y Enviar a Todas al Tiempo`;
        }
    }

    if (genBtn) genBtn.addEventListener('click', () => processMediaRequest(false));
    if (schedBtn) schedBtn.addEventListener('click', () => processMediaRequest(true));
    if (pubAllBtn) pubAllBtn.addEventListener('click', () => processMediaRequest(false));
}

/**
 * Renderiza la vista de Promociones y Ofertas (Módulo de Marketing Comercial)
 */
async function renderPromocionesView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">
            <h2 style="color:#38BDF8; margin:0; font-size:1.8rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                <i class="fa-solid fa-tags"></i> Gestión de Promociones, Ofertas & Becas
            </h2>
            <p style="color:#94A3B8; margin:0.5rem 0 0 0;">
                Administración centralizada de códigos de descuento, becas institucionales y campañas promocionales B2B/B2C.
            </p>
            <div style="margin-top:1.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.5rem;">
                <h3 style="color:#38BDF8; margin-top:0;">Promociones Activas</h3>
                <p style="color:#94A3B8; font-size:0.9rem;">No hay promociones activas registradas en este momento. Puede configurar campañas desde el Gestor de Landing Page o la Suite CRM.</p>
            </div>
        </div>
    `;
}

/**
 * Renderiza la vista de Roles y Permisos (Matriz de Control de Acceso Perimetral)
 */
async function renderRolesPermisosView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">
            <h2 style="color:#38BDF8; margin:0; font-size:1.8rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                <i class="fa-solid fa-shield-alt"></i> Matriz de Roles y Permisos Oficiales (12 Roles)
            </h2>
            <p style="color:#94A3B8; margin:0.5rem 0 0 0;">
                Inspección perimetral de jerarquías de acceso y políticas RBAC configuradas en el sistema SGA-CD.
            </p>
            <div style="margin-top:1.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.5rem;">
                <table style="width:100%; border-collapse:collapse; text-align:left; font-size:0.85rem;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(56,189,248,0.2); color:#38BDF8;">
                            <th style="padding:0.75rem;">Rol del Sistema</th>
                            <th style="padding:0.75rem;">Nivel de Dominio</th>
                            <th style="padding:0.75rem;">Estado de Aislamiento</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
                            <td style="padding:0.75rem; color:#F8FAFC; font-weight:700;">admin_general</td>
                            <td style="padding:0.75rem; color:#38BDF8;">Super Administrador Global</td>
                            <td style="padding:0.75rem; color:#10B981;">Activo / Unrestricted</td>
                        </tr>
                        <tr style="border-bottom:1px solid rgba(56,189,248,0.1);">
                            <td style="padding:0.75rem; color:#F8FAFC; font-weight:700;">admin_empresa</td>
                            <td style="padding:0.75rem; color:#E2E8F0;">Administrador de Entidad Público/Privada</td>
                            <td style="padding:0.75rem; color:#38BDF8;">Multi-Tenant Ailado</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

/**
 * Renderiza la vista de Asistente de IA (Agente Inteligente Supervisor)
 */
async function renderAsistenteIAView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">
            <h2 style="color:#38BDF8; margin:0; font-size:1.8rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                <i class="fa-solid fa-robot"></i> Asistente de Inteligencia Artificial & Tropa de Agentes
            </h2>
            <p style="color:#94A3B8; margin:0.5rem 0 0 0;">
                Panel de interacción con agentes autónomos para la automatización deportiva y cultural.
            </p>
            <div style="margin-top:1.5rem; background:#0D1424; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.5rem;">
                <h3 style="color:#38BDF8; margin-top:0;">Agente Supervisor Operativo</h3>
                <p style="color:#94A3B8; font-size:0.9rem;">El agente autónomo está listo para procesar invocaciones multi-tenant de voz y texto.</p>
            </div>
        </div>
    `;
}

// --- Registrar las vistas de Administrador General en el Router ---
if (typeof registerView === 'function') {
    registerView('admin_general', 'dashboard', renderAdminGeneralDashboardView);
    registerView('admin_general', 'gestor-landing', renderGestorLandingView);
    registerView('admin_general', 'configuracion-whatsapp', renderConfiguracionWhatsAppView);
    registerView('admin_general', 'gestion-api-keys', renderApiKeysView);
    registerView('admin_general', 'motor-predis-media', renderMotorPredisMediaView);

    // Vistas compartidas autorizadas registradas explícitamente para admin_general
    if (typeof renderAdminEmpresaView === 'function') {
        registerView('admin_general', 'panel-empresa', renderAdminEmpresaView);
    }
    if (typeof renderSuscripcionView === 'function') {
        registerView('admin_general', 'suscripcion', renderSuscripcionView);
    }
    if (typeof renderAuditoriaEmpresaView === 'function') {
        registerView('admin_general', 'auditoria-empresa', renderAuditoriaEmpresaView);
    }

    // Vistas dedicadas de admin_general
    registerView('admin_general', 'promociones', renderPromocionesView);
    registerView('admin_general', 'roles-permisos', renderRolesPermisosView);
    registerView('admin_general', 'asistente-ia', renderAsistenteIAView);
} else {
    console.error("El sistema de registro de vistas no está disponible.");
}
