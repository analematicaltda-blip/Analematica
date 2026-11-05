document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('accessToken');
    const logoutBtn = document.getElementById('logout-btn');
    let currentUser = null;

    // --- Helper for XSS Sanitization ---
    function sanitizeHTML(str) {
        if (!str) return '';
        const temp = document.createElement('div');
        temp.textContent = String(str);
        return temp.innerHTML;
    }

    // --- 1. Proteger la ruta y validar Token JWT con Expiración ---
    if (!token) {
        window.SGAWorkspace?.remember();
        window.location.href = 'login.html';
        return;
    }

    try {
        const payloadBase64 = token.split('.')[1];
        if (!payloadBase64) throw new Error('JWT inválido');
        const decodedPayload = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(payloadBase64.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0))));
        const currentTime = Math.floor(Date.now() / 1000);

        if (decodedPayload.exp && decodedPayload.exp < currentTime) {
            console.warn('El token JWT ha expirado. Redirigiendo a inicio de sesión.');
            localStorage.clear();
            window.location.href = 'login.html';
            return;
        }
    } catch (e) {
        console.error('Error al verificar integridad o caducidad de la sesión:', e);
        localStorage.clear();
        window.location.href = 'login.html';
        return;
    }

    // --- 2. Configurar el botón de cierre de sesión y supresión ARCO ---
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.clear();
            window.location.href = 'login.html';
        });
    }

    const arcoDeleteBtn = document.getElementById('arco-delete-btn');
    if (arcoDeleteBtn) {
        arcoDeleteBtn.addEventListener('click', async () => {
            const confirmDelete = confirm('¿Estás seguro de ejercer tu Derecho ARCO de eliminación? Tus datos personales serán anonimizados y tu cuenta desactivada.');
            if (!confirmDelete) return;

            try {
                const response = await fetch(`${config.apiBaseUrl}/api/v1/auth/me/data`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message || 'Tus datos han sido anonimizados exitosamente.');
                    localStorage.clear();
                    window.location.href = 'login.html';
                } else {
                    alert(`Error: ${data.detail || 'No se pudo procesar la solicitud.'}`);
                }
            } catch (err) {
                console.error('Error procesando supresión de datos:', err);
                alert('No se pudo conectar con el servidor.');
            }
        });
    }

    // --- Sidebar Collapsible & Mobile Responsive Mechanics (GSAP Orchestration) ---
    function setupSidebarMechanics() {
        const sidebar = document.getElementById('app-sidebar');
        const toggle = document.getElementById('sidebar-toggle-btn');
        const hamburger = document.getElementById('mobile-hamburger-btn');
        const overlay = document.getElementById('sidebar-overlay');
        const nav = document.getElementById('app-nav');
        const mobile = window.matchMedia('(max-width: 768px)');
        if (!sidebar || !toggle || !hamburger || !overlay) return;
        hamburger.setAttribute('aria-controls', sidebar.id);
        hamburger.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-expanded', 'true');
        const close = (restoreFocus = false) => {
            sidebar.classList.remove('mobile-open');
            sidebar.inert = mobile.matches;
            overlay.classList.remove('active');
            sidebar.removeAttribute('aria-modal');
            sidebar.removeAttribute('role');
            hamburger.setAttribute('aria-expanded', 'false');
            if (restoreFocus) hamburger.focus();
        };
        const focusable = () => [...sidebar.querySelectorAll('button, a[href], input, select')]
            .filter(el => !el.disabled && el.getClientRects().length);
        hamburger.addEventListener('click', () => {
            if (sidebar.classList.contains('mobile-open')) return close(true);
            sidebar.classList.remove('collapsed');
            sidebar.classList.add('mobile-open');
            sidebar.inert = false;
            overlay.classList.add('active');
            sidebar.setAttribute('role', 'dialog');
            sidebar.setAttribute('aria-modal', 'true');
            sidebar.setAttribute('aria-label', 'Navegación principal');
            hamburger.setAttribute('aria-expanded', 'true');
            focusable()[0]?.focus();
        });
        toggle.addEventListener('click', () => {
            const collapsed = sidebar.classList.toggle('collapsed');
            toggle.setAttribute('aria-expanded', String(!collapsed));
            toggle.setAttribute('aria-label', collapsed ? 'Expandir menú' : 'Retraer menú');
        });
        overlay.addEventListener('click', () => close(true));
        nav?.addEventListener('click', e => {
            if (e.target.closest('.nav-group-title') && sidebar.classList.contains('collapsed')) toggle.click();
            if (e.target.closest('a[data-view]') && mobile.matches) close(true);
        });
        document.addEventListener('keydown', e => {
            if (!sidebar.classList.contains('mobile-open')) return;
            if (e.key === 'Escape') close(true);
            if (e.key === 'Tab') {
                const items = focusable();
                const first = items[0], last = items[items.length - 1];
                if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
                else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
            }
        });
        mobile.addEventListener('change', () => { close(); sidebar.classList.remove('collapsed'); toggle.setAttribute('aria-expanded', 'true'); });
        close();
    }

    // --- Silent-Refresh Cycle (Automated JWT Token Renewal) ---
    function startSilentTokenRefresh() {
        setInterval(async () => {
            const currentToken = localStorage.getItem('accessToken');
            if (!currentToken) return;

            try {
                const payloadBase64 = currentToken.split('.')[1];
                if (!payloadBase64) return;
                const decoded = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(payloadBase64.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0))));
                const now = Math.floor(Date.now() / 1000);
                const remainingSec = decoded.exp - now;

                if (remainingSec > 0 && remainingSec < 300) {
                    console.log('[Security]: Renovando token de sesión JWT silenciosamente...');
                    const response = await fetch(`${config.apiBaseUrl}/api/v1/auth/refresh`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${currentToken}`, 'Content-Type':'application/json' },
                        body: JSON.stringify({refresh_token:localStorage.getItem('refreshToken')})
                    });
                    if (response.ok) {
                        const data = await response.json();
                        if (data.access_token) {
                            localStorage.setItem('accessToken', data.access_token);
                        }
                    }
                }
            } catch (err) {
                console.warn('[Security]: Silent refresh adaptativo:', err);
            }
        }, 60000);
    }

    // --- 3. Cargar datos del usuario y renderizar la aplicación ---
    function initializeApp() {
        const userRoles = JSON.parse(localStorage.getItem('userRoles') || '[]');
        const userId = localStorage.getItem('userId');
        const userName = localStorage.getItem('userName');

        if (!userRoles || !userId || !userName) {
            console.error('Información de usuario incompleta en localStorage.');
            localStorage.clear();
            window.location.href = 'login.html';
            return;
        }

        currentUser = {
            id: userId,
            name: userName,
            roles: userRoles,
            primaryRole: userRoles[0] || 'default'
        };

        renderUserInfo(currentUser);
        if (!window.SGAWorkspace) renderNavigation(currentUser.primaryRole);
        setupEventListeners(token, currentUser.primaryRole);
        setupSidebarMechanics();
        translatePage();
        initializeNotifications();
        startSilentTokenRefresh();
        if (window.SGAWorkspace) window.SGAWorkspace.start();
        else renderContentForView('dashboard', token, currentUser.primaryRole);
    }

    // --- 4. Configurar listeners de eventos ---
    function setupEventListeners(authToken, roleName) {
        const floatingAgentIcon = document.getElementById('floating-agent-icon');
        const closeChatBtn = document.getElementById('close-chat-btn');
        const chatForm = document.getElementById('chat-form');

        if (floatingAgentIcon) floatingAgentIcon.addEventListener('click', () => toggleChat(true));
        if (closeChatBtn) closeChatBtn.addEventListener('click', () => toggleChat(false));
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const input = document.getElementById('chat-input');
                if (input.value.trim()) {
                    sendChatMessage(input.value.trim(), authToken);
                    input.value = '';
                }
            });
        }

        // Micrófono para nota de voz
        const micBtn = document.getElementById('chat-mic-btn');
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        if (micBtn) {
            micBtn.addEventListener('click', async () => {
                if (!isRecording) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);

                        mediaRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                            audioChunks = [];
                            sendAudioMessage(audioBlob, authToken);
                            stream.getTracks().forEach(track => track.stop());
                        };

                        mediaRecorder.start();
                        isRecording = true;
                        micBtn.style.color = '#38BDF8';
                        addMessageToLog('Grabando audio... habla ahora. Pulsa de nuevo para finalizar.', 'agent');

                    } catch (err) {
                        console.error("Error al acceder al micrófono:", err);
                        addMessageToLog('Error: No se pudo acceder al dispositivo de captura de audio.', 'agent');
                    }
                } else {
                    if (mediaRecorder) mediaRecorder.stop();
                    isRecording = false;
                    micBtn.style.color = '';
                }
            });
        }

        const navContainer = document.getElementById('app-nav');
        const langSelect = document.getElementById('language-select');
        const themeToggle = document.getElementById('theme-toggle');

        if (navContainer) {
            navContainer.addEventListener('click', (e) => {
                const link = e.target.closest('a[data-view]');
                if (link) {
                    e.preventDefault();
                    const viewName = link.dataset.view;
                    if (viewName) {
                        renderContentForView(viewName, authToken, roleName);
                    }
                }
            });
        }
        if (langSelect) langSelect.addEventListener('change', (e) => setLanguage(e.target.value));

        function applyTheme(theme) {
            document.body.setAttribute('data-theme', theme);
            if (themeToggle) themeToggle.checked = theme === 'dark';
        }
        function toggleTheme() {
            const newTheme = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        }
        if (themeToggle) themeToggle.addEventListener('change', toggleTheme);
        const savedTheme = localStorage.getItem('theme') || 'dark';
        applyTheme(savedTheme);
    }

    // --- 5. Agente de IA y Chat Sanitizado ---
    let chatInitiated = false;

    function toggleChat(show) {
        const chatContainer = document.getElementById('agent-chat-container');
        if (!chatContainer) return;

        if (show) {
            chatContainer.style.display = 'flex';
            if (!chatInitiated) {
                startAgentConversation(token);
                chatInitiated = true;
            }
        } else {
            chatContainer.style.display = 'none';
        }
    }

    function addMessageToLog(messageContent, sender) {
        const chatLog = document.getElementById('chat-log');
        if (!chatLog) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${sender}`;

        if (typeof messageContent === 'object' && messageContent.image_url) {
            const textP = document.createElement('p');
            textP.textContent = messageContent.text || '';
            msgDiv.appendChild(textP);

            const img = document.createElement('img');
            img.src = `${config.apiBaseUrl}${messageContent.image_url}`;
            img.alt = 'Gráfico generado por IA';
            img.className = 'chat-image';
            msgDiv.appendChild(img);

        } else {
            const rawText = typeof messageContent === 'string' ? messageContent : (messageContent.text || '');
            msgDiv.textContent = rawText;
        }

        chatLog.appendChild(msgDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    async function startAgentConversation(authToken) {
        addMessageToLog('Conectando con el asistente de inteligencia artificial...', 'agent');
        await sendChatMessage("", authToken, true);
    }

    async function sendAudioMessage(audioBlob, authToken) {
        addMessageToLog('Procesando nota de voz...', 'user');
        try {
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'grabacion.webm');
            const response = await fetch(`${config.apiBaseUrl}/api/v1/agent/invoke-voice`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${authToken}` },
                body: formData
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al procesar el audio.');
            }
            const structuredResponse = await response.json();
            addMessageToLog(structuredResponse, 'agent');
            speakText(structuredResponse.text);
        } catch (error) {
            addMessageToLog({ text: `Error de audio: ${error.message}` }, 'agent');
        }
    }

    async function sendChatMessage(prompt, authToken, isInitial = false) {
        if (!isInitial) {
            addMessageToLog(prompt, 'user');
        }
        try {
            const response = await fetch(`${config.apiBaseUrl}/api/v1/agent/invoke`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
                body: JSON.stringify({
                    prompt: prompt,
                    area: "Cultura",
                    thread_id: `user_${currentUser.id}`
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error en la respuesta del agente.');
            }
            const structuredResponse = await response.json();
            addMessageToLog(structuredResponse, 'agent');
            if (structuredResponse.text) speakText(structuredResponse.text);
        } catch (error) {
            addMessageToLog({ text: `Atención: Servidor de agentes operando en modo adaptativo. (${error.message})` }, 'agent');
        }
    }

    // --- 6. Renderizado de Información de Usuario Sanitizada ---
    function renderUserInfo(user) {
        const userInfoDiv = document.getElementById('user-info');
        if (userInfoDiv) {
            const cleanName = sanitizeHTML(user.name);
            const cleanRoles = sanitizeHTML(user.roles.join(', '));
            userInfoDiv.innerHTML = `
                <p><strong>${cleanName}</strong></p>
                <span>${cleanRoles}</span>
            `;
        }
    }

    function initializeNotifications() {
        const bell = document.querySelector('.notification-bell');
        if (bell) {
            bell.addEventListener('click', () => {
                alert('No tienes notificaciones pendientes.');
            });
        }
    }

    // --- 7. Text-to-Speech (TTS) ---
    function speakText(text) {
        if ('speechSynthesis' in window && text) {
            const floatingIcon = document.getElementById('floating-agent-icon');
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'es-ES';
            utterance.volume = 1;

            utterance.onstart = () => {
                if (floatingIcon) floatingIcon.classList.add('is-speaking');
            };

            utterance.onend = () => {
                if (floatingIcon) floatingIcon.classList.remove('is-speaking');
            };

            window.speechSynthesis.speak(utterance);
        }
    }

    // Iniciar
    initializeApp();
});
