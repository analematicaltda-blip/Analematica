
import React from 'react';
import { useDrag } from 'react-dnd';
import { availableBlocks, ItemTypes } from './data';
import { useFunnelBuilder } from '../../context/FunnelBuilderContext';

const LibraryBlock: React.FC<{ item: typeof availableBlocks[0] }> = ({ item }) => {
    const [{ isDragging }, drag] = useDrag(() => ({ 
        type: ItemTypes.LIBRARY_BLOCK, 
        item: { type: item.type }, 
        collect: (monitor) => ({ isDragging: !!monitor.isDragging() }), 
    }));
    return (
        // FIX: Added 'as any' to the drag ref to resolve a type mismatch issue
        // between the react-dnd drag connector and the expected ref type for a DOM element.
        <div ref={drag as any} className={`flex flex-col items-center p-2 rounded-lg cursor-move transition-all ${isDragging ? 'bg-primary/20 scale-105' : 'bg-muted hover:bg-accent'}`} title={item.name}>
            <item.icon className="w-5 h-5 mb-1" />
            <span className="text-[10px]">{item.name}</span>
        </div>
    );
};

const BlockLibrary: React.FC = () => {
    const { activeFunnel, activePageId, setActivePageId } = useFunnelBuilder();

    return (
        <div className="w-60 bg-card border-r p-4 flex flex-col">
            <h3 className="font-bold mb-4">Bloques</h3>
            <div className="grid grid-cols-3 gap-2">
                {availableBlocks.map(b => <LibraryBlock key={b.type} item={b} />)}
            </div>
            <h3 className="font-bold mt-8 mb-4">Páginas del Embudo</h3>
            <div className="space-y-1">
                {activeFunnel?.pages.map(p => 
                    <button 
                        key={p.id} 
                        onClick={() => setActivePageId(p.id)} 
                        className={`w-full text-left p-2 rounded text-sm ${activePageId === p.id ? 'bg-accent font-bold' : 'hover:bg-accent/50'}`}
                    >
                        {p.name}
                    </button>
                )}
            </div>
        </div>
    );
};

export default BlockLibrary;
