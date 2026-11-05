/* ═══════════════════════════════════════════
   App Controller — SocialAuditPro
   ═══════════════════════════════════════════ */

let selectedPlatforms = [];
let currentStep = 1;
let activeTab = null;

/* ── Init ── */
document.addEventListener('DOMContentLoaded', () => {
    renderPlatformCards();
    renderStepIndicator();
    setTimeout(() => document.getElementById('loader').classList.add('hidden'), 800);
});

/* ── Step 1: Platform Selection ── */
function renderPlatformCards() {
    const grid = document.getElementById('platformsGrid');
    grid.innerHTML = Object.values(PLATFORMS).map(p => `
        <div class="platform-card" id="card-${p.id}" onclick="togglePlatform('${p.id}')" 
             style="--platform-color:${p.color}">
            <span class="platform-icon">${p.icon}</span>
            <div class="platform-name">${p.name}</div>
            <div class="platform-desc">${p.desc}</div>
        </div>
    `).join('');
}

function togglePlatform(id) {
    const idx = selectedPlatforms.indexOf(id);
    const card = document.getElementById(`card-${id}`);
    if (idx > -1) {
        selectedPlatforms.splice(idx, 1);
        card.classList.remove('selected');
    } else {
        selectedPlatforms.push(id);
        card.classList.add('selected');
    }
    document.getElementById('btnNext1').disabled = selectedPlatforms.length === 0;
}

/* ── Step Navigation ── */
function goToStep(step) {
    if (step === 2 && selectedPlatforms.length === 0) return;
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step${step}`).classList.add('active');
    currentStep = step;
    renderStepIndicator();
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (step === 2) renderForms();
    if (step === 3) document.getElementById('btnExportPDF').style.display = 'flex';
    else document.getElementById('btnExportPDF').style.display = 'none';
}

function renderStepIndicator() {
    const ind = document.getElementById('stepIndicator');
    ind.innerHTML = [1, 2, 3].map(s =>
        `<div class="step-dot ${s === currentStep ? 'active' : ''} ${s < currentStep ? 'done' : ''}"></div>`
    ).join('');
}

/* ── Step 2: Forms ── */
function renderForms() {
    const tabs = document.getElementById('platformTabs');
    const container = document.getElementById('formsContainer');

    tabs.innerHTML = selectedPlatforms.map(pid => {
        const p = PLATFORMS[pid];
        return `<button class="platform-tab" id="tab-${pid}" onclick="switchTab('${pid}')">
            <span class="tab-icon">${p.icon}</span> ${p.name}
        </button>`;
    }).join('');

    container.innerHTML = selectedPlatforms.map(pid => {
        const p = PLATFORMS[pid];
        return `<div class="form-panel" id="form-${pid}">
            ${p.fields.map(section => `
                <div class="form-section">
                    <div class="form-section-title">
                        <span class="section-icon">${section.section.split(' ')[0]}</span>
                        ${section.section.substring(section.section.indexOf(' ') + 1)}
                    </div>
                    <div class="form-grid">
                        ${section.fields.map(f => renderField(f)).join('')}
                    </div>
                </div>
            `).join('')}
        </div>`;
    }).join('');

    switchTab(selectedPlatforms[0]);
}

function renderField(f) {
    const optionalTag = f.optional ? ' <span class="optional">(opcional)</span>' : '';
    const reqAttr = f.required ? 'required' : '';
    const fullClass = f.type === 'textarea' ? ' full' : '';

    let input;
    if (f.type === 'select') {
        input = `<select id="${f.id}" ${reqAttr}>
            <option value="">Seleccionar...</option>
            ${f.options.map(o => `<option value="${o}">${o}</option>`).join('')}
        </select>`;
    } else if (f.type === 'textarea') {
        input = `<textarea id="${f.id}" placeholder="${f.placeholder || ''}" ${reqAttr}></textarea>`;
    } else {
        const step = f.step ? `step="${f.step}"` : '';
        input = `<input type="${f.type}" id="${f.id}" placeholder="${f.placeholder || ''}" ${step} ${reqAttr}>`;
    }

    return `<div class="form-group${fullClass}">
        <label for="${f.id}">${f.label}${optionalTag}</label>
        ${input}
    </div>`;
}

function switchTab(pid) {
    activeTab = pid;
    document.querySelectorAll('.platform-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.form-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`tab-${pid}`).classList.add('active');
    document.getElementById(`form-${pid}`).classList.add('active');
}

/* ── Step 3: Generate Report ── */
function generateReport() {
    const allData = collectFormData();
    const reportContent = document.getElementById('reportContent');
    const now = new Date();
    document.getElementById('reportDate').textContent =
        `Generado el ${now.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} — ${now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;

    // Report nav
    const reportNav = document.getElementById('reportNav');
    reportNav.innerHTML = selectedPlatforms.map(pid => {
        const p = PLATFORMS[pid];
        return `<button class="report-nav-btn" onclick="scrollToReport('${pid}')">
            ${p.icon} ${p.name}
        </button>`;
    }).join('') + `<button class="report-nav-btn" onclick="scrollToReport('global-summary')">📋 Resumen Global</button>`;

    // Generate per-platform reports
    let html = '';
    selectedPlatforms.forEach(pid => {
        html += generatePlatformReport(pid, allData);
    });

    // Global summary
    html += generateGlobalSummary(selectedPlatforms, allData);

    reportContent.innerHTML = html;
    goToStep(3);

    // Animate metric bars
    setTimeout(() => {
        document.querySelectorAll('.metric-bar-fill').forEach(bar => {
            const w = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => bar.style.width = w, 100);
        });
    }, 300);
}

function collectFormData() {
    const data = {};
    selectedPlatforms.forEach(pid => {
        const p = PLATFORMS[pid];
        p.fields.forEach(section => {
            section.fields.forEach(f => {
                const el = document.getElementById(f.id);
                if (el) data[f.id] = el.value;
            });
        });
    });
    return data;
}

function scrollToReport(id) {
    const el = document.getElementById(`report-${id}`) || document.querySelector(`.global-summary`);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Highlight nav
        document.querySelectorAll('.report-nav-btn').forEach(b => b.classList.remove('active'));
        event.target.classList.add('active');
    }
}

/* ── PDF Export ── */
function exportToPDF() {
    // Add print-specific title
    const style = document.createElement('style');
    style.id = 'print-style';
    style.textContent = `
        @media print {
            .step { display: block !important; }
            #step1, #step2 { display: none !important; }
            #step3 { display: block !important; }
        }
    `;
    document.head.appendChild(style);
    window.print();
    setTimeout(() => {
        const ps = document.getElementById('print-style');
        if (ps) ps.remove();
    }, 1000);
}
