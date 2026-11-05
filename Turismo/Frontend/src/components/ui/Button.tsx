import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'outline' | 'ghost' | 'icon';
  color?: 'primary' | 'danger';
}

export const Button = ({
  children,
  variant = 'primary',
  color = 'primary',
  className = '',
  ...props
}: ButtonProps) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-xl text-sm font-bold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none active:scale-95';

  const variantClasses = {
    primary: `text-white ${color === 'primary' ? 'bg-brand hover:bg-brand-light focus:ring-brand shadow-lg shadow-brand/20' : 'bg-red-600 hover:bg-red-700 focus:ring-red-500 shadow-lg shadow-red-500/20'}`,
    outline: `border ${color === 'primary' ? 'border-brand/30 text-brand dark:text-brand-light hover:bg-brand/5 dark:border-white/10' : 'border-red-600 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20'}`,
    ghost: 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-brand-deep/50 hover:text-slate-900 dark:hover:text-white',
    icon: `hover:bg-slate-100 dark:hover:bg-brand-deep/50 rounded-xl p-2 ${color === 'danger' ? 'text-red-600 hover:bg-red-100' : 'text-slate-600 dark:text-slate-400'}`,
  };

  const sizeClasses = variant === 'icon' ? 'h-10 w-10' : 'px-6 py-2.5';

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
