'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { RoleUIConfig, NavSection, NavLink } from '@/ui/role-config/superadmin';
import { FiShield, FiChevronRight } from 'react-icons/fi';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface SidebarProps {
  config: RoleUIConfig;
  userName?: string;
  userEmail?: string;
}

const SidebarItem = ({ link, isActive }: { link: NavLink, isActive: boolean }) => {
  const Icon = link.icon;
  return (
    <Link href={link.href}>
      <div
        className={cn(
          "group flex items-center px-4 py-3 mb-1 rounded-xl transition-all duration-300 cursor-pointer",
          isActive
            ? "bg-[var(--brand-primary)] text-white shadow-lg shadow-brand/20"
            : "text-[var(--text-secondary)] hover:bg-[var(--background-card)] hover:text-[var(--text-primary)]"
        )}
        aria-label={link.label}
        data-intent={link.intent}
      >
        <Icon className={cn("mr-3 h-5 w-5 transition-transform duration-300", !isActive && "group-hover:scale-110")} />
        <span className="text-sm font-bold tracking-tight">{link.label}</span>
        {isActive && <FiChevronRight className="ml-auto h-4 w-4" />}
      </div>
    </Link>
  );
};

const SidebarSection = ({ section }: { section: NavSection }) => {
  const pathname = usePathname();
  return (
    <div className="mb-6">
      <h3 className="px-4 mb-3 text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-muted)]">
        {section.title}
      </h3>
      <div className="space-y-px">
        {section.links.map((link) => (
          <SidebarItem
            key={link.href}
            link={link}
            isActive={pathname === link.href}
          />
        ))}
      </div>
    </div>
  );
};

export const Sidebar = ({ config, userName, userEmail }: SidebarProps) => {
  return (
    <aside className="w-72 h-screen flex-shrink-0 bg-[var(--background-sidebar)] border-r border-[var(--border-default)] flex flex-col overflow-hidden transition-colors duration-300">
      {/* Brand Header */}
      <div className="p-8">
        <div className="flex items-center gap-3 mb-10">
          <div className="w-10 h-10 bg-[var(--brand-primary)] rounded-xl flex items-center justify-center text-white shadow-xl shadow-brand/20">
            <FiShield size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-black text-[var(--text-primary)] tracking-tighter leading-none">SARITA</h2>
            <p className="text-[9px] font-black text-[var(--brand-primary)] uppercase tracking-[0.3em] mt-1">Sovereign ERP</p>
          </div>
        </div>

        {/* User profile brief */}
        {userName && (
          <div className="bg-[var(--background-card)] p-4 rounded-2xl border border-[var(--border-default)] shadow-sm">
            <p className="text-xs font-black text-[var(--text-primary)] truncate">{userName}</p>
            <p className="text-[10px] font-bold text-[var(--text-muted)] truncate">{userEmail}</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 overflow-y-auto custom-scrollbar">
        {config.sidebarSections.map((section, idx) => (
          <SidebarSection key={idx} section={section} />
        ))}
      </nav>

      {/* Footer / Status */}
      <div className="p-6 border-t border-[var(--border-default)]">
        <div className="bg-[var(--brand-deep)] rounded-2xl p-4 text-white/90 relative overflow-hidden group cursor-pointer">
          <div className="relative z-10">
            <p className="text-[10px] font-black uppercase tracking-widest text-white/40 mb-1">Status</p>
            <p className="text-xs font-bold leading-tight">Agentes de Inteligencia activos.</p>
          </div>
          <div className="absolute -right-2 -bottom-2 opacity-10 group-hover:scale-125 transition-transform duration-700">
            <FiShield size={48} />
          </div>
        </div>
      </div>
    </aside>
  );
};
