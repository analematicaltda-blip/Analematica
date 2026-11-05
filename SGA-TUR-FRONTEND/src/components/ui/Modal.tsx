// frontend/src/components/ui/Modal.tsx
'use client';
import React from 'react';
import { FiX } from 'react-icons/fi';
interface ModalProps { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode; }
export default function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="text-xl font-semibold">{title}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800"><FiX size={24} /></button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}
