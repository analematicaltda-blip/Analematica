
import React from 'react';
import EditorToolbar from './EditorToolbar';
import BlockLibrary from './BlockLibrary';
import Canvas from './Canvas';
import PropertiesPanel from './PropertiesPanel';
import { useFunnelBuilder } from '../../context/FunnelBuilderContext';

const Editor: React.FC = () => {
    const { isMediaLibraryOpen, setIsMediaLibraryOpen, allData, mediaLibraryCallback } = useFunnelBuilder();

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
             {isMediaLibraryOpen && (
                <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
                    <div className="bg-card p-6 rounded-lg shadow-xl w-full max-w-4xl">
                        <h3 className="text-lg font-bold mb-4">Biblioteca de Medios</h3>
                        <div className="grid grid-cols-5 gap-4 max-h-[60vh] overflow-y-auto">
                            {allData.mediaLibrary.map(asset => (
                                <div key={asset.id} className="cursor-pointer group" onClick={() => { mediaLibraryCallback?.(asset.url); setIsMediaLibraryOpen(false); }}>
                                    <img src={asset.url} alt={asset.name} className="w-full h-32 object-cover rounded-md ring-2 ring-transparent group-hover:ring-primary"/>
                                    <p className="text-xs truncate mt-1">{asset.name}</p>
                                </div>
                            ))}
                        </div>
                        <div className="flex justify-end mt-4"><button onClick={() => setIsMediaLibraryOpen(false)} className="px-4 py-2 rounded bg-muted">Cerrar</button></div>
                    </div>
                </div>
            )}
            <EditorToolbar />
            <div className="flex-1 flex overflow-hidden">
                <BlockLibrary />
                <Canvas />
                <PropertiesPanel />
            </div>
        </div>
    );
};

export default Editor;
