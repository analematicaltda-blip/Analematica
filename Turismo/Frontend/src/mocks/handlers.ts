import { http, HttpResponse } from 'msw';

// URL base de la API, debe coincidir con la configuración del cliente
const API_BASE_URL = 'http://localhost:8000/api';

interface LoginRequestBody {
  username?: string;
  email?: string;
  password?: string;
}

interface RegistrationRequestBody {
  email: string;
  password1: string;
  password2: string;
}

interface LlmConfigRequestBody {
    provider?: string;
    apiKey?: string;
}

// Simulación de "base de datos" en memoria para usuarios y configuraciones
const users = new Map();
const llmConfig = {
  provider: 'local',
  apiKey: '',
};

export const handlers = [
  // --- MANEJADOR DE LOGIN MEJORADO ---
  // Devuelve el token y el objeto de usuario en la misma respuesta.
  http.post(`${API_BASE_URL}/auth/login/`, async ({ request }) => {
    const body = await request.json() as LoginRequestBody;
    const username = body.username || body.email;

    const userProfiles = {
      'admin': { role: 'ADMIN', pk: 1 },
      'prestador': { role: 'PRESTADOR', pk: 2 },
      'artesano': { role: 'ARTESANO', pk: 3 },
      'turista': { role: 'TURISTA', pk: 4 },
      'directivo': { role: 'FUNCIONARIO_DIRECTIVO', pk: 5 },
      'profesional': { role: 'FUNCIONARIO_PROFESIONAL', pk: 6 },
    };

    const profile = userProfiles[username];

    if (profile) {
      return HttpResponse.json({
        key: `mock-token-for-${username}`,
        user: {
          pk: profile.pk,
          username: username,
          email: `${username}@example.com`,
          role: profile.role,
        },
      });
    }

    return HttpResponse.json(
      { non_field_errors: ['Credenciales inválidas.'] },
      { status: 400 }
    );
  }),

  // --- MANEJADORES DE REGISTRO POR ROL ---
  // Se crea un manejador para cada endpoint de registro específico
  ...['turista', 'prestador', 'artesano', 'administrador', 'funcionario_directivo', 'funcionario_profesional'].map(role =>
    http.post(`${API_BASE_URL}/auth/registration/${role}/`, async ({ request }) => {
      const body = await request.json() as RegistrationRequestBody;

      if (body.password1 !== body.password2) {
        return HttpResponse.json({ password2: ['Las contraseñas no coinciden.'] }, { status: 400 });
      }
      if (users.has(body.email)) {
          return HttpResponse.json({ email: ['Este correo ya está en uso.'] }, { status: 400 });
      }

      users.set(body.email, { ...body, role: role.toUpperCase() });
      return HttpResponse.json({ detail: `Registro de ${role} exitoso.` }, { status: 201 });
    })
  ),

  // --- MANEJADOR DE CONFIGURACIÓN DEL MENÚ (HEADER) ---
  http.get(`${API_BASE_URL}/config/menu-items/`, () => {
    return HttpResponse.json([
      { id: 1, title: 'Inicio', url: '/', children: [] },
      { id: 2, title: 'Descubre', url: '/descubre', children: [] },
      {
        id: 3,
        title: 'Directorio',
        url: '/directorio',
        children: [
          { id: 4, title: 'Prestadores', url: '/directorio/prestadores' },
          { id: 5, title: 'Artesanos', url: '/directorio/artesanos' },
        ],
      },
      { id: 6, title: 'Institucional', url: '/institucional', children: [] },
    ]);
  }),

  // --- MANEJADORES PARA LA CONFIGURACIÓN DE IA (LLM) ---
  http.get(`${API_BASE_URL}/config/my-llm/`, () => {
    return HttpResponse.json(llmConfig);
  }),

  http.post(`${API_BASE_URL}/config/my-llm/`, async ({ request }) => {
    const newConfig = await request.json() as LlmConfigRequestBody;
    llmConfig.provider = newConfig.provider || llmConfig.provider;
    llmConfig.apiKey = newConfig.apiKey || llmConfig.apiKey;
    return HttpResponse.json(llmConfig, { status: 200 });
  }),

  // --- MANEJADOR DE DATOS DE USUARIO AUTENTICADO ---
  // Devuelve datos de usuario basados en el token de autorización
  http.get(`${API_BASE_URL}/auth/user/`, ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    if (authHeader && authHeader.startsWith('Token mock-token-')) {
        const token = authHeader.substring('Token '.length);
        const roleKey = token.replace('mock-token-', '');

        const roleMap = {
            'admin': 'ADMINISTRADOR',
            'prestador': 'PRESTADOR',
            'artesano': 'ARTESANO',
            'turista': 'TURISTA',
            'directivo': 'FUNCIONARIO_DIRECTIVO',
            'profesional': 'FUNCIONARIO_PROFESIONAL'
        };

        const userRole = roleMap[roleKey] || 'TURISTA';

        return HttpResponse.json({
            pk: 1,
            username: roleKey,
            email: `${roleKey}@example.com`,
            role: userRole,
        });
    }
    return new HttpResponse(null, { status: 401 });
  }),
];