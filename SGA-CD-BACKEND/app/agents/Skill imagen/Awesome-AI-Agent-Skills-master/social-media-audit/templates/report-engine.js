/* Report Engine — Generates audit report HTML for each platform */

function generatePlatformReport(platformId, data) {
    const p = PLATFORMS[platformId];
    if (!p) return '';
    const g = (key) => data[key] || null;
    const ph = (key, fallback) => {
        const v = g(key);
        if (v && v !== '') return { value: v, isPlaceholder: false };
        return { value: fallback, isPlaceholder: true };
    };
    const renderVal = (obj) => obj.isPlaceholder
        ? `<span style="color:#FFB432;font-style:italic">${obj.value} ⚠</span>`
        : obj.value;
    const placeholders = [];
    const checkPH = (key, fallback, label) => {
        const r = ph(key, fallback);
        if (r.isPlaceholder) placeholders.push(label);
        return r;
    };

    // Generate sections based on platform type
    let sections = '';

    // 1. Branding Section
    sections += buildBrandingSection(platformId, data, checkPH, renderVal);
    // 2. Copy & CTA
    sections += buildCopySection(platformId, data, checkPH, renderVal);
    // 3. Content & Posts
    sections += buildContentSection(platformId, data, checkPH, renderVal);
    // 4. Live/Streams (if applicable)
    if (['instagram','tiktok','twitch','kick'].includes(platformId)) {
        sections += buildLiveSection(platformId, data, checkPH, renderVal);
    }
    // 5. SEO & Optimization
    sections += buildSEOSection(platformId, data, checkPH, renderVal);
    // 5.5 Content Suggestions (Instagram, TikTok, YouTube)
    if (['instagram','tiktok','youtube'].includes(platformId)) {
        sections += buildSuggestionsSection(platformId, data);
    }
    // 6. Competitive Analysis
    sections += buildCompetitiveSection(platformId, data, checkPH, renderVal);
    // 7. Recommendations
    sections += buildRecommendationsSection(platformId, data, checkPH, renderVal);

    // Placeholders note
    let phNote = '';
    if (placeholders.length > 0) {
        phNote = `<div class="placeholder-note">Datos faltantes marcados con ⚠: ${placeholders.join(', ')}</div>`;
    }

    return `
    <div class="report-platform" id="report-${platformId}">
        <div class="report-platform-header" style="border-left:4px solid ${p.color}">
            <span class="report-platform-icon">${p.icon}</span>
            <div>
                <div class="report-platform-title">${p.name}</div>
                <div class="report-platform-subtitle">${p.desc} — Auditoría completa</div>
            </div>
        </div>
        ${phNote}
        ${sections}
    </div>`;
}

function buildBrandingSection(pid, data, checkPH, renderVal) {
    const cfg = getBrandingConfig(pid);
    const coherencia = evaluateBranding(pid, data);
    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(108,99,255,0.15)">🎨</span> Branding y Coherencia Visual</h3>
        <table class="report-table">
            <tr><th>Aspecto</th><th>Estado</th><th>Evaluación</th></tr>
            ${cfg.map(item => {
                const val = checkPH(item.key, item.fallback, item.label);
                const score = item.evaluate ? item.evaluate(val.value) : 'info';
                return `<tr><td>${item.label}</td><td>${renderVal(val)}</td><td><span class="tag tag-${score}">${scoreLabel(score)}</span></td></tr>`;
            }).join('')}
        </table>
        <div class="metric-row">
            <span class="metric-label">Coherencia general</span>
            <div class="metric-bar"><div class="metric-bar-fill" style="width:${coherencia}%;background:var(--gradient-main)"></div></div>
            <span class="metric-value">${coherencia}%</span>
        </div>
    </div>`;
}

function buildCopySection(pid, data, checkPH, renderVal) {
    const items = getCopyConfig(pid);
    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(255,101,132,0.15)">✍️</span> Copy y Llamadas a la Acción (CTA)</h3>
        <table class="report-table">
            <tr><th>Elemento</th><th>Contenido actual</th><th>Evaluación</th></tr>
            ${items.map(item => {
                const val = checkPH(item.key, item.fallback, item.label);
                const score = item.evaluate ? item.evaluate(val.value, val.isPlaceholder) : 'info';
                return `<tr><td>${item.label}</td><td>${renderVal(val)}</td><td><span class="tag tag-${score}">${scoreLabel(score)}</span></td></tr>`;
            }).join('')}
        </table>
    </div>`;
}

function buildContentSection(pid, data, checkPH, renderVal) {
    const prefix = getPrefix(pid);
    const freq = checkPH(`${prefix}_frecuencia`, '3', 'Frecuencia de publicación');
    const eng = checkPH(`${prefix}_engagement`, '2.0', 'Engagement');
    const engVal = parseFloat(eng.value) || 2;
    const engScore = engVal >= 5 ? 'good' : engVal >= 2 ? 'warning' : 'bad';
    const freqVal = parseFloat(freq.value) || 3;
    const benchmark = getEngagementBenchmark(pid);

    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(67,233,123,0.15)">📊</span> Contenido y Publicaciones</h3>
        <div class="metric-row">
            <span class="metric-label">Frecuencia de publicación</span>
            <div class="metric-bar"><div class="metric-bar-fill" style="width:${Math.min(freqVal/7*100,100)}%;background:var(--gradient-success)"></div></div>
            <span class="metric-value">${renderVal(freq)}/sem</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Engagement rate</span>
            <div class="metric-bar"><div class="metric-bar-fill" style="width:${Math.min(engVal/10*100,100)}%;background:${engScore==='good'?'var(--gradient-success)':engScore==='warning'?'linear-gradient(90deg,#FFB432,#FF8C00)':'linear-gradient(90deg,#FF6584,#FF3355)'}"></div></div>
            <span class="metric-value">${renderVal(eng)}%</span>
        </div>
        <div style="margin-top:12px;padding:12px;background:rgba(0,0,0,0.2);border-radius:8px;">
            <p style="font-size:0.85rem;color:var(--text-secondary)"><strong style="color:var(--text-primary)">Benchmark del sector:</strong> El engagement promedio en ${PLATFORMS[pid].name} es <strong>${benchmark}%</strong>. 
            ${engVal >= benchmark ? `<span class="tag tag-good">Por encima del promedio ✓</span>` : `<span class="tag tag-warning">Por debajo del promedio</span>`}</p>
        </div>
    </div>`;
}

function buildLiveSection(pid, data, checkPH, renderVal) {
    const prefix = getPrefix(pid);
    const liveFreq = checkPH(`${prefix}_live_freq`, 'Esporádico', 'Frecuencia de Lives');
    const liveDur = checkPH(`${prefix}_live_duracion`, '30', 'Duración de Lives');
    const liveViewers = checkPH(`${prefix}_live_viewers`, '20', 'Viewers de Lives');

    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(255,50,50,0.15)">🔴</span> Live / Streaming</h3>
        <table class="report-table">
            <tr><th>Métrica</th><th>Valor</th><th>Evaluación</th></tr>
            <tr><td>Frecuencia</td><td>${renderVal(liveFreq)}</td><td><span class="tag tag-${liveFreq.value==='No hago'?'bad':'good'}">${liveFreq.value==='No hago'?'Oportunidad perdida':'Activo'}</span></td></tr>
            <tr><td>Duración promedio</td><td>${renderVal(liveDur)} min</td><td><span class="tag tag-${parseInt(liveDur.value)>=30?'good':'warning'}">${parseInt(liveDur.value)>=30?'Adecuada':'Corta'}</span></td></tr>
            <tr><td>Viewers concurrentes</td><td>${renderVal(liveViewers)}</td><td><span class="tag tag-info">Monitorear</span></td></tr>
        </table>
        ${liveFreq.value === 'No hago' ? `
        <div class="recommendation-item urgent">
            <span class="rec-number">!</span>
            <span class="rec-text"><strong>Recomendación urgente:</strong> Los Lives generan hasta 3x más engagement. Comienza con 1 sesión semanal de 30 min.</span>
        </div>` : ''}
    </div>`;
}

function buildSEOSection(pid, data, checkPH, renderVal) {
    const prefix = getPrefix(pid);
    const items = getSEOConfig(pid, checkPH);
    const seoScore = calculateSEOScore(pid, data);
    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(0,210,255,0.15)">🔍</span> SEO Interno y Optimización</h3>
        <div class="metric-row">
            <span class="metric-label">Puntuación SEO del perfil</span>
            <div class="metric-bar"><div class="metric-bar-fill" style="width:${seoScore}%;background:var(--gradient-info)"></div></div>
            <span class="metric-value">${seoScore}/100</span>
        </div>
        <table class="report-table">
            <tr><th>Factor</th><th>Estado</th><th>Impacto</th></tr>
            ${items.map(i => `<tr><td>${i.label}</td><td>${renderVal(i.val)}</td><td><span class="tag tag-${i.score}">${i.impact}</span></td></tr>`).join('')}
        </table>
    </div>`;
}

function buildCompetitiveSection(pid, data, checkPH, renderVal) {
    const p = PLATFORMS[pid];
    const prefix = getPrefix(pid);
    const followers = parseInt(data[`${prefix}_seguidores`] || data[`${prefix}_suscriptores`] || data[`${prefix}_conexiones`] || data[`${prefix}_miembros`]) || 0;
    const eng = parseFloat(data[`${prefix}_engagement`]) || 0;
    const bench = getEngagementBenchmark(pid);
    const tier = followers > 100000 ? 'Grande' : followers > 10000 ? 'Mediano' : followers > 1000 ? 'Pequeño' : 'Emergente';

    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(255,180,50,0.15)">⚔️</span> Análisis Competitivo Básico</h3>
        <table class="report-table">
            <tr><th>Indicador</th><th>Tu cuenta</th><th>Benchmark sector</th><th>Diferencia</th></tr>
            <tr><td>Engagement Rate</td><td>${eng}%</td><td>${bench}%</td><td><span class="tag tag-${eng>=bench?'good':'warning'}">${eng>=bench?'+':''}${(eng-bench).toFixed(1)}%</span></td></tr>
            <tr><td>Tier de cuenta</td><td colspan="3"><span class="tag tag-info">${tier}</span> (${followers.toLocaleString()} seguidores)</td></tr>
        </table>
        <p style="font-size:0.85rem;color:var(--text-secondary);margin-top:12px;">💡 <strong>Oportunidad:</strong> ${getCompetitiveInsight(pid, tier, eng, bench)}</p>
    </div>`;
}

function buildRecommendationsSection(pid, data, checkPH, renderVal) {
    const recs = generateRecommendations(pid, data);
    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(67,233,123,0.15)">💡</span> Recomendaciones Prácticas</h3>
        ${recs.map((r, i) => `
            <div class="recommendation-item ${r.type}">
                <span class="rec-number">${i+1}</span>
                <span class="rec-text"><strong>${r.title}</strong><br>${r.desc}</span>
            </div>
        `).join('')}
    </div>`;
}

/* ── Helper Functions ── */
function getPrefix(pid) {
    const map = { instagram:'ig', tiktok:'tt', facebook:'fb', youtube:'yt', linkedin:'li', twitter:'tw', pinterest:'pi', twitch:'twi', kick:'ki', whatsapp:'wa', telegram:'tg' };
    return map[pid] || pid;
}

function scoreLabel(s) {
    return { good:'Bien',warning:'Mejorable',bad:'Urgente',info:'Info' }[s] || s;
}

function getEngagementBenchmark(pid) {
    return { instagram:3.5, tiktok:5.7, facebook:1.5, youtube:3.5, linkedin:2.8, twitter:1.2, pinterest:1.0, twitch:4, kick:3, whatsapp:0, telegram:0 }[pid] || 2;
}

function evaluateBranding(pid, data) {
    let score = 50;
    const prefix = getPrefix(pid);
    if (data[`${prefix}_url`]) score += 15;
    if (data[`${prefix}_objetivo`]) score += 10;
    if (data[`${prefix}_nicho`] || data[`${prefix}_categoria`]) score += 10;
    if (data[`${prefix}_bio`]) score += 15;
    return Math.min(score, 100);
}

function calculateSEOScore(pid, data) {
    let score = 40;
    const prefix = getPrefix(pid);
    if (data[`${prefix}_url`]) score += 10;
    if (data[`${prefix}_hashtags`]) score += 15;
    if (data[`${prefix}_bio`]) score += 15;
    if (data[`${prefix}_seo`] === 'Sí, siempre' || data[`${prefix}_seo`] === 'Sí') score += 20;
    return Math.min(score, 100);
}

function getBrandingConfig(pid) {
    return [
        { key: `${getPrefix(pid)}_url`, label: 'Perfil / URL', fallback: 'No proporcionado', evaluate: v => v !== 'No proporcionado' ? 'good' : 'bad' },
        { key: `${getPrefix(pid)}_objetivo`, label: 'Objetivo definido', fallback: 'Sin definir', evaluate: v => v !== 'Sin definir' ? 'good' : 'warning' },
        { key: `${getPrefix(pid)}_nicho`, label: 'Nicho claro', fallback: 'No especificado', evaluate: v => v !== 'No especificado' ? 'good' : 'warning' },
    ];
}

function getCopyConfig(pid) {
    const prefix = getPrefix(pid);
    const items = [
        { key: `${prefix}_cta`, label: 'CTA principal', fallback: 'No definido', evaluate: (v, ph) => ph ? 'warning' : 'good' },
    ];
    if (['instagram','tiktok','twitter'].includes(pid)) {
        items.push({ key: `${prefix}_hashtags`, label: 'Hashtags', fallback: 'Sin hashtags definidos', evaluate: (v, ph) => ph ? 'bad' : 'good' });
    }
    if (pid === 'instagram') {
        items.push({ key: `${prefix}_bio`, label: 'Bio del perfil', fallback: 'No proporcionada', evaluate: (v, ph) => ph ? 'warning' : 'good' });
    }
    return items;
}

function getSEOConfig(pid, checkPH) {
    const prefix = getPrefix(pid);
    const items = [];
    items.push({ label: 'Perfil completo', val: checkPH(`${prefix}_url`, 'No verificado', 'URL del perfil'), score: 'good', impact: 'Alto' });
    if (['instagram','tiktok','twitter'].includes(pid)) {
        const h = checkPH(`${prefix}_hashtags`, 'Sin definir', 'Hashtags');
        items.push({ label: 'Estrategia de hashtags', val: h, score: h.isPlaceholder ? 'warning' : 'good', impact: 'Alto' });
    }
    if (pid === 'youtube') {
        const s = checkPH('yt_seo', 'No', 'SEO de videos');
        items.push({ label: 'SEO en títulos/desc.', val: s, score: s.value === 'Sí, siempre' ? 'good' : 'warning', impact: 'Crítico' });
        const m = checkPH('yt_miniaturas', 'Básicas', 'Miniaturas');
        items.push({ label: 'Miniaturas optimizadas', val: m, score: m.value === 'Profesionales' ? 'good' : 'warning', impact: 'Alto' });
    }
    if (pid === 'pinterest') {
        const s = checkPH('pi_seo', 'No', 'SEO de pins');
        items.push({ label: 'SEO en pins', val: s, score: s.value === 'Sí' ? 'good' : 'bad', impact: 'Crítico' });
    }
    return items;
}

/* ── Content Suggestions Section (Instagram, TikTok, YouTube) ── */
function buildSuggestionsSection(pid, data) {
    const prefix = getPrefix(pid);
    const nicho = data[`${prefix}_nicho`] || data[`${prefix}_categoria`] || 'general';
    const s = getContentSuggestions(pid, nicho);

    return `
    <div class="report-section">
        <h3><span class="rs-icon" style="background:rgba(255,200,50,0.15)">🚀</span> Sugerencias de Contenido para ${PLATFORMS[pid].name}</h3>

        <div style="margin-bottom:20px">
            <h4 style="font-size:0.9rem;font-weight:700;margin-bottom:10px;color:var(--accent-4)">📌 Hashtags Recomendados</h4>
            <div style="margin-bottom:8px">
                <span style="font-size:0.75rem;color:var(--text-muted);font-weight:600">ALTO VOLUMEN (>500K posts)</span><br>
                ${s.hashtags.high.map(h => `<span class="tag tag-info">${h}</span>`).join(' ')}
            </div>
            <div style="margin-bottom:8px">
                <span style="font-size:0.75rem;color:var(--text-muted);font-weight:600">VOLUMEN MEDIO (50K-500K)</span><br>
                ${s.hashtags.medium.map(h => `<span class="tag tag-good">${h}</span>`).join(' ')}
            </div>
            <div style="margin-bottom:8px">
                <span style="font-size:0.75rem;color:var(--text-muted);font-weight:600">NICHO (&lt;50K) — Mayor engagement</span><br>
                ${s.hashtags.niche.map(h => `<span class="tag tag-warning">${h}</span>`).join(' ')}
            </div>
            <p style="font-size:0.8rem;color:var(--text-muted);margin-top:8px">💡 <strong>Fórmula ideal:</strong> ${s.hashtagFormula}</p>
        </div>

        <div style="margin-bottom:20px">
            <h4 style="font-size:0.9rem;font-weight:700;margin-bottom:10px;color:var(--accent-2)">🎯 Fórmulas de Títulos que Funcionan</h4>
            <table class="report-table">
                <tr><th>Fórmula</th><th>Ejemplo para tu nicho</th><th>Por qué funciona</th></tr>
                ${s.titles.map(t => `<tr><td><strong>${t.formula}</strong></td><td>${t.example}</td><td><span class="tag tag-info">${t.why}</span></td></tr>`).join('')}
            </table>
        </div>

        <div style="margin-bottom:20px">
            <h4 style="font-size:0.9rem;font-weight:700;margin-bottom:10px;color:var(--accent-3)">💡 Ideas de Contenido (Próximas 2 Semanas)</h4>
            ${s.ideas.map((idea, i) => `
                <div class="recommendation-item ${i < 2 ? 'quick' : ''}" style="margin-bottom:8px">
                    <span class="rec-number">${i+1}</span>
                    <span class="rec-text"><strong>${idea.type}:</strong> ${idea.desc}${idea.hook ? '<br><em style="color:var(--accent-4)">Hook: "' + idea.hook + '"</em>' : ''}</span>
                </div>
            `).join('')}
        </div>

        ${pid === 'youtube' ? `
        <div>
            <h4 style="font-size:0.9rem;font-weight:700;margin-bottom:10px;color:var(--accent-1)">🖼️ Tips para Miniaturas</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                <div style="padding:12px;background:rgba(67,233,123,0.06);border-radius:8px;border:1px solid rgba(67,233,123,0.15)">
                    <strong style="color:var(--accent-3)">✅ Hacer</strong><br>
                    <span style="font-size:0.82rem;color:var(--text-secondary)">• Rostro con expresión exagerada<br>• Texto grande (3-5 palabras)<br>• Colores contrastantes<br>• Fondo limpio sin ruido</span>
                </div>
                <div style="padding:12px;background:rgba(255,101,132,0.06);border-radius:8px;border:1px solid rgba(255,101,132,0.15)">
                    <strong style="color:var(--accent-2)">❌ Evitar</strong><br>
                    <span style="font-size:0.82rem;color:var(--text-secondary)">• Texto pequeño ilegible<br>• Repetir el título del video<br>• Imágenes genéricas de stock<br>• Demasiados elementos</span>
                </div>
            </div>
        </div>` : ''}
    </div>`;
}

function getContentSuggestions(pid, nicho) {
    const nichoLower = nicho.toLowerCase();

    const hashtagDB = {
        instagram: {
            general: {
                high: ['#instagood','#photooftheday','#reels','#explorepage','#trending','#viral'],
                medium: ['#contentcreator','#smallbusiness','#emprendedor','#marketingdigital','#crecimiento'],
                niche: ['#comunidadlatina','#marcapersonal','#emprendedores2025','#negociosonline','#tunicho']
            },
            fitness: {
                high: ['#fitness','#gym','#workout','#fitnessmotivation','#healthylifestyle','#training'],
                medium: ['#fitfam','#gymlife','#personaltrainer','#fitnessjourney','#homeworkout'],
                niche: ['#entrenamientofuncional','#rutinasencasa','#fitnesslatinoamerica','#coachfitness','#retofitness']
            },
            moda: {
                high: ['#fashion','#style','#ootd','#fashionista','#outfitoftheday','#streetstyle'],
                medium: ['#fashionblogger','#modafemenina','#lookdeldia','#tendencias','#estilopersonal'],
                niche: ['#modasostenible','#modaaccesible','#capsulewardrobe','#outfitinspo','#slowfashion']
            },
            gastronomia: {
                high: ['#food','#foodie','#instafood','#foodporn','#cooking','#recipe'],
                medium: ['#homecooking','#recetasfaciles','#comidacasera','#cheflife','#foodblogger'],
                niche: ['#comidalatina','#recetassaludables','#cocinaperuana','#gastronomiasostenible','#mealprep']
            }
        },
        tiktok: {
            general: {
                high: ['#fyp','#parati','#viral','#trending','#tiktok','#foryoupage'],
                medium: ['#tiktokviral','#tendencia','#contenido','#creadordecontenido','#emprendedortiktok'],
                niche: ['#tiktoklatino','#aprendeentiktok','#datoscuriosos','#videopyme','#tiktoknegocios']
            },
            fitness: {
                high: ['#fyp','#fitness','#gym','#workout','#fitnesstiktok','#gymtok'],
                medium: ['#workoutroutine','#fitnesschallenge','#personaltrainer','#gymmotivation','#healthytiktok'],
                niche: ['#rutina30dias','#entrenamientocasa','#fitnessprincipiantes','#retogym','#progresofitness']
            },
            moda: {
                high: ['#fyp','#fashion','#ootd','#style','#fashiontiktok','#getreadywithme'],
                medium: ['#grwm','#outfitcheck','#fashionhacks','#thriftflip','#styleinspo'],
                niche: ['#modarealista','#outfitbarato','#lookpordia','#tiendaonline','#modelatina']
            },
            gastronomia: {
                high: ['#fyp','#food','#recipe','#cooking','#foodtiktok','#asmrfood'],
                medium: ['#receta','#cocinafacil','#recetasviral','#foodhack','#whatieatinaday'],
                niche: ['#recetasen1minuto','#cocinacreativa','#cocinaparauno','#mealpreptiktok','#streeteats']
            }
        },
        youtube: {
            general: {
                high: ['#youtube','#youtuber','#video','#subscribe','#tutorial','#howto'],
                medium: ['#youtubechannel','#youtubevideos','#contentcreator','#vlog','#review'],
                niche: ['#youtubeenespanol','#canalnuevo','#crecerenyoutube','#monetizacion','#tutorialespanol']
            },
            fitness: {
                high: ['#fitness','#workout','#gym','#exercise','#homeworkout','#fitnesstips'],
                medium: ['#fullbodyworkout','#weightloss','#musclebuilding','#yogapractice','#cardio'],
                niche: ['#rutinacompleta','#ejerciciosencasa','#coachonline','#transformacion','#retofitness30dias']
            },
            tech: {
                high: ['#tech','#technology','#review','#unboxing','#gadgets','#smartphone'],
                medium: ['#techreview','#bestphones','#techsetup','#pcgaming','#setupgamer'],
                niche: ['#techespanol','#mejoresapps','#presupuestobajo','#programacion','#techlatinoamerica']
            },
            gastronomia: {
                high: ['#cooking','#recipe','#food','#chef','#foodie','#kitchen'],
                medium: ['#easyrecipe','#cookingathome','#recipeideas','#mealprep','#baking'],
                niche: ['#recetaspaso','#cocinaparaprincipiantes','#comidarapida','#cocinalatina','#postrescaseros']
            }
        }
    };

    let nicheKey = 'general';
    if (/fitness|gym|entrena|deporte|salud/i.test(nichoLower)) nicheKey = 'fitness';
    else if (/moda|fashion|ropa|estilo|textil/i.test(nichoLower)) nicheKey = 'moda';
    else if (/comida|gastr|cocina|restaurant|food|receta|pollo|pizza|sushi/i.test(nichoLower)) nicheKey = 'gastronomia';
    else if (/tech|tecnolog|programa|software|gaming/i.test(nichoLower)) nicheKey = pid === 'youtube' ? 'tech' : 'general';

    const hashtags = (hashtagDB[pid] && hashtagDB[pid][nicheKey]) || hashtagDB[pid]?.general || hashtagDB.instagram.general;

    const titleFormulas = {
        instagram: [
            { formula: 'Número + Beneficio', example: `5 ${nicheKey === 'fitness' ? 'ejercicios que queman grasa en 10 min' : nicheKey === 'moda' ? 'outfits que elevan cualquier look' : nicheKey === 'gastronomia' ? 'recetas con solo 3 ingredientes' : 'trucos que nadie te cuenta'}`, why: 'Genera curiosidad' },
            { formula: 'Pregunta provocadora', example: `¿Sigues haciendo esto en ${nicho}? 🚫`, why: 'Detiene el scroll' },
            { formula: 'Antes vs Después', example: `Mi ${nicheKey === 'fitness' ? 'transformación en 90 días' : nicheKey === 'moda' ? 'armario antes vs ahora' : 'evolución como creador'}`, why: 'Prueba social' },
            { formula: 'POV / Storytelling', example: `POV: descubres ${nicheKey === 'gastronomia' ? 'el ingrediente secreto' : nicheKey === 'fitness' ? 'que llevas años entrenando mal' : 'algo que cambia todo'}`, why: 'Conexión emocional' },
        ],
        tiktok: [
            { formula: 'Hook + Revelación', example: `Nadie te dice esto sobre ${nicho}...`, why: 'Retención alta' },
            { formula: 'Tutorial rápido', example: `Cómo ${nicheKey === 'fitness' ? 'activar el core correctamente' : nicheKey === 'moda' ? 'combinar colores como pro' : nicheKey === 'gastronomia' ? 'hacer esto en 60 segundos' : 'dominar esto'} en 30s`, why: 'Valor inmediato' },
            { formula: 'Contraste/Shock', example: `Lo que ves vs lo que realmente pasa en ${nicho}`, why: 'Viralidad alta' },
            { formula: 'Trend + Nicho', example: `[Sonido trending] + tu mensaje de ${nicho}`, why: 'Algoritmo favorable' },
            { formula: 'Respuesta a comentario', example: `"¿Cómo haces para...?" — Aquí te explico`, why: 'Comunidad + reach' },
        ],
        youtube: [
            { formula: 'Cómo + Resultado', example: `Cómo ${nicheKey === 'fitness' ? 'ganar músculo sin gimnasio' : nicheKey === 'tech' ? 'armar un PC gaming por $500' : nicheKey === 'gastronomia' ? 'cocinar como chef profesional en casa' : 'lograr X'} (Guía Completa)`, why: 'SEO + CTR alto' },
            { formula: 'Número + Superlativos', example: `Los 7 ${nicheKey === 'tech' ? 'gadgets que NECESITAS' : nicheKey === 'fitness' ? 'errores que DESTRUYEN tu progreso' : 'secretos de ' + nicho} en 2025`, why: 'Curiosidad + urgencia' },
            { formula: 'Desafío/Experimento', example: `Probé ${nicheKey === 'fitness' ? 'entrenar 2x al día por 30 días' : nicheKey === 'gastronomia' ? 'cocinar solo con $10 por una semana' : 'hacer X por 30 días'} y esto pasó...`, why: 'Storytelling + retención' },
            { formula: 'Vs / Comparación', example: `${nicheKey === 'tech' ? 'iPhone vs Samsung' : nicheKey === 'fitness' ? 'Cardio vs Pesas' : 'A vs B'}: ¿Cuál es MEJOR? (La verdad)`, why: 'Debate = engagement' },
        ]
    };

    const contentIdeas = {
        instagram: [
            { type: 'Reel educativo', desc: `Tutorial rápido de 30-60s sobre un tip práctico de ${nicho}`, hook: '¿Sabías que el 90% de la gente hace esto mal?' },
            { type: 'Carrusel informativo', desc: `"5 errores comunes en ${nicho}" — diseño limpio con swipe`, hook: null },
            { type: 'Story interactiva', desc: `Quiz o encuesta sobre preferencias de tu audiencia en ${nicho}`, hook: null },
            { type: 'Reel trending', desc: `Adapta el audio trending más popular a tu nicho de ${nicho}`, hook: 'POV: cuando descubres que...' },
            { type: 'Post de valor', desc: `Infografía con datos o estadísticas relevantes de ${nicho}`, hook: null },
            { type: 'Behind the scenes', desc: 'Muestra tu proceso, espacio de trabajo o día a día auténtico', hook: 'Un día normal en mi vida como...' },
        ],
        tiktok: [
            { type: 'Hook viral', desc: `Video con gancho fuerte en los primeros 2 segundos sobre ${nicho}`, hook: 'PARA, necesitas saber esto...' },
            { type: 'Tutorial express', desc: 'Paso a paso en menos de 60s — alto valor en poco tiempo', hook: 'En 30 segundos te enseño...' },
            { type: 'Storytime', desc: `Cuenta una experiencia real de ${nicho} que sorprenda`, hook: 'La peor experiencia que tuve con...' },
            { type: 'Respuesta a comentario', desc: 'Graba respondiendo la pregunta más frecuente de tu audiencia', hook: null },
            { type: 'Trend adaptado', desc: `Usa el sonido trending #1 adaptándolo a tu mensaje de ${nicho}`, hook: null },
            { type: 'Duet/Stitch', desc: 'Reacciona o complementa un video viral de tu nicho', hook: 'Esto es lo que realmente pasa...' },
            { type: 'TikTok Live temático', desc: `Q&A en vivo sobre ${nicho} con interacción directa del chat`, hook: null },
        ],
        youtube: [
            { type: 'Video largo (tutorial)', desc: `Guía completa de 10-15 min sobre un tema core de ${nicho}`, hook: 'En este video te muestro paso a paso...' },
            { type: 'Short viral', desc: 'Clip de 30-60s con el mejor momento de un video largo', hook: 'El truco que nadie te enseña...' },
            { type: 'Video lista', desc: `"Top 7 cosas de ${nicho} que debes conocer en 2025"`, hook: '¿Conoces todos estos?' },
            { type: 'Vlog/BTS', desc: `Muestra un día real o proceso detrás de tu contenido de ${nicho}`, hook: null },
            { type: 'Comparación/Review', desc: 'Compara 2-3 opciones populares en tu nicho con veredicto final', hook: 'Probé los 3 más populares y solo 1 vale la pena' },
            { type: 'Responde comentarios', desc: 'Video respondiendo las mejores preguntas de tu comunidad', hook: null },
        ]
    };

    const hashtagFormula = {
        instagram: '3 de alto volumen + 5 de volumen medio + 7 de nicho = 15 hashtags por post',
        tiktok: '2 generales (#fyp #parati) + 3 de nicho + 1-2 trending = 5-7 hashtags',
        youtube: '3-5 hashtags en descripción + keywords en título y tags. Los 3 primeros aparecen sobre el título'
    };

    return {
        hashtags: hashtags,
        hashtagFormula: hashtagFormula[pid],
        titles: titleFormulas[pid] || titleFormulas.instagram,
        ideas: (contentIdeas[pid] || contentIdeas.instagram)
    };
}

function getCompetitiveInsight(pid, tier, eng, bench) {
    if (eng >= bench * 1.5) return `Tu engagement es excepcional para ${PLATFORMS[pid].name}. Capitaliza esta ventaja con colaboraciones y contenido viral.`;
    if (eng >= bench) return `Estás por encima del promedio. Enfócate en consistencia y experimentación con nuevos formatos.`;
    if (tier === 'Emergente') return `Como cuenta emergente, prioriza contenido de valor y engagement sobre crecimiento rápido. La autenticidad es tu mayor activo.`;
    return `Tu engagement está por debajo del benchmark. Revisa horarios de publicación, calidad visual y relevancia del contenido para tu audiencia.`;
}

function generateRecommendations(pid, data) {
    const recs = [];
    const prefix = getPrefix(pid);
    const eng = parseFloat(data[`${prefix}_engagement`]) || 0;
    const bench = getEngagementBenchmark(pid);
    const freq = parseInt(data[`${prefix}_frecuencia`]) || 0;

    // Quick wins
    if (!data[`${prefix}_hashtags`] && ['instagram','tiktok','twitter'].includes(pid)) {
        recs.push({ type: 'quick', title: 'Quick Win: Define tu estrategia de hashtags', desc: `Investiga 20-30 hashtags relevantes en ${PLATFORMS[pid].name}. Mezcla hashtags populares (>100K posts), medianos (10K-100K) y de nicho (<10K).` });
    }

    if (eng < bench) {
        recs.push({ type: 'urgent', title: 'Mejorar engagement rate', desc: `Tu engagement (${eng}%) está por debajo del benchmark (${bench}%). Publica en horarios pico, usa CTAs claros y responde todos los comentarios en las primeras 2 horas.` });
    }

    if (freq < 3 && !['youtube','twitch','kick'].includes(pid)) {
        recs.push({ type: 'urgent', title: 'Aumentar frecuencia de publicación', desc: `${freq} publicaciones por semana es insuficiente. El mínimo recomendado para ${PLATFORMS[pid].name} es 3-5/semana. Crea un calendario editorial y batch-produce contenido.` });
    }

    // Platform-specific
    if (pid === 'instagram') {
        if (!data.ig_reels || parseInt(data.ig_reels) < 3) {
            recs.push({ type: 'quick', title: 'Potencia los Reels', desc: 'Los Reels obtienen hasta 2x más alcance que posts estáticos. Apunta a mínimo 3-5 Reels/semana con hooks fuertes en los primeros 3 segundos.' });
        }
        if (data.ig_live_freq === 'No hago') {
            recs.push({ type: '', title: 'Implementa IG Lives', desc: 'Los Lives aumentan la visibilidad del perfil y el engagement. Comienza con 1 Live semanal temático con preguntas interactivas.' });
        }
    }
    if (pid === 'tiktok') {
        if (data.tt_tendencias === 'Nunca' || data.tt_tendencias === 'Rara vez') {
            recs.push({ type: 'urgent', title: 'Sigue las tendencias', desc: 'TikTok premia el contenido que usa tendencias actuales. Dedica 15 min diarios a explorar la página "Para ti" y adapta trends a tu nicho.' });
        }
        recs.push({ type: 'quick', title: 'Optimiza los primeros 2 segundos', desc: 'El hook inicial determina si el usuario se queda. Usa preguntas provocadoras, datos impactantes o movimiento visual inmediato.' });
    }
    if (pid === 'youtube') {
        if (data.yt_miniaturas !== 'Profesionales') {
            recs.push({ type: 'urgent', title: 'Mejora tus miniaturas', desc: 'Las miniaturas son el factor #1 de CTR en YouTube. Usa rostros expresivos, texto grande (3-5 palabras), colores contrastantes y composición clara.' });
        }
        if (data.yt_shorts !== 'Sí, frecuente') {
            recs.push({ type: 'quick', title: 'Aprovecha YouTube Shorts', desc: 'Los Shorts pueden multiplicar tu alcance 10x. Reutiliza clips de tus videos largos o crea contenido vertical exclusivo.' });
        }
    }
    if (pid === 'linkedin') {
        recs.push({ type: 'quick', title: 'Publica carruseles educativos', desc: 'Los carruseles en LinkedIn tienen 3x más engagement que posts de texto. Comparte frameworks, listas y casos de estudio de tu industria.' });
    }
    if (pid === 'whatsapp') {
        if (data.wa_auto !== 'Sí, bienvenida + ausencia') {
            recs.push({ type: 'quick', title: 'Configura mensajes automáticos', desc: 'Activa mensaje de bienvenida + ausencia + respuestas rápidas. Reduce tiempo de respuesta y mejora la experiencia del cliente.' });
        }
        if (data.wa_catalogo !== 'Sí, actualizado') {
            recs.push({ type: 'urgent', title: 'Activa y actualiza tu catálogo', desc: 'El catálogo de WhatsApp Business es una tienda gratuita. Sube productos con fotos, precios y descripciones claras.' });
        }
    }

    // Generic if few recs
    if (recs.length < 3) {
        recs.push({ type: '', title: 'Analiza métricas semanalmente', desc: `Revisa las estadísticas de ${PLATFORMS[pid].name} cada semana. Identifica qué formatos y horarios generan más engagement y replica esos patrones.` });
        recs.push({ type: 'quick', title: 'Interacción con la comunidad', desc: 'Responde comentarios en los primeros 60 minutos, interactúa con cuentas de tu nicho y crea contenido basado en preguntas frecuentes de tu audiencia.' });
    }

    return recs;
}

/* ── Global Summary Generator ── */
function generateGlobalSummary(selectedPlatforms, allData) {
    const priorities = [];
    selectedPlatforms.forEach(pid => {
        const prefix = getPrefix(pid);
        const eng = parseFloat(allData[`${prefix}_engagement`]) || 0;
        const bench = getEngagementBenchmark(pid);
        const p = PLATFORMS[pid];
        const urgency = eng < bench * 0.5 ? 'high' : eng < bench ? 'medium' : 'low';
        priorities.push({ platform: p.name, icon: p.icon, urgency, eng, bench,
            action: eng < bench ? `Mejorar engagement (actual ${eng}% vs benchmark ${bench}%)` : `Mantener y escalar (${eng}% engagement)`
        });
    });
    priorities.sort((a, b) => { const order = { high: 0, medium: 1, low: 2 }; return order[a.urgency] - order[b.urgency]; });

    return `
    <div class="global-summary">
        <h2>📋 Resumen Global y Plan de Acción</h2>
        <h3 style="font-size:1rem;margin:16px 0 12px;color:var(--text-secondary)">Prioridades por Red</h3>
        <ul class="priority-list">
            ${priorities.map(p => `
                <li>
                    <span style="font-size:1.3rem">${p.icon}</span>
                    <span class="priority-badge ${p.urgency}">${p.urgency === 'high' ? 'Alta' : p.urgency === 'medium' ? 'Media' : 'Baja'}</span>
                    <span style="flex:1"><strong>${p.platform}:</strong> ${p.action}</span>
                </li>
            `).join('')}
        </ul>
        <h3 style="font-size:1rem;margin:24px 0 12px;color:var(--text-secondary)">Plan de Acción Inmediato (Próximos 30 días)</h3>
        <div class="recommendation-item urgent">
            <span class="rec-number">1</span>
            <span class="rec-text"><strong>Semana 1-2:</strong> Optimiza perfiles, bios, fotos y CTAs en todas las redes seleccionadas. Asegura coherencia visual.</span>
        </div>
        <div class="recommendation-item quick">
            <span class="rec-number">2</span>
            <span class="rec-text"><strong>Semana 2-3:</strong> Implementa calendario editorial unificado. Define formatos y horarios óptimos por red.</span>
        </div>
        <div class="recommendation-item">
            <span class="rec-number">3</span>
            <span class="rec-text"><strong>Semana 3-4:</strong> Activa estrategias de engagement: responde en <1h, interactúa con cuentas afines, lanza Lives o contenido interactivo.</span>
        </div>
        <h3 style="font-size:1rem;margin:24px 0 12px;color:var(--text-secondary)">KPIs Sugeridos</h3>
        <table class="report-table">
            <tr><th>KPI</th><th>Frecuencia</th><th>Meta sugerida</th></tr>
            <tr><td>Engagement Rate</td><td>Semanal</td><td>Superar benchmark del sector</td></tr>
            <tr><td>Crecimiento de seguidores</td><td>Mensual</td><td>+5-10% mensual orgánico</td></tr>
            <tr><td>Alcance/Impresiones</td><td>Semanal</td><td>+15% mes a mes</td></tr>
            <tr><td>Conversiones/Clicks</td><td>Semanal</td><td>CTR >2% en CTAs</td></tr>
            <tr><td>Tiempo de respuesta</td><td>Diario</td><td><60 minutos</td></tr>
        </table>
    </div>`;
}
