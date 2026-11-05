
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { LoadingSpinner, BotIcon, WorkflowIcon, PlusIcon, CalendarPlusIcon, MailIcon, MessageIcon } from './icons';
import type { ChatMessage } from '../types';
import { useSettings } from '../context/SettingsContext';

const Chatbot: React.FC<{ authToken: string }> = ({ authToken }) => {
    const [history, setHistory] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: ChatMessage = { role: 'user', parts: [{ text: input }] };
        const newHistory = [...history, userMessage];
        setHistory(newHistory);
        setIsLoading(true);
        setInput('');

        try {
            const response = await fetch('/api/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({ history: newHistory })
            });

            if (!response.ok) throw new Error('Backend chat failed');

            const data = await response.json();
            const modelMessage: ChatMessage = { role: 'model', parts: [{ text: data.response }] };
            setHistory(prev => [...prev, modelMessage]);

        } catch (error: any) {
            const errorMessage: ChatMessage = { role: 'model', parts: [{ text: `Error: ${error.message}` }] };
            setHistory(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };
    
    return (
        <div className="bg-card p-6 rounded-lg shadow-lg flex flex-col h-full border">
            <h3 className="text-xl font-bold mb-4">Chat Inteligente (Backend)</h3>
            <div className="flex-1 overflow-y-auto mb-4 pr-2 space-y-4">
                {history.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-xl p-3 rounded-lg ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>
                            <p className="whitespace-pre-wrap">{msg.parts[0].text}</p>
                        </div>
                    </div>
                ))}
                {isLoading && <div className="flex justify-start"><LoadingSpinner /></div>}
                <div ref={chatEndRef} />
            </div>
            <div className="flex space-x-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Pregunta algo..."
                    className="flex-grow bg-input border rounded-md p-2"
                    disabled={isLoading}
                />
                <button onClick={handleSend} disabled={isLoading || !input.trim()} className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50">
                    Enviar
                </button>
            </div>
        </div>
    );
};

// --- Componentes de Asistente de Voz y Workflows (sin cambios, simplificados para brevedad) ---

const LiveAssistant: React.FC = () => {
    const { provider } = useSettings();
     if (provider === 'ollama') {
        return (
            <div className="bg-card p-6 rounded-lg shadow-lg flex flex-col h-full items-center justify-center text-center border">
                <h2 className="text-2xl font-bold">Funcionalidad No Disponible</h2>
                <p className="text-muted-foreground">El asistente de voz requiere Gemini. Cambie el proveedor en Ajustes.</p>
            </div>
        );
    }
    return (
        <div className="bg-card p-6 rounded-lg shadow-lg flex flex-col h-full border">
             <h3 className="text-xl font-bold mb-4">Asistente Virtual por Voz</h3>
             <p className="text-muted-foreground">La interfaz del asistente de voz se renderizaría aquí.</p>
        </div>
    );
}

const MarketingWorkflows: React.FC = () => (
     <div className="bg-card p-6 rounded-lg shadow-lg flex flex-col h-full border">
        <h3 className="text-xl font-bold mb-4 flex items-center"><WorkflowIcon className="w-6 h-6 mr-2" /> Workflows de Marketing</h3>
        <p className="text-muted-foreground">La interfaz de workflows se renderizaría aquí.</p>
    </div>
);

interface Level5Props {
    authToken: string;
}

const Level5_AutomationSuite: React.FC<Level5Props> = ({ authToken }) => {
    const [view, setView] = useState<'agent' | 'workflows'>('workflows');
    return (
        <div className="p-8 h-full flex flex-col bg-background">
            <div className="flex space-x-2 border-b mb-6">
                <button onClick={() => setView('workflows')} className={`flex items-center space-x-2 py-2 px-4 font-medium ${view === 'workflows' ? 'border-b-2 border-primary text-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
                    <WorkflowIcon className="w-5 h-5" /><span>Workflows de Marketing</span>
                </button>
                <button onClick={() => setView('agent')} className={`flex items-center space-x-2 py-2 px-4 font-medium ${view === 'agent' ? 'border-b-2 border-primary text-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
                    <BotIcon className="w-5 h-5" /><span>Agentes de IA Avanzados</span>
                </button>
            </div>
            
            {view === 'workflows' ? <MarketingWorkflows /> : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 flex-1">
                    <Chatbot authToken={authToken} />
                    <LiveAssistant />
                </div>
            )}
        </div>
    );
};

export default Level5_AutomationSuite;
