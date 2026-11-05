import React, { useState, useEffect } from 'react';
import { User, AuditLog, Permission, Role } from '../types';
import { getSalesForecast } from '../services/geminiService';
import { 
    UsersIcon, TrendingUpIcon, SupportIcon, MegaphoneIcon, EuroIcon, 
    FileExportIcon, PlusIcon, ShieldCheckIcon, AppStoreIcon, GooglePlayIcon 
} from './icons';

// --- MOCK DATA ---
const mockUsers: User[] = [
    { id: 'usr-1', name: 'Admin General', email: 'admin@empresa.com', role: 'Admin', avatarUrl: 'https://randomuser.me/api/portraits/lego/1.jpg', permissions: ['view_financials', 'export_data', 'manage_users', 'delete_contacts'] },
    { id: 'usr-2', name: 'Ana Gómez', email: 'ana.gomez@empresa.com', role: 'Vendedor', avatarUrl: 'https://randomuser.me/api/portraits/women/68.jpg', permissions: ['export_data'] },
    { id: 'usr-3', name: 'Carlos Díaz', email: 'carlos.diaz@empresa.com', role: 'Vendedor', avatarUrl: 'https://randomuser.me/api/portraits/men/68.jpg', permissions: [] },
    { id: 'usr-4', name: 'Laura Pausini', email: 'laura.p@empresa.com', role: 'Soporte', avatarUrl: 'https://randomuser.me/api/portraits/women/69.jpg', permissions: [] },
];

const mockAuditLogs: AuditLog[] = [
    { id: 'log-1', userName: 'Ana Gómez', userAvatarUrl: 'https://randomuser.me/api/portraits/women/68.jpg', action: "actualizó la etapa de 'Innovatech' a Propuesta.", timestamp: new Date(Date.now() - 3600000).toISOString() },
    { id: 'log-2', userName: 'Admin General', userAvatarUrl: 'https://randomuser.me/api/portraits/lego/1.jpg', action: "exportó el 'Reporte Semanal de Ventas'.", timestamp: new Date(Date.now() - 2 * 3600000).toISOString() },
    { id: 'log-3', userName: 'Carlos Díaz', userAvatarUrl: 'https://randomuser.me/api/portraits/men/68.jpg', action: "registró una llamada con 'Quantum Dynamics'.", timestamp: new Date(Date.now() - 5 * 3600000).toISOString() },
];

const permissionLabels: Record<Permission, string> = {
    view_financials: "Ver reportes financieros",
    export_data: "Exportar datos de clientes",
    manage_users: "Gestionar usuarios y roles",
    delete_contacts: "Eliminar contactos y empresas"
};

// --- SUB-COMPONENTS ---
const KpiCard: React.FC<{ icon: React.FC<{className?: string}>, title: string, value: string, change?: string }> = ({ icon: Icon, title, value, change }) => (
    <div className="bg-card p-5 rounded-lg border shadow-sm">
        <div className="flex justify-between items-center">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <Icon className="w-5 h-5 text-muted-foreground" />
        </div>
        <div className="mt-2 flex items-baseline space-x-2">
            <p className="text-3xl font-bold text-foreground">{value}</p>
            {change && <span className={`text-sm font-semibold ${change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>{change}</span>}
        </div>
    </div>
);

// --- TABS ---
const DashboardTab: React.FC = () => {
    // This would typically use a charting library like Chart.js or Recharts
    const SalesForecastChart = () => {
        const [forecastData, setForecastData] = useState<{month: string, forecast: number}[]>([]);
        useEffect(() => {
            const historicalData = [ {month: "Ene", sales: 150}, {month: "Feb", sales: 180}, {month: "Mar", sales: 220}, {month: "Abr", sales: 210}, {month: "May", sales: 250}];
            getSalesForecast(historicalData).then(setForecastData);
        }, []);
        const chartData = [...[{month: "May", sales: 250, isForecast: false}], ...forecastData.map(d=>({month: d.month, sales: d.forecast, isForecast: true}))];
        return (
            <div className="bg-card p-6 rounded-xl h-80 flex flex-col border shadow-md">
                <h4 className="font-bold text-foreground">Predicción de Ventas IA</h4>
                <div className="flex-1 flex items-end space-x-4 p-4">
                     {/* Simplified bar chart */}
                    {chartData.map((d, i) => (
                        <div key={i} className="flex-1 flex flex-col items-center justify-end h-full">
                           <div className={`${d.isForecast ? 'bg-primary/50' : 'bg-primary' } w-full rounded-t-md`} style={{height: `${(d.sales / 350) * 100}%`}}></div>
                           <span className="text-xs mt-2 text-muted-foreground">{d.month}</span>
                        </div>
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="p-8 space-y-8">
            <div className="flex justify-between items-center">
                <h3 className="text-2xl font-bold text-foreground">Dashboard de Analítica</h3>
                <button className="bg-primary px-4 py-2 rounded-lg text-primary-foreground font-semibold">Personalizar Dashboard</button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KpiCard icon={TrendingUpIcon} title="ROI Campañas" value="3.5x" change="+0.2" />
                <KpiCard icon={EuroIcon} title="CAC (Adquisición)" value="€45.20" change="-5%" />
                <KpiCard icon={UsersIcon} title="LTV (Vida Cliente)" value="€1,280" />
                <KpiCard icon={MegaphoneIcon} title="Conversión Funnel" value="4.1%" change="+0.5%" />
            </div>
            <div className="bg-amber-50 border border-amber-200 p-3 rounded-lg flex items-center gap-2 text-xs text-amber-700 font-medium italic">
                <span>Nota: Los cálculos de CAC/LTV se basan en datos de inversión en marketing y recurrencia detectada. (Cálculo parcial – backend en progreso)</span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <SalesForecastChart />
                {/* Another chart could go here */}
            </div>
        </div>
    );
};

const UserManagementTab: React.FC = () => {
    // ... logic for user management
    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-6">
                 <h3 className="text-2xl font-bold text-foreground">Gestión de Usuarios</h3>
                <button className="flex items-center space-x-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
                    <PlusIcon className="w-5 h-5"/>
                    <span>Invitar Usuario</span>
                </button>
            </div>
             <div className="bg-card rounded-xl border shadow-lg">
                <table className="w-full text-left">
                    <thead className="border-b text-sm text-muted-foreground">
                        <tr>
                            <th className="p-4">Usuario</th>
                            <th className="p-4">Rol</th>
                            <th className="p-4">Permisos Adicionales</th>
                            <th className="p-4">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {mockUsers.map(user => (
                            <tr key={user.id} className="border-b">
                                <td className="p-4 flex items-center space-x-3">
                                    <img src={user.avatarUrl} alt={user.name} className="w-10 h-10 rounded-full" />
                                    <div><p className="font-bold">{user.name}</p><p className="text-sm text-muted-foreground">{user.email}</p></div>
                                </td>
                                <td className="p-4">{user.role}</td>
                                <td className="p-4">
                                    <div className="flex flex-wrap gap-1">
                                    {user.permissions.length > 0 
                                        ? user.permissions.map(p => <span key={p} className="text-xs bg-accent text-accent-foreground px-2 py-1 rounded-full" title={permissionLabels[p]}>{permissionLabels[p]}</span>)
                                        : <span className="text-xs text-muted-foreground">Ninguno</span>
                                    }
                                    </div>
                                </td>
                                <td className="p-4"><button className="text-primary hover:underline">Editar</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
};

const SecurityTab: React.FC = () => (
    <div className="p-8 space-y-8">
        <div className="bg-card p-6 rounded-xl border shadow-sm">
            <h4 className="font-bold text-foreground flex items-center mb-4"><ShieldCheckIcon className="w-6 h-6 mr-2 text-green-400"/>Ajustes de Seguridad</h4>
            {/* Security settings form elements would go here */}
        </div>
        <div className="bg-card p-6 rounded-xl border shadow-sm">
            <h4 className="font-bold text-foreground">Registro de Auditoría</h4>
            <div className="mt-4 space-y-3">
                {mockAuditLogs.map(log => (
                    <div key={log.id} className="flex items-center space-x-3">
                        <img src={log.userAvatarUrl} alt={log.userName} className="w-8 h-8 rounded-full" />
                        <div>
                            <p className="text-sm"><span className="font-bold">{log.userName}</span> {log.action}</p>
                            <p className="text-xs text-muted-foreground">{new Date(log.timestamp).toLocaleString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    </div>
);

const IntegrationsTab: React.FC = () => (
    <div className="p-8">
        <h3 className="text-2xl font-bold text-foreground mb-6">Marketplace de Aplicaciones</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-card p-4 rounded-xl text-center border shadow-sm">
                <AppStoreIcon className="w-12 h-12 mx-auto mb-2"/>
                <h4 className="font-bold">App Store Connect</h4>
                <p className="text-sm text-muted-foreground mb-3">Sincroniza datos de tu app iOS.</p>
                <button className="w-full bg-primary text-primary-foreground py-2 rounded-md font-semibold">Conectar</button>
            </div>
            <div className="bg-card p-4 rounded-xl text-center border shadow-sm">
                <GooglePlayIcon className="w-12 h-12 mx-auto mb-2"/>
                 <h4 className="font-bold">Google Play Console</h4>
                <p className="text-sm text-muted-foreground mb-3">Sincroniza datos de tu app Android.</p>
                 <button className="w-full bg-muted py-2 rounded-md font-semibold">Próximamente</button>
            </div>
        </div>
    </div>
);


// --- MAIN COMPONENT ---
const Level6_AnalyticsAdmin: React.FC = () => {
    const [view, setView] = useState<'dashboard' | 'users' | 'security' | 'integrations'>('dashboard');

    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: TrendingUpIcon },
        { id: 'users', label: 'Usuarios y Roles', icon: UsersIcon },
        { id: 'security', label: 'Seguridad', icon: ShieldCheckIcon },
        { id: 'integrations', label: 'Integraciones', icon: AppStoreIcon },
    ];

    const renderContent = () => {
        switch (view) {
            case 'users': return <UserManagementTab />;
            case 'security': return <SecurityTab />;
            case 'integrations': return <IntegrationsTab />;
            case 'dashboard':
            default:
                return <DashboardTab />;
        }
    };
    
    return (
        <div className="p-8 h-full flex flex-col">
            <div className="flex space-x-2 border-b mb-6">
                {navItems.map(item => (
                    <button 
                        key={item.id}
                        onClick={() => setView(item.id as any)} 
                        className={`flex items-center space-x-2 py-2 px-4 font-medium ${view === item.id ? 'border-b-2 border-primary text-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
                        <item.icon className="w-5 h-5" /><span>{item.label}</span>
                    </button>
                ))}
            </div>
            <div className="flex-1 overflow-y-auto">
                {renderContent()}
            </div>
        </div>
    );
};

// FIX: Added 'export default' to resolve the missing default export error in App.tsx.
// The component was defined but not exported, causing the import to fail.
export default Level6_AnalyticsAdmin;
