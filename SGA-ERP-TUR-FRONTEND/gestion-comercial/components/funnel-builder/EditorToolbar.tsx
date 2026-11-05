
import React from 'react';
import * as Icons from '../icons';
import { useFunnelBuilder } from '../../context/FunnelBuilderContext';

const EditorToolbar: React.FC = () => {
    const {
        undo, canUndo, redo, canRedo,
        activeBreakpoint, setActiveBreakpoint,
        saveStatus
    } = useFunnelBuilder();

    const SaveStatusIndicator = () => {
        switch(saveStatus) {
            case 'saving': return <div className="flex items-center gap-2 text-sm text-muted-foreground"><Icons.LoadingSpinner className="w-4 h-4" /> Guardando...</div>;
            case 'error': return <div className="flex items-center gap-2 text-sm text-amber-600 font-bold bg-amber-50 px-2 py-1 rounded"><Icons.AlertTriangleIcon className="w-4 h-4" /> Modo Demo - Backend Pendiente</div>;
            case 'saved': default: return <div className="flex items-center gap-2 text-sm text-green-500"><Icons.CheckIcon className="w-4 h-4" /> Guardado localmente</div>;
        }
    };

    return (
        <div className="flex-shrink-0 h-14 bg-card border-b flex items-center justify-between px-4">
            <div className="flex items-center gap-2">
                <button onClick={undo} disabled={!canUndo} className="p-2 rounded disabled:text-muted-foreground/50 disabled:cursor-not-allowed hover:bg-accent" title="Deshacer"><Icons.ChevronLeftIcon className="w-5 h-5"/></button>
                <button onClick={redo} disabled={!canRedo} className="p-2 rounded disabled:text-muted-foreground/50 disabled:cursor-not-allowed hover:bg-accent" title="Rehacer"><Icons.ChevronRightIcon className="w-5 h-5" /></button>
            </div>
             <div className="flex items-center gap-2 bg-muted p-1 rounded-lg">
                <button onClick={() => setActiveBreakpoint('desktop')} className={`p-1.5 rounded-md ${activeBreakpoint === 'desktop' ? 'bg-background shadow' : ''}`}><Icons.ComputerDesktopIcon /></button>
                <button onClick={() => setActiveBreakpoint('tablet')} className={`p-1.5 rounded-md ${activeBreakpoint === 'tablet' ? 'bg-background shadow' : ''}`}><Icons.DeviceTabletIcon /></button>
                <button onClick={() => setActiveBreakpoint('mobile')} className={`p-1.5 rounded-md ${activeBreakpoint === 'mobile' ? 'bg-background shadow' : ''}`}><Icons.DevicePhoneMobileIcon /></button>
            </div>
            <div className="flex items-center gap-4">
                <SaveStatusIndicator />
                <button onClick={() => alert('Simulado: La publicación requiere infraestructura de hosting de Landings.')} className="bg-primary text-primary-foreground font-bold px-4 py-1.5 rounded-md">Publicar</button>
            </div>
        </div>
    );
};

export default EditorToolbar;
