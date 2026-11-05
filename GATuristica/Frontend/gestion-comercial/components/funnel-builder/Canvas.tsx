
import React, { useRef, useCallback } from 'react';
import { useDrag, useDrop, DropTargetMonitor } from 'react-dnd';
import { Block, BlockStyles } from '../../types';
import { useFunnelBuilder } from '../../context/FunnelBuilderContext';
import { ItemTypes, createDefaultBlock } from './data';
import * as Icons from '../icons';

const BlockRenderer: React.FC<{ block: Block }> = React.memo(({ block }) => {
    const { props, styles } = block;
    const getProp = (key: string, defaultValue: any = '') => props[key]?.value ?? defaultValue;
    const style: React.CSSProperties = {
        paddingTop: `${styles.padding.top}px`,
        paddingRight: `${styles.padding.right}px`,
        paddingBottom: `${styles.padding.bottom}px`,
        paddingLeft: `${styles.padding.left}px`,
        backgroundColor: styles.backgroundColor,
        color: styles.textColor,
        textAlign: styles.textAlign,
    };

    switch (block.type) {
        case 'hero':
            const bgImage = getProp('backgroundImage');
            const heroStyle: React.CSSProperties = { ...style, backgroundSize: 'cover', backgroundPosition: 'center', ...(bgImage && { backgroundImage: `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${bgImage})` }) };
            return <div className="relative flex items-center justify-center bg-no-repeat" style={heroStyle}>
                <div className="relative z-10 px-4">
                    <h1 className="text-5xl font-extrabold mb-4 drop-shadow-lg">{getProp('title')}</h1>
                    <p className="text-xl opacity-90 max-w-2xl mx-auto drop-shadow-md">{getProp('subtitle')}</p>
                    <a href={getProp('ctaUrl')} className="mt-8 inline-block bg-primary text-primary-foreground px-8 py-3 rounded-lg font-bold text-lg hover:bg-primary/90 transition-transform hover:scale-105">{getProp('ctaText')}</a>
                </div></div>;
        case 'services':
            const items = getProp('items', []) as {id: string, icon: string, title: string, description: string}[];
            return <div style={style}><div className="container mx-auto px-4"><h2 className="text-4xl font-bold text-center mb-16">{getProp('title')}</h2><div className="grid md:grid-cols-3 gap-12">{items.map((service) => {
                const Icon = (Icons as any)[service.icon as keyof typeof Icons] || Icons.SparklesIcon;
                return <div key={service.id} className="text-center p-6 bg-card rounded-xl shadow-md border"><div className="inline-block p-4 bg-primary/10 rounded-full mb-4"><Icon className="w-10 h-10 text-primary" /></div><h3 className="text-2xl font-bold mb-3">{service.title}</h3><p className="text-muted-foreground leading-relaxed">{service.description}</p></div>
            })}</div></div></div>;
        case 'gallery':
            const images = getProp('images', []) as string[];
            return <div style={style}><div className="container mx-auto px-4"><h2 className="text-4xl font-bold text-center mb-16">{getProp('title')}</h2><div className="grid grid-cols-2 md:grid-cols-3 gap-4">{images.map((src, i) => <div key={i} className="overflow-hidden rounded-lg shadow-lg group/gallery"><img src={src} alt={`Gallery image ${i + 1}`} className="w-full h-full object-cover aspect-square transition-transform duration-300 group-hover/gallery:scale-110" /></div>)}</div></div></div>;
        case 'testimonials':
            const testimonials = getProp('testimonials', []) as { id: string, avatarUrl: string, name: string, role: string, quote: string }[];
            return <div style={style}><div className="container mx-auto px-4"><h2 className="text-4xl font-bold text-center mb-16">{getProp('title')}</h2><div className="grid md:grid-cols-3 gap-8">{testimonials.map((testimonial) => <div key={testimonial.id} className="bg-card p-6 rounded-xl shadow-lg border flex flex-col"><p className="text-muted-foreground mb-4 flex-grow">"{testimonial.quote}"</p><div className="flex items-center mt-auto"><img src={testimonial.avatarUrl} alt={testimonial.name} className="w-12 h-12 rounded-full mr-4 object-cover" /><div><p className="font-bold">{testimonial.name}</p><p className="text-sm text-muted-foreground">{testimonial.role}</p></div></div></div>)}</div></div></div>;
        default:
            return <div className="container mx-auto p-8 my-4 bg-card border border-dashed"><h3 className="font-bold text-lg capitalize">{block.type} Block</h3><p className="text-sm text-muted-foreground">{JSON.stringify(block.props, null, 2)}</p></div>;
    }
});

const BlockActionsToolbar: React.FC<{ block: Block; onDuplicate: () => void; onDelete: () => void; dragHandle: any; }> = ({ block, onDuplicate, onDelete, dragHandle }) => {
    return (
        <div className="absolute top-2 right-2 flex items-center gap-1 bg-card/80 backdrop-blur-sm p-1 rounded-lg shadow-lg z-20 opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="bg-primary text-primary-foreground px-2 py-1 text-xs rounded font-bold capitalize">{block.type}</div>
            <button onClick={(e) => { e.stopPropagation(); onDuplicate(); }} className="p-1.5 bg-card rounded text-foreground hover:bg-accent" title="Duplicar"><Icons.DuplicateIcon className="w-4 h-4" /></button>
            <button onClick={(e) => { e.stopPropagation(); onDelete(); }} className="p-1.5 bg-destructive text-destructive-foreground rounded hover:bg-destructive/80" title="Eliminar"><Icons.TrashIcon className="w-4 h-4" /></button>
            <div ref={dragHandle} className="p-1.5 bg-card rounded text-foreground hover:bg-accent cursor-move" title="Mover"><Icons.GripVerticalIcon className="w-4 h-4" /></div>
        </div>
    );
};

const CanvasBlock: React.FC<{ block: Block; index: number; moveBlock: (d: number, h: number) => void; }> = ({ block, index, moveBlock }) => {
    const { activeBlockId, setActiveBlockId, updateData, activePage } = useFunnelBuilder();
    const isSelected = activeBlockId === block.id;

    const ref = useRef<HTMLDivElement>(null);
    const [, drop] = useDrop({ 
        accept: [ItemTypes.BLOCK, ItemTypes.LIBRARY_BLOCK], 
        hover(item: { index?: number; type: string }, m: DropTargetMonitor) { 
            if (!ref.current) return;
            if (item.type === ItemTypes.LIBRARY_BLOCK) return;

            const dragIndex = item.index!; 
            const hoverIndex = index; 
            if (dragIndex === hoverIndex) return; 

            const hoverBoundingRect = ref.current.getBoundingClientRect(); 
            const hoverMiddleY = (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2; 
            const clientOffset = m.getClientOffset(); 
            if (!clientOffset) return; 
            const hoverClientY = clientOffset.y - hoverBoundingRect.top; 
            if (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) return; 
            if (dragIndex > hoverIndex && hoverClientY > hoverMiddleY) return; 
            
            moveBlock(dragIndex, hoverIndex); 
            item.index = hoverIndex; 
        },
        drop: (item: { type: string, index?: number }) => {
            if (item.type === ItemTypes.LIBRARY_BLOCK) {
                return { droppedAt: index };
            }
        }
    });

    const [{ isDragging }, drag, dragPreview] = useDrag({ 
        type: ItemTypes.BLOCK, 
        item: () => ({ id: block.id, index }), 
        collect: (m) => ({ isDragging: m.isDragging() }), 
    });
    
    drop(ref);

    const onDuplicate = (id: string) => updateData(d => {
        const p = d.landingPages.flatMap(lp => lp.funnels).flatMap(f => f.pages).find(pg => pg.id === activePage?.id); 
        if(p){ 
            const btd = p.blocks.find(b => b.id === id); 
            if(!btd) return; 
            const nb = {...btd, id: `blk-${Date.now()}`}; 
            const i = p.blocks.findIndex(b => b.id === id); 
            p.blocks.splice(i + 1, 0, nb); 
            p.blocks = p.blocks.map((b, i) => ({...b, order: i + 1}));
        }
    });

    const onDelete = (id: string) => updateData(d => { 
        const p = d.landingPages.flatMap(lp => lp.funnels).flatMap(f => f.pages).find(pg => pg.id === activePage?.id); 
        if(p) p.blocks = p.blocks.filter(b => b.id !== id);
    });

    return (
        // FIX: Added 'as any' to the dragPreview ref to resolve a type mismatch issue
        // between the react-dnd drag connector and the expected ref type for a DOM element.
        <div ref={dragPreview as any} style={{ opacity: isDragging ? 0.3 : 1 }}>
            <div ref={ref} className="relative group" onClick={() => setActiveBlockId(block.id)}>
                <div className={`absolute -inset-1 border-2 pointer-events-none transition-all z-10 rounded-lg ${isSelected ? 'border-primary shadow-2xl' : 'border-transparent group-hover:border-primary/50'}`}/>
                {isSelected && <BlockActionsToolbar block={block} onDuplicate={() => onDuplicate(block.id)} onDelete={() => onDelete(block.id)} dragHandle={drag} />}
                <BlockRenderer block={block} />
            </div>
        </div>
    );
};

const Canvas: React.FC = () => {
    const { activePage, updateData, activeBreakpoint } = useFunnelBuilder();
    
    const moveBlock = useCallback((dragIndex: number, hoverIndex: number) => {
        updateData(draft => {
            const page = draft.landingPages.flatMap(lp => lp.funnels).flatMap(f => f.pages).find(p => p.id === activePage?.id);
            if (page) {
                const newBlocks = [...page.blocks];
                const [draggedItem] = newBlocks.splice(dragIndex, 1);
                if (draggedItem) newBlocks.splice(hoverIndex, 0, draggedItem);
                page.blocks = newBlocks.map((b, i) => ({ ...b, order: i + 1 }));
            }
        });
    }, [activePage?.id, updateData]);
    
    const handleDropFromLibrary = useCallback((type: any, index: number) => {
        updateData(draft => {
            const page = draft.landingPages.flatMap(lp => lp.funnels).flatMap(f => f.pages).find(p => p.id === activePage?.id);
            if(page) {
                const newBlock = createDefaultBlock(type, 0);
                const newBlocks = [...page.blocks];
                newBlocks.splice(index, 0, newBlock);
                page.blocks = newBlocks.map((b, i) => ({ ...b, order: i + 1 }));
            }
        });
    }, [activePage?.id, updateData]);

    const [, drop] = useDrop(() => ({ 
        accept: ItemTypes.LIBRARY_BLOCK, 
        drop: (item: { type: string }, monitor) => { 
            const dropResult = monitor.getDropResult<{ droppedAt?: number }>();
            if (!monitor.didDrop() || dropResult?.droppedAt === undefined) {
                handleDropFromLibrary(item.type, activePage?.blocks.length || 0);
            } else if (dropResult.droppedAt !== undefined) {
                handleDropFromLibrary(item.type, dropResult.droppedAt);
            }
        } 
    }));

    const breakpointClasses = {
        desktop: 'w-full min-h-full',
        tablet: 'w-[768px] min-h-[1024px] shadow-2xl rounded-[24px] my-8 ring-8 ring-gray-800 bg-white',
        mobile: 'w-[375px] min-h-[667px] shadow-2xl rounded-[24px] my-8 ring-8 ring-gray-800 bg-white'
    };

    return (
        // FIX: Added 'as any' to the drop ref to resolve a type mismatch issue
        // between the react-dnd drop connector and the expected ref type for a DOM element.
        <div ref={drop as any} className="flex-1 overflow-y-auto bg-muted flex justify-center">
            <div className={`mx-auto transition-all duration-300 ease-in-out ${breakpointClasses[activeBreakpoint]}`}>
                <div className="overflow-y-auto h-full w-full bg-white">
                    {activePage?.blocks.sort((a,b) => a.order - b.order).map((block, index) => (
                        <CanvasBlock key={block.id} block={block} index={index} moveBlock={moveBlock} />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Canvas;
