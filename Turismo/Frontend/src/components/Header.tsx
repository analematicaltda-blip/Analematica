'use client';

import React from 'react';
import { Menu, Bell, User, Sun, Moon, ShieldCheck } from 'lucide-react';
import { FiLock } from 'react-icons/fi';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { useDashboard } from '@/contexts/DashboardContext';
import { PermissionGuard } from '@/ui/guards/PermissionGuard';

interface HeaderProps {
  isSidebarOpen: boolean;
  setIsSidebarOpen: (isOpen: boolean) => void;
}

const Header: React.FC<HeaderProps> = ({ isSidebarOpen, setIsSidebarOpen }) => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();
  const { isAuditMode, toggleAuditMode } = useDashboard();

  return (
    <header className="bg-white dark:bg-black border-b border-gray-100 dark:border-white/5 transition-colors sticky top-0 z-40">
      <div className="mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Botón para menú móvil */}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="lg:hidden text-gray-500 dark:text-slate-400 hover:text-brand transition-colors"
            aria-label="Abrir menú"
          >
            <Menu className="h-6 w-6" />
          </button>

          {/* Contexto del Nodo */}
          <div className="hidden sm:flex items-center gap-4">
             <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-brand rounded-full animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500">
                  Ecosistema Sarita ● Turismo
                </span>
             </div>
             <div className="h-4 w-px bg-gray-100 dark:bg-white/10" />
             <div className="px-3 py-1 bg-slate-100 dark:bg-brand-deep rounded-lg flex items-center gap-2" title="Aislamiento Institucional Verificado (Modelo: ProviderProfile)">
                <FiLock size={10} className="text-slate-400" />
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">
                   Entidad ID: {user?.id?.substring(0,8) || 'GLOBAL-01'} ● Modelo: {user?.role === 'PRESTADOR' ? 'ProviderProfile' : 'Systemic'}
                </span>
             </div>
          </div>

          <div className="flex-1"></div>

          {/* Acciones del Sistema */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            {/* Modo Auditor (F-C+) */}
            <PermissionGuard allowedRoles={['SuperAdmin', 'AdminPlataforma', 'Auditor']}>
               <button
                 onClick={toggleAuditMode}
                 className={`flex items-center gap-2 px-3 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border ${
                   isAuditMode
                   ? 'bg-amber-100 text-amber-700 border-amber-200'
                   : 'bg-slate-50 dark:bg-brand-deep text-slate-400 dark:text-slate-500 border-transparent'
                 }`}
                 title={isAuditMode ? "Desactivar Modo Auditor" : "Activar Modo Auditor"}
               >
                 <ShieldCheck size={16} className={isAuditMode ? 'animate-pulse' : ''} />
                 <span className="hidden lg:inline">{isAuditMode ? 'Modo Auditor ON' : 'Activar Auditoría'}</span>
               </button>
            </PermissionGuard>

            {/* Toggle Día/Noche */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-slate-50 dark:bg-brand-deep text-slate-500 dark:text-brand-light hover:bg-brand/10 transition-all border border-transparent dark:border-white/5"
              title={`Cambiar a modo ${theme === 'light' ? 'Noche' : 'Día'}`}
            >
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>

            <button className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:text-brand hover:bg-brand/10 transition-all relative">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-black" />
            </button>

            <div className="h-8 w-px bg-gray-100 dark:bg-white/10 mx-2" />

            <button className="flex items-center gap-3 p-1 sm:pr-4 rounded-2xl hover:bg-slate-50 dark:hover:bg-brand-deep transition-all group">
              <div className="w-8 h-8 bg-brand/10 dark:bg-brand/20 rounded-lg flex items-center justify-center text-brand">
                 <User size={18} />
              </div>
              <div className="hidden sm:flex flex-col items-start leading-tight">
                 <span className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-brand transition-colors">
                   {user?.username || 'Usuario'}
                 </span>
                 <span className="text-[10px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-tighter">
                   {user?.role || 'Soberano'}
                 </span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
