// --- Módulo de Internacionalización (MILA) - Propuesta de Integración ---

const translations = {
    es: {
        welcome: 'Bienvenido',
        logout: 'Cerrar Sesión',
        // --- Menú ---
        'dashboard': 'Dashboard',
        'gestionar-empresas': 'Gestionar Empresas',
        'roles-y-permisos': 'Roles y Permisos',
        'verificar-roles-bd': 'Verificar Roles BD',
        // ... añadir todas las claves de navegación y de la UI
    },
    en: {
        welcome: 'Welcome',
        logout: 'Logout',
        // --- Menu ---
        'dashboard': 'Dashboard',
        'gestionar-empresas': 'Manage Companies',
        'roles-y-permisos': 'Roles & Permissions',
        'verificar-roles-bd': 'Verify DB Roles',
        // ... add all navigation and UI keys
    }
};

let currentLanguage = 'es';

function setLanguage(lang) {
    if (translations[lang]) {
        currentLanguage = lang;
        translatePage();
    }
}

function translatePage() {
    document.querySelectorAll('[data-i18n-key]').forEach(element => {
        const key = element.getAttribute('data-i18n-key');
        if (translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
}

// Función para ser llamada desde otros scripts
function getTranslatedString(key) {
    return translations[currentLanguage][key] || key;
}
