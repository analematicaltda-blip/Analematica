import React, { useState } from 'react';
import { Formulario, Pregunta, submitRespuestas, Respuesta } from '@/services/formService';

interface FormFillerProps {
  form: Formulario;
  onBack: () => void;
}

const FormFiller = ({ form, onBack }: FormFillerProps) => {
  const [answers, setAnswers] = useState<Respuesta>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (
    questionId: number,
    value: string,
    type: Pregunta['tipo_pregunta']
  ) => {
    setAnswers((prev) => {
      const newAnswers = { ...prev };
      if (type === 'SELECCION_MULTIPLE') {
        const currentSelection = (newAnswers[questionId] as string[] | undefined) || [];
        const newSelection = currentSelection.includes(value)
          ? currentSelection.filter((item) => item !== value)
          : [...currentSelection, value];
        newAnswers[questionId] = newSelection;
      } else {
        newAnswers[questionId] = value;
      }
      return newAnswers;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    for (const q of form.preguntas || []) {
      if (q.es_obligatoria && !answers[q.id!]) {
        alert(`La pregunta "${q.texto_pregunta}" es obligatoria.`);
        setIsSubmitting(false);
        return;
      }
    }

    try {
      if (form.id) {
        await submitRespuestas(form.id, answers);
        alert('Formulario enviado con éxito!');
        onBack();
      }
    } catch (err) {
      setError('Hubo un error al enviar el formulario. Por favor, inténtelo de nuevo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderQuestion = (question: Pregunta) => {
    const commonClasses = "mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm";
    const questionId = question.id!;
    const answerValue = answers[questionId];

    switch (question.tipo_pregunta) {
      case 'TEXTO_CORTO':
        return <input type="text" value={answerValue as string || ''} onChange={(e) => handleInputChange(questionId, e.target.value, question.tipo_pregunta)} className={commonClasses} />;
      case 'TEXTO_LARGO':
        return <textarea rows={4} value={answerValue as string || ''} onChange={(e) => handleInputChange(questionId, e.target.value, question.tipo_pregunta)} className={commonClasses}></textarea>;
      case 'NUMERO':
        return <input type="number" value={answerValue as number | ''} onChange={(e) => handleInputChange(questionId, e.target.value, question.tipo_pregunta)} className={commonClasses} />;
      case 'FECHA':
        return <input type="date" value={answerValue as string || ''} onChange={(e) => handleInputChange(questionId, e.target.value, question.tipo_pregunta)} className={commonClasses} />;
      case 'SELECCION_UNICA':
        return (
          <div className="mt-2 space-y-2">
            {question.opciones?.map((option) => (
              <label key={option.id} className="flex items-center">
                <input type="radio" name={`question-${questionId}`} value={option.texto_opcion} checked={answerValue === option.texto_opcion} onChange={(e) => handleInputChange(questionId, e.target.value, question.tipo_pregunta)} className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300" />
                <span className="ml-3 text-sm text-gray-700">{option.texto_opcion}</span>
              </label>
            ))}
          </div>
        );
      case 'SELECCION_MULTIPLE':
        return (
          <div className="mt-2 space-y-2">
            {question.opciones?.map((option) => (
              <label key={option.id} className="flex items-center">
                <input type="checkbox" value={option.texto_opcion} checked={(answerValue as string[] || []).includes(option.texto_opcion)} onChange={(e) => handleInputChange(questionId, e.target.value, question.tipo_pregunta)} className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded" />
                <span className="ml-3 text-sm text-gray-700">{option.texto_opcion}</span>
              </label>
            ))}
          </div>
        );
      default:
        return <p className="text-red-500">Tipo de pregunta no soportado.</p>;
    }
  };

  return (
    <div className="bg-white p-8 rounded-2xl shadow-lg">
      <div className="flex justify-between items-start mb-8">
        <div>
            <h1 className="text-3xl font-bold text-gray-900">{form.titulo}</h1>
            <p className="mt-2 text-lg text-gray-600">{form.descripcion}</p>
        </div>
        <button onClick={onBack} className="bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300">
            &larr; Volver a la lista
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {(form.preguntas || []).map((q) => (
          <div key={q.id}>
            <label className="block text-sm font-medium text-gray-700">
              {q.texto_pregunta}
              {q.es_obligatoria && <span className="text-red-500 ml-1">*</span>}
            </label>
            {renderQuestion(q)}
          </div>
        ))}
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-indigo-600 text-white py-2 px-6 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400"
          >
            {isSubmitting ? 'Enviando...' : 'Guardar Respuestas'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormFiller;