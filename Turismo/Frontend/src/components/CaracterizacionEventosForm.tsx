"use client";

"use client";

import React, { useState, useEffect, FormEvent } from 'react';
import Image from 'next/image';
import { CaracterizacionEmpresaEventos } from '@/services/api';

interface Props {
  initialData?: CaracterizacionEmpresaEventos | null;
  onSubmit: (formData: FormData) => void;
  onCancel: () => void;
  prestadorId: number;
  readOnly?: boolean;
}

const CaracterizacionEventosForm: React.FC<Props> = ({ initialData, onSubmit, onCancel, prestadorId, readOnly = false }) => {
  const [formData, setFormData] = useState<Partial<CaracterizacionEmpresaEventos>>({
    prestador: prestadorId,
    nombre_representante_legal: '',
    nit: '',
    municipio: '',
    direccion_oficina: '',
    nombre_administrador: '',
    celular_contacto: '',
    pagina_web: '',
    tiene_rnt: false,
    numero_rnt: '',
    empleados_hombres_menor_25: 0,
    empleados_hombres_25_40: 0,
    empleados_hombres_mayor_40: 0,
    empleados_mujeres_menor_25: 0,
    empleados_mujeres_25_40: 0,
    empleados_mujeres_mayor_40: 0,
    empleados_lgtbi: 0,
    contratacion_empleados: {},
    grupos_especiales_empleados: {},
    tiempo_funcionamiento: '',
    servicios_ofrecidos: {},
    forma_prestacion_servicios: '',
    forma_prestacion_servicios_otro: '',
    pertenece_gremio: false,
    nombre_gremio: '',
    rutas_servicios: '',
    nivel_academico_empleados: {},
    capacitaciones_recibidas: [],
    tiene_certificacion_norma: false,
    nombre_certificacion_norma: '',
    ha_participado_ferias: false,
    nombre_ferias: '',
    necesidades_fortalecimiento: '',
  });
  const [logoFile, setLogoFile] = useState<File | null>(null);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
        const { checked } = e.target as HTMLInputElement;
        setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
        setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleJsonChange = (
    category: keyof CaracterizacionEmpresaEventos,
    key: string,
    value: string | boolean
  ) => {
    setFormData((prev) => {
      const currentCategory = prev[category] as Record<string, unknown> | undefined;
      return {
        ...prev,
        [category]: {
          ...(currentCategory || {}),
          [key]: value,
        },
      };
    });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const data = new FormData();

    (Object.keys(formData) as Array<keyof CaracterizacionEmpresaEventos>).forEach(key => {
        const value = formData[key];
        if (key === 'logo') return;
        if (typeof value === 'object' && value !== null) {
            data.append(key, JSON.stringify(value));
        } else if (value !== null && value !== undefined) {
            data.append(key, String(value));
        }
    });

    if (logoFile) {
      data.append('logo', logoFile);
    }

    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 border-b pb-4">
        Caracterización de Empresa de Eventos
      </h2>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-700">1. Datos Generales</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input type="text" name="nombre_representante_legal" value={formData.nombre_representante_legal} onChange={handleChange} placeholder="Nombre del Representante Legal" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
          <input type="text" name="nit" value={formData.nit} onChange={handleChange} placeholder="NIT" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
          <input type="text" name="municipio" value={formData.municipio} onChange={handleChange} placeholder="Municipio" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
          <input type="text" name="direccion_oficina" value={formData.direccion_oficina} onChange={handleChange} placeholder="Dirección de la Oficina" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
          <input type="text" name="nombre_administrador" value={formData.nombre_administrador} onChange={handleChange} placeholder="Nombre del Administrador" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
          <input type="text" name="celular_contacto" value={formData.celular_contacto} onChange={handleChange} placeholder="Celular de Contacto" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
          <input type="url" name="pagina_web" value={formData.pagina_web} onChange={handleChange} placeholder="Página Web" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
          <div>
            <label className="flex items-center space-x-2">
              <input type="checkbox" name="tiene_rnt" checked={formData.tiene_rnt} onChange={handleChange} disabled={readOnly} />
              <span>¿Cuenta con RNT?</span>
            </label>
            {formData.tiene_rnt && <input type="text" name="numero_rnt" value={formData.numero_rnt} onChange={handleChange} placeholder="Número RNT" className="w-full mt-2 px-3 py-2 border rounded-md" disabled={readOnly} />}
          </div>
          <div>
            <label>Logo de la empresa</label>
            <input type="file" name="logo" onChange={(e) => setLogoFile(e.target.files ? e.target.files[0] : null)} className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
            {initialData?.logo && !logoFile && <Image src={initialData.logo} alt="Logo actual" width={80} height={80} className="h-20 w-auto mt-2" />}
          </div>
        </div>

        <h4 className="text-lg font-semibold text-gray-600 pt-4">1.14 Conteo de Empleados</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <input type="number" name="empleados_hombres_menor_25" value={formData.empleados_hombres_menor_25} onChange={handleChange} placeholder="Hombres < 25" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
            <input type="number" name="empleados_hombres_25_40" value={formData.empleados_hombres_25_40} onChange={handleChange} placeholder="Hombres 25-40" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
            <input type="number" name="empleados_hombres_mayor_40" value={formData.empleados_hombres_mayor_40} onChange={handleChange} placeholder="Hombres > 40" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
            <input type="number" name="empleados_mujeres_menor_25" value={formData.empleados_mujeres_menor_25} onChange={handleChange} placeholder="Mujeres < 25" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
            <input type="number" name="empleados_mujeres_25_40" value={formData.empleados_mujeres_25_40} onChange={handleChange} placeholder="Mujeres 25-40" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
            <input type="number" name="empleados_mujeres_mayor_40" value={formData.empleados_mujeres_mayor_40} onChange={handleChange} placeholder="Mujeres > 40" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
            <input type="number" name="empleados_lgtbi" value={formData.empleados_lgtbi} onChange={handleChange} placeholder="LGTBI" className="w-full px-3 py-2 border rounded-md" disabled={readOnly} />
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-700">2. Especificaciones</h3>
        <div>
          <label>Tiempo de Funcionamiento</label>
          <select name="tiempo_funcionamiento" value={formData.tiempo_funcionamiento} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" disabled={readOnly}>
            <option value="">Seleccione...</option>
            <option value="MENOS_1_ANO">Menos de 1 Año</option>
            <option value="ENTRE_1_Y_3">Entre 1 y 3 años</option>
            <option value="ENTRE_3_Y_5">Entre 3 y 5 años</option>
            <option value="MAS_DE_5">Más de 5 años</option>
          </select>
        </div>
        <div>
            <label>Servicios Ofrecidos</label>
            <div className="space-y-2">
                <label className="flex items-center space-x-2">
                    <input type="checkbox" checked={!!(formData.servicios_ofrecidos as Record<string, unknown>)?.ferias} onChange={e => handleJsonChange('servicios_ofrecidos', 'ferias', e.target.checked)} disabled={readOnly} />
                    <span>Organización de Ferias</span>
                </label>
                <label className="flex items-center space-x-2">
                    <input type="checkbox" checked={!!(formData.servicios_ofrecidos as Record<string, unknown>)?.eventos} onChange={e => handleJsonChange('servicios_ofrecidos', 'eventos', e.target.checked)} disabled={readOnly} />
                    <span>Organización de Eventos</span>
                </label>
                <label className="flex items-center space-x-2">
                    <input type="checkbox" checked={!!(formData.servicios_ofrecidos as Record<string, unknown>)?.convenciones} onChange={e => handleJsonChange('servicios_ofrecidos', 'convenciones', e.target.checked)} disabled={readOnly} />
                    <span>Organización de Convenciones</span>
                </label>
                 <label className="flex items-center space-x-2">
                    <input type="checkbox" checked={!!(formData.servicios_ofrecidos as Record<string, unknown>)?.conciertos} onChange={e => handleJsonChange('servicios_ofrecidos', 'conciertos', e.target.checked)} disabled={readOnly} />
                    <span>Organización de Conciertos</span>
                </label>
                <input type="text" value={String((formData.servicios_ofrecidos as Record<string, unknown>)?.otro || '')} onChange={e => handleJsonChange('servicios_ofrecidos', 'otro', e.target.value)} placeholder="Otro, ¿cuál?" className="w-full mt-2 px-3 py-2 border rounded-md" disabled={readOnly} />
            </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-700">4. Necesidades del Operador</h3>
        <textarea name="necesidades_fortalecimiento" value={formData.necesidades_fortalecimiento} onChange={handleChange} placeholder="¿En qué temas les gustaría profundizar?" className="w-full px-3 py-2 border rounded-md" rows={4} disabled={readOnly}></textarea>
      </div>

      <div className="flex justify-end space-x-4 pt-8">
        <button type="button" onClick={onCancel} className="px-6 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400">
          {readOnly ? 'Cerrar' : 'Cancelar'}
        </button>
        {!readOnly && (
            <button type="submit" className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                Guardar Caracterización
            </button>
        )}
      </div>
    </form>
  );
};

export default CaracterizacionEventosForm;