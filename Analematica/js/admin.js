/**
 * ANALEMÁTICA - LÓGICA DEL PANEL DE ADMINISTRADOR GENERAL & CONSOLA MILITAR DE AGENTES (DEAA-V2.1)
 * Paleta Estricta: Azul Metálico y Azul Claro únicamente. Prohibidos: Blanco, Rojo, Amarillo.
 */

const STORAGE_KEY = 'analematica_landing_config';
const LEADS_KEY = 'analematica_leads_data';

// Configuración por defecto canónica de la landing page Analemática
const DEFAULT_CONFIG = {
    header: {
        brand_name: "ANALEMÁTICA",
        brand_tag: "INGENIERÍA MODULAR",
        brand_logo: "assets/analema-logo.svg",
        nav_cta_text: "Diagnóstico",
        nav_cta_href: "#contacto"
    },
    hero: {
        badge: "Plataforma Modular Multi-Inquilino 2031",
        title: 'Sincronizamos la gestión institucional con el <span class="highlight-cyan">ritmo de vida</span> de los ciudadanos.',
        subtitle: "En Analemática transformamos procesos administrativos complejos en soluciones digitales multi-inquilino, fluidas y seguras. Automatice la operación de su entidad, proteja sus datos y devuélvale el control del tiempo a su comunidad.",
        btn_primary: "Agendar Consultoría Técnica",
        btn_secondary: "Explorar Ecosistemas",
        metrics: [
            { value: "40%", label: "Menor tiempo de espera" },
            { value: "100%", label: "Aislamiento Multi-Tenant" },
            { value: "24/7", label: "Auditoría STAR Inmutable" }
        ],
        card_badge: "PRECISIÓN DE ALTO NIVEL",
        card_legend: "Arquitectura cuántica de datos y sincronización armónica de tiempos administrativos."
    },
    desafio: {
        tag: "EL DESAFÍO DE LA GESTIÓN CIUDADANA",
        title: "El costo invisible de los sistemas obsoletos.",
        desc: "Gestionar una institución o entidad pública con herramientas del pasado fragmenta la información, genera cuellos de botella y sobrecarga al personal administrativo. Cuando los ciudadanos se enfrentan a plataformas lentas, procesos desconectados y trámites manuales, la confianza institucional se debilita. El verdadero problema no es la falta de voluntad, sino la ausencia de una infraestructura tecnológica moderna, integrada y auditable que pueda escalar de forma segura al ritmo que la sociedad lo exige.",
        cards: [
            {
                title: "Pérdida Crítica de Tiempo",
                desc: "Filas interminables, radicación presencial y demoras burocráticas que paralizan los trámites ciudadanos y consumen horas valiosas de la comunidad."
            },
            {
                title: "Bases de Datos Desconectadas",
                desc: "Silos de información aislados que duplican registros, dificultan el cruce de datos interdepartamental y provocan incongruencias operativas."
            },
            {
                title: "Falta de Trazabilidad y Auditoría",
                desc: "Vulnerabilidad ante manipulaciones, falta de bitácoras inmutables y opacidad en la rendición de cuentas que deterioran la confianza ciudadana."
            }
        ]
    },
    filosofia: {
        tag: "LA FILOSOFÍA DE ANALEMÁTICA",
        title: "Precisión e ingeniería para ordenar el caos administrativo.",
        desc: "Inspirados en la precisión del analema —la curva perfecta que traza el Sol para marcar el paso del tiempo—, en Analemática diseñamos software bajo estándares de ingeniería de alta precisión. No creamos parches digitales; estructuramos ecosistemas modulares en Python que automatizan flujos operativos, garantizan la inmutabilidad de los registros y simplifican el día a día de las personas. Convertimos los procesos burocráticos rígidos en ciclos dinámicos, predecibles y accesibles para todos.",
        pillars: [
            {
                title: "Precisión Temporal",
                desc: "Sincronización exacta de cada fase administrativa y optimización de tiempos de respuesta institucionales."
            },
            {
                title: "Ingeniería Robusta en Python",
                desc: "Arquitecturas backend asíncronas de ultra alto rendimiento, tolerantes a fallos y altamente escalables."
            }
        ],
        diagram_caption: "La Curva del Analema: Símbolo de constancia astronómica traducido a gobernanza digital y precisión operativa permanente."
    },
    mision: {
        title: "Misión",
        text: "Desarrollar soluciones tecnológicas innovadoras y de alta precisión que automaticen la gestión organizativa, optimizando el tiempo y simplificando la vida de los ciudadanos y las comunidades. Nos comprometemos a transformar la complejidad operativa en procesos fluidos, accesibles y multientorno, garantizando la seguridad, la inclusión y la eficiencia en cada interacción diaria."
    },
    vision: {
        title: "Visión 2031",
        text: "Posicionarse para el año 2031 como la plataforma tecnológica de referencia en sistemas de gestión modular y multi-inquilino a nivel regional, siendo reconocidos por marcar el ritmo de la transformación digital sustentada en inteligencia artificial. Aspiramos a conectar comunidades, instituciones y ciudadanos bajo un ecosistema digital integrado, seguro y global que evolucione de manera constante y armónica."
    },
    verticales: {
        tag: "CATÁLOGO MODULAR ESPECIALIZADO",
        title: "Ecosistemas modulares para cada sector.",
        desc: "Nuestra arquitectura se adapta a las necesidades específicas de su organización a través de módulos especializados listos para su implementación:",
        cards: [
            {
                title: "ERP para Prestadores de Servicio Turístico",
                desc: "Planificación integral de recursos empresariales para el sector turístico: gestión centralizada de reservas, inventarios de alojamiento y tours, facturación electrónica, control de comisiones y nómina especializada en operaciones turísticas."
            },
            {
                title: "Información Turística y Geolocalización",
                desc: "Sistema de información turística, geolocalización de destinos y ofertas turísticas: mapeo interactivo de atractivos patrimoniales y naturales, catálogo inteligente de ofertas y experiencias, rutas sugeridas en tiempo real y analítica de afluencia de visitantes."
            }
        ],
        sgacd: {
            title: "Formación Cultural y Deportiva (SGA-CD)",
            desc: "Optimice escuelas de formación, instructores y reservas de escenarios deportivos o culturales desde una sola plataforma. Administre disciplinas, talleres de danza e instrumentos con seguimiento biométrico y acreditaciones en tiempo real.",
            notice: "Al hacer clic en este módulo, será redireccionado de forma exclusiva a la página oficial de ventas e Onboarding del sistema SGA-CD.",
            btn_text: "Visitar Plataforma SGA-CD ↗",
            url: "/sga/"
        }
    },
    adn: {
        tag: "NUESTROS ESTÁNDARES DE INGENIERÍA",
        title: "Infraestructura robusta diseñada para el futuro.",
        desc: "Cada línea de código en Analemática está pensada para ofrecer la máxima seguridad y rendimiento. Implementamos arquitecturas Multi-Inquilino (Multi-Tenant) que garantizan un aislamiento total y seguro de los datos entre diferentes organizaciones en una misma instancia. Respaldamos la transparencia de su entidad mediante el sistema STAR, una bitácora de auditoría inmutable que rastrea acciones críticas en tiempo real, e integramos asistentes analíticos impulsados por Inteligencia Artificial (LangChain) para la generación predictiva de reportes y estadísticas avanzadas.",
        cards: [
            {
                title: "Arquitectura Multi-Inquilino (Multi-Tenant)",
                desc: "Esquema de aislamiento lógico estricto por institución. Cada alcaldía, instituto o entidad opera con independencia de datos, cifrado dedicado y alta concurrencia."
            },
            {
                title: "Bitácora de Auditoría Inmutable (STAR)",
                desc: "Registro criptográfico no repudiable de eventos y modificaciones en tiempo real. Máxima trazabilidad legal requerida por entidades públicas y órganos de control."
            },
            {
                title: "Agentes Analíticos con IA (LangChain)",
                desc: "Inteligencia analítica predictiva en Python para proyección de presupuestos, detección de patrones de demanda ciudadana y generación autónoma de informes ejecutivos."
            }
        ]
    },
    impacto: {
        tag: "BENEFICIOS TANGIBLES Y VALOR HUMANO",
        title: "Tecnología con impacto humano.",
        desc: "La verdadera innovación se mide en la calidad de vida de las personas. Al centralizar y automatizar sus operaciones con nuestras soluciones, las instituciones lograrán reducir hasta en un 40% los tiempos de espera en trámites y asignación de recursos. Gracias a nuestro módulo de internacionalización lingüística aplicada (MILA), garantizamos plataformas accesibles e inclusivas, eliminando las barreras del idioma y transformando la interacción digital entre el ciudadano y la organización en una experiencia transparente, rápida y libre de fricciones.",
        cards: [
            {
                pill: "40% AHORRO",
                title: "Reducción de Tiempos de Espera",
                desc: "Eliminación de filas presenciales y trámites engorrosos mediante radicación virtual inmediata y resolución ágil de peticiones ciudadanas."
            },
            {
                pill: "MILA INTEGRADO",
                title: "Inclusión Lingüística y Accesibilidad",
                desc: "Adaptabilidad total a comunidades diversas y dialectos regionales para garantizar que ningún ciudadano quede excluido de los servicios institucionales."
            },
            {
                pill: "100% TRANSPARENTE",
                title: "Confianza y Cercanía Comunitaria",
                desc: "Comunicación bidireccional clara, estados de trámites actualizados al segundo y rendición de cuentas pública sin intermediarios."
            }
        ]
    },
    contacto: {
        tag: "TRANSFORMACIÓN DIGITAL INMEDIATA",
        title: "Modernice su organización hoy mismo.",
        desc: "El camino hacia una gestión eficiente y ciudadana comienza con una infraestructura tecnológica correcta. Déjenos sus datos y uno de nuestros ingenieros senior de Analemática se pondrá en contacto con usted para realizar un diagnóstico técnico de sus sistemas actuales y diseñar una solución a la medida de sus desafíos operativos.",
        btn_text: "Enviar Solicitud de Diagnóstico",
        success_msg: "La solicitud quedó registrada en el CRM de Analemática para su atención por el equipo autorizado."
    },
    footer: {
        bio: "Desarrollamos soluciones de alta precisión para ordenar el caos administrativo y transformar la relación entre entidades y ciudadanos.",
        copyright: "© 2025 Analemática. Todos los derechos reservados. Desarrollado con precisión de ingeniería modular.",
        status: "Sistemas Operativos 99.98%"
    }
};

let currentConfig = null;
let publishedRevision=0;
let saving=false;
function mergeContent(defaults,published){const value=JSON.parse(JSON.stringify(defaults));for(const [key,item] of Object.entries(published||{})){if(item&&typeof item==='object'&&!Array.isArray(item))value[key]=mergeContent(value[key]||{},item);else value[key]=item;}return value;}


// Acceso y modificación segura de propiedades anidadas
function getNestedValue(obj, path) {
    return path.split('.').reduce((prev, curr) => prev ? prev[curr] : undefined, obj);
}

function setNestedValue(obj, path, value) {
    const keys = path.split('.');
    let cur = obj;
    for (let i = 0; i < keys.length - 1; i++) {
        if (!cur[keys[i]]) cur[keys[i]] = {};
        cur = cur[keys[i]];
    }
    cur[keys[keys.length - 1]] = value;
}

// Inicialización de datos
function loadConfig() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            currentConfig = JSON.parse(stored);
        } else {
            currentConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
        }
    } catch (e) {
        console.error("Error al cargar configuración:", e);
        currentConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
    }
}

// Poblar formulario con valores actuales
function populateForms() {
    const inputs = document.querySelectorAll('[data-key]');
    inputs.forEach(input => {
        const key = input.getAttribute('data-key');
        const val = getNestedValue(currentConfig, key);
        if (val !== undefined && val !== null) {
            input.value = val;
        }
    });
}

// Guardar configuración en localStorage
async function saveConfig(showToastMsg = true) {
    const inputs = document.querySelectorAll('[data-key]');
    inputs.forEach(input => {
        const key = input.getAttribute('data-key');
        setNestedValue(currentConfig, key, input.value);
    });

    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentConfig));

    if (!showToastMsg) return; // Local draft; publish explicitly with Guardar Todo.
    if(saving){showToast('Hay una publicación en curso. Espera antes de guardar de nuevo.');return;}
    saving=true;const button=document.getElementById('btnGlobalSave');if(button)button.disabled=true;
    try {const result=await AnaleConnection.request('/config',{authorized:true,method:'PUT',body:JSON.stringify({config:currentConfig,revision:publishedRevision})});publishedRevision=result.revision;showToast('Configuración publicada en el servidor de Analemática.');}
    catch(error){showToast(error.message+' El borrador local se conserva.');}
    finally{saving=false;if(button)button.disabled=false;}
}

// Toast de notificación
function showToast(msg) {
    const toast = document.getElementById('adminToast');
    const toastMsg = document.getElementById('toastMessage');
    if (toast && toastMsg) {
        toastMsg.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Manejo de tabs del sidebar
function setupTabs() {
    const tabButtons = document.querySelectorAll('.nav-tab-btn');
    const panes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');

            tabButtons.forEach(b => b.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPane = document.getElementById(tabId);
            if (targetPane) targetPane.classList.add('active');
            if(innerWidth<=1024){document.getElementById('corporate-sidebar')?.classList.remove('console-menu-open');document.getElementById('console-menu-toggle')?.setAttribute('aria-expanded','false');}
        });
    });
}

// Bandeja de Leads
async function renderLeads() {
    const tbody=document.getElementById('leadsTableBody');if(!tbody)return;
    try {const data=await AnaleConnection.request('/inquiries',{authorized:true});tbody.replaceChildren();
        for(const lead of data.leads){const row=document.createElement('tr');for(const key of ['fecha','nombre','entidad','correo','telefono']){const cell=document.createElement('td');cell.style.padding='0.6rem';cell.textContent=lead[key]||'';row.append(cell);}tbody.append(row);}
        if(!data.leads.length){const row=tbody.insertRow(),cell=row.insertCell();cell.colSpan=5;cell.textContent='No hay solicitudes registradas en el servidor.';}
    }catch(error){tbody.replaceChildren();const row=tbody.insertRow(),cell=row.insertCell();cell.colSpan=5;cell.textContent=error.message;}
}

// =============================================================================
// MOTOR TÁCTICO MILITAR: DILIGENCIADO & TECLEADO MECÁNICO AUTÓNOMO POR VOZ Y TEXTO
// =============================================================================
function appendTacticalLog(tag, message) {
    const container = document.getElementById('tacticalTerminalLogs');
    if (!container) return;

    const time = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    for(const [cls,value] of [['log-time','['+time+']'],['log-tag',tag+':'],['log-msg',message]]){const part=document.createElement('span');part.className=cls;part.textContent=value;entry.append(part);}
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

// Efecto de tecleado autónomo en el campo especificado
async function typeWriterIntoElement(element, text) {
    // Si la pestaña contenedora no está activa, activarla para visualización
    const parentPane = element.closest('.tab-pane');
    if (parentPane && !parentPane.classList.contains('active')) {
        const paneId = parentPane.id;
        const matchingBtn = document.querySelector(`.nav-tab-btn[data-tab="${paneId}"]`);
        if (matchingBtn) matchingBtn.click();
    }

    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    element.classList.add('typewriter-highlight');
    element.focus();
    element.value = '';

    const chars = text.split('');
    for (let i = 0; i < chars.length; i++) {
        element.value += chars[i];
        element.dispatchEvent(new Event('input', { bubbles: true }));
        await new Promise(r => setTimeout(r, 18));
    }

    element.dispatchEvent(new Event('change', { bubbles: true }));
    saveConfig(false);

    setTimeout(() => {
        element.classList.remove('typewriter-highlight');
    }, 1200);
}

// Instancia del Coronel Comandante de la Landing Page de Analemática
let coronelAnalematicaInstance = null;

function getCoronelAnalematica() {
    if (!coronelAnalematicaInstance && typeof window.CoronelAnalematica === 'function') {
        coronelAnalematicaInstance = new window.CoronelAnalematica(appendTacticalLog, showToast);
    }
    return coronelAnalematicaInstance;
}

// Intérprete semántico de órdenes de mando
let activeCommand=false,lastReversible=null,pendingCommand=null;
async function processAgentCommand(orderText) {
    let command=String(orderText||'').trim();if(!command)return;
    if(activeCommand){showToast('Hay una orden en curso. Espera su resultado.');return;}
    if(/^deshacer (?:la )?(?:última|ultima) orden$/i.test(command.replace(/[.!?]+$/,''))){
        if(!lastReversible){showToast('No hay un cambio reciente que deshacer en esta sesión.');return;}
        command='Deshacer '+lastReversible;
    }
    const target=document.getElementById('console-target')?.value||'sga';
    if(!pendingCommand||pendingCommand.command!==command||pendingCommand.target!==target)pendingCommand={command,target,request_id:crypto.randomUUID()};
    activeCommand=true;const executeButton=document.getElementById('btnExecuteCommand');if(executeButton)executeButton.disabled=true;
    const message=document.getElementById('command-message'),details=document.getElementById('command-data'),undo=document.getElementById('command-undo');
    if(message)message.textContent='Procesando la orden en el servidor…';if(details)details.textContent='';
    appendTacticalLog('ORDEN',command);
    try{
        const result=await AnaleConnection.request('/commands',{authorized:true,method:'POST',body:JSON.stringify(pendingCommand)});pendingCommand=null;
        if(!['read','executed'].includes(result.status))throw new Error('El servidor no confirmó la operación.');
        if(message)message.textContent=result.message+' Referencia: '+result.id;
        if(details)details.textContent=JSON.stringify(result.data,null,2);
        appendTacticalLog(result.status==='executed'?'CONFIRMADO':'CONSULTA',result.message);
        if(result.reversible){lastReversible=result.id;if(undo)undo.hidden=false;}else if(result.operation==='undo'){lastReversible=null;if(undo)undo.hidden=true;}
        if(result.target==='analematica'&&result.status==='executed'){
            try{const published=await AnaleConnection.request('/config');currentConfig=mergeContent(DEFAULT_CONFIG,published.config);publishedRevision=published.revision;populateForms();}
            catch{appendTacticalLog('AVISO','El cambio quedó confirmado. Recarga para actualizar los formularios.');}
        }
    }catch(error){if(message)message.textContent=error.message;appendTacticalLog('NO CONFIRMADO',error.message);}
    finally{activeCommand=false;if(executeButton)executeButton.disabled=false;}
}

// Reconocimiento de Voz
function setupSpeechRecognition() {
    const micBtn = document.getElementById('btnVoiceMic');
    if (!micBtn) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micBtn.title = "Reconocimiento de voz no soportado por este navegador.";
        micBtn.disabled=true;
        micBtn.style.opacity = "0.5";
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'es-CO';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        micBtn.classList.add('listening');
        appendTacticalLog("MICRÓFONO MILITAR", "Escuchando orden verbal del Administrador...");
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        appendTacticalLog("VOZ DETECTADA", `"${transcript}"`);
        const input = document.getElementById('tacticalCommandInput');
        if (input) input.value = transcript;
        processAgentCommand(transcript);
    };

    recognition.onerror = (event) => {
        appendTacticalLog("MICRÓFONO ERROR", `Detalle: ${event.error}`);
        micBtn.classList.remove('listening');
    };

    recognition.onend = () => {
        micBtn.classList.remove('listening');
    };

    micBtn.addEventListener('click', () => {
        try {
            recognition.start();
        } catch (e) {
            recognition.stop();
        }
    });
}

// Configurar eventos globales
document.addEventListener('DOMContentLoaded', async () => {
    try {const identity=await AnaleConnection.owner();document.getElementById('console-owner-status').textContent=identity.user.name+' · Dueño';const published=await AnaleConnection.request('/config');loadConfig();currentConfig=mergeContent(DEFAULT_CONFIG,published.config);publishedRevision=published.revision;}
    catch(error){sessionStorage.setItem('analematica-login-error',error.message);location.replace('/login.html');return;}

    document.body.removeAttribute('data-admin-pending');
    populateForms();
    setupTabs();
    document.getElementById('console-tools-toggle')?.addEventListener('click',()=>{const actions=document.querySelector('.admin-header-actions');actions.classList.toggle('console-editor-open');document.getElementById('console-tools-toggle').setAttribute('aria-expanded',String(actions.classList.contains('console-editor-open')));});
    document.getElementById('console-menu-toggle')?.addEventListener('click',()=>{const menu=document.getElementById('corporate-sidebar');menu.classList.toggle('console-menu-open');document.getElementById('console-menu-toggle').setAttribute('aria-expanded',String(menu.classList.contains('console-menu-open')));});
    document.getElementById('command-undo')?.addEventListener('click',()=>processAgentCommand('Deshacer última orden'));
    document.getElementById('console-logout')?.addEventListener('click',()=>{for(const key of ['accessToken','refreshToken','userId','userName','userRoles'])localStorage.removeItem(key);sessionStorage.removeItem('sga-panel-return');location.replace('/login.html');});
    setupSpeechRecognition();
    renderLeads();

    // Botón Guardar Global
    const btnSave = document.getElementById('btnGlobalSave');
    if (btnSave) {
        btnSave.addEventListener('click', () => saveConfig(true));
    }

    // Auto-guardado en inputs
    const allInputs = document.querySelectorAll('[data-key]');
    allInputs.forEach(input => {
        input.addEventListener('change', () => saveConfig(false));
    });

    // Ejecutar comando táctico escrito
    const btnExec = document.getElementById('btnExecuteCommand');
    const cmdInput = document.getElementById('tacticalCommandInput');

    if (btnExec && cmdInput) {
        btnExec.addEventListener('click', () => {
            const val = cmdInput.value;
            cmdInput.value = '';
            processAgentCommand(val);
        });

        cmdInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const val = cmdInput.value;
                cmdInput.value = '';
                processAgentCommand(val);
            }
        });
    }

    // Comandos rápidos sugeridos
    const quickCmds = document.querySelectorAll('.quick-command-btn');
    quickCmds.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            processAgentCommand(cmd);
        });
    });

    // Exportar configuración JSON
    const btnExport = document.getElementById('btnExportData');
    if (btnExport) {
        btnExport.addEventListener('click', () => {
            saveConfig(false);
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentConfig, null, 2));
            const dlAnchor = document.createElement('a');
            dlAnchor.setAttribute("href", dataStr);
            dlAnchor.setAttribute("download", `analematica_config_${Date.now()}.json`);
            dlAnchor.click();
            showToast("Archivo JSON exportado correctamente.");
        });
    }

    // Importar configuración JSON
    const btnImport = document.getElementById('btnImportData');
    const importInput = document.getElementById('importFileInput');
    if (btnImport && importInput) {
        btnImport.addEventListener('click', () => importInput.click());
        importInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const parsed = JSON.parse(event.target.result);
                    currentConfig = parsed;
                    populateForms();
                    saveConfig(true);
        
                } catch (err) {
                    alert("Error: Archivo JSON no válido.");
                }
            };
            reader.readAsText(file);
        });
    }

    // Restablecer valores de fábrica
    const btnReset = document.getElementById('btnResetDefaults');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (confirm("¿Está seguro de que desea restablecer todos los campos a los valores iniciales de fábrica de Analemática?")) {
                currentConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
                populateForms();
                saveConfig(true);

            }
        });
    }

    // Refresh only: never delete public inquiries or CRM history from this page.
    const btnRefresh=document.getElementById('btnClearLeads');
    if(btnRefresh){btnRefresh.textContent='Actualizar prospectos';btnRefresh.addEventListener('click',renderLeads);}
});
