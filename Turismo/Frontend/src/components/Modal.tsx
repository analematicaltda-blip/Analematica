"use client";

import React, { ReactNode } from 'react';
import { FiX } from 'react-icons/fi';

interface ModalProps {
  title: string;
  onClose: () => void;
  children: ReactNode;
}

const Modal: React.FC<ModalProps> = ({ title, onClose, children }) => {
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
      onClick={onClose} // Cierra el modal si se hace clic en el fondo
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 my-8 overflow-hidden"
        onClick={(e) => e.stopPropagation()} // Evita que el clic dentro del modal lo cierre
      >
        <div className="flex justify-between items-center px-6 py-4 border-b border-gray-200">
          <h3 id="modal-title" className="text-xl font-bold text-gray-800">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Cerrar modal"
          >
            <FiX size={24} />
          </button>
        </div>
        <div className="p-6 overflow-y-auto" style={{ maxHeight: '70vh' }}>
          {children}
        </div>
        <div className="px-6 py-3 bg-gray-50 text-right">
             <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
                >
                Cerrar
            </button>
        </div>
      </div>
    </div>
  );
};

export default Modal;