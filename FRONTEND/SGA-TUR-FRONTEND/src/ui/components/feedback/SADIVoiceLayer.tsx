'use client';

import React, { useState, useEffect, useRef } from 'react';
import { FiMic, FiMicOff, FiZap, FiLoader, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export type SADIState = 'idle' | 'listening' | 'processing' | 'confirming' | 'success' | 'error';

interface VoiceLayerProps {
  onAudioReady: (blob: Blob) => void;
  state: SADIState;
  responseMessage?: string;
  className?: string;
}

export const SADIVoiceLayer = ({ onAudioReady, state, responseMessage, className }: VoiceLayerProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        onAudioReady(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
    } catch (err) {
      console.error("Error accessing microphone", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && state === 'listening') {
      mediaRecorderRef.current.stop();
    }
  };

  const handleMouseDown = () => {
    if (state === 'idle' || state === 'success' || state === 'error') {
       startRecording();
    }
  };

  const handleMouseUp = () => {
    stopRecording();
  };

  return (
    <div className={cn("fixed bottom-8 right-8 z-50 flex flex-col items-end gap-4", className)}>
      {/* Response Tooltip */}
      {(state !== 'idle' || responseMessage) && (
        <div className={cn(
          "max-w-xs p-4 rounded-[1.5rem] shadow-2xl border backdrop-blur-md animate-in slide-in-from-bottom-2 duration-300",
          state === 'error' ? "bg-rose-500/10 border-rose-500/20 text-rose-700" :
          state === 'success' ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-700" :
          "bg-[var(--background-card)] border-[var(--border-default)] text-[var(--text-primary)]"
        )}>
          <div className="flex items-center gap-2 mb-2">
            {state === 'processing' && <FiLoader className="animate-spin text-indigo-500" />}
            {state === 'success' && <FiCheckCircle className="text-emerald-500" />}
            {state === 'error' && <FiAlertCircle className="text-rose-500" />}
            <span className="text-[10px] font-black uppercase tracking-widest opacity-40">Brazo Ejecutor IA (SARITA)</span>
          </div>
          <p className="text-xs font-bold leading-relaxed italic">
            {state === 'listening' ? "Capturando directiva institucional..." :
             state === 'processing' ? "Analizando impacto y autoridad..." :
             responseMessage || "Esperando instrucción soberana..."}
          </p>
        </div>
      )}

      {/* Main Mic Button */}
      <button
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => { setIsHovered(false); stopRecording(); }}
        className={cn(
          "w-20 h-20 rounded-[2rem] flex items-center justify-center transition-all duration-500 shadow-2xl relative group overflow-hidden",
          state === 'listening' ? "bg-rose-600 scale-110 shadow-rose-500/40" :
          state === 'processing' ? "bg-indigo-600 shadow-indigo-500/40" :
          state === 'confirming' ? "bg-amber-500 shadow-amber-500/40" :
          "bg-[var(--brand-primary)] shadow-brand/40 hover:scale-105"
        )}
      >
        {/* Pulsating Ring */}
        {state === 'listening' && (
          <div className="absolute inset-0 rounded-[2rem] border-4 border-white animate-ping opacity-20" />
        )}

        {/* Glow Effect */}
        <div className={cn(
          "absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500",
          state === 'listening' && "opacity-40"
        )} />

        <div className="relative z-10 text-white">
          {state === 'listening' ? <FiMicOff size={32} /> :
           state === 'processing' ? <FiLoader size={32} className="animate-spin" /> :
           <FiMic size={32} />}
        </div>

        {/* Intent Badge */}
        <div className="absolute bottom-2 right-2">
           <FiZap size={12} className={cn(
             "text-white/40 group-hover:text-white transition-colors",
             state !== 'idle' && "text-white animate-pulse"
           )} />
        </div>
      </button>
    </div>
  );
};
