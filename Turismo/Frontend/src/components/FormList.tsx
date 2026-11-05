import React, { useState, useEffect } from 'react';
import { getFormularios, Formulario } from '@/services/formService';
import { getPrestadorProfile, PrestadorProfile } from '@/services/prestadorService';
import { useAuth } from '@/contexts/AuthContext';

interface FormListProps {
  onFillForm: (form: Formulario) => void;
}

const FormList = ({ onFillForm }: FormListProps) => {
  const [forms, setForms] = useState<Formulario[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchAndFilterForms = async () => {
      if (user?.role !== 'PRESTADOR') {
          setIsLoading(false);
          return;
      }
      try {
        setIsLoading(true);
        // Obtener perfil y todos los formularios en paralelo
        const [profile, allForms] = await Promise.all([
          getPrestadorProfile(),
          getFormularios(),
        ]);

        const providerCategorySlug = profile.categoria?.slug;
        const piscinaFormTitulo = "Caracterización para Establecimientos con Piscina";

        const filteredForms = allForms.filter(form => {
          // 1. Incluir formularios sin categoría (genéricos)
          if (!form.categoria) {
              // Excluir el de piscinas si no es la categoría correcta
              if (form.titulo === piscinaFormTitulo) {
                  return providerCategorySlug === 'hoteles' || providerCategorySlug === 'alojamientos';
              }
              return true;
          }
          // 2. Incluir el formulario que coincide con la categoría del prestador
          return form.categoria.slug === providerCategorySlug;
        });

        setForms(filteredForms);
        setError(null);
      } catch (err) {
        setError('No se pudieron cargar los formularios disponibles.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchAndFilterForms();
  }, [user]);

  return (
    <div className="bg-white p-4 sm:p-6 lg:p-8 rounded-2xl shadow-lg">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Mis Formularios de Caracterización</h2>
      <p className="mb-6 text-gray-600">
        Complete los formularios para ayudarnos a entender mejor su negocio y mejorar nuestros servicios turísticos.
      </p>

      {isLoading && <p>Cargando formularios...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!isLoading && !error && forms.length > 0 && (
        <ul className="space-y-4">
          {forms.map((form) => (
            <li key={form.id} className="p-4 border rounded-lg flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-lg">{form.titulo}</h3>
                <p className="text-sm text-gray-500">{form.descripcion}</p>
              </div>
              <button
                onClick={() => onFillForm(form)}
                className="bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600"
              >
                Llenar Formulario
              </button>
            </li>
          ))}
        </ul>
      )}
       {!isLoading && !error && forms.length === 0 && (
        <p className="text-gray-500">No hay formularios disponibles para su categoría en este momento.</p>
      )}
    </div>
  );
};

export default FormList;