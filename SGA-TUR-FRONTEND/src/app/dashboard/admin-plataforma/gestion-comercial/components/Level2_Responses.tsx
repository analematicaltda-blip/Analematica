
import React, { useState, useEffect } from 'react';
import { Opportunity, PipelineStage } from '../types/sales';
import { getOpportunities, moveOpportunity } from '../services/sales';
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

const PipelineView: React.FC<{ opportunities: Opportunity[]; setOpportunities: React.Dispatch<React.SetStateAction<Opportunity[]>>; onSelectOpportunity: (opportunity: Opportunity) => void; }> = ({ opportunities, setOpportunities, onSelectOpportunity }) => {
    const handleDragStart = (e: React.DragEvent<HTMLDivElement>, opportunityId: number) => {
        e.dataTransfer.setData('opportunityId', opportunityId.toString());
    };
    const handleDrop = async (e: React.DragEvent<HTMLDivElement>, stageId: PipelineStage) => {
        e.preventDefault();
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
                                        <OpportunityCard opportunity={opportunity} onSelect={() => onSelectOpportunity(opportunity)} />
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
const OpportunityCard: React.FC<{ opportunity: Opportunity; onSelect: () => void }> = ({ opportunity, onSelect }) => {
    // const seller = sellers.find(s => s.id === opportunity.assignedTo); // Backend doesn't support this yet
    const daysSinceUpdate = Math.floor((new Date().getTime() - new Date(opportunity.last_updated).getTime()) / (1000 * 60 * 60 * 24));
    const isInactive = daysSinceUpdate > 7;
    return (
        <div className="bg-card p-3 rounded-lg shadow-md cursor-pointer border border-transparent hover:border-primary hover:shadow-xl transition-all group" onClick={onSelect} >
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
            case 'pipeline': return <PipelineView opportunities={opportunities} setOpportunities={setOpportunities} onSelectOpportunity={setSelectedOpportunity} />;
            default: return <PipelineView opportunities={opportunities} setOpportunities={setOpportunities} onSelectOpportunity={setSelectedOpportunity} />;
        }
    };

    return (
         <div className="h-full flex text-foreground">
            {/* Main Content Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <div className="p-4 border-b flex justify-between items-center h-[65px] flex-shrink-0">
                     <div></div>
                    <div className="flex items-center space-x-4">
                        <div className="relative flex items-center">
                            <SearchIcon className="w-5 h-5 absolute left-3 text-muted-foreground" />
                            <input type="text" placeholder="Buscar..." className="bg-input rounded-md py-2 pl-10 pr-4 w-64 text-foreground placeholder-muted-foreground" />
                        </div>
                        <button className="flex items-center space-x-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors">
                            <PlusIcon className="w-5 h-5"/> 
                            <span className="font-semibold">Añadir Lead</span>
                        </button>
                    </div>
                </div>
                <main className="flex-1 overflow-auto">
                    {renderContent()}
                </main>
            </div>
        </div>
    );
};

export default Level2_Responses;
