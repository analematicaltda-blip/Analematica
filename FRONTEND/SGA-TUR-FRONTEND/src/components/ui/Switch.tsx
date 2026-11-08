'use client';
import React from 'react';
interface SwitchProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>,'onChange'> {
 checked:boolean;
 onCheckedChange?:(checked:boolean)=>void;
}
/** Controlled switch. A display without a change handler cannot change settings. */
export function Switch({checked,onCheckedChange,disabled,className='',...props}:SwitchProps){
 const locked=disabled||!onCheckedChange;
 return <button {...props} type="button" role="switch" aria-checked={checked} aria-label={props['aria-label']||'Configuración'} disabled={locked} onClick={()=>onCheckedChange?.(!checked)} className={'inline-flex h-7 w-12 items-center rounded-full border border-sky-300 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300 disabled:opacity-60 '+className} style={{...props.style,background:checked?'#1a3262':'#0a1128',color:'#ffffff'}}><span aria-hidden="true" className={'h-5 w-5 rounded-full bg-white transition-transform '+(checked?'translate-x-6':'translate-x-1')}/></button>;
}
