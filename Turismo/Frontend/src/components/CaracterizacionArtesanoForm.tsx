"use client";

import React, { useState, useEffect, FormEvent } from 'react';
import Image from 'next/image';
import { CaracterizacionArtesano } from '@/services/api';

interface Props {
  initialData?: CaracterizacionArtesano | null;
  onSubmit: (formData: FormData) => void;
  onCancel: () => void;
  artesanoId: number;
  readOnly?: boolean;
}

const FormSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
    <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">{title}</h3>
    <div className="space-y-4">{children}</div>
  </div>
);

const CaracterizacionArtesanoForm: React.FC<Props> = ({ initialData, onSubmit, onCancel, artesanoId, readOnly = false }) => {
  const [formData, setFormData] = useState<Partial<CaracterizacionArtesano>>({});
  const [fotoFile, setFotoFile] = useState<File | null>(null);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    } else {
      setFormData({
        artesano: artesanoId,
        oficios_artesanales: {},
        idiomas: {},
        capacitaciones_recibidas: [],
      });
    }
  }, [initialData, artesanoId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const isCheckbox = type === 'checkbox';
    const { checked } = e.target as HTMLInputElement;
    setFormData(prev => ({ ...prev, [name]: isCheckbox ? checked : value }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (readOnly) return;

    const data = new FormData();
    // Use a type assertion for the keys to ensure type safety
    (Object.keys(formData) as Array<keyof CaracterizacionArtesano>).forEach(key => {
        const value = formData[key];
        if (key === 'foto' || value instanceof File) return;

        if (typeof value === 'object' && value !== null) {
            // Ensure array is stringified correctly
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
        Caracterización de Artesanos
      </h2>

      <FormSection title="1. Identificación General">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input name="documento_identidad" value={formData.documento_identidad || ''} onChange={handleChange} placeholder="Documento de Identidad" className="input" disabled={readOnly} />
            <input name="celular" value={formData.celular || ''} onChange={handleChange} placeholder="Celular" className="input" disabled={readOnly} />
            <input name="email" value={formData.email || ''} type="email" onChange={handleChange} placeholder="Email" className="input" disabled={readOnly} />
        </div>
         <div>
            <label>Foto del Artesano</label>
            <input type="file" name="foto" onChange={(e) => setFotoFile(e.target.files ? e.target.files[0] : null)} className="input" disabled={readOnly} />
            {initialData?.foto && !fotoFile && <Image src={initialData.foto} alt="Foto actual" width={96} height={96} className="h-24 w-24 object-cover rounded-full mt-2" />}
        </div>
      </FormSection>

      <FormSection title="2. Especialidad Artesanal">
        <select name="tipo_artesania" value={formData.tipo_artesania || ''} onChange={handleChange} className="input" disabled={readOnly}>
            <option value="">Seleccione tipo de artesanía...</option>
            <option value="INDIGENA">Artesanía Indígena</option>
            <option value="CONTEMPORANEA">Artesanía Contemporánea o Neoartesanía</option>
            <option value="TRADICIONAL">Tradicional popular</option>
            <option value="OTRA">Otra</option>
        </select>
        {formData.tipo_artesania === 'OTRA' && (
            <input name="tipo_artesania_otra" value={formData.tipo_artesania_otra || ''} onChange={handleChange} placeholder="Especifique otra" className="input mt-2" disabled={readOnly} />
        )}
        <textarea name="descripcion_proceso" value={formData.descripcion_proceso || ''} onChange={handleChange} placeholder="Breve descripción del proceso de elaboración" className="input w-full" rows={4} disabled={readOnly}></textarea>
      </FormSection>

      <FormSection title="3. Formación y Experiencia">
         <label><input type="checkbox" name="certificado_aptitud_sena" checked={formData.certificado_aptitud_sena || false} onChange={handleChange} disabled={readOnly} /> ¿Posee certificado de aptitud Profesional SENA?</label>
         <textarea name="temas_profundizar" value={formData.temas_profundizar || ''} onChange={handleChange} placeholder="¿En qué temas les gustaría profundizar?" className="input w-full" rows={3} disabled={readOnly}></textarea>
         <textarea name="elementos_maquinaria_necesaria" value={formData.elementos_maquinaria_necesaria || ''} onChange={handleChange} placeholder="Elementos o maquinaria que necesita" className="input w-full" rows={3} disabled={readOnly}></textarea>
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

export default CaracterizacionArtesanoForm;

// Basic styling for inputs and buttons (add to your global CSS if needed)
// .input { @apply w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm; }
// .btn-primary { @apply px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700; }
// .btn-secondary { @apply px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300; }
// label { @apply flex items-center space-x-2; }