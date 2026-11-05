"use client";

import React, { useState, useEffect, FormEvent } from 'react';
import Image from 'next/image';
import { CaracterizacionGuiaTuristico } from '@/services/api';

interface Props {
  initialData?: CaracterizacionGuiaTuristico | null;
  onSubmit: (formData: FormData) => void;
  onCancel: () => void;
  prestadorId: number;
  readOnly?: boolean;
}

const FormSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
    <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">{title}</h3>
    <div className="space-y-4">{children}</div>
  </div>
);

const CaracterizacionGuiaTuristicoForm: React.FC<Props> = ({ initialData, onSubmit, onCancel, prestadorId, readOnly = false }) => {
  const [formData, setFormData] = useState<Partial<CaracterizacionGuiaTuristico>>({});
  const [fotoFile, setFotoFile] = useState<File | null>(null);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    } else {
      setFormData({
        prestador: prestadorId,
        nombres_apellidos: '',
        especialidades: {},
        idiomas: {},
        capacitaciones_recibidas: [],
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
    category: keyof CaracterizacionGuiaTuristico,
    key: string,
    value: boolean
  ) => {
    setFormData((prev) => ({
      ...prev,
      [category]: {
        ...((prev[category] as Record<string, unknown>) || {}),
        [key]: value,
      },
    }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (readOnly) return;

    const data = new FormData();
    (Object.keys(formData) as Array<keyof CaracterizacionGuiaTuristico>).forEach(key => {
        const value = formData[key];
        if (key === 'foto' || value instanceof File) return;

        if (typeof value === 'object' && value !== null) {
            data.append(key, JSON.stringify(value));
        } else if (value !== null && value !== undefined) {
            data.append(key, String(value));
        }
    });

    if (fotoFile) {
      data.append('foto', fotoFile);
    }

    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">
        Caracterización de Guías Turísticos
      </h2>

      <FormSection title="1. Identificación General">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input name="nombres_apellidos" value={formData.nombres_apellidos || ''} onChange={handleChange} placeholder="Nombres y Apellidos" className="input" disabled={readOnly} />
            <input name="documento_identidad" value={formData.documento_identidad || ''} onChange={handleChange} placeholder="Documento de Identidad" className="input" disabled={readOnly} />
            <input name="direccion_ubicacion" value={formData.direccion_ubicacion || ''} onChange={handleChange} placeholder="Dirección" className="input" disabled={readOnly} />
            <input name="municipio" value={formData.municipio || ''} onChange={handleChange} placeholder="Municipio" className="input" disabled={readOnly} />
            <input name="celular" value={formData.celular || ''} onChange={handleChange} placeholder="Celular" className="input" disabled={readOnly} />
            <input name="email" value={formData.email || ''} type="email" onChange={handleChange} placeholder="Email" className="input" disabled={readOnly} />
        </div>
        <div>
            <label>Foto del Guía</label>
            <input type="file" name="foto" onChange={(e) => setFotoFile(e.target.files ? e.target.files[0] : null)} className="input" disabled={readOnly} />
            {initialData?.foto && !fotoFile && <Image src={initialData.foto} alt="Foto actual" width={96} height={96} className="h-24 w-24 object-cover rounded-full mt-2" />}
        </div>
      </FormSection>

      <FormSection title="2. Especialidad del Guía">
        <p>Marque las especialidades que apliquen:</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            <label><input type="checkbox" checked={!!(formData.especialidades as Record<string, boolean>)?.agroturismo} onChange={e => handleJsonChange('especialidades', 'agroturismo', e.target.checked)} disabled={readOnly} /> Agroturismo</label>
            <label><input type="checkbox" checked={!!(formData.especialidades as Record<string, boolean>)?.aviturismo} onChange={e => handleJsonChange('especialidades', 'aviturismo', e.target.checked)} disabled={readOnly} /> Aviturismo</label>
            <label><input type="checkbox" checked={!!(formData.especialidades as Record<string, boolean>)?.ecoturismo} onChange={e => handleJsonChange('especialidades', 'ecoturismo', e.target.checked)} disabled={readOnly} /> Ecoturismo</label>
            {/* Add more specialities as needed */}
        </div>
      </FormSection>

      <FormSection title="3. Formación y Experiencia">
        <label><input type="checkbox" name="tecnologia_guianza_sena" checked={formData.tecnologia_guianza_sena || false} onChange={handleChange} disabled={readOnly} /> ¿Posee la tecnología en Guianza Turística que oferta el SENA?</label>
        <input name="numero_tarjeta_profesional" value={formData.numero_tarjeta_profesional || ''} onChange={handleChange} placeholder="Número de Tarjeta Profesional" className="input" disabled={readOnly} />
        <input name="fecha_tarjeta" value={formData.fecha_tarjeta || ''} type="date" onChange={handleChange} placeholder="Fecha Tarjeta Profesional" className="input" disabled={readOnly} />
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

export default CaracterizacionGuiaTuristicoForm;

// Basic styling for inputs and buttons (add to your global CSS if needed)
// .input { @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm; }
// .btn-primary { @apply px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700; }
// .btn-secondary { @apply px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300; }
// label { @apply flex items-center space-x-2; }