'use client';

import React, { useState, useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { RegisterData } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import FormField from '@/components/ui/FormField';
import { toast } from 'react-toastify';

type FormErrors = {
  [key: string]: string[];
};

interface Department {
  id: number;
  name: string;
}

interface Municipality {
  id: number;
  name: string;
}

interface Categoria {
    id: number;
    nombre: string;
}

interface Rubro {
    id: number;
    nombre: string;
}

export default function RegisterPage() {
  const { register: registerUser } = useAuth();
  const router = useRouter();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [municipalities, setMunicipalities] = useState<Municipality[]>([]);
  const [categories, setCategories] = useState<Categoria[]>([]);
  const [rubros, setRubros] = useState<Rubro[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<RegisterData>({
    defaultValues: {
      role: 'TURISTA',
    },
  });

  const [success, setSuccess] = useState<string | null>(null);

  const role = watch('role');
  const departmentId = watch('department_id');

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [depts, cats, rubs] = await Promise.all([
          api.get('/departments/'),
          api.get('/prestadores/categorias/'),
          api.get('/artesanos/rubros/')
        ]);
        setDepartments(depts.data.results || depts.data);
        setCategories(cats.data.results || cats.data);
        setRubros(rubs.data.results || rubs.data);
      } catch (error) {
        console.error("Error fetching initial data:", error);
        toast.error('ERROR DE API: No se pudo cargar la información inicial para el registro.');
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    const fetchMunicipalities = async () => {
      if (departmentId) {
        try {
          const response = await api.get(`/municipalities/?department=${departmentId}`);
          setMunicipalities(response.data.results || response.data);
        } catch (error) {
          toast.error('No se pudieron cargar los municipios.');
        }
      } else {
        setMunicipalities([]);
      }
    };
    fetchMunicipalities();
  }, [departmentId]);

  const onSubmit: SubmitHandler<RegisterData> = async (data) => {
    setSuccess(null);

    if (data.password1 !== data.password2) {
      setError('password2', {
        type: 'manual',
        message: 'Las contraseñas no coinciden.',
      });
      toast.error('Las contraseñas no coinciden.');
      return;
    }

    try {
      await registerUser(data);
      // El toast de éxito ya se maneja en el AuthContext
      setSuccess('¡Registro exitoso! Serás redirigido para iniciar sesión.');
      setTimeout(() => router.push('/login'), 3000);
    } catch (err: unknown) {
      const errorData = err as FormErrors;

      if (typeof errorData === 'object' && errorData !== null) {
        // Lógica para mostrar errores en los campos del formulario
        for (const key in errorData) {
          if (Object.prototype.hasOwnProperty.call(data, key)) {
            const fieldName = key as keyof RegisterData;
            const message = Array.isArray(errorData[fieldName]) ? errorData[fieldName]![0] : String(errorData[fieldName]);
            setError(fieldName, { type: 'manual', message });
          }
        }

        // Lógica unificada para mostrar el toast de error
        const errorMessages = Object.entries(errorData).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`);
        const displayMessage = process.env.NODE_ENV === 'production'
          ? "Ocurrió un error. Por favor verifica tus datos e intenta nuevamente."
          : `Error de Registro (dev): ${errorMessages.join(' ')}`;

        toast.error(displayMessage, { autoClose: 10000 });

      } else {
         toast.error('Ocurrió un error inesperado. Por favor, inténtalo de nuevo.');
      }
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-center text-gray-900">Crear una Cuenta</h1>

        {success && (
          <div className="p-4 text-green-800 bg-green-100 border border-green-200 rounded-md">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            name="email"
            label="Correo Electrónico"
            type="email"
            register={register}
            errors={errors}
            autoComplete="email"
            required
          />

          <FormField
            name="username"
            label="Nombre de Usuario"
            register={register}
            errors={errors}
            autoComplete="username"
            required
          />

          <FormField
            name="password1"
            label="Contraseña"
            type="password"
            register={register}
            errors={errors}
            autoComplete="new-password"
            required
            validation={{
              validate: (value: string) =>
                value === watch('password1') || 'Las contraseñas no coinciden.'
            }}
          />

          <FormField
            name="password2"
            label="Confirmar Contraseña"
            type="password"
            register={register}
            errors={errors}
            autoComplete="new-password"
            required
          />

          <div>
            <label
              htmlFor="role"
              className="block text-sm font-medium text-gray-700"
            >
              Quiero registrarme como:
            </label>
            <select
              id="role"
              {...register('role')}
              className="w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="TURISTA">Turista</option>
              <option value="PRESTADOR">Prestador de Servicios Turísticos</option>
              <option value="ARTESANO">Artesano</option>
              <option value="ADMINISTRADOR">Administrador</option>
              <option value="FUNCIONARIO_DIRECTIVO">Funcionario Directivo</option>
              <option value="FUNCIONARIO_PROFESIONAL">Funcionario Profesional</option>
            </select>
          </div>

          {/* --- Campos de Ubicación --- */}
          <div className="p-4 space-y-4 border-l-4 border-blue-500 bg-blue-50">
            <h3 className="font-medium text-gray-800">Información de Ubicación</h3>
            <div>
              <label htmlFor="department_id" className="block text-sm font-medium text-gray-700">Departamento</label>
              <select
                id="department_id"
                {...register('department_id', { required: 'Este campo es obligatorio.' })}
                className={`w-full px-3 py-2 mt-1 border rounded-md shadow-sm ${errors.department_id ? 'border-red-500' : 'border-gray-300'}`}
              >
                <option value="">Selecciona un departamento</option>
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>{dept.name}</option>
                ))}
              </select>
              {errors.department_id && <p className="mt-1 text-xs text-red-600">{errors.department_id.message}</p>}
            </div>

            <div>
              <label htmlFor="municipality_id" className="block text-sm font-medium text-gray-700">Municipio</label>
              <select
                id="municipality_id"
                {...register('municipality_id', { required: 'Este campo es obligatorio.' })}
                disabled={!departmentId || municipalities.length === 0}
                className={`w-full px-3 py-2 mt-1 border rounded-md shadow-sm ${errors.municipality_id ? 'border-red-500' : 'border-gray-300'} disabled:bg-gray-200`}
              >
                <option value="">Selecciona un municipio</option>
                {municipalities.map((mun) => (
                  <option key={mun.id} value={mun.id}>{mun.name}</option>
                ))}
              </select>
              {errors.municipality_id && <p className="mt-1 text-xs text-red-600">{errors.municipality_id.message}</p>}
            </div>
          </div>

          {/* --- Campos para Prestador --- */}
          {role === 'PRESTADOR' && (
            <div className="p-4 space-y-4 border-l-4 border-green-500 bg-green-50">
              <h3 className="font-medium text-gray-800">Información del Prestador de Servicios</h3>

              <div className="bg-white p-4 rounded-xl border border-green-100 shadow-sm mb-4">
                  <FormField
                    name="rnt_number"
                    label="Registro Nacional de Turismo (RNT)"
                    register={register}
                    errors={errors}
                    placeholder="Ej: 12345"
                  />
                  <p className="text-[10px] text-slate-500 mt-1 italic">Si posees RNT, ingresalo para validar automáticamente tu información estatal.</p>
              </div>

              <FormField name="nombre_negocio" label="Nombre del Establecimiento" register={register} errors={errors} required />
              <div>
                  <label htmlFor="categoria_id" className="block text-sm font-medium text-gray-700">Categoría del Servicio</label>
                  <select
                      id="categoria_id"
                      {...register('categoria_id', { required: 'Este campo es obligatorio.' })}
                      className={`w-full px-3 py-2 mt-1 border rounded-md shadow-sm ${errors.categoria_id ? 'border-red-500' : 'border-gray-300'}`}
                  >
                      <option value="">Selecciona una categoría</option>
                      {categories.map((cat) => (
                          <option key={cat.id} value={cat.id}>{cat.nombre}</option>
                      ))}
                  </select>
                  {errors.categoria_id && <p className="mt-1 text-xs text-red-600">{errors.categoria_id.message}</p>}
              </div>
            </div>
          )}

          {/* --- Campos para Artesano --- */}
          {role === 'ARTESANO' && (
            <div className="p-4 space-y-4 border-l-4 border-yellow-500 bg-yellow-50">
              <h3 className="font-medium text-gray-800">Información del Artesano</h3>
              <FormField name="nombre_taller" label="Nombre del Taller" register={register} errors={errors} required />
              <div>
                  <label htmlFor="rubro_id" className="block text-sm font-medium text-gray-700">Rubro Principal</label>
                  <select
                      id="rubro_id"
                      {...register('rubro_id', { required: 'Este campo es obligatorio.' })}
                      className={`w-full px-3 py-2 mt-1 border rounded-md shadow-sm ${errors.rubro_id ? 'border-red-500' : 'border-gray-300'}`}
                  >
                      <option value="">Selecciona un rubro</option>
                      {rubros.map((rub) => (
                          <option key={rub.id} value={rub.id}>{rub.nombre}</option>
                      ))}
                  </select>
                  {errors.rubro_id && <p className="mt-1 text-xs text-red-600">{errors.rubro_id.message}</p>}
              </div>
            </div>
          )}

          {/* --- Campos para Administrador --- */}
          {role === 'ADMINISTRADOR' && (
            <div className="p-4 space-y-4 border-l-4 border-red-500 bg-red-50">
                <h3 className="font-medium text-gray-800">Información del Administrador</h3>
                <FormField name="cargo" label="Cargo" register={register} errors={errors} required />
                <FormField name="dependencia_asignada" label="Dependencia Asignada" register={register} errors={errors} required />
                <FormField name="nivel_acceso" label="Nivel de Acceso" register={register} errors={errors} required />
            </div>
          )}

          {/* --- Campos para Funcionario Directivo --- */}
          {role === 'FUNCIONARIO_DIRECTIVO' && (
            <div className="p-4 space-y-4 border-l-4 border-purple-500 bg-purple-50">
                <h3 className="font-medium text-gray-800">Información del Funcionario Directivo</h3>
                <FormField name="dependencia" label="Dependencia" register={register} errors={errors} required />
                <FormField name="nivel_direccion" label="Nivel de Dirección" register={register} errors={errors} required />
                <FormField name="area_funcional" label="Área Funcional" register={register} errors={errors} required />
            </div>
          )}

          {/* --- Campos para Funcionario Profesional --- */}
          {role === 'FUNCIONARIO_PROFESIONAL' && (
            <div className="p-4 space-y-4 border-l-4 border-indigo-500 bg-indigo-50">
                <h3 className="font-medium text-gray-800">Información del Funcionario Profesional</h3>
                <FormField name="dependencia" label="Dependencia" register={register} errors={errors} required />
                <FormField name="profesion" label="Profesión" register={register} errors={errors} required />
                <FormField name="area_asignada" label="Área Asignada" register={register} errors={errors} required />
            </div>
          )}

          <div className="flex items-start gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
            <input
              type="checkbox"
              id="tos_consent"
              required
              className="mt-1 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <label htmlFor="tos_consent" className="text-xs text-slate-600 leading-relaxed font-medium">
              Declaro haber leído y aceptado los <span className="text-indigo-600 underline cursor-pointer">Términos de Operación Institucional</span> y la <span className="text-indigo-600 underline cursor-pointer">Política de Tratamiento de Datos del Ecosistema Sarita</span>. Entiendo que toda acción queda registrada para fines de auditoría legal.
            </label>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-4 py-2 font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300"
            >
              {isSubmitting ? 'Registrando...' : 'Crear Cuenta'}
            </button>
          </div>
        </form>

        <div className="text-sm text-center">
          <Link
            href="/login"
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            ¿Ya tienes una cuenta? Inicia sesión
          </Link>
        </div>
      </div>
    </div>
  );
}