import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?:React.ReactNode;
  variant?:'primary'|'default'|'secondary'|'outline'|'ghost'|'icon'|'destructive'|'link';
  size?:'default'|'sm'|'lg'|'icon';
  color?:'primary'|'danger';
}

export const Button=({children,variant='primary',size,color='primary',className='',...props}:ButtonProps)=>{
 const base='inline-flex items-center justify-center rounded-xl text-sm font-bold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-300 disabled:opacity-50 disabled:pointer-events-none active:scale-95 text-white';
 const filled='bg-brand hover:bg-[#2563eb] shadow-lg shadow-brand/20';
 const variants={primary:filled,default:filled,secondary:'bg-[#142850] hover:bg-[#1a3262]',outline:'border border-sky-300 hover:bg-[#142850]',ghost:'hover:bg-[#142850]',icon:'hover:bg-[#142850]',destructive:'bg-brand border border-rose-400 hover:bg-[#1a3262]',link:'underline decoration-sky-300 underline-offset-4'};
 const sizes={default:'px-6 py-2.5',sm:'px-3 py-1.5 text-xs',lg:'px-8 py-3',icon:'h-10 w-10 p-2'};
 const selected=size||(variant==='icon'?'icon':'default');
 return <button className={`${base} ${variants[variant]} ${sizes[selected]} ${color==='danger'?'border border-rose-400':''} ${className}`} {...props}>{children}</button>;
};
