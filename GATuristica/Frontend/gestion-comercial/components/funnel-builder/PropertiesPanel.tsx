
import React, { useState } from 'react';
import { Block, BlockProp, PropValue, BlockProps, BlockStyles, ThemeSettings } from '../../types';
import * as Icons from '../icons';
import { useFunnelBuilder } from '../../context/FunnelBuilderContext';

const ObjectArrayEditor: React.FC<{ items: any[], itemSchema: BlockProps, onChange: (newArray: any[]) => void }> = ({ items, itemSchema, onChange }) => {
    const { setIsMediaLibraryOpen, setMediaLibraryCallback } = useFunnelBuilder();
    const [openIndex, setOpenIndex] = useState<number | null>(0);

    const handleItemChange = (index: number, key: string, value: any) => {
        const newItems = [...items];
        newItems[index] = { ...newItems[index], [key]: value };
        onChange(newItems);
    };

    const handleAddItem = () => {
        const newItem: { [key: string]: any } = { id: `item-${Date.now()}` };
        Object.entries(itemSchema).forEach(([key, prop]) => {
            newItem[key] = prop.value;
        });
        onChange([...items, newItem]);
        setOpenIndex(items.length);
    };

    const handleRemoveItem = (id: string) => {
        onChange(items.filter(item => item.id !== id));
    };
    
    const handleMoveItem = (dragIndex: number, hoverIndex: number) => {
        const newItems = [...items];
        const [draggedItem] = newItems.splice(dragIndex, 1);
        if (draggedItem) newItems.splice(hoverIndex, 0, draggedItem);
        onChange(newItems);
    };

    const renderItemControl = (item: any, index: number, fieldKey: string, fieldProp: BlockProp) => {
         switch (fieldProp.type) {
            case 'string': return <input type="text" value={item[fieldKey]} onChange={e => handleItemChange(index, fieldKey, e.target.value)} className="w-full bg-input p-1 rounded border text-sm" />;
            case 'longtext': return <textarea value={item[fieldKey]} onChange={e => handleItemChange(index, fieldKey, e.target.value)} className="w-full bg-input p-1 rounded border text-sm" rows={3} />;
            case 'image': return <div><img src={item[fieldKey]} className="w-full h-20 object-cover rounded bg-muted mb-1" /><button onClick={() => { setMediaLibraryCallback(() => url => handleItemChange(index, fieldKey, url)); setIsMediaLibraryOpen(true); }} className="w-full p-1 bg-muted rounded hover:bg-accent text-xs">Cambiar</button></div>;
            case 'icon':
                const iconList = Object.keys(Icons) as (keyof typeof Icons)[];
                return <select value={item[fieldKey]} onChange={e => handleItemChange(index, fieldKey, e.target.value)} className="w-full bg-input p-1 rounded border text-sm"><option value="">Icono</option>{iconList.map(iconName => <option key={iconName} value={iconName}>{iconName}</option>)}</select>;
            default: return null;
        }
    };

    return (
        <div className="space-y-2">
            {items.map((item, index) => (
                <div key={item.id} className="bg-muted/50 p-2 rounded-lg">
                    <div className="flex items-center justify-between">
                        <button onClick={() => setOpenIndex(openIndex === index ? null : index)} className="flex items-center gap-2 font-semibold text-sm flex-grow text-left">
                            <Icons.ChevronRightIcon className={`w-4 h-4 transition-transform ${openIndex === index ? 'rotate-90' : ''}`} />
                            {item.title || `Elemento ${index + 1}`}
                        </button>
                        <button onClick={() => handleRemoveItem(item.id)} className="p-1 text-destructive"><Icons.TrashIcon className="w-4 h-4" /></button>
                    </div>
                    {openIndex === index && (
                        <div className="p-2 mt-2 border-t space-y-2">
                            {Object.entries(itemSchema).map(([key, prop]) => (
                                <div key={key}>
                                    <label className="text-xs font-medium text-muted-foreground">{prop.label}</label>
                                    {renderItemControl(item, index, key, prop)}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ))}
            <button onClick={handleAddItem} className="w-full p-2 mt-2 bg-muted rounded hover:bg-accent text-sm">[+] Añadir Elemento</button>
        </div>
    );
};


const PropertiesPanel: React.FC = () => {
    const { activeBlock, updateData, activeFunnel, setIsMediaLibraryOpen, setMediaLibraryCallback, activePage } = useFunnelBuilder();
    
    if (!activeBlock || !activeFunnel) {
        return <div className="w-96 bg-card border-l p-4 text-center text-muted-foreground"><p className="mt-10">Selecciona un bloque del lienzo para editar sus propiedades.</p></div>;
    }

    const onUpdateBlock = (updatedBlock: Block) => {
        updateData(d => {
            const page = d.landingPages.flatMap(lp => lp.funnels).flatMap(f => f.pages).find(p => p.id === activePage?.id);
            if (page) {
                const blockIndex = page.blocks.findIndex(b => b.id === updatedBlock.id);
                if (blockIndex > -1) page.blocks[blockIndex] = updatedBlock;
            }
        });
    }

    const handlePropChange = (key: string, value: PropValue) => {
        const newBlock = { ...activeBlock, props: { ...activeBlock.props, [key]: { ...activeBlock.props[key], value } } };
        onUpdateBlock(newBlock);
    };
    
    const handleStyleChange = (key: keyof BlockStyles, value: any) => {
        const newBlock = { ...activeBlock, styles: { ...activeBlock.styles, [key]: value } };
        onUpdateBlock(newBlock);
    };

    const handleObjectArrayChange = (propKey: string, newArray: any[]) => {
        handlePropChange(propKey, newArray);
    };

    const iconList = Object.keys(Icons) as (keyof typeof Icons)[];

    const renderPropControl = (key: string, prop: BlockProp) => {
        switch (prop.type) {
            case 'string': return <input type="text" value={prop.value as string} onChange={e => handlePropChange(key, e.target.value)} className="w-full bg-input p-2 rounded border" />;
            case 'longtext': return <textarea value={prop.value as string} onChange={e => handlePropChange(key, e.target.value)} className="w-full bg-input p-2 rounded border" rows={4} />;
            case 'url': return <input type="url" value={prop.value as string} onChange={e => handlePropChange(key, e.target.value)} className="w-full bg-input p-2 rounded border" />;
            case 'color': return <input type="color" value={prop.value as string} onChange={e => handlePropChange(key, e.target.value)} className="w-full h-10 p-1 bg-input rounded border" />;
            case 'image': return <div><img src={prop.value as string} className="w-full h-32 object-cover rounded bg-muted mb-2" /><button onClick={() => { setMediaLibraryCallback(() => url => handlePropChange(key, url)); setIsMediaLibraryOpen(true); }} className="w-full p-2 bg-muted rounded hover:bg-accent text-sm">Cambiar Imagen</button></div>;
            case 'icon': return <select value={prop.value as string} onChange={e => handlePropChange(key, e.target.value)} className="w-full bg-input p-2 rounded border"><option value="">Seleccionar Icono</option>{iconList.map(iconName => <option key={iconName} value={iconName}>{iconName}</option>)}</select>;
            case 'array:image':
                const images = prop.value as string[];
                return <div>
                    <div className="grid grid-cols-3 gap-2">{images.map((img, i) => <div key={i} className="relative group/img"><img src={img} className="w-full h-16 object-cover rounded"/><button onClick={() => handlePropChange(key, images.filter((_, idx) => idx !== i))} className="absolute top-1 right-1 bg-destructive/80 text-white rounded-full p-0.5 opacity-0 group-hover/img:opacity-100"><Icons.XMarkIcon className="w-3 h-3"/></button></div>)}</div>
                    <button onClick={() => { setMediaLibraryCallback(() => url => handlePropChange(key, [...images, url])); setIsMediaLibraryOpen(true); }} className="w-full p-2 mt-2 bg-muted rounded hover:bg-accent text-sm">Añadir Imagen</button>
                </div>;
            case 'array:object':
                const items = (prop.value || []) as any[];
                return <ObjectArrayEditor items={items} itemSchema={prop.options.itemSchema} onChange={newArray => handleObjectArrayChange(key, newArray)} />;
            default: return <p className="text-xs text-muted-foreground">Tipo de control no implementado: {prop.type}</p>;
        }
    };

    return (
        <div className="w-96 bg-card border-l overflow-y-auto">
            <div className="p-4 border-b sticky top-0 bg-card/80 backdrop-blur-sm z-10"><h3 className="font-bold">Propiedades de: <span className="text-primary capitalize">{activeBlock.type}</span></h3></div>
            <div className="p-4 space-y-4">
                {Object.entries(activeBlock.props).map(([key, prop]) => (
                    <div key={key}>
                        <label className="block text-sm font-medium text-muted-foreground mb-1">{prop.label}</label>
                        {renderPropControl(key, prop)}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PropertiesPanel;
