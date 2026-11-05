"use client";

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import CaracterizacionEventosForm from './CaracterizacionEventosForm';
import CaracterizacionAgroturismoForm from './CaracterizacionAgroturismoForm';
import CaracterizacionGuiaTuristicoForm from './CaracterizacionGuiaTuristicoForm';
import {
    getCaracterizacionByPrestadorId, createCaracterizacion, updateCaracterizacion, CaracterizacionEmpresaEventos,
    getAgroturismoCaracterizacionByPrestadorId, createAgroturismoCaracterizacion, updateAgroturismoCaracterizacion, CaracterizacionAgroturismo,
    getGuiaCaracterizacionByPrestadorId, createGuiaCaracterizacion, updateGuiaCaracterizacion, CaracterizacionGuiaTuristico
} from '@/services/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface AdminPrestador {
  id: number;
  nombre_negocio: string;
  aprobado: boolean;
  fecha_creacion: string;
  categoria_nombre: string;
  usuario_email: string;
}

export default function PrestadorManager() {
  const { user, token } = useAuth();
  const [prestadores, setPrestadores] = useState<AdminPrestador[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'approved' | 'pending'>('pending');

  const [isEventosModalOpen, setIsEventosModalOpen] = useState(false);
  const [eventosCaracterizacionData, setEventosCaracterizacionData] = useState<CaracterizacionEmpresaEventos | null>(null);

  const [isAgroModalOpen, setIsAgroModalOpen] = useState(false);
  const [agroCaracterizacionData, setAgroCaracterizacionData] = useState<CaracterizacionAgroturismo | null>(null);

  const [isGuiaModalOpen, setIsGuiaModalOpen] = useState(false);
  const [guiaCaracterizacionData, setGuiaCaracterizacionData] = useState<CaracterizacionGuiaTuristico | null>(null);

  const [selectedPrestador, setSelectedPrestador] = useState<AdminPrestador | null>(null);
  const [isReadOnly, setIsReadOnly] = useState(false);

  const fetchPrestadores = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);

    let url = `${API_BASE_URL}/admin/prestadores/`;
    if (filter !== 'all') {
      url += `?aprobado=${filter === 'approved'}`;
    }

    try {
      const response = await axios.get(url, {
        headers: { Authorization: `Token ${token}` },
      });
      setPrestadores(response.data.results);
    } catch (err) {
      setError('No se pudo cargar la lista de prestadores.');
    } finally {
      setIsLoading(false);
    }
  }, [token, filter]);

  useEffect(() => {
    fetchPrestadores();
  }, [fetchPrestadores]);

  const handleApprove = async (id: number) => {
    if (!window.confirm('¿Está seguro de que desea aprobar a este prestador?')) return;

    try {
      await axios.patch(`${API_BASE_URL}/admin/prestadores/${id}/approve/`, {}, {
        headers: { Authorization: `Token ${token}` },
      });
      fetchPrestadores();
    } catch (err) {
      alert('Error al aprobar el prestador.');
    }
  };

  const handleOpenModal = async (prestador: AdminPrestador, type: 'eventos' | 'agroturismo' | 'guias') => {
    setSelectedPrestador(prestador);
    const readOnly = user?.role === 'FUNCIONARIO_DIRECTIVO' || user?.role === 'FUNCIONARIO_PROFESIONAL';
    setIsReadOnly(readOnly);

    if (type === 'eventos') {
      const data = await getCaracterizacionByPrestadorId(prestador.id);
      setEventosCaracterizacionData(data);
      setIsEventosModalOpen(true);
    } else if (type === 'agroturismo') {
      const data = await getAgroturismoCaracterizacionByPrestadorId(prestador.id);
      setAgroCaracterizacionData(data);
      setIsAgroModalOpen(true);
    } else if (type === 'guias') {
        const data = await getGuiaCaracterizacionByPrestadorId(prestador.id);
        setGuiaCaracterizacionData(data);
        setIsGuiaModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setIsEventosModalOpen(false);
    setIsAgroModalOpen(false);
    setIsGuiaModalOpen(false);
    setSelectedPrestador(null);
    setEventosCaracterizacionData(null);
    setAgroCaracterizacionData(null);
    setGuiaCaracterizacionData(null);
    setIsReadOnly(false);
  };

  const handleEventosFormSubmit = async (formData: FormData) => {
    if (!selectedPrestador || isReadOnly) return;
    try {
      if (eventosCaracterizacionData) {
        await updateCaracterizacion(eventosCaracterizacionData.id, formData);
      } else {
        formData.append('prestador', String(selectedPrestador.id));
        await createCaracterizacion(formData);
      }
      alert('Caracterización de Eventos guardada con éxito.');
      handleCloseModal();
    } catch (error) {
      alert('Error al guardar la caracterización de eventos.');
    }
  };

  const handleAgroFormSubmit = async (formData: Partial<CaracterizacionAgroturismo>) => {
    if (!selectedPrestador || isReadOnly) return;
    try {
      const dataToSubmit = { ...formData, prestador: selectedPrestador.id };
      if (agroCaracterizacionData) {
        await updateAgroturismoCaracterizacion(agroCaracterizacionData.id, dataToSubmit);
      } else {
        await createAgroturismoCaracterizacion(dataToSubmit);
      }
      alert('Caracterización de Agroturismo guardada con éxito.');
      handleCloseModal();
    } catch (error) {
      alert('Error al guardar la caracterización de agroturismo.');
    }
  };

  const handleGuiaFormSubmit = async (formData: FormData) => {
    if (!selectedPrestador || isReadOnly) return;
    try {
        if (guiaCaracterizacionData) {
            await updateGuiaCaracterizacion(guiaCaracterizacionData.id, formData);
        } else {
            formData.append('prestador', String(selectedPrestador.id));
            await createGuiaCaracterizacion(formData);
        }
        alert('Caracterización de Guía guardada con éxito.');
        handleCloseModal();
    } catch (error) {
        alert('Error al guardar la caracterización de guía.');
    }
  };

  const isFuncionario = user?.role === 'FUNCIONARIO_DIRECTIVO' || user?.role === 'FUNCIONARIO_PROFESIONAL';

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Gestión de Prestadores de Servicios</h2>

      {isEventosModalOpen && selectedPrestador && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
            <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <CaracterizacionEventosForm
                    initialData={eventosCaracterizacionData}
                    onSubmit={handleEventosFormSubmit}
                    onCancel={handleCloseModal}
                    prestadorId={selectedPrestador.id}
                    readOnly={isReadOnly}
                />
            </div>
        </div>
      )}

      {isAgroModalOpen && selectedPrestador && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
            <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <CaracterizacionAgroturismoForm
                    initialData={agroCaracterizacionData}
                    onSubmit={handleAgroFormSubmit}
                    onCancel={handleCloseModal}
                    prestadorId={selectedPrestador.id}
                    readOnly={isReadOnly}
                />
            </div>
        </div>
      )}

      {isGuiaModalOpen && selectedPrestador && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
            <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <CaracterizacionGuiaTuristicoForm
                    initialData={guiaCaracterizacionData}
                    onSubmit={handleGuiaFormSubmit}
                    onCancel={handleCloseModal}
                    prestadorId={selectedPrestador.id}
                    readOnly={isReadOnly}
                />
            </div>
        </div>
      )}

      <div className="flex justify-end mb-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value as 'all' | 'approved' | 'pending')}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white"
        >
          <option value="pending">Pendientes</option>
          <option value="approved">Aprobados</option>
          <option value="all">Todos</option>
        </select>
      </div>
      {isLoading ? (
        <p>Cargando prestadores...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-2 px-4 text-left">Negocio</th>
                <th className="py-2 px-4 text-left">Email Contacto</th>
                <th className="py-2 px-4 text-left">Categoría</th>
                <th className="py-2 px-4 text-left">Fecha Registro</th>
                <th className="py-2 px-4 text-left">Estado</th>
                <th className="py-2 px-4 text-left">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {prestadores.map((p) => (
                <tr key={p.id} className="border-b">
                  <td className="py-2 px-4">{p.nombre_negocio}</td>
                  <td className="py-2 px-4">{p.usuario_email}</td>
                  <td className="py-2 px-4">{p.categoria_nombre}</td>
                  <td className="py-2 px-4">{new Date(p.fecha_creacion).toLocaleDateString()}</td>
                  <td className="py-2 px-4">
                    {p.aprobado ? (
                      <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-200 rounded-full">Aprobado</span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-semibold text-yellow-800 bg-yellow-200 rounded-full">Pendiente</span>
                    )}
                  </td>
                  <td className="py-2 px-4 space-x-2">
                    {!p.aprobado && (
                      <button
                        onClick={() => handleApprove(p.id)}
                        className="px-3 py-1 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
                      >
                        Aprobar
                      </button>
                    )}
                    {p.categoria_nombre === 'Agencias de Eventos' && (
                         <button
                            onClick={() => handleOpenModal(p, 'eventos')}
                            className="px-3 py-1 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                        >
                            {isFuncionario ? 'Ver Eventos' : 'Editar Eventos'}
                        </button>
                    )}
                    {p.categoria_nombre === 'Agroturismo' && (
                         <button
                            onClick={() => handleOpenModal(p, 'agroturismo')}
                            className="px-3 py-1 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700"
                        >
                            {isFuncionario ? 'Ver Agroturismo' : 'Editar Agroturismo'}
                        </button>
                    )}
                    {p.categoria_nombre === 'Guia Turistico' && (
                        <button
                            onClick={() => handleOpenModal(p, 'guias')}
                            className="px-3 py-1 text-sm font-medium text-white bg-teal-600 rounded-md hover:bg-teal-700"
                        >
                            {isFuncionario ? 'Ver Guía' : 'Editar Guía'}
                        </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {prestadores.length === 0 && <p className="text-center py-4">No hay prestadores en esta categoría.</p>}
        </div>
      )}
    </div>
  );
}