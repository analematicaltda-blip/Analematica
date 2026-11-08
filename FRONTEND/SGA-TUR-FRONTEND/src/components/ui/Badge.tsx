import React from 'react';
import {cn} from '@/lib/utils';
export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>{
 variant?:'default'|'secondary'|'outline'|'destructive'|'success'|'warning';
}
function Badge({className,variant='default',...props}:BadgeProps){
 const variants={default:'bg-[#142850] border-sky-300',secondary:'bg-[#0e1b38] border-blue-400',outline:'border-sky-300',destructive:'bg-[#0e1b38] border-rose-400',success:'bg-[#0e1b38] border-emerald-400',warning:'bg-[#0e1b38] border-amber-300'};
 return <div className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold text-white transition-colors focus:outline-none focus:ring-2 focus:ring-sky-300',variants[variant],className)} {...props}/>;
}
export {Badge};
