"use client";

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

type Language = 'es' | 'en';

interface LanguageContextType {
  language: Language;
  setLanguage: (language: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguageState] = useState<Language>('es');

  useEffect(() => {
    // Al cargar, intentar obtener el idioma guardado en localStorage
    const savedLanguage = localStorage.getItem('appLanguage') as Language;
    if (savedLanguage && ['es', 'en'].includes(savedLanguage)) {
      setLanguageState(savedLanguage);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    // Guardar el nuevo idioma en el estado y en localStorage
    localStorage.setItem('appLanguage', lang);
    setLanguageState(lang);
    // Forzar un refresco de la página para que el middleware de Django detecte el nuevo header
    // y sirva el contenido en el idioma correcto.
    window.location.reload();
  };

  const value = {
    language,
    setLanguage,
  };

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage debe ser usado dentro de un LanguageProvider');
  }
  return context;
};