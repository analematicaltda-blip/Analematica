import React, { createContext, useState, useContext, PropsWithChildren } from 'react';
import type { LLMProvider } from '../types';

interface SettingsContextType {
    provider: LLMProvider;
    setProvider: (provider: LLMProvider) => void;
    ollamaEndpoint: string;
    setOllamaEndpoint: (endpoint: string) => void;
    ollamaConnectionStatus: 'idle' | 'testing' | 'success' | 'error';
    testOllamaConnection: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

// FIX: Changed component signature to use PropsWithChildren to resolve complex type inference issue.
export const SettingsProvider: React.FC<PropsWithChildren<{}>> = ({ children }) => {
    const [provider, setProvider] = useState<LLMProvider>('gemini');
    const [ollamaEndpoint, setOllamaEndpoint] = useState('http://localhost:11434');
    const [ollamaConnectionStatus, setOllamaConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');

    const testOllamaConnection = async () => {
        setOllamaConnectionStatus('testing');
        try {
            // Ollama's root endpoint often just returns "Ollama is running"
            const response = await fetch(ollamaEndpoint, { method: 'GET' });
            if (response.ok) {
                setOllamaConnectionStatus('success');
            } else {
                throw new Error('La respuesta del servidor no fue OK');
            }
        } catch (error) {
            console.error("Error testing Ollama connection:", error);
            setOllamaConnectionStatus('error');
        }
    };
    
    return (
        <SettingsContext.Provider value={{
            provider,
            setProvider,
            ollamaEndpoint,
            setOllamaEndpoint,
            ollamaConnectionStatus,
            testOllamaConnection
        }}>
            {children}
        </SettingsContext.Provider>
    );
};

export const useSettings = () => {
    const context = useContext(SettingsContext);
    if (context === undefined) {
        throw new Error('useSettings must be used within a SettingsProvider');
    }
    return context;
};
