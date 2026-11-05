'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { FiChevronRight, FiSearch, FiSun, FiMoon, FiBell } from 'react-icons/fi';
import { useTheme } from '@/contexts/ThemeContext';

const Breadcrumbs = () => {
  const pathname = usePathname();
  const paths = pathname.split('/').filter(p => p);

  return (
    <nav className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">
      {paths.map((path, idx) => {
        const href = `/${paths.slice(0, idx + 1).join('/')}`;
        const isLast = idx === paths.length - 1;
        const label = path.replace(/[-_]/g, ' ');

        return (
          <React.Fragment key={href}>
            {idx > 0 && <FiChevronRight className="h-3 w-3" />}
            {isLast ? (
              <span className="text-[var(--brand-primary)] italic">{label}</span>
            ) : (
              <Link href={href} className="hover:text-[var(--text-primary)] transition-colors">
                {label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export const Topbar = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="h-20 bg-[var(--background-main)]/80 backdrop-blur-md border-b border-[var(--border-default)] flex items-center justify-between px-8 sticky top-0 z-30 transition-colors duration-300">
      <div className="flex items-center gap-12">
        <Breadcrumbs />

        {/* Global Smart Search */}
        <div className="hidden lg:flex items-center relative">
          <FiSearch className="absolute left-4 text-[var(--text-muted)]" size={18} />
          <input
            type="text"
            placeholder="Instruye o busca..."
            className="pl-12 pr-6 py-2.5 bg-[var(--background-card)] border border-[var(--border-default)] rounded-2xl text-sm w-80 focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent outline-none transition-all placeholder:italic"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Kernel Status Indicator */}
        <div className="px-4 py-2 bg-[var(--status-success)]/10 rounded-full flex items-center gap-2">
          <div className="w-2 h-2 bg-[var(--status-success)] rounded-full animate-pulse" />
          <span className="text-[10px] font-black text-[var(--status-success)] uppercase tracking-tighter">Kernel Active</span>
        </div>

        <button
          onClick={toggleTheme}
          className="p-2.5 text-[var(--text-secondary)] hover:bg-[var(--background-card)] rounded-xl transition-all"
          aria-label="Toggle Theme"
        >
          {theme === 'dark' ? <FiSun size={20} /> : <FiMoon size={20} />}
        </button>

        <button className="p-2.5 text-[var(--text-secondary)] hover:bg-[var(--background-card)] rounded-xl transition-all relative">
          <FiBell size={20} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-[var(--status-error)] rounded-full border-2 border-[var(--background-main)]" />
        </button>
      </div>
    </header>
  );
};
