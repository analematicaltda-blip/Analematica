"use client";

"use client";

import React, { useState, useEffect, useCallback } from 'react';
import {
  Formulario,
  getFormularioDetalle,
  getRespuestasPorFormulario,
} from '@/services/formService';
import { FiEye, FiDownload } from 'react-icons/fi';
import Modal from './Modal';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// --- Interfaces ---
interface OpcionPregunta {
    id: number;
    texto_opcion: string;
    valor_interno?: string;
}

interface PreguntaConOpciones {
    id: number;
    texto_pregunta: string;
    tipo_pregunta: string;
    opciones: OpcionPregunta[];
}

interface RespuestaIndividual {
  id: number;
  pregunta: number;
  pregunta_texto: string;
  respuesta: unknown; // Safer than 'any'
  fecha_respuesta: string;
}

interface RespuestaAgrupada {
  usuario_id: number;
  nombre_display: string;
  rol: string;
  fecha_ultima_respuesta: string | null;
  respuestas: RespuestaIndividual[];
}

interface RespuestaDetallada {
  pregunta_texto: string;
  respuesta: unknown; // Safer than 'any'
}

// --- Componente de Gráfico ---
const RespuestaChart = ({ pregunta, respuestas }: { pregunta: PreguntaConOpciones, respuestas: RespuestaAgrupada[] }) => {
  if (!['SELECCION_UNICA', 'SELECCION_MULTIPLE'].includes(pregunta.tipo_pregunta)) {
    return null;
  }

  const responseCounts: { [key: string]: number } = {};

  respuestas.forEach(grupo => {
    const respuestaPregunta = grupo.respuestas.find(r => r.pregunta === pregunta.id);
    if (respuestaPregunta && respuestaPregunta.respuesta) {
      const valorRespuesta = Array.isArray(respuestaPregunta.respuesta)
        ? respuestaPregunta.respuesta
        : [String(respuestaPregunta.respuesta)];

      valorRespuesta.forEach((val: string) => {
        const opcion = pregunta.opciones.find((o) => o.valor_interno === val || o.texto_opcion === val);
        const displayName = opcion ? opcion.texto_opcion : val;
        responseCounts[displayName] = (responseCounts[displayName] || 0) + 1;
      });
    }
  });

  const chartData = Object.entries(responseCounts).map(([name, value]) => ({ name, value }));
  if (chartData.length === 0) return null;

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

  return (
    <div className="my-6 p-4 border rounded-lg shadow-sm bg-white">
      <h4 className="font-semibold text-lg mb-2 text-gray-700">{pregunta.texto_pregunta}</h4>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#8884d8" label>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value} respuesta(s)`}/>
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

// --- Componente Principal ---
const FormularioDetailView: React.FC<{ formId: number }> = ({ formId }) => {
  const [formulario, setFormulario] = useState<Formulario | null>(null);
  const [respuestasAgrupadas, setRespuestasAgrupadas] = useState<RespuestaAgrupada[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRespuestas, setSelectedRespuestas] = useState<RespuestaDetallada[] | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [formData, respuestasData] = await Promise.all([
        getFormularioDetalle(formId),
        getRespuestasPorFormulario(formId),
      ]);
      setFormulario(formData);
      setRespuestasAgrupadas(respuestasData);
    } catch {
      setError('No se pudieron cargar los detalles del formulario.');
    } finally {
      setIsLoading(false);
    }
  }, [formId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const viewRespuestas = (respuestaAgrupada: RespuestaAgrupada) => {
    if (respuestaAgrupada && formulario) {
      const detalles: RespuestaDetallada[] = formulario.preguntas!.map(pregunta => {
        const respuestaEncontrada = respuestaAgrupada.respuestas.find(r => r.pregunta === pregunta.id);
        return {
          pregunta_texto: pregunta.texto_pregunta,
          respuesta: respuestaEncontrada ? respuestaEncontrada.respuesta : 'Sin respuesta',
        };
      });
      setSelectedRespuestas(detalles);
      setIsModalOpen(true);
    }
  };

  const exportToCSV = () => {
    if (!formulario || respuestasAgrupadas.length === 0) return;

    const headers = ["Usuario ID", "Nombre", "Rol", ...formulario.preguntas.map(p => `"${p.texto_pregunta.replace(/"/g, '""')}"`)];
    let csvContent = headers.join(",") + "\r\n";

    respuestasAgrupadas.forEach(grupo => {
      const row = [String(grupo.usuario_id), `"${grupo.nombre_display}"`, `"${grupo.rol}"`];
      formulario.preguntas.forEach(pregunta => {
        const respuesta = grupo.respuestas.find(r => r.pregunta === pregunta.id);
        let valor = 'Sin respuesta';
        if (respuesta && respuesta.respuesta !== null) {
            if(Array.isArray(respuesta.respuesta)) {
                valor = respuesta.respuesta.join('; ');
            } else if (typeof respuesta.respuesta === 'object') {
                valor = JSON.stringify(respuesta.respuesta);
            } else {
                valor = String(respuesta.respuesta);
            }
        }
        row.push(`"${valor.replace(/"/g, '""')}"`);
      });
      csvContent += row.join(",") + "\r\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `${formulario.titulo.replace(/\s/g, '_')}_respuestas.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) return <p className="p-8">Cargando datos del formulario...</p>;
  if (error) return <p className="p-8 text-red-500">{error}</p>;
  if (!formulario) return <p className="p-8">Formulario no encontrado.</p>;

  return (
    <div className="bg-gray-50 p-8 rounded-lg">
      <div className="flex justify-between items-start mb-8">
        <div>
            <h2 className="text-3xl font-bold text-gray-800">{formulario.titulo}</h2>
            <p className="mt-2 text-gray-600">{formulario.descripcion}</p>
        </div>
        <button
            onClick={exportToCSV}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={respuestasAgrupadas.length === 0}
        >
            <FiDownload className="mr-2"/>
            Exportar a CSV
        </button>
      </div>

      {/* --- Sección de Análisis Visual --- */}
      {respuestasAgrupadas.length > 0 && (
        <div className="mb-8">
          <h3 className="text-2xl font-semibold mb-4 pb-2 border-b">Resultados Consolidados</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {formulario.preguntas
                  .filter(p => ['SELECCION_UNICA', 'SELECCION_MULTIPLE'].includes(p.tipo_pregunta))
                  .map(pregunta => (
                      <RespuestaChart key={pregunta.id} pregunta={pregunta as PreguntaConOpciones} respuestas={respuestasAgrupadas} />
              ))}
          </div>
        </div>
      )}

      {/* --- Sección de Respuestas Individuales --- */}
      <div className="overflow-x-auto">
        <h3 className="text-2xl font-semibold mb-4">Respuestas Individuales</h3>
        {respuestasAgrupadas.length > 0 ? (
          <div className="bg-white rounded-lg shadow">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {respuestasAgrupadas.map(respuesta => (
                  <tr key={respuesta.usuario_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{respuesta.nombre_display}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{respuesta.rol}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {respuesta.fecha_ultima_respuesta ? new Date(respuesta.fecha_ultima_respuesta).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button onClick={() => viewRespuestas(respuesta)} className="text-indigo-600 hover:text-indigo-900 flex items-center">
                        <FiEye className="mr-1" /> Ver
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 px-4 bg-white rounded-lg shadow">
            <p className="text-gray-500">Aún no se han recibido respuestas para este formulario.</p>
          </div>
        )}
      </div>

      {isModalOpen && selectedRespuestas && (
        <Modal title="Detalle de Respuestas" onClose={() => setIsModalOpen(false)}>
          <div className="space-y-4">
            {selectedRespuestas.map((item, index) => (
              <div key={index}>
                <h4 className="font-semibold text-gray-800">{item.pregunta_texto}</h4>
                <div className="text-gray-600 pl-4 mt-1 border-l-2 border-gray-200">
                  {item.respuesta === 'Sin respuesta' ? (
                     <span className="text-gray-400 italic">Sin respuesta</span>
                  ) : typeof item.respuesta === 'object' && item.respuesta !== null ? (
                    <pre className="bg-gray-100 p-2 rounded text-sm whitespace-pre-wrap">{JSON.stringify(item.respuesta, null, 2)}</pre>
                  ) : (
                    String(item.respuesta)
                  )}
                </div>
              </div>
            ))}
          </div>
        </Modal>
      )}
    </div>
  );
};

export default FormularioDetailView;