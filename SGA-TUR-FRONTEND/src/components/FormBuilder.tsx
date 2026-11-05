import React, { useState, useEffect } from 'react';
import { getFormularios, createFormulario, Formulario } from '@/services/formService';

// Sub-componente para el formulario de creación
const NewFormCreator = ({ onSave, onCancel }: { onSave: (data: Formulario) => Promise<void>, onCancel: () => void }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) {
      alert('El título es obligatorio.');
      return;
    }
    setIsSaving(true);
    await onSave({
      titulo: title,
      descripcion: description,
      es_publico: isPublic,
    });
    setIsSaving(false);
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Crear Nuevo Formulario</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="form-title" className="block text-sm font-medium text-gray-700">Título del Formulario</label>
          <input type="text" id="form-title" value={title} onChange={(e) => setTitle(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" required />
        </div>
        <div>
          <label htmlFor="form-description" className="block text-sm font-medium text-gray-700">Descripción</label>
          <textarea id="form-description" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
        </div>
        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input id="form-public" type="checkbox" checked={isPublic} onChange={(e) => setIsPublic(e.target.checked)} className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded" />
          </div>
          <div className="ml-3 text-sm">
            <label htmlFor="form-public" className="font-medium text-gray-700">Hacer Público</label>
            <p className="text-gray-500">Permitir que los prestadores vean y llenen este formulario.</p>
          </div>
        </div>
        <div className="flex justify-end space-x-3">
          <button type="button" onClick={onCancel} className="bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300">Cancelar</button>
          <button type="submit" disabled={isSaving} className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300">{isSaving ? 'Guardando...' : 'Guardar'}</button>
        </div>
      </form>
    </div>
  );
};

import { getFormularioDetalle, Pregunta } from '@/services/formService';

// Sub-componente para gestionar las preguntas de un formulario
const QuestionManager = ({ form }: { form: Formulario }) => {
  const [questions, setQuestions] = useState<Pregunta[]>(form.preguntas || []);

  useEffect(() => {
    setQuestions(form.preguntas || []);
  }, [form]);

  return (
    <div>
      <div className="border-b pb-4 mb-4">
        <h3 className="text-2xl font-bold">{form.titulo}</h3>
        <p className="text-gray-600">{form.descripcion}</p>
      </div>
      <h3 className="text-xl font-semibold mb-3">Preguntas del Formulario</h3>
      {questions.length > 0 ? (
        <ul className="space-y-3">
          {questions.map(q => (
            <li key={q.id} className="p-3 bg-gray-50 rounded-md border flex justify-between items-center">
              <div>
                <p className="font-semibold">{q.orden}. {q.texto_pregunta}</p>
                <p className="text-sm text-gray-500">
                  Tipo: {q.tipo_pregunta} {q.es_obligatoria ? <span className="font-bold text-red-500">(Obligatoria)</span> : ''}
                </p>
              </div>
              <div>
                {/* Botones de acción irán aquí */}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-center py-4 text-gray-500">Este formulario aún no tiene preguntas.</p>
      )}
      <button className="mt-6 bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600">
        + Añadir Pregunta
      </button>
    </div>
  )
}

const FormBuilder = () => {
  const [forms, setForms] = useState<Formulario[]>([]);
  const [selectedForm, setSelectedForm] = useState<Formulario | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchForms = async () => {
    try {
      setIsLoading(true);
      const data = await getFormularios();
      setForms(data);
      setError(null);
    } catch (err) {
      setError('No se pudieron cargar los formularios.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchForms();
  }, []);

  const handleSelectForm = async (form: Formulario) => {
    if (!form.id) return;
    setIsCreating(false);
    setIsDetailLoading(true);
    setError(null);
    try {
      const detailedForm = await getFormularioDetalle(form.id);
      setSelectedForm(detailedForm);
    } catch (err) {
      setError('No se pudo cargar el detalle del formulario.');
      setSelectedForm(null);
    } finally {
      setIsDetailLoading(false);
    }
  };

  const handleCreateNew = () => {
    setSelectedForm(null);
    setIsCreating(true);
  };

  const handleCancelCreate = () => {
    setIsCreating(false);
  };

  const handleSaveNewForm = async (formData: Formulario) => {
    try {
      const newForm = await createFormulario(formData);
      setForms([...forms, newForm]);
      setIsCreating(false);
      setSelectedForm(newForm);
    } catch (err) {
      alert('Error al guardar el formulario.');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Gestor de Formularios de Caracterización</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-1 bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-3">Formularios Existentes</h2>
          <button onClick={handleCreateNew} className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 mb-4">
            + Crear Nuevo Formulario
          </button>
          {isLoading ? (
            <p>Cargando...</p>
          ) : error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <ul>
              {forms.map((form) => (
                <li key={form.id} className={`p-2 rounded-md cursor-pointer ${selectedForm?.id === form.id ? 'bg-blue-100' : 'hover:bg-gray-100'}`} onClick={() => handleSelectForm(form)}>
                  {form.title}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="col-span-2 bg-white p-4 rounded-lg shadow">
          {isCreating && <NewFormCreator onSave={handleSaveNewForm} onCancel={handleCancelCreate} />}
          {selectedForm && (
            <div>
              <h2 className="text-xl font-semibold">Editando: {selectedForm.title}</h2>
              {/* Form editing fields and question builder will go here */}
            </div>
          )}
          {!isCreating && !selectedForm && (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">Seleccione un formulario para editar o cree uno nuevo.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FormBuilder;