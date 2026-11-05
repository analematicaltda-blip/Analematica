import React, { useState } from 'react';
import { 
    PaintBrushIcon, TemplateIcon, FormIcon, GlobeAltIcon, TrendingUpIcon, 
    ChartBarIcon, BeakerIcon, UserCircleIcon, LinkIcon, CreditCardIcon, 
    WorkflowIcon, UsersIcon, ShieldCheckIcon, ServerIcon, MegaphoneIcon, 
    CodeBracketIcon, SparklesIcon, CogIcon
} from './icons';

const adminSections = [
  { id: 'editor', title: '1. Editor Visual (UX/UI)', icon: PaintBrushIcon, description: "Gestiona la configuración del editor visual, las guías de diseño y las opciones de previsualización." },
  { id: 'blocks', title: '2. Bloques y Componentes', icon: TemplateIcon, description: "Administra la biblioteca de bloques pre-construidos, componentes dinámicos y bloques reutilizables." },
  { id: 'forms', title: '3. Formularios y Captura de Datos', icon: FormIcon, description: "Configura campos de formulario, validaciones, integraciones y reglas de consentimiento (GDPR/CCPA)." },
  { id: 'templates', title: '4. Plantillas', icon: TemplateIcon, description: "Gestiona la biblioteca de plantillas, categorías y el marketplace interno." },
  { id: 'publishing', title: '5. Publicación y Dominios', icon: GlobeAltIcon, description: "Controla la configuración de dominios personalizados, SSL, CDN y opciones de exportación." },
  { id: 'performance', title: '6. Rendimiento y Optimización', icon: TrendingUpIcon, description: "Define las reglas de optimización de imágenes, caché, minificación de assets y monitoreo de rendimiento." },
  { id: 'seo', title: '7. SEO, Analítica y Tracking', icon: ChartBarIcon, description: "Configura integraciones de analítica (GA4, GTM), sitemaps, y meta tags por defecto." },
  { id: 'ab_testing', title: '8. A/B Testing y Experimentación', icon: BeakerIcon, description: "Gestiona la configuración del motor de A/B testing, cálculo de significancia y distribución de tráfico." },
  { id: 'personalization', title: '9. Personalización', icon: UserCircleIcon, description: "Define reglas de contenido dinámico basadas en geolocalización, parámetros de URL y segmentos de usuario." },
  { id: 'integrations', title: '10. Integraciones y Automatización', icon: LinkIcon, description: "Administra las integraciones nativas (CRMs, Email, Pagos) y conectores no-code como Zapier." },
  { id: 'ecommerce', title: '11. E-commerce y Pagos', icon: CreditCardIcon, description: "Configura pasarelas de pago (Stripe, PayPal), gestión de cupones y webhooks de pago." },
  { id: 'workflows', title: '12. Workflows Integrados', icon: WorkflowIcon, description: "Crea y gestiona plantillas de workflows de automatización (triggers y acciones) disponibles para los clientes." },
  { id: 'collaboration', title: '13. Colaboración y Flujo Editorial', icon: UsersIcon, description: "Define los roles de usuario por defecto, flujos de aprobación y notificaciones de colaboración." },
  { id: 'security', title: '14. Seguridad y Cumplimiento', icon: ShieldCheckIcon, description: "Gestiona la configuración de seguridad global, autenticación (SSO, 2FA), y logs de auditoría." },
  { id: 'operations', title: '15. Operaciones y Monitoreo', icon: ServerIcon, description: "Accede al panel de superadmin para monitorear el uso por tenant, salud del sistema y logs." },
  { id: 'monetization', title: '17. Monetización y Gestión Comercial', icon: MegaphoneIcon, description: 'Configura planes, precios, pruebas gratuitas y cupones promocionales para los clientes del SaaS.'},
  { id: 'api', title: '20. APIs y Extensibilidad', icon: CodeBracketIcon, description: 'Gestiona el acceso a la API, webhooks, y el sistema de plugins para extender la plataforma.'},
  { id: 'ai_features', title: '24. Funciones de IA', icon: SparklesIcon, description: 'Configura y gestiona las integraciones de IA para generación de texto, imágenes y personalización.'}
];


const AdminSectionContent: React.FC<{ section: typeof adminSections[0] }> = ({ section }) => {
    return (
        <div className="bg-card p-8 rounded-lg shadow-lg border h-full">
            <div className="flex items-center space-x-4 mb-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                    <section.icon className="w-8 h-8 text-primary" />
                </div>
                <div>
                    <h2 className="text-3xl font-bold text-foreground">{section.title}</h2>
                </div>
            </div>
            <p className="text-muted-foreground mt-2">{section.description}</p>
            <div className="mt-8 border-t pt-6">
                <h3 className="text-xl font-semibold mb-4">Configuraciones</h3>
                <div className="text-center text-muted-foreground bg-muted p-10 rounded-lg">
                    <p>Las opciones de configuración para esta sección aparecerán aquí.</p>
                </div>
            </div>
        </div>
    );
};

const LevelAdminPanel: React.FC = () => {
    // FIX: Updated the default active section to use a valid `id` from the new `adminSections` array.
    // The previous component had a different structure, and this change prevents a runtime error where
    // `activeSection` could be undefined.
    const [activeSectionId, setActiveSectionId] = useState(adminSections[0]?.id);
    const activeSection = adminSections.find(s => s.id === activeSectionId) || adminSections[0];

    return (
        <div className="h-full flex text-foreground bg-background">
            {/* Sidebar for Admin Sections */}
            <aside className="w-80 bg-card p-4 border-r flex flex-col h-full overflow-y-auto">
                <h2 className="text-xl font-bold p-2 mb-4">Panel de Capas</h2>
                <nav className="flex-1">
                    <ul className="space-y-1">
                        {adminSections.map(section => (
                            <li key={section.id}>
                                <button
                                    onClick={() => setActiveSectionId(section.id)}
                                    className={`w-full flex items-center space-x-3 p-2.5 rounded-lg text-left transition-colors duration-200 ${
                                        activeSectionId === section.id
                                            ? 'bg-primary/10 text-primary font-semibold'
                                            : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                                    }`}
                                >
                                    <section.icon className="w-5 h-5 flex-shrink-0" />
                                    <span className="text-sm">{section.title}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </nav>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 p-8 overflow-y-auto">
                {activeSection && <AdminSectionContent section={activeSection} />}
            </main>
        </div>
    );
};

export default LevelAdminPanel;
