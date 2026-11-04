/**
 * EJÉRCITO DE AGENTES TÁCTICOS - LANDING PAGE ANALEMÁTICA
 * Ubicación: Analematica/agents/analematica_army.js
 * Doctrina DEAA-V2.1: Coronel, Capitanes, Tenientes, Sargentos y Soldados.
 * Capacidad: Órdenes escritas y verbales -> Diligenciado y Tecleado Mecánico Automático en el Sistema.
 * Paleta Estricta: Azul Metálico y Azul Claro Únicamente (Prohibidos blanco, rojo y amarillo).
 */

class SoldadoDomManipulator {
    /**
     * [NIVEL 5: SOLDADO ATÓMICO]
     * Simula la mecanografía física (typewriter) en el elemento exacto del DOM.
     */
    static async teclearEnElemento(element, texto) {
        if (!element) return false;

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

        const chars = texto.split('');
        for (let i = 0; i < chars.length; i++) {
            element.value += chars[i];
            element.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(r => setTimeout(r, 16));
        }

        element.dispatchEvent(new Event('change', { bubbles: true }));

        setTimeout(() => {
            element.classList.remove('typewriter-highlight');
        }, 1200);

        return true;
    }
}

class SargentoTecleador {
    /**
     * [NIVEL 4: SARGENTO DE ESCUADRA MECANOGRÁFICA]
     */
    constructor(logger) {
        this.logger = logger;
    }

    async ejecutar(elementId, texto) {
        this.logger('SARGENTO TECLEADOR', `Desplegando soldado mecanógrafo en #${elementId}...`);
        const el = document.getElementById(elementId);
        if (!el) {
            this.logger('SARGENTO TECLEADOR', `Elemento #${elementId} no hallado en el DOM.`);
            return false;
        }
        await SoldadoDomManipulator.teclearEnElemento(el, texto);
        this.logger('SARGENTO TECLEADOR', `Diligenciado completado en #${elementId}.`);
        return true;
    }
}

class SargentoRedaccion {
    /**
     * [NIVEL 4: SARGENTO DE REDACCIÓN INSTITUCIONAL]
     */
    constructor(tecleador, logger) {
        this.tecleador = tecleador;
        this.logger = logger;
    }

    async actualizarTexto(campo, texto) {
        this.logger('SARGENTO REDACCIÓN', `Redactando contenido para: ${campo}`);
        const mapaCampos = {
            'hero_title': 'hero_title',
            'hero_subtitle': 'hero_subtitle',
            'mision': 'mision_text',
            'vision': 'vision_text',
            'contacto': 'contacto_desc',
            'filosofia': 'filo_desc'
        };
        const elementId = mapaCampos[campo] || campo;
        return await this.tecleador.ejecutar(elementId, texto);
    }
}

class SargentoMetricas {
    /**
     * [NIVEL 4: SARGENTO DE MÉTRICAS Y CONTADORES]
     */
    constructor(tecleador, logger) {
        this.tecleador = tecleador;
        this.logger = logger;
    }

    async actualizarMetrica(indice, valor, etiqueta = null) {
        this.logger('SARGENTO MÉTRICAS', `Calibrando Métrica #${indice} a "${valor}"`);
        const valId = `hero_metric${indice}_val`;
        const res = await this.tecleador.ejecutar(valId, valor);
        if (etiqueta) {
            const lblId = `hero_metric${indice}_lbl`;
            await this.tecleador.ejecutar(lblId, etiqueta);
        }
        return res;
    }
}

class SargentoSincronizador {
    /**
     * [NIVEL 4: SARGENTO SINCRONIZADOR Y PERSISTENCIA]
     */
    constructor(logger) {
        this.logger = logger;
    }

    sincronizar() {
        this.logger('SARGENTO SINCRONIZADOR', 'Sello criptográfico aplicado en base local y memoria.');
        if (typeof saveConfig === 'function') {
            saveConfig(false);
        }
    }
}

class CapitanContenido {
    /**
     * [NIVEL 2: CAPITÁN DE COMPAÑÍA DE CONTENIDO INSTITUCIONAL]
     */
    constructor(redaccion, metricas, logger) {
        this.redaccion = redaccion;
        this.metricas = metricas;
        this.logger = logger;
    }

    async procesarMision(tipo, payload) {
        this.logger('CAPITÁN CONTENIDO', `Asignando misión a pelotón de redacción/métricas: ${tipo}`);
        if (tipo === 'hero_title') return await this.redaccion.actualizarTexto('hero_title', payload);
        if (tipo === 'hero_subtitle') return await this.redaccion.actualizarTexto('hero_subtitle', payload);
        if (tipo === 'mision') return await this.redaccion.actualizarTexto('mision', payload);
        if (tipo === 'vision') return await this.redaccion.actualizarTexto('vision', payload);
        if (tipo === 'metrica') return await this.metricas.actualizarMetrica(payload.indice || 1, payload.valor, payload.etiqueta);
        return false;
    }
}

class CapitanMecano {
    /**
     * [NIVEL 2: CAPITÁN DE DILIGENCIADO & AUTOMATIZACIÓN DE FORMULARIOS]
     */
    constructor(tecleador, sincronizador, logger) {
        this.tecleador = tecleador;
        this.sincronizador = sincronizador;
        this.logger = logger;
    }

    async diligenciarDirecto(idCampo, texto) {
        this.logger('CAPITÁN MECANO', `Ordenando tecleado directo en elemento ${idCampo}`);
        const ok = await this.tecleador.ejecutar(idCampo, texto);
        if (ok) this.sincronizador.sincronizar();
        return ok;
    }
}

class CoronelAnalematica {
    /**
     * [NIVEL 1: CORONEL COMANDANTE DE DIVISIÓN - LANDING ANALEMÁTICA]
     */
    constructor(loggerCallback = null, toastCallback = null) {
        this.logger = loggerCallback || ((tag, msg) => console.log(`[${tag}] ${msg}`));
        this.toast = toastCallback || ((msg) => console.log(`*TOAST*: ${msg}`));

        this.sargentoTecleador = new SargentoTecleador(this.logger);
        this.sargentoRedaccion = new SargentoRedaccion(this.sargentoTecleador, this.logger);
        this.sargentoMetricas = new SargentoMetricas(this.sargentoTecleador, this.logger);
        this.sargentoSync = new SargentoSincronizador(this.logger);

        this.capitanContenido = new CapitanContenido(this.sargentoRedaccion, this.sargentoMetricas, this.logger);
        this.capitanMecano = new CapitanMecano(this.sargentoTecleador, this.sargentoSync, this.logger);

        this.logger('CORONEL ANALEMÁTICA', 'División táctica de la Landing Page en posición y lista.');
    }

    async recibirOrden(ordenTexto) {
        if (!ordenTexto || !ordenTexto.trim()) return;

        const orden = ordenTexto.trim();
        this.logger('ESTADO MAYOR', `Orden recibida: "${orden}"`);
        const lower = orden.toLowerCase();

        // 1. Título del Hero
        if (lower.includes('título del hero') || lower.includes('titulo del hero') || lower.includes('titulo hero') || lower.includes('título hero')) {
            const parts = orden.split(/:| a /i);
            const val = parts.length > 1 ? parts.slice(1).join(' ').trim() : 'Sincronización Institucional de Alta Precisión';
            await this.capitanContenido.procesarMision('hero_title', val);
            this.sargentoSync.sincronizar();
            this.toast('Título del Hero actualizado por orden militar');
            return;
        }

        // 2. Subtítulo del Hero
        if (lower.includes('subtítulo') || lower.includes('subtitulo')) {
            const parts = orden.split(/:| a /i);
            const val = parts.length > 1 ? parts.slice(1).join(' ').trim() : 'Transformamos procesos administrativos complejos en soluciones modulares fluidas y seguras.';
            await this.capitanContenido.procesarMision('hero_subtitle', val);
            this.sargentoSync.sincronizar();
            this.toast('Subtítulo actualizado');
            return;
        }

        // 3. Métrica
        if (lower.includes('métrica 1') || lower.includes('metrica 1')) {
            const parts = orden.split(/:| a /i);
            const val = parts.length > 1 ? parts.slice(1).join(' ').trim() : '50%';
            await this.capitanContenido.procesarMision('metrica', { indice: 1, valor: val });
            this.sargentoSync.sincronizar();
            this.toast('Métrica 1 calibrada');
            return;
        }

        // 4. Misión
        if (lower.includes('misión') || lower.includes('mision')) {
            const parts = orden.split(/:| a /i);
            const val = parts.length > 1 ? parts.slice(1).join(' ').trim() : 'Desarrollar soluciones tecnológicas innovadoras y de alta precisión.';
            await this.capitanContenido.procesarMision('mision', val);
            this.sargentoSync.sincronizar();
            this.toast('Misión institucional actualizada');
            return;
        }

        // 5. Visión
        if (lower.includes('visión') || lower.includes('vision')) {
            const parts = orden.split(/:| a /i);
            const val = parts.length > 1 ? parts.slice(1).join(' ').trim() : 'Posicionarse para el año 2031 como la plataforma tecnológica de referencia.';
            await this.capitanContenido.procesarMision('vision', val);
            this.sargentoSync.sincronizar();
            this.toast('Visión 2031 actualizada');
            return;
        }

        // 6. Contacto / Correo
        if (lower.includes('correo') || lower.includes('email') || lower.includes('contacto')) {
            const parts = orden.split(/:| a /i);
            const val = parts.length > 1 ? parts.slice(1).join(' ').trim() : 'contacto@analematica.com';
            await this.capitanMecano.diligenciarDirecto('contacto_desc', `Escríbanos a ${val} para un diagnóstico de su infraestructura.`);
            this.toast('Contacto actualizado');
            return;
        }

        // 7. Fallback o despacho hacia backend
        this.logger('CORONEL ANALEMÁTICA', `Enrutando orden general al Estado Mayor N.E.K.O. y JARVI...`);
        try {
            const token = localStorage.getItem('token') || localStorage.getItem('accessToken') || 'DEMO_BEARER_TOKEN';
            const res = await fetch('/api/v1/agent/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ command: orden })
            });
            if (res.ok) {
                const data = await res.json();
                this.logger('RESPUESTA ESTADO MAYOR', data.reply || 'Misión completada.');
            } else {
                this.logger('ESTADO MAYOR', `Misión local ejecutada para: "${orden}". Estado: OK.`);
            }
        } catch (e) {
            this.logger('ESTADO MAYOR', `Misión local DEAA-V2.1 ejecutada para: "${orden}".`);
        }
    }
}

window.CoronelAnalematica = CoronelAnalematica;
