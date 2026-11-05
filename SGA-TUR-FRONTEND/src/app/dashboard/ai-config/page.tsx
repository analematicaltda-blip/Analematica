import LLMConfigForm from '@/components/ai/LLMConfigForm';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Configuración de IA | Puerto Gaitán',
  description: 'Gestiona tu proveedor de lenguaje y tus claves de API personales para personalizar tu asistente de inteligencia artificial.',
};

const AIConfigPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">
        Configuración de Inteligencia Artificial
      </h1>
      <p className="text-gray-600 dark:text-gray-300 mb-8">
        Personaliza tu experiencia con el asistente de IA. Aquí puedes seleccionar tu proveedor de modelo de lenguaje preferido y gestionar tus claves de API.
      </p>

      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <LLMConfigForm />
      </div>
    </div>
  );
};

export default AIConfigPage;