'use client';

import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import FormField from '@/components/ui/FormField'; // Importar el nuevo componente

// Tipos para los datos de los formularios
type LoginFormInputs = {
  identifier: string;
  password: string;
};

type MfaFormInputs = {
  code: string;
};

export default function LoginPage() {
  const { login, mfaRequired, verifyMfa } = useAuth();
  const [error, setError] = useState<string | null>(null);

  // Hook de formulario para el login principal
  const {
    register: registerLogin,
    handleSubmit: handleLoginSubmit,
    formState: { errors: loginErrors, isSubmitting: isLoginSubmitting },
  } = useForm<LoginFormInputs>();

  // Hook de formulario para el código MFA
  const {
    register: registerMfa,
    handleSubmit: handleMfaSubmit,
    formState: { errors: mfaErrors, isSubmitting: isMfaSubmitting },
    reset: resetMfaForm,
  } = useForm<MfaFormInputs>();

  // --- Envío del formulario de login ---
  const onLoginSubmit: SubmitHandler<LoginFormInputs> = async (data) => {
    setError(null);
    try {
      await login(data.identifier, data.password);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Error al iniciar sesión. Verifica tus credenciales.');
      }
    }
  };

  // --- Envío del formulario MFA ---
  const onMfaSubmit: SubmitHandler<MfaFormInputs> = async (data) => {
    setError(null);
    try {
      await verifyMfa(data.code);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Código incorrecto. Intenta nuevamente.');
      }
      resetMfaForm();
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        {!mfaRequired ? (
          <>
            <h2 className="text-2xl font-bold text-center text-gray-900">
              Acceso al Sistema
            </h2>

            {error && <div className="p-4 text-red-800 bg-red-100 border border-red-200 rounded-md">{error}</div>}

            <form className="space-y-6" onSubmit={handleLoginSubmit(onLoginSubmit)}>
              <FormField
                name="identifier"
                label="Correo Electrónico o Usuario"
                register={registerLogin}
                errors={loginErrors}
                autoComplete="username"
                disabled={isLoginSubmitting}
                required
              />
              <FormField
                name="password"
                label="Contraseña"
                type="password"
                register={registerLogin}
                errors={loginErrors}
                autoComplete="current-password"
                disabled={isLoginSubmitting}
                required
              />
              <div>
                <button
                  type="submit"
                  disabled={isLoginSubmitting}
                  className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400"
                >
                  {isLoginSubmitting ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                </button>
              </div>
            </form>
            <div className="text-sm text-center text-gray-600">
              <p>
                ¿No tienes una cuenta?{' '}
                <Link href="/registro" className="font-medium text-indigo-600 hover:text-indigo-500">
                  Regístrate aquí
                </Link>
              </p>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-2xl font-bold text-center text-gray-900">
              Verificación de dos pasos
            </h2>
            <p className="text-sm text-center text-gray-600">
              Hemos enviado un código a su correo electrónico. Por favor, introdúzcalo a continuación.
            </p>

            {error && <div className="p-4 text-red-800 bg-red-100 border border-red-200 rounded-md">{error}</div>}

            <form className="space-y-6" onSubmit={handleMfaSubmit(onMfaSubmit)}>
              <FormField
                name="code"
                label="Código de Verificación"
                register={registerMfa}
                errors={mfaErrors}
                inputMode="numeric"
                autoComplete="one-time-code"
                disabled={isMfaSubmitting}
                required
                className="block w-full px-3 py-2 mt-1 text-center tracking-[0.5em] placeholder-gray-400 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
              <div>
                <button
                  type="submit"
                  disabled={isMfaSubmitting}
                  className="w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400"
                >
                  {isMfaSubmitting ? 'Verificando...' : 'Verificar Código'}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}