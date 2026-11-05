
import React, { useState, useEffect } from 'react';
import { 
    AnalyticsIcon, MegaphoneIcon, MailIcon, SmsIcon, MmsIcon, WhatsAppIcon, 
    FacebookIcon, InstagramIcon, XIcon, TikTokIcon, YouTubeIcon, TwitchIcon, 
    TemplateIcon, SaveIcon, DuplicateIcon, CodeBracketIcon, PlusCircleIcon, SparklesIcon, XMarkIcon
} from './icons';
import { MarketingChannel, Campaign } from '../types'; // Tipos simplificados

interface Level1Props {
    authToken: string;
}

// Canales ahora se define como una constante estática, ya que no cambia.
const ALL_CHANNELS: MarketingChannel[] = [
    { id: 'email', name: 'Email', icon: MailIcon, status: 'connected', category: 'messaging' },
    { id: 'whatsapp', name: 'WhatsApp', icon: WhatsAppIcon, status: 'connected', category: 'messaging' },
    { id: 'sms', name: 'SMS', icon: SmsIcon, status: 'connected', category: 'messaging' },
    { id: 'facebook', name: 'Facebook', icon: FacebookIcon, status: 'connected', category: 'social' },
    { id: 'instagram', name: 'Instagram', icon: InstagramIcon, status: 'connected', category: 'social' },
];

const ChannelStatusBar = ({ channels }: { channels: MarketingChannel[] }) => (
    <div className="bg-card p-3 rounded-lg flex flex-wrap gap-x-4 gap-y-2 items-center mb-6 border shadow-sm">
        <div className="flex items-center gap-2">
            <h3 className="font-semibold text-muted-foreground whitespace-nowrap">Canales Conectados:</h3>
            <span className="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-bold uppercase tracking-tighter">Simulado – Backend Pendiente</span>
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-2 items-center">
            {channels.map(channel => (
                <div key={channel.id} className="group relative flex items-center space-x-1.5" title={channel.name}>
                    <channel.icon className={`w-5 h-5 ${channel.status === 'connected' ? 'text-foreground' : 'text-gray-600'}`} />
                    <div className={`w-2 h-2 ${channel.status === 'connected' ? 'bg-green-500' : 'bg-red-500'} rounded-full`} />
                </div>
            ))}
        </div>
    </div>
);

const CampaignCreator: React.FC<{ authToken: string; onCampaignCreated: (newCampaign: Campaign) => void; }> = ({ authToken, onCampaignCreated }) => {
    const [campaignName, setCampaignName] = useState('');
    const [selectedChannels, setSelectedChannels] = useState<Set<string>>(new Set(['email']));
    const [content, setContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChannelToggle = (id: string) => {
        setSelectedChannels(prev => {
            const newSelection = new Set(prev);
            if (newSelection.has(id)) newSelection.delete(id);
            else newSelection.add(id);
            return newSelection;
        });
    };

    const handleSubmit = async () => {
        if (!campaignName || selectedChannels.size === 0) {
            alert('Por favor, asigna un nombre y selecciona al menos un canal.');
            return;
        }
        setIsSubmitting(true);
        try {
            const response = await fetch('/api/marketing/campaigns/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    name: campaignName,
                    channels: Array.from(selectedChannels).map(ch => ({ channel_type: ch, is_active: true })),
                    content: { subject: `Asunto para ${campaignName}`, body_text: content }
                })
            });
            if (!response.ok) throw new Error('Failed to create campaign');
            const newCampaign = await response.json();
            onCampaignCreated(newCampaign);
            // Reset form
            setCampaignName('');
            setContent('');
            setSelectedChannels(new Set(['email']));
        } catch (error) {
            console.error("Error creating campaign:", error);
            alert("No se pudo crear la campaña.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="bg-card rounded-lg p-6 border shadow-md">
            <ChannelStatusBar channels={ALL_CHANNELS} />
            <div className="space-y-4">
                <div>
                    <h3 className="font-bold text-lg mb-2">Paso 1: Nombre de la Campaña</h3>
                    <input type="text" value={campaignName} onChange={e => setCampaignName(e.target.value)} placeholder="Ej. Lanzamiento de Verano" className="w-full bg-input border rounded-md p-2" />
                </div>
                <div>
                    <h3 className="font-bold text-lg mb-2">Paso 2: Selecciona Canales</h3>
                    <div className="flex flex-wrap gap-2">
                        {ALL_CHANNELS.map(channel => (
                            <label key={channel.id} className="flex items-center space-x-2 p-2 bg-background rounded-md cursor-pointer hover:bg-accent">
                                <input type="checkbox" checked={selectedChannels.has(channel.id)} onChange={() => handleChannelToggle(channel.id)} className="h-5 w-5 bg-input border-border rounded text-primary focus:ring-primary" />
                                <channel.icon className="w-5 h-5" />
                                <span>{channel.name}</span>
                            </label>
                        ))}
                    </div>
                </div>
                <div>
                    <h3 className="font-bold text-lg mb-2">Paso 3: Contenido</h3>
                    <textarea rows={6} value={content} onChange={e => setContent(e.target.value)} placeholder="Escribe el contenido principal de tu campaña..." className="w-full bg-input border rounded-md p-2" />
                </div>
            </div>
             <div className="flex justify-between items-center pt-6 border-t mt-6">
                <div className="text-xs text-amber-600 font-medium italic">
                    Nota: La ejecución real de envíos requiere integración de SADI/Gateways.
                </div>
                <button onClick={handleSubmit} disabled={isSubmitting} className="bg-green-600 text-white px-6 py-2 rounded-md hover:opacity-90 disabled:opacity-50">
                    {isSubmitting ? 'Creando (Modo Demo)...' : 'Crear Campaña'}
                </button>
            </div>
        </div>
    );
};

const CampaignList: React.FC<{ campaigns: Campaign[] }> = ({ campaigns }) => (
    <div className="bg-card rounded-xl border shadow-md mt-8">
        <h4 className="p-4 font-bold text-foreground">Campañas Creadas</h4>
        <table className="w-full text-left">
            <thead className="border-b border-t text-sm text-muted-foreground">
                <tr><th className="p-4">Nombre</th><th className="p-4">Estado</th><th className="p-4">Fecha Creación</th></tr>
            </thead>
            <tbody>
                {campaigns.length === 0 && (
                    <tr><td colSpan={3} className="text-center p-8 text-muted-foreground">No hay campañas. ¡Crea una para empezar!</td></tr>
                )}
                {campaigns.map(c => (
                    <tr key={c.id} className="border-b">
                        <td className="p-4 font-semibold">{c.name}</td>
                        <td className="p-4 capitalize">{c.status}</td>
                        <td className="p-4">{new Date(c.created_at).toLocaleDateString()}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
);

const Level1_Communication: React.FC<Level1Props> = ({ authToken }) => {
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchCampaigns = async () => {
            try {
                const response = await fetch('/api/marketing/campaigns/', {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                if (!response.ok) throw new Error('Failed to fetch campaigns');
                const data = await response.json();
                setCampaigns(data);
            } catch (error) {
                console.error("Error fetching campaigns:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchCampaigns();
    }, [authToken]);

    const handleCampaignCreated = (newCampaign: Campaign) => {
        setCampaigns(prev => [newCampaign, ...prev]);
    };

    if(isLoading) return <div className="p-8">Cargando campañas...</div>;

    return (
        <div className="p-8 h-full overflow-y-auto">
            <div className="flex space-x-2 border-b mb-6">
                <button className="flex items-center space-x-2 py-2 px-4 font-medium border-b-2 border-primary text-foreground">
                    <MegaphoneIcon className="w-5 h-5" /><span>Campañas</span>
                </button>
                 <button className="flex items-center space-x-2 py-2 px-4 font-medium text-muted-foreground hover:text-foreground">
                    <AnalyticsIcon className="w-5 h-5" /><span>Analíticas (Próximamente)</span>
                </button>
            </div>
            
            <CampaignCreator authToken={authToken} onCampaignCreated={handleCampaignCreated} />
            <CampaignList campaigns={campaigns} />
        </div>
    );
};

export default Level1_Communication;
