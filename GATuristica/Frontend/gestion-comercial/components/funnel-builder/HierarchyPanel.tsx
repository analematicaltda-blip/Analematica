
import React, { useState } from 'react';
import * as Icons from '../icons';
import { useFunnelBuilder } from '../../context/FunnelBuilderContext';

const HierarchyPanel: React.FC = () => {
    const {
        filteredCategorias,
        filteredSubcategorias,
        filteredLandingPages,
        activeCategoriaId,
        setActiveCategoriaId,
        activeSubcategoriaId,
        setActiveSubcategoriaId,
        activeLandingPageId,
        setActiveLandingPageId,
        activeLandingPage,
        activeFunnelId,
        setActiveFunnelId,
        setActivePageId,
        isCreateFunnelModalOpen,
        setIsCreateFunnelModalOpen,
        handleCreateFunnel,
    } = useFunnelBuilder();

    const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);
    const [newFunnelName, setNewFunnelName] = useState('');

    const renderIcon = (icon: any) => {
        if (typeof icon === 'string') return <span className="mr-2">{icon}</span>;
        if (typeof icon === 'function') {
            const IconComponent = icon as React.FC<{className?: string}>;
            return <IconComponent className="w-5 h-5 mr-2" />;
        }
        return null;
    };

    const onCreateFunnel = () => {
        handleCreateFunnel(newFunnelName);
        setNewFunnelName('');
    }

    return (
        <>
            {isCreateFunnelModalOpen && activeLandingPage && (
                <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
                    <div className="bg-card p-6 rounded-lg shadow-xl w-full max-w-md">
                        <h3 className="text-lg font-bold mb-4">Crear Nuevo Embudo para "{activeLandingPage.nombre}"</h3>
                        <input type="text" value={newFunnelName} onChange={e => setNewFunnelName(e.target.value)} placeholder="Nombre del Embudo" className="w-full bg-input p-2 rounded border mb-4" autoFocus />
                        <div className="flex justify-end gap-2">
                            <button onClick={() => setIsCreateFunnelModalOpen(false)} className="px-4 py-2 rounded bg-muted">Cancelar</button>
                            <button onClick={onCreateFunnel} disabled={!newFunnelName.trim()} className="px-4 py-2 rounded bg-primary text-primary-foreground disabled:opacity-50">Crear</button>
                        </div>
                    </div>
                </div>
            )}
            <aside className={`bg-card border-r flex flex-col transition-all duration-300 ${leftPanelCollapsed ? 'w-16' : 'w-80'}`}>
                <div className="p-4 border-b flex-shrink-0">
                    <h2 className="text-lg font-semibold truncate">Jerarquía de Contenido</h2>
                </div>
                {!leftPanelCollapsed && (
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        <div>
                            <h3 className="font-semibold text-sm text-muted-foreground mb-2">Categorías</h3>
                            <div className="space-y-1">
                                {filteredCategorias.map(c => 
                                    <button key={c.id} onClick={() => { setActiveCategoriaId(c.id); setActiveSubcategoriaId(null); setActiveLandingPageId(null); setActiveFunnelId(null); setActivePageId(null); }} className={`w-full text-left p-2 rounded-md flex items-center ${activeCategoriaId === c.id ? 'bg-accent font-bold' : 'hover:bg-accent/50'}`}>{renderIcon(c.icon)} {c.nombre}</button>
                                )}
                            </div>
                        </div>
                        {activeCategoriaId && <div><h3 className="font-semibold text-sm text-muted-foreground mb-2">Sub-Categorías</h3><div className="space-y-1">{filteredSubcategorias.map(s => <button key={s.id} onClick={() => { setActiveSubcategoriaId(s.id); setActiveLandingPageId(null); setActiveFunnelId(null); setActivePageId(null); }} className={`w-full text-left p-2 rounded-md ${activeSubcategoriaId === s.id ? 'bg-accent font-bold' : 'hover:bg-accent/50'}`}>{s.nombre}</button>)}</div></div>}
                        {activeSubcategoriaId && <div><h3 className="font-semibold text-sm text-muted-foreground mb-2">Landing Pages</h3><div className="space-y-1">{filteredLandingPages.map(lp => <button key={lp.id} onClick={() => { setActiveLandingPageId(lp.id); setActiveFunnelId(lp.funnels[0]?.id || null); setActivePageId(lp.funnels[0]?.pages[0]?.id || null) }} className={`w-full text-left p-2 rounded-md ${activeLandingPageId === lp.id ? 'bg-accent font-bold' : 'hover:bg-accent/50'}`}>{lp.nombre}</button>)}</div></div>}
                        {activeLandingPage && <div className="border-t pt-4">
                            <h3 className="font-semibold text-sm text-muted-foreground mb-2">Embudos en "{activeLandingPage.nombre}"</h3>
                            <select value={activeFunnelId || ''} onChange={e => { setActiveFunnelId(e.target.value); const fun = activeLandingPage.funnels.find(f => f.id === e.target.value); setActivePageId(fun?.pages[0]?.id || null); }} className="w-full bg-input p-2 rounded border mb-2"><option value="" disabled>Selecciona un embudo</option>{activeLandingPage.funnels.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}</select>
                            <button onClick={() => setIsCreateFunnelModalOpen(true)} className="w-full text-sm mt-2 p-2 bg-primary/10 text-primary rounded-md hover:bg-primary/20">[+] Crear Embudo</button>
                        </div>}
                    </div>
                )}
                <div className="p-2 border-t mt-auto flex-shrink-0">
                    <button onClick={() => setLeftPanelCollapsed(!leftPanelCollapsed)} className="w-full flex items-center justify-center p-2 rounded-lg text-muted-foreground hover:bg-accent">
                        {leftPanelCollapsed ? <Icons.ChevronDoubleRightIcon /> : <Icons.ChevronDoubleLeftIcon />}
                    </button>
                </div>
            </aside>
        </>
    );
};

export default HierarchyPanel;
