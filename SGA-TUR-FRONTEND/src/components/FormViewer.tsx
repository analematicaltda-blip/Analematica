import React from 'react';

// Mock data representing a form and its submitted answers
const mockFilledForm = {
  formInfo: {
    id: 1,
    title: 'Caracterización de Alojamiento',
    description: 'Revisión de la información del establecimiento.',
  },
  providerInfo: {
    name: 'Hotel Lazo Real',
    id: 101,
  },
  answers: [
    { questionId: 1, questionText: 'Nombre del Establecimiento', answer: 'Hotel Lazo Real' },
    { questionId: 2, questionText: 'Descripción del Establecimiento', answer: 'Un hotel de lujo en el corazón de la ciudad, con vistas espectaculares.' },
    { questionId: 3, questionText: 'Número de Habitaciones', answer: '50' },
    { questionId: 4, questionText: '¿Cuenta con piscina?', answer: 'Sí' },
    { questionId: 5, questionText: 'Servicios Ofrecidos', answer: ['Wifi', 'Parqueadero', 'Restaurante'] },
    { questionId: 6, questionText: 'Fecha de Apertura', answer: '2018-05-20' },
  ],
};

const FormViewer = ({ filledForm = mockFilledForm }) => {
  const renderAnswer = (answer) => {
    if (Array.isArray(answer.answer)) {
      return (
        <ul className="list-disc list-inside">
          {answer.answer.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      );
    }
    return <p className="text-gray-800">{answer.answer || 'No respondido'}</p>;
  };

  return (
    <div className="bg-white p-8 rounded-2xl shadow-lg">
      <div className="border-b pb-4 mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{filledForm.formInfo.title}</h1>
        <p className="mt-1 text-lg text-gray-600">
          Respuestas de: <span className="font-semibold">{filledForm.providerInfo.name}</span>
        </p>
      </div>

      <div className="space-y-6">
        {filledForm.answers.map((answer) => (
          <div key={answer.questionId} className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-600">{answer.questionText}</h3>
            <div className="mt-2 text-base">
              {renderAnswer(answer)}
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-end mt-8">
        <button
          type="button"
          className="bg-gray-600 text-white py-2 px-6 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        >
          Cerrar Vista
        </button>
      </div>
    </div>
  );
};

export default FormViewer;