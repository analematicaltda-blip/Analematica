 'use client';

import React, { createContext, useState, useContext, ReactNode, useRef, useEffect } from 'react';
import axios from 'axios';

// --- Type Definitions ---
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
}

interface AgentContextType {
  isChatOpen: boolean;
  toggleChat: () => void;
  conversation: Message[];
  sendCommand: (command: string) => Promise<void>;
  isLoading: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// --- Context Creation ---
const AgentContext = createContext<AgentContextType | undefined>(undefined);

// --- Provider Component ---
interface AgentProviderProps {
  children: ReactNode;
}

export function AgentProvider({ children }: AgentProviderProps) {
  // Aquí usamos tu token directamente
  const token = 'ae7df2947b52128f13d81c8716bc9bc0a073151b';

  const [isChatOpen, setIsChatOpen] = useState(false);
  const [conversation, setConversation] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const toggleChat = () => {
    setIsChatOpen(prev => !prev);
  };

  const addMessage = (text: string, sender: 'user' | 'agent') => {
    const newMessage: Message = { id: Date.now().toString() + text, text, sender };
    setConversation(prev => [...prev, newMessage]);
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  const pollTaskStatus = (taskId: string) => {
    stopPolling();

    pollingIntervalRef.current = setInterval(async () => {
      try {
        const headers = { Authorization: `Token ${token}` };
        const response = await axios.get(`${API_BASE_URL}/agent/tasks/${taskId}/`, {
          headers,
        });

        const { status, report } = response.data;

        if (status === 'COMPLETED' || status === 'FAILED') {
          stopPolling();
          addMessage(report || 'La tarea ha finalizado sin un informe detallado.', 'agent');
          setIsLoading(false);
        }
      } catch (error) {
        stopPolling();
        addMessage('Hubo un error al verificar el estado de la tarea. Por favor, inténtalo de nuevo.', 'agent');
        setIsLoading(false);
      }
    }, 3000);
  };

  const sendCommand = async (command: string) => {
    if (!command.trim()) {
      return;
    }

    addMessage(command, 'user');
    setIsLoading(true);

    try {
      const headers = { Authorization: `Token ${token}` };

      const response = await axios.post(
        `${API_BASE_URL}/agent/tasks/`,
        { orden: command },
        { headers }
      );

      const { task_id } = response.data;
      if (task_id) {
        addMessage('Comando recibido. El agente está procesando tu solicitud...', 'agent');
        pollTaskStatus(task_id);
      } else {
        throw new Error('No se recibió un ID de tarea del servidor.');
      }

    } catch (error) {
      addMessage("Lo siento, no pude enviar tu comando al centro de mando en este momento.", 'agent');
      setIsLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, []);

  const value = {
    isChatOpen,
    toggleChat,
    conversation,
    sendCommand,
    isLoading,
  };

  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
}

// --- Custom Hook ---
export function useAgent() {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgent debe ser usado dentro de un AgentProvider');
  }
  return context;
}