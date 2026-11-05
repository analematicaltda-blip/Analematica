'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAgent } from '@/contexts/AgentContext';
import { FiX, FiSend, FiMic, FiLoader } from 'react-icons/fi';

// --- Helper Components ---
const TypingIndicator = () => (
    <div className="flex items-center space-x-2">
        <span className="text-gray-500">El agente está pensando</span>
        <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
        </div>
    </div>
);

// --- Main Component ---
interface AgentInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AgentInterface({ isOpen, onClose }: AgentInterfaceProps) {
  const { conversation, sendCommand, isLoading } = useAgent();
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null); // Using 'any' for SpeechRecognition to avoid browser-specific type issues

  // --- Speech Recognition Logic ---
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'es-ES';

        recognition.onresult = (event) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            setInput(prevInput => prevInput + finalTranscript);
          }
        };

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);
        recognition.onerror = (event) => {
            setIsListening(false);
        };

        recognitionRef.current = recognition;
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleMicClick = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  };

  // --- Component Logic ---
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      sendCommand(input);
      setInput('');
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed bottom-28 right-8 z-50 w-full max-w-md h-auto bg-white rounded-2xl shadow-2xl flex flex-col border-2 font-sans animate-glowing-border">
      {/* Header */}
      <header className="flex items-center justify-between p-4 border-b-2 border-teal-200 bg-teal-50 rounded-t-xl">
        <h2 className="text-lg font-bold text-teal-800">Asistente Turístico</h2>
        <button onClick={onClose} className="p-2 text-gray-500 rounded-full hover:bg-gray-200 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-400" aria-label="Cerrar asistente">
          <FiX className="h-6 w-6" />
        </button>
      </header>

      {/* Mode Selection */}
      <div className="flex justify-center p-2 border-b border-gray-200 bg-white">
        <div className="inline-flex rounded-md shadow-sm" role="group">
          <button
            type="button"
            onClick={handleMicClick}
            className={`px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-l-lg hover:bg-gray-100 focus:z-10 focus:ring-2 focus:ring-blue-500 ${isListening ? 'bg-red-100 text-red-700' : ''}`}
          >
            Modo Conversacional
          </button>
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-gray-900 bg-white border-t border-b border-r border-gray-200 rounded-r-md hover:bg-gray-100 focus:z-10 focus:ring-2 focus:ring-blue-500"
            onClick={() => document.getElementById('chat-input')?.focus()}
          >
            Modo Escrito
          </button>
        </div>
      </div>

      {/* Message Display Area */}
      <div className="flex-1 p-6 overflow-y-auto h-96 space-y-4">
        {conversation.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}`}>
              <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
            <div className="flex justify-start">
                <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-2xl bg-gray-200 text-gray-800">
                    <TypingIndicator />
                </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <footer className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            id="chat-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Escuchando..." : "Escribe tu comando o pregunta..."}
            className="w-full pl-4 pr-24 py-3 rounded-full bg-gray-100 border-transparent focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500 transition-all"
            disabled={isLoading}
          />
          <div className="absolute right-2 flex items-center">
            <button type="button" onClick={handleMicClick} className={`p-3 rounded-full hover:bg-gray-200 focus:outline-none ${isListening ? 'text-red-500 animate-pulse' : 'text-gray-500 hover:text-blue-600'}`} aria-label="Usar micrófono" disabled={isLoading || !recognitionRef.current}>
              <FiMic className="h-5 w-5" />
            </button>
            <button type="submit" className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 transform hover:scale-105 disabled:bg-blue-400 disabled:scale-100" aria-label="Enviar mensaje" disabled={isLoading || !input.trim()}>
              {isLoading ? <FiLoader className="h-5 w-5 animate-spin"/> : <FiSend className="h-5 w-5" />}
            </button>
          </div>
        </form>
      </footer>
    </div>
  );
}