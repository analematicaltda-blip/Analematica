
import React from 'react';
import { FunnelBuilderProvider, useFunnelBuilder } from '../context/FunnelBuilderContext';
import { PermissionGuard } from '@/ui/guards/PermissionGuard';
import HierarchyPanel from './funnel-builder/HierarchyPanel';
import Editor from './funnel-builder/Editor';
import * as Icons from './icons';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

const FunnelBuilder: React.FC = () => {
    const { activeFunnel, activeCadena, setActiveFunnelId } = useFunnelBuilder();

    if (!activeCadena) {
        return (
            <div className="flex-1 flex items-center justify-center text-center text-muted-foreground p-8">
                <Icons.LoadingSpinner className="w-10 h-10"/>
            </div>
        );
    }
    
    return (
        <div className="flex-1 flex overflow-hidden">
            <HierarchyPanel />
            <main className="flex-1 flex flex-col bg-background overflow-hidden">
                {activeFunnel ? (
                    <Editor />
                ) : (
                    <div className="flex-1 flex items-center justify-center text-center text-muted-foreground p-8">
                        <div>
                            <Icons.CursorArrowRaysIcon className="w-16 h-16 mx-auto mb-4"/>
                            <h2 className="text-2xl font-bold">No Funnels Found</h2>
                            <p className="max-w-md mt-2">Get started by creating a new funnel.</p>
                            <PermissionGuard deniedRoles={['Auditor', 'Observador']}>
                                <button className="mt-6 flex items-center space-x-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90" onClick={() => setActiveFunnelId('new')}>
                                    <Icons.PlusIcon className="w-5 h-5" />
                                    <span>Crear Embudo</span>
                                </button>
                            </PermissionGuard>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

const Header: React.FC = () => {
    const { allData, activeCadenaId, setActiveCadenaId, setActiveCategoriaId, setActiveSubcategoriaId, setActiveLandingPageId, setActiveFunnelId, setActivePageId } = useFunnelBuilder();

    return (
         <header className="flex-shrink-0 h-16 bg-card border-b flex items-center justify-between px-4 z-20">
            <div className="flex items-center space-x-2">
                <Icons.FunnelIcon className="w-6 h-6 text-primary" />
                <h1 className="text-xl font-bold">Arquitecto de Embudos</h1>
            </div>
            <div className="flex-grow flex justify-center">
                <div className="bg-muted p-1 rounded-lg flex space-x-1">
                    {allData.cadenas.map(c => (
                        <button 
                            key={c.id} 
                            onClick={() => { 
                                setActiveCadenaId(c.id); 
                                setActiveCategoriaId(null); 
                                setActiveSubcategoriaId(null); 
                                setActiveLandingPageId(null); 
                                setActiveFunnelId(null); 
                                setActivePageId(null); 
                            }} 
                            className={`px-3 py-1 text-sm rounded-md font-semibold ${activeCadenaId === c.id ? `text-white shadow` : `hover:bg-accent`}`} 
                            style={activeCadenaId === c.id ? {backgroundColor: c.color_primario} : {}}
                        >
                            {c.nombre}
                        </button>
                    ))}
                </div>
            </div>
            <div className="flex items-center space-x-4">
                <PermissionGuard deniedRoles={['Auditor', 'Observador']}>
                    <button className="flex items-center space-x-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors" onClick={() => setActiveFunnelId('new')}>
                        <Icons.PlusIcon className="w-5 h-5"/>
                        <span className="font-semibold">New Funnel</span>
                    </button>
                </PermissionGuard>
                <Icons.BellIcon className="w-6 h-6 text-muted-foreground"/>
                <Icons.UserCircleIcon className="w-8 h-8 text-muted-foreground"/>
            </div>
        </header>
    );
}


interface LevelFunnelsProps {
  authToken: string;
}

const LevelFunnels: React.FC<LevelFunnelsProps> = ({ authToken }) => (
    <DndProvider backend={HTML5Backend}>
        <FunnelBuilderProvider authToken={authToken}>
            <div className="h-full flex flex-col font-sans text-foreground bg-background">
                <Header />
                <FunnelBuilder />
            </div>
        </FunnelBuilderProvider>
    </DndProvider>
);

export default LevelFunnels;
