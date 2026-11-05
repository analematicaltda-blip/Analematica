import React, { useState } from 'react';
import { Playbook } from '../types';
import { 
    ClipboardListIcon, SendGridIcon, TwilioIcon, ReactIcon, PostgresIcon, 
    XIcon, FacebookIcon, TikTokIcon, YouTubeIcon, GoogleIcon 
} from './icons';

// MOCK DATA
const initialPlaybook: Playbook = {
    title: 'Playbook de Crecimiento Estándar',
    macro_flow: ['Captura', 'Segmentación', 'Nutrición', 'Clasificación', 'Embudo', 'Venta', 'Postventa', 'Fidelización', 'Reactivación', 'Análisis IA', 'Mejora'],
    sections: [
        { title: '1. Captura y Entrada de Leads', content: "Canales: Formularios web, Meta Ads, TikTok Ads, Chatbots, CSV.\nAutomatización: Asignar a segmento 'Nuevos Leads', enviar email de bienvenida, notificar a vendedor." },
        { title: '2. Nutrición y Seguimiento', content: "Workflow multicanal: Email (Día 0), WhatsApp (Día 1), SMS (Día 7 si no hay interacción). Usa IA para personalizar mensajes." },
        { title: '3. Clasificación de Leads (Scoring)', content: "Puntuación automática basada en interacciones (apertura de correos, clics, visitas). Clasifica en 'Caliente', 'Tibio', 'Frío'." },
        { title: '4. Embudo de Ventas Automatizado', content: "Cada cliente gestiona su propio embudo visual. Automatizaciones por etapa (ej: al mover a 'Negociación', notificar al supervisor)." },
        { title: '5. Publicación Social Automatizada', content: "Envío simultáneo a Facebook, Instagram, X, TikTok, etc. IA recomienda horarios y formatos." },
        { title: '6. Retención y Postventa', content: "Trigger 'Lead convertido en cliente'. Acciones: Email de agradecimiento, crear ticket de seguimiento, activar flujo de fidelización." },
        { title: '7. Reactivación y Remarketing', content: "Trigger 'Inactivo por 30 días'. Acciones: Email con oferta, WhatsApp recordatorio, retargeting en Meta Ads." },
        { title: '8. Analítica y Optimización', content: "Métricas automáticas: Tasa de apertura, conversión por canal, ROI. IA predice leads con mayor probabilidad de compra." }
    ],
    tech_stack: [
        { name: 'Envío de correos', tool: 'SendGrid', icon: SendGridIcon },
        { name: 'WhatsApp/SMS', tool: 'Twilio', icon: TwilioIcon },
        { name: 'Redes Sociales', tool: 'Meta API, etc.', icon: FacebookIcon },
        { name: 'IA / Contenido', tool: 'Gemini API', icon: GoogleIcon },
        { name: 'Frontend', tool: 'React', icon: ReactIcon },
        { name: 'Base de Datos', tool: 'PostgreSQL', icon: PostgresIcon }
    ]
};

const LevelPlaybooks: React.FC = () => {
    const [playbook, setPlaybook] = useState(initialPlaybook);
    const [isEditing, setIsEditing] = useState(false);

    const handleSectionChange = (index: number, content: string) => {
        const newSections = [...playbook.sections];
        // FIX: Added non-null assertion as TypeScript couldn't infer that `newSections[index]` would always exist,
        // even though the logic guarantees it. This resolves the potential "undefined" error.
        newSections[index]!.content = content;
        setPlaybook({ ...playbook, sections: newSections });
    };

    return (
        <div className="p-8 h-full overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-foreground flex items-center">
                    <ClipboardListIcon className="w-8 h-8 mr-3 text-primary"/>
                    Arquitecto de Playbooks
                </h2>
                <button 
                    onClick={() => setIsEditing(!isEditing)} 
                    className={`px-4 py-2 rounded-md font-semibold text-white ${isEditing ? 'bg-destructive' : 'bg-primary'}`}
                >
                    {isEditing ? 'Finalizar Edición' : 'Editar Playbook'}
                </button>
            </div>

            {/* Macro Flow Diagram */}
            <div className="mb-8">
                <h3 className="text-xl font-bold mb-4">Flujo Completo del Cliente (Vista Macro)</h3>
                <div className="flex flex-wrap gap-2 items-center text-sm">
                    {playbook.macro_flow.map((step, index) => (
                        <React.Fragment key={step}>
                            <span className="bg-muted px-3 py-1 rounded-full text-muted-foreground">{step}</span>
                            {index < playbook.macro_flow.length - 1 && <span className="text-muted-foreground">&rarr;</span>}
                        </React.Fragment>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    {playbook.sections.map((section, index) => (
                        <div key={index} className="bg-card p-6 rounded-lg shadow-lg border">
                            <h4 className="text-lg font-bold text-primary mb-2">{section.title}</h4>
                            {isEditing ? (
                                <textarea 
                                    value={section.content}
                                    onChange={(e) => handleSectionChange(index, e.target.value)}
                                    className="w-full h-32 bg-input p-2 rounded border border-primary/50 text-foreground"
                                />
                            ) : (
                                <p className="text-foreground whitespace-pre-wrap">{section.content}</p>
                            )}
                        </div>
                    ))}
                </div>

                {/* Tech Stack Sidebar */}
                <div className="space-y-6">
                    <div className="bg-card p-6 rounded-lg shadow-lg border">
                        <h4 className="text-lg font-bold text-primary mb-4">Arquitectura Tecnológica</h4>
                        <div className="grid grid-cols-2 gap-4">
                            {playbook.tech_stack.map((tech, index) => (
                                <div key={index} className="bg-muted p-3 rounded-md text-center">
                                    <tech.icon className="w-8 h-8 mx-auto mb-2 text-foreground" />
                                    <p className="text-xs font-semibold">{tech.name}</p>
                                    <p className="text-xs text-muted-foreground">{tech.tool}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                     <div className="bg-card p-6 rounded-lg shadow-lg border">
                        <h4 className="text-lg font-bold text-primary mb-4">Gestión Multi-Tenant (SaaS)</h4>
                        <p className="text-sm text-foreground">Cada cliente del sistema tiene su propio panel aislado con datos, campañas y embudos. El administrador general puede gestionar suscriptores, monitorear el uso y ver reportes globales.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LevelPlaybooks;
