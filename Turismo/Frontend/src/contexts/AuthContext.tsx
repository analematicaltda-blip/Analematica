'use client';

import React, { createContext, useState, useContext, ReactNode, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useEntity } from './EntityContext';
import { toast } from 'react-toastify';
import api from '@/services/api'; // Importar la instancia centralizada de Axios
import axios from 'axios'; // Importar axios solo para el type guard isAxiosError

interface SavedItem {
  id: number;
  content_type_name: string;
  object_id: number;
}

// --- Tipos de Datos ---

interface CategoriaPrestador {
  id: number;
  nombre: string;
  slug: string;
}

interface PrestadorProfile {
  id: number;
  nombre_negocio: string;
  descripcion: string;
  telefono: string;
  email_contacto: string;
  latitud: number;
  longitud: number;
  categoria: CategoriaPrestador;
  // Añade otros campos del perfil del prestador que necesites
}

interface User {
  pk: number;
  username: string;
  email: string;
  role:
    | 'ADMIN'
    | 'ADMIN_ENTIDAD'
    | 'FUNCIONARIO_DIRECTIVO'
    | 'FUNCIONARIO_PROFESIONAL'
    | 'PRESTADOR'
    | 'ARTESANO'
    | 'TURISTA';
  perfil_prestador?: PrestadorProfile; // El perfil es opcional
}

export interface RegisterData {
  // Campos comunes
  username?: string;
  email: string;
  password1: string;
  password2:string;
  role:
    | 'TURISTA'
    | 'PRESTADOR'
    | 'ARTESANO'
    | 'ADMINISTRADOR'
    | 'FUNCIONARIO_DIRECTIVO'
    | 'FUNCIONARIO_PROFESIONAL';

  department_id?: number;
  municipality_id?: number;

  // Campos para Prestador
  nombre_negocio?: string;
  categoria_id?: number;

  // Campos para Artesano
  nombre_taller?: string;
  rubro_id?: number;

  // Campos para Administrador
  cargo?: string;
  dependencia_asignada?: string;
  nivel_acceso?: string;

  // Campos para Funcionario Directivo
  dependencia?: string;
  nivel_direccion?: string;
  area_funcional?: string;

  // Campos para Funcionario Profesional
  // 'dependencia' ya está definido
  profesion?: string;
  area_asignada?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  mfaRequired: boolean;
  login: (identifier: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  verifyMfa: (code: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isItemSaved: (contentType: string, objectId: number) => boolean;
  toggleSaveItem: (contentType: string, objectId: number) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [loginCredentials, setLoginCredentials] = useState<{ identifier: string; password?: string; code?: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [savedItemsMap, setSavedItemsMap] = useState<Map<string, number>>(new Map());
  const router = useRouter();
  const { loadEntity, clearEntity } = useEntity();

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    clearEntity();
    setMfaRequired(false);
    setLoginCredentials(null);
    setSavedItemsMap(new Map());
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
    }
    // La redirección se manejará en las páginas o layouts que lo requieran.
  }, [clearEntity]);

  const completeLogin = useCallback((key: string, userData: User) => {
    setToken(key);
    setUser(userData);
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', key);
    }
    setMfaRequired(false);
    toast.success(`¡Bienvenido, ${userData.username}!`);

    switch (userData.role) {
      case 'TURISTA':
        router.push('/mi-viaje');
        break;
      case 'PRESTADOR':
      case 'ARTESANO':
      case 'ADMIN':
      case 'FUNCIONARIO_DIRECTIVO':
      case 'FUNCIONARIO_PROFESIONAL':
        router.push('/dashboard');
        break;
      default:
        router.push('/');
    }
  }, [router]);

  const fetchUserData = useCallback(async () => {
    try {
      const userResponse = await api.get<User>('/auth/user/');
      const userData = userResponse.data;
      setUser(userData);

      if (userData.role === 'TURISTA') {
        const savedItemsResponse = await api.get<{ results: SavedItem[] }>('/mi-viaje/');
        const itemMap = new Map(
          savedItemsResponse.data.results.map((item) => [
            `${item.content_type_name}_${item.object_id}`,
            item.id,
          ])
        );
        setSavedItemsMap(itemMap);
      } else {
        setSavedItemsMap(new Map());
      }

      // Normalización de Contexto: Cargar entidad si el rol es operativo/admin
      const rolesWithEntity = ['ADMIN', 'ADMIN_ENTIDAD', 'PRESTADOR', 'ARTESANO', 'FUNCIONARIO_DIRECTIVO'];
      if (rolesWithEntity.includes(userData.role)) {
        await loadEntity();
      } else {
        clearEntity();
      }

      return userData;
    } catch (error) {
      logout();
      return null;
    }
  }, [logout, loadEntity, clearEntity]);

useEffect(() => {
  const checkAuth = async () => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      try {
        await fetchUserData();
      } catch (error) {
        // El error ya es manejado dentro de fetchUserData (que llama a logout),
        // pero lo atrapamos aquí para prevenir cualquier error no controlado.
        console.error("Fallo al autenticar con el token almacenado:", error);
      }
    }
  };

  const initialize = async () => {
    try {
      if (typeof window !== 'undefined') {
        await checkAuth();
      }
    } finally {
      // Nos aseguramos de que el estado de carga se desactive siempre.
      setIsLoading(false);
    }
  };

  initialize();
}, [fetchUserData]);

  const login = async (identifier: string, password: string) => {
    try {
      const payload = {
        email: identifier,
        password,
      };
      const response = await api.post<{ key: string; user: User }>('/auth/login/', payload);

      if (response.data && response.data.key && response.data.user) {
        completeLogin(response.data.key, response.data.user);
      } else {
        setMfaRequired(true);
        setLoginCredentials({ identifier, password });
      }
    } catch (err: unknown) {
      if (process.env.NODE_ENV === 'production') {
        toast.error("Ocurrió un error. Por favor verifica tus datos e intenta nuevamente.");
      } else {
        if (axios.isAxiosError(err) && err.response) {
          const errorMsg = err.response.data?.non_field_errors?.[0] || 'El usuario o la contraseña son incorrectos.';
          toast.error(`Error de Login (dev): ${errorMsg}`);
        } else {
          toast.error("Error de conexión (dev).");
        }
      }
      throw err;
    }
  };

  const verifyMfa = async (code: string) => {
    if (!loginCredentials?.identifier) {
      throw new Error('No se encontraron credenciales para la verificación MFA.');
    }
    try {
      const payload = {
        username: loginCredentials.identifier,
        password: loginCredentials.password,
        code,
      };
      const response = await api.post('/auth/login/', payload);
      if (response.data?.key) {
        // Primero, establece el token para que fetchUserData funcione
        setToken(response.data.key);
        if (typeof window !== 'undefined') {
          localStorage.setItem('authToken', response.data.key);
        }
        // Ahora, obtén los datos del usuario
        const userData = await fetchUserData();
        if (userData) {
          completeLogin(response.data.key, userData);
        } else {
            throw new Error('No se pudieron obtener los datos del usuario tras la verificación MFA.');
        }
      } else {
        throw new Error('Respuesta inesperada del servidor durante la verificación MFA.');
      }
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response) {
        const errorMsg = err.response.data?.non_field_errors?.[0] || 'El código de verificación es incorrecto.';
        throw new Error(errorMsg);
      }
      throw new Error('Error al verificar el código. Inténtelo de nuevo.');
    }
  };

  const isItemSaved = (contentType: string, objectId: number): boolean => {
    return savedItemsMap.has(`${contentType}_${objectId}`);
  };

  const toggleSaveItem = async (contentType: string, objectId: number) => {
    if (!user || user.role !== 'TURISTA') {
      toast.warn("Necesitas iniciar sesión como turista para guardar favoritos.");
      router.push('/login');
      return;
    }
    const itemKey = `${contentType}_${objectId}`;
    const savedItemId = savedItemsMap.get(itemKey);
    try {
      if (savedItemId) {
        await api.delete(`/mi-viaje/${savedItemId}/`);
        toast.success("Elemento eliminado de tu viaje.");
      } else {
        await api.post('/mi-viaje/', { content_type: contentType, object_id: objectId });
        toast.success("Elemento añadido a tu viaje.");
      }
      // Volver a cargar los datos del usuario para actualizar la lista de guardados
      await fetchUserData();
    } catch (error) {
      toast.error("Hubo un error al procesar tu solicitud.");
    }
  };

  const register = async (data: RegisterData) => {
    // Determinar el endpoint correcto usando una estructura switch para mayor robustez.
    let endpoint = '';
    switch (data.role) {
      case 'TURISTA':
        endpoint = '/auth/registration/turista/';
        break;
      case 'PRESTADOR':
        endpoint = '/auth/registration/prestador/';
        break;
      case 'ARTESANO':
        endpoint = '/auth/registration/artesano/';
        break;
      case 'ADMINISTRADOR':
        endpoint = '/auth/registration/administrador/';
        break;
      case 'FUNCIONARIO_DIRECTIVO':
        endpoint = '/auth/registration/funcionario_directivo/';
        break;
      case 'FUNCIONARIO_PROFESIONAL':
        endpoint = '/auth/registration/funcionario_profesional/';
        break;
      default:
        // Lanzar un error si el rol no es válido para evitar enviar a un endpoint vacío.
        toast.error(`Error: Rol de registro no válido: ${data.role}`);
        throw new Error(`Rol de registro no válido: ${data.role}`);
    }

    // Construir el payload base con campos comunes
    const payload: { [key: string]: string | number | undefined } = {
      username: data.username || `${data.email.split('@')[0]}${Math.floor(Math.random() * 10000)}`,
      email: data.email,
      password1: data.password1,
      password2: data.password2,
      role: data.role, // Enviar siempre el rol
    };

    // Añadir campos de ubicación para todos los roles
    payload.department_id = data.department_id;
    payload.municipality_id = data.municipality_id;

    // Añadir campos específicos del rol al payload
    switch (data.role) {
      case 'PRESTADOR':
        payload.nombre_negocio = data.nombre_negocio;
        payload.categoria_id = data.categoria_id;
        break;
      case 'ARTESANO':
        payload.nombre_taller = data.nombre_taller;
        payload.rubro_id = data.rubro_id;
        break;
      case 'ADMINISTRADOR':
        payload.cargo = data.cargo;
        payload.dependencia_asignada = data.dependencia_asignada;
        payload.nivel_acceso = data.nivel_acceso;
        break;
      case 'FUNCIONARIO_DIRECTIVO':
        payload.dependencia = data.dependencia;
        payload.nivel_direccion = data.nivel_direccion;
        payload.area_funcional = data.area_funcional;
        break;
      case 'FUNCIONARIO_PROFESIONAL':
        payload.dependencia = data.dependencia;
        payload.profesion = data.profesion;
        payload.area_asignada = data.area_asignada;
        break;
    }

    try {
      await api.post(endpoint, payload);
      // Mensaje de éxito unificado y amigable para el usuario, como se solicitó.
      toast.success("¡Registro exitoso! Ahora puedes iniciar sesión.");
    } catch (err: unknown) {
      if (process.env.NODE_ENV === 'production') {
        toast.error("Ocurrió un error. Por favor verifica tus datos e intenta nuevamente.");
      } else {
        if (axios.isAxiosError(err) && err.response?.data) {
          const errors = err.response.data;
          const errorMessages = Object.entries(errors).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`);
          toast.error(`Error de Registro (dev): ${errorMessages.join(' ')}`, { autoClose: 10000 });
        } else {
          toast.error("Error de conexión o respuesta inesperada (dev).");
        }
      }
      throw err;
    }
  };

  const value: AuthContextType = {
    isAuthenticated: !!token,
    user,
    token,
    mfaRequired,
    login,
    register,
    verifyMfa,
    logout,
    isLoading,
    isItemSaved,
    toggleSaveItem,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};
