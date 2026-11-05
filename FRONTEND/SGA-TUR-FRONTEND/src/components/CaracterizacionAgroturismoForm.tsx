"use client";

import React, { useState, useEffect, FormEvent } from 'react';
import { CaracterizacionAgroturismo } from '@/services/api';

interface Props {
  initialData?: CaracterizacionAgroturismo | null;
  onSubmit: (formData: Partial<CaracterizacionAgroturismo>) => void;
  onCancel: () => void;
  prestadorId: number;
  readOnly?: boolean;
}

// Helper component for form sections
const FormSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
    <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">{title}</h3>
    <div className="space-y-4">{children}</div>
  </div>
);

const CaracterizacionAgroturismoForm: React.FC<Props> = ({ initialData, onSubmit, onCancel, prestadorId, readOnly = false }) => {
  const [formData, setFormData] = useState<Partial<CaracterizacionAgroturismo>>({});

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    } else {
      // Initialize with default structure if no initial data
      setFormData({
        prestador: prestadorId,
        razon_social: '',
        // ... initialize all other fields to avoid uncontrolled component warnings
        servicios_ofrecidos: {},
        caracteristicas_agroturismo: {},
        especialidad_agricola: {},
        especialidad_pecuaria: {},
        especialidad_avicola: {},
        especialidad_agroindustrial: {},
        actividades_agricolas: {},
        actividades_avicolas: {},
        actividades_agroindustriales: {},
        actividades_pecuarias: {},
        actividades_piscicultura: {},
        actividades_ecoturismo: {},
        actividades_turismo_aventura: {},
        otras_actividades_turismo: {},
        caracteristicas_a_potencializar: {},
        formacion_asesoria_deseada: {},
        medios_promocion: {},
        datos_encuestado: {},
      });
    }
  }, [initialData, prestadorId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const isCheckbox = type === 'checkbox';
    const { checked } = e.target as HTMLInputElement;
    setFormData(prev => ({ ...prev, [name]: isCheckbox ? checked : value }));
  };

  const handleJsonChange = (
    category: keyof CaracterizacionAgroturismo,
    key: string,
    value: boolean
  ) => {
    setFormData((prev) => {
      const currentCategory = prev[category] as Record<string, unknown>;
      const newCategoryState = {
        ...(currentCategory || {}),
        [key]: value,
      };
      return { ...prev, [category]: newCategoryState };
    });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (readOnly) return;
    // Remove empty fields before submitting
    const cleanedData = Object.fromEntries(
      Object.entries(formData).filter(([, v]) => v != null)
    );
    onSubmit(cleanedData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">
        Caracterización de Operadores de Agroturismo
      </h2>

      {/* Formulario 1: GENERALIDADES */}
      <FormSection title="Generalidades">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input name="razon_social" value={formData.razon_social || ''} onChange={handleChange} placeholder="Razón Social" className="input" disabled={readOnly} />
            <input name="camara_comercio_nit" value={formData.camara_comercio_nit || ''} onChange={handleChange} placeholder="NIT" className="input" disabled={readOnly} />
            <input name="rnt_numero" value={formData.rnt_numero || ''} onChange={handleChange} placeholder="Número RNT" className="input" disabled={readOnly} />
            <input name="email_contacto" value={formData.email_contacto || ''} onChange={handleChange} placeholder="Email" className="input" disabled={readOnly} />
            <input name="telefono_fax" value={formData.telefono_fax || ''} onChange={handleChange} placeholder="Teléfono/Fax" className="input" disabled={readOnly} />
            <input name="pagina_web" value={formData.pagina_web || ''} onChange={handleChange} placeholder="Página Web" className="input" disabled={readOnly} />
        </div>
      </FormSection>

      {/* Formulario 2: ACTIVIDADES POTENCIALES */}
      <FormSection title="Actividades Potenciales del Agroturismo">
        <p className="text-sm text-gray-600">Indique con una X según corresponda.</p>
        <div>
            <h4 className="font-semibold">Actividades Agrícolas</h4>
            <label>
                <input type="checkbox" checked={(formData.actividades_agricolas as Record<string, boolean>)?.observacion_cultivos || false} onChange={e => handleJsonChange('actividades_agricolas', 'observacion_cultivos', e.target.checked)} disabled={readOnly} />
                Observación de Manejo de cultivos
            </label>
            {/* ... add all other checkboxes from the document ... */}
        </div>
      </FormSection>

      {/* Formulario 3: POTENCIALIZACIÓN Y FORMACIÓN */}
      <FormSection title="Potencialización y Formación">
        <div>
            <h4 className="font-semibold">¿Cuál de las siguientes características de Agroturismo desea potencializar?</h4>
            <label>
                <input type="checkbox" checked={(formData.caracteristicas_a_potencializar as Record<string, boolean>)?.agricola || false} onChange={e => handleJsonChange('caracteristicas_a_potencializar', 'agricola', e.target.checked)} disabled={readOnly} />
                Agrícola
            </label>
            {/* ... other checkboxes ... */}
        </div>
        <textarea name="otras_actividades_a_potencializar" value={formData.otras_actividades_a_potencializar || ''} onChange={handleChange} placeholder="Otras actividades específicas a potencializar" className="input w-full" rows={3} disabled={readOnly}></textarea>
      </FormSection>

      <div className="flex justify-end space-x-4 pt-4">
        <button type="button" onClick={onCancel} className="btn-secondary">
          {readOnly ? 'Cerrar' : 'Cancelar'}
        </button>
        {!readOnly && (
            <button type="submit" className="btn-primary">
                Guardar Caracterización
            </button>
        )}
      </div>
    </form>
  );
};

export default CaracterizacionAgroturismoForm;

// Basic styling for inputs and buttons (add to your global CSS if needed)
// .input { @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm; }
// .btn-primary { @apply px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700; }
// .btn-secondary { @apply px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300; }
// label { @apply flex items-center space-x-2; }