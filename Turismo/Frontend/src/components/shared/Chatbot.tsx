'use client';

import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiMessageSquare } from 'react-icons/fi';
import { Button } from '@/components/ui/Button';
import api from '@/services/api';

interface Message {
  text: string;
  isUser: boolean;
}

const ChatMessage = ({ message }: { message: Message }) => (
  <div className={`flex items-start gap-3 ${message.isUser ? 'justify-end' : ''}`}>
    {!message.isUser && <FiMessageSquare className="h-6 w-6 text-blue-500 flex-shrink-0" />}
    <div className={`px-4 py-2 rounded-lg max-w-sm ${message.isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
      <p className="text-sm">{message.text}</p>
    </div>
  </div>
);

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { text: '¡Hola! Soy tu asistente virtual. ¿Cómo puedo ayudarte a planear tu viaje con la plataforma de Turismo?', isUser: false }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = { text: inputValue, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await api.post('/agent/chat/', { message: inputValue });
      const reply = response.data.reply?.output || response.data.reply || "No he podido procesar tu solicitud en este momento.";
      const botMessage: Message = { text: reply, isUser: false };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = { text: 'Lo siento, estoy teniendo problemas para conectarme. Inténtalo de nuevo más tarde.', isUser: false };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(!isOpen)}
          className="rounded-full w-16 h-16 shadow-lg"
        >
          <FiMessageSquare className="h-8 w-8" />
        </Button>
      </div>

      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[32rem] bg-white rounded-lg shadow-2xl z-50 flex flex-col">
          <header className="bg-blue-600 text-white p-4 rounded-t-lg">
            <h3 className="font-bold text-lg">Asistente Virtual</h3>
          </header>

          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))}
            {isLoading && <ChatMessage message={{ text: 'Escribiendo...', isUser: false }} />}
            <div ref={chatEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="p-4 border-t flex items-center gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Escribe tu mensaje..."
              className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <Button type="submit" variant="primary" className="rounded-full w-12 h-12" disabled={isLoading}>
              <FiSend className="h-5 w-5" />
            </Button>
          </form>
        </div>
      )}
    </>
  );
};

export default Chatbot;