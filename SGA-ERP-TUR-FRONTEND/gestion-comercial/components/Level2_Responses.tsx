
import React, { useState, useEffect } from 'react';
import { Opportunity, PipelineStage } from '../types/sales';
import { getOpportunities, moveOpportunity } from '../services/sales';
import { PermissionGuard, usePermissions } from '@/ui/guards/PermissionGuard';
import { auditLogger } from '@/services/auditLogger';
import {
    TrendingUpIcon, EuroIcon, CheckCircleIcon, UsersIcon, ClipboardListIcon,
    PipelineIcon, DashboardIcon, PlusIcon, SearchIcon, PhoneIcon, MailIcon, 
    BriefcaseIcon, XMarkIcon, AlertTriangleIcon, LinkedInIcon, CalendarPlusIcon, 
    MessageIcon, TargetIcon, FormIcon, SupportIcon, BookOpenIcon, 
    ChatBubbleLeftRightIcon, KanbanIcon, ListIcon, TicketIcon, HourglassIcon, 
    PaperAirplaneIcon, ArchiveBoxIcon, GoogleIcon, PinterestIcon, SnapchatIcon, 
    WhatsAppIcon, TelegramIcon, ZoomIcon, TeamsIcon, SmsIcon, TwitchIcon, 
    FacebookIcon, InstagramIcon, TikTokIcon, YouTubeIcon, XIcon, StarIcon, 
    InvoiceIcon, SapIcon, QuickbooksIcon, ShopifyIcon, ChevronRightIcon,
    ContactsIcon
} from './icons';

// --- STAGES CONFIG ---
const pipelineStages: { id: PipelineStage, title: string }[] = [ { id: 'new', title: 'Nuevos Leads' }, { id: 'contacted', title: 'Contactados' }, { id: 'proposal', title: 'Propuesta Enviada' }, { id: 'negotiation', title: 'Negociación' }, { id: 'won', title: 'Ganado' }, { id: 'lost', title: 'Perdido' }];

const PipelineView: React.FC<{ opportunities: Opportunity[]; setOpportunities: React.Dispatch<React.SetStateAction<Opportunity[]>>; onSelectOpportunity: (opportunity: Opportunity) => void; selectedId: number | null; }> = ({ opportunities, setOpportunities, onSelectOpportunity, selectedId }) => {
    const handleDragStart = (e: React.DragEvent<HTMLDivElement>, opportunityId: number) => {
        e.dataTransfer.setData('opportunityId', opportunityId.toString());
    };
    const { isReadOnly, role } = usePermissions();

    const handleDrop = async (e: React.DragEvent<HTMLDivElement>, stageId: PipelineStage) => {
        e.preventDefault();
        if (isReadOnly) {
            auditLogger.log({
                type: 'ACTION_DENIED',
                view: 'Sales CRM',
                action: 'Move Opportunity',
                userRole: role,
                status: 'ERROR'
            });
            return;
        }
        const opportunityId = parseInt(e.dataTransfer.getData('opportunityId'), 10);
        e.currentTarget.classList.remove('bg-accent');

        // Optimistic UI update
        const originalOpportunities = opportunities;
        setOpportunities(prev => prev.map(o => o.id === opportunityId ? { ...o, stage: stageId, last_updated: new Date().toISOString() } : o));

        try {
            await moveOpportunity(opportunityId, stageId);
            // On success, the state is already updated. We could refetch or trust the optimistic update.
        } catch (error) {
            console.error("Failed to move opportunity:", error);
            // If the API call fails, revert the change
            setOpportunities(originalOpportunities);
        }
    };
    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.currentTarget.classList.add('bg-accent');
    };
    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.currentTarget.classList.remove('bg-accent');
    };
    return (
        <div className="flex-1 p-8 overflow-x-auto">
            <div className="flex space-x-6 min-w-max h-full">
                {pipelineStages.map(stage => {
                    const opportunitiesInStage = opportunities.filter(o => o.stage === stage.id);
                    const stageValue = opportunitiesInStage.reduce((sum, o) => sum + o.value, 0);
                    return (
                        <div key={stage.id} className="w-80 bg-secondary rounded-xl flex flex-col h-full" onDrop={(e) => handleDrop(e, stage.id)} onDragOver={handleDragOver} onDragLeave={handleDragLeave}>
                            <div className={`p-4 border-b`}>
                                <h4 className="font-bold text-foreground flex justify-between items-center">
                                    <span>{stage.title}</span>
                                    <span className="text-sm font-normal text-muted-foreground">{opportunitiesInStage.length}</span>
                                </h4>
                                <p className="text-sm text-muted-foreground">€{stageValue.toLocaleString()}</p>
                            </div>
                            <div className="p-2 space-y-2 overflow-y-auto flex-1">
                                {opportunitiesInStage.map(opportunity => (
                                    <div key={opportunity.id} draggable onDragStart={(e) => handleDragStart(e, opportunity.id)}>
                                        <OpportunityCard
                                            opportunity={opportunity}
                                            onSelect={() => onSelectOpportunity(opportunity)}
                                            isSelected={selectedId === opportunity.id}
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
const OpportunityCard: React.FC<{ opportunity: Opportunity; onSelect: () => void; isSelected?: boolean }> = ({ opportunity, onSelect, isSelected }) => {
    // const seller = sellers.find(s => s.id === opportunity.assignedTo); // Backend doesn't support this yet
    const daysSinceUpdate = Math.floor((new Date().getTime() - new Date(opportunity.last_updated || new Date()).getTime()) / (1000 * 60 * 60 * 24));
    const isInactive = daysSinceUpdate > 7;
    return (
        <div className={`bg-card p-3 rounded-lg shadow-md cursor-pointer border transition-all group ${isSelected ? 'border-primary ring-2 ring-primary/20' : 'border-transparent hover:border-primary/50'}`} onClick={onSelect} >
            <div className="flex justify-between items-start">
                <p className="font-bold text-foreground text-sm group-hover:text-primary transition-colors">{opportunity.name}</p>
                 {/* Priority indicator removed as it's not in the backend model */}
            </div>
            <p className="text-xs text-muted-foreground truncate">{opportunity.company_name}</p>
            <div className="flex justify-between items-end mt-3">
                <div className="flex flex-col">
                    <span className="text-sm font-semibold text-foreground">€{opportunity.value.toLocaleString()}</span>
                    <div className="flex items-center space-x-1 mt-1">
                        {isInactive && <AlertTriangleIcon className="w-4 h-4 text-yellow-400" title={`Inactivo por ${daysSinceUpdate} días`} />}
                        {/* Tags removed as they are not in the backend model */}
                    </div>
                </div>
                {/* Seller avatar removed */}
            </div>
        </div>
    );
};

const OpportunityDetail: React.FC<{ opportunity: Opportunity; onClose: () => void; onWon: (id: number) => void }> = ({ opportunity, onClose, onWon }) => {
    const [note, setNote] = useState('');
    const [history, setHistory] = useState([
        { id: 1, type: 'status', text: 'Lead creado automáticamente desde Funnel Ecohotel.', date: '2024-05-10 10:00' },
        { id: 2, type: 'call', text: 'Llamada de primer contacto. Interesado en paquete premium.', date: '2024-05-12 14:30' },
        { id: 3, type: 'note', text: 'Solicitó cotización detallada por email.', date: '2024-05-15 09:15' },
    ]);

    const addNote = () => {
        if (!note.trim()) return;
        setHistory(prev => [{ id: Date.now(), type: 'note', text: note, date: new Date().toLocaleString() }, ...prev]);
        setNote('');
    };

    return (
        <div className="w-96 bg-card border-l flex flex-col h-full shadow-2xl animate-in slide-in-from-right duration-300">
            <div className="p-6 border-b flex justify-between items-center bg-slate-50 dark:bg-black/20">
                <h3 className="font-black uppercase tracking-tighter text-lg">Expediente CRM</h3>
                <button onClick={onClose} className="p-1 hover:bg-slate-200 dark:hover:bg-white/10 rounded-full"><XMarkIcon className="w-6 h-6"/></button>
            </div>
            <div className="p-6 space-y-6 flex-1 overflow-y-auto no-scrollbar">
                <div>
                    <h4 className="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-2">Información de Lead</h4>
                    <div className="bg-slate-100 dark:bg-white/5 p-4 rounded-xl">
                        <p className="font-bold text-lg leading-tight">{opportunity.name}</p>
                        <p className="text-sm text-slate-500">{opportunity.company_name}</p>
                        <div className="mt-4 flex items-center gap-2">
                             <div className="bg-brand/10 text-brand px-2 py-1 rounded-md text-[10px] font-black uppercase">{opportunity.stage}</div>
                             <div className="font-black text-slate-900 dark:text-white">€{opportunity.value.toLocaleString()}</div>
                        </div>
                    </div>
                </div>

                <div className="flex gap-2">
                    <button className="flex-1 bg-brand text-white text-xs font-black py-2 rounded-lg flex items-center justify-center gap-1"><PhoneIcon className="w-3 h-3"/> Llamar</button>
                    <button className="flex-1 bg-slate-200 dark:bg-white/10 text-xs font-black py-2 rounded-lg flex items-center justify-center gap-1"><MailIcon className="w-3 h-3"/> Email</button>
                    <button className="flex-1 bg-emerald-600 text-white text-xs font-black py-2 rounded-lg flex items-center justify-center gap-1"><WhatsAppIcon className="w-3 h-3"/> Chat</button>
                </div>

                {opportunity.stage === 'won' && (
                    <div className="bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 p-4 rounded-xl animate-pulse">
 
                        <div className="flex justify-between items-start mb-2">
                           <p className="text-xs font-bold text-emerald-800 dark:text-emerald-400 italic">Oportunidad Ganada: Lista para Facturación</p>
                           <span className="text-[8px] bg-emerald-100 text-emerald-700 px-1 rounded font-black">BACKEND REAL</span>
                        </div>
                        <PermissionGuard deniedRoles={['Auditor', 'Observador']} fallback={<p className="text-[10px] text-slate-400">Solo lectura: No se puede facturar desde este perfil.</p>}>
                            <button
                                onClick={() => onWon(opportunity.id)}
                                className="w-full bg-emerald-600 text-white font-black text-xs py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-emerald-700 transition-colors"
                            >
                                <InvoiceIcon className="w-4 h-4" /> GENERAR FACTURA ERP
                            </button>
                        </PermissionGuard>
 
                    </div>
                )}

                <div>
                    <h4 className="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-2">Bitácora de Seguimiento</h4>
                    <div className="space-y-4">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={note}
                                onChange={e => setNote(e.target.value)}
                                placeholder="Agregar nota de seguimiento..."
                                className="flex-1 bg-slate-100 dark:bg-white/5 border-none rounded-lg text-xs p-3 focus:ring-1 ring-brand"
                            />
                            <button onClick={addNote} className="bg-slate-900 text-white px-4 rounded-lg"><PlusIcon className="w-4 h-4"/></button>
                        </div>
                        <div className="space-y-3 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-px before:bg-slate-200 dark:before:bg-white/10">
                            {history.map(item => (
                                <div key={item.id} className="relative pl-8">
                                    <div className="absolute left-1.5 top-1.5 w-3 h-3 rounded-full border-2 border-white dark:border-slate-900 bg-brand"></div>
                                    <p className="text-[10px] text-slate-400 font-bold mb-1 uppercase tracking-wider">{item.date}</p>
                                    <p className="text-xs text-slate-700 dark:text-slate-300 bg-white dark:bg-white/5 p-3 rounded-xl border border-slate-100 dark:border-white/5">{item.text}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- MAIN COMPONENT ---
const Level2_Responses: React.FC = () => {
    type MainView = 'pipeline';
    const [view, setView] = useState<MainView>('pipeline');
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [noData, setNoData] = useState<boolean>(false);

    useEffect(() => {
        const fetchOpportunities = async () => {
            try {
                const { data, meta } = await getOpportunities();
                if (meta?.reason === 'NO_DATA' || (data && data.length === 0)) {
                    setNoData(true);
                    setOpportunities([]);
                } else {
                    setNoData(false);
                    setOpportunities(data);
                }
            } catch (error) {
                console.error("Failed to fetch opportunities:", error);
                setError("Failed to fetch opportunities. Please try again later.");
            }
        };

        fetchOpportunities();
    }, []);
    
    const renderContent = () => {
        if (error) {
            return <div className="p-8 text-destructive">{error}</div>;
        }
        if (noData) {
            return (
                <div className="flex-1 flex items-center justify-center text-center text-muted-foreground p-8">
                    <div>
                        <TrendingUpIcon className="w-16 h-16 mx-auto mb-4"/>
                        <h2 className="text-2xl font-bold">No Opportunities Found</h2>
                        <p className="max-w-md mt-2">Get started by creating a new opportunity.</p>
                        <button className="mt-6 flex items-center space-x-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
                            <PlusIcon className="w-5 h-5" />
                            <span>Crear Oportunidad</span>
                        </button>
                    </div>
                </div>
            );
        }
        switch(view) {
            case 'pipeline': return <PipelineView opportunities={opportunities} setOpportunities={setOpportunities} onSelectOpportunity={setSelectedOpportunity} selectedId={selectedOpportunity?.id || null} />;
            default: return <PipelineView opportunities={opportunities} setOpportunities={setOpportunities} onSelectOpportunity={setSelectedOpportunity} selectedId={selectedOpportunity?.id || null} />;
        }
    };

    const handleWon = (id: number) => {
        alert(`Iniciando flujo de Facturación ERP para Oportunidad #${id}. Se generará Factura en estado BORRADOR con impacto en Libro Diario.`);
        // Aquí se llamaría al servicio de facturación
    };

    return (
         <div className="h-full flex text-foreground overflow-hidden">
            {/* Main Content Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <div className="p-4 border-b flex justify-between items-center h-[65px] flex-shrink-0">
                     <div></div>
                    <div className="flex items-center space-x-4">
                        <div className="relative flex items-center">
                            <SearchIcon className="w-5 h-5 absolute left-3 text-muted-foreground" />
                            <input type="text" placeholder="Buscar..." className="bg-input rounded-md py-2 pl-10 pr-4 w-64 text-foreground placeholder-muted-foreground" />
                        </div>
                        <PermissionGuard deniedRoles={['Auditor', 'Observador']}>
                            <button className="flex items-center space-x-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors">
                                <PlusIcon className="w-5 h-5"/>
                                <span className="font-semibold">Añadir Lead</span>
                            </button>
                        </PermissionGuard>
                    </div>
                </div>
                <main className="flex-1 overflow-auto bg-slate-100 dark:bg-black/40">
                    {renderContent()}
                </main>
            </div>
            {selectedOpportunity && (
                <OpportunityDetail
                    opportunity={selectedOpportunity}
                    onClose={() => setSelectedOpportunity(null)}
                    onWon={handleWon}
                />
            )}
        </div>
    );
};

export default Level2_Responses;
