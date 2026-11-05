
import React from 'react';
import { useSettings } from '../context/SettingsContext';
import { LoadingSpinner } from './icons';

const Settings: React.FC = () => {
    const {
        provider,
        setProvider,
        ollamaEndpoint,
        setOllamaEndpoint,
        ollamaConnectionStatus,
        testOllamaConnection
    } = useSettings();

    const renderConnectionStatus = () => {
        switch(ollamaConnectionStatus) {
            case 'testing':
                return <div className="flex items-center text-yellow-400"><LoadingSpinner className="w-4 h-4 mr-2" /> Probando...</div>;
            case 'success':
                return <div className="text-green-400">Conexión exitosa</div>;
            case 'error':
                return <div className="text-red-400">Error en la conexión</div>;
            case 'idle':
            default:
                return <div className="text-muted-foreground">Prueba la conexión para verificar.</div>;
        }
    }

    return (
        <div className="p-8 h-full">
            <h2 className="text-3xl font-bold mb-6 text-foreground">Ajustes del Proveedor de IA</h2>
            <div className="bg-card rounded-lg p-6 max-w-2xl mx-auto shadow-2xl space-y-8 border">
                <div>
                    <h3 className="text-xl font-bold mb-4">Seleccionar Proveedor</h3>
                    <div className="flex space-x-4">
                        <button
                            onClick={() => setProvider('gemini')}
                            className={`flex-1 p-4 rounded-lg text-center transition-all duration-200 ${provider === 'gemini' ? 'bg-primary text-primary-foreground shadow-lg' : 'bg-muted hover:bg-accent'}`}
                        >
                            <span className="block font-bold text-lg">Google Gemini</span>
                            <span className="text-sm text-primary/80">(Nube / Online)</span>
                        </button>
                        <button
                            onClick={() => setProvider('ollama')}
                            className={`flex-1 p-4 rounded-lg text-center transition-all duration-200 ${provider === 'ollama' ? 'bg-purple-600 text-white shadow-lg' : 'bg-muted hover:bg-accent'}`}
                        >
                             <span className="block font-bold text-lg">Ollama</span>
                            <span className="text-sm text-purple-200">(Local / Offline)</span>
                        </button>
                    </div>
                </div>

                {provider === 'ollama' && (
                    <div className="border-t pt-6">
                        <h3 className="text-xl font-bold mb-4">Configuración de Ollama</h3>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="ollama-endpoint" className="block text-sm font-medium text-muted-foreground mb-1">
                                    Endpoint de la API de Ollama
                                </label>
                                <input
                                    id="ollama-endpoint"
                                    type="text"
                                    value={ollamaEndpoint}
                                    onChange={(e) => setOllamaEndpoint(e.target.value)}
                                    className="w-full bg-input border rounded-md p-2 text-foreground placeholder-muted-foreground focus:ring-purple-500 focus:border-purple-500"
                                    placeholder="http://localhost:11434"
                                />
                            </div>
                            <div className="flex items-center space-x-4">
                                <button
                                    onClick={testOllamaConnection}
                                    disabled={ollamaConnectionStatus === 'testing'}
                                    className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:bg-purple-400"
                                >
                                    Probar Conexión
                                </button>
                                {renderConnectionStatus()}
                            </div>
                            <div className="text-sm text-muted-foreground p-3 bg-muted/50 rounded-md">
                                <p>Asegúrate de que Ollama esté instalado y ejecutándose en tu dispositivo. Puedes descargarlo desde <a href="https://ollama.com/" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:underline">ollama.com</a>.</p>
                                <p className="mt-2">Para que funcione offline, necesitas descargar un modelo previamente, por ejemplo: <code className="bg-muted px-1 rounded">ollama run llama3</code></p>
                            </div>
                        </div>
                    </div>
                )}
                 {provider === 'gemini' && (
                    <div className="border-t pt-6">
                         <h3 className="text-xl font-bold mb-4">Configuración de Gemini</h3>
                         <div className="text-sm text-muted-foreground p-3 bg-muted/50 rounded-md">
                            <p>La conexión con Google Gemini utiliza la clave de API configurada en el entorno.</p>
                            <p className="mt-2">Funciones avanzadas como la generación de imágenes (Imagen), video (Veo) y el asistente de voz en tiempo real (Live API) solo están disponibles con este proveedor.</p>
                         </div>
                    </div>
                 )}
            </div>
        </div>
    );
};

export default Settings;
