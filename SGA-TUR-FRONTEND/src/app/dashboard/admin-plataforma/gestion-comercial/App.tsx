
import React, { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { AppView } from './types';
import { BotIcon, CogIcon, TrendingUpIcon, MegaphoneIcon, ChartBarIcon, ChevronDoubleLeftIcon, ChevronDoubleRightIcon, BellIcon, UserCircleIcon, SparklesIcon, MenuIcon, FunnelIcon, ClipboardListIcon, ServerIcon } from './components/icons';
import Level1_Communication from './components/Level1_Communication';
import Level2_Responses from './components/Level2_Responses';
import LevelAIStudio from './components/LevelAIStudio';
import Level5_AutomationSuite from './components/Level5_AutomationSuite';
import Level6_AnalyticsAdmin from './components/Level6_AnalyticsAdmin';
import LevelFunnels from './components/LevelFunnels';
import LevelPlaybooks from './components/LevelPlaybooks';
import LevelAdminPanel from './components/LevelAdminPanel';
import { SettingsProvider } from './context/SettingsContext';
import Settings from './components/Settings';
import Login from './components/Login';

const App = () => {
  const [authToken, setAuthToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [activeView, setActiveView] = useState<AppView>(AppView.FUNNELS);
  const [isNavCollapsed, setIsNavCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLoginSuccess = (token: string) => {
    localStorage.setItem('authToken', token);
    setAuthToken(token);
    setActiveView(AppView.FUNNELS); // Redirect to a default view after login
  };

  const navItems = [
    { id: AppView.COMMUNICATION, label: 'Marketing', icon: MegaphoneIcon },
    { id: AppView.RESPONSES, label: 'Ventas y CRM', icon: TrendingUpIcon },
    { id: AppView.AI_STUDIO, label: 'Estudio AI', icon: SparklesIcon },
    { id: AppView.AUTOMATION, label: 'Suite de Automatización', icon: BotIcon },
    { id: AppView.FUNNELS, label: 'Arquitecto de Embudos', icon: FunnelIcon },
    { id: AppView.PLAYBOOKS, label: 'Arquitecto de Playbooks', icon: ClipboardListIcon },
    { id: AppView.ADMIN, label: 'Analítica y Admin', icon: ChartBarIcon },
    { id: AppView.ADMIN_PANEL, label: 'Panel de Capas', icon: ServerIcon },
    { id: AppView.SETTINGS, label: 'Ajustes', icon: CogIcon },
  ];

  const activeNavItem = navItems.find(item => item.id === activeView);

  const renderContent = () => {
    switch (activeView) {
      case AppView.COMMUNICATION: return <Level1_Communication authToken={authToken!} />;
      case AppView.RESPONSES: return <Level2_Responses />;
      case AppView.AI_STUDIO: return <LevelAIStudio />;
      case AppView.AUTOMATION: return <Level5_AutomationSuite authToken={authToken!} />;
      case AppView.FUNNELS: return <LevelFunnels authToken={authToken!} />;
      case AppView.PLAYBOOKS: return <LevelPlaybooks />;
      case AppView.ADMIN: return <Level6_AnalyticsAdmin />;
      case AppView.ADMIN_PANEL: return <LevelAdminPanel />;
      case AppView.SETTINGS: return <Settings />;
      default: return <div className="p-8">Seleccione una opción del menú</div>;
    }
  };

  const NavigationMenu = ({ isCollapsed }: { isCollapsed: boolean }) => (
    <nav className={`bg-card flex flex-col justify-between border-r shadow-md transition-all duration-300 ease-in-out ${isCollapsed ? 'w-20' : 'w-64'}`}>
      <div>
        <div className={`flex items-center p-4 mb-4 h-[65px] border-b ${isCollapsed ? 'justify-center' : 'justify-start'}`}>
          <div className="bg-primary/10 p-2 rounded-lg">
            <SparklesIcon className="w-6 h-6 text-primary" />
          </div>
          {!isCollapsed && <h1 className="text-xl font-bold text-foreground ml-3 tracking-tighter">Gestor IA</h1>}
        </div>
        <ul>
          {navItems.map((item) => (
            <li key={item.id} className="px-3 my-1">
              <button
                onClick={() => { setActiveView(item.id); isMobile && setIsMobileMenuOpen(false); }}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all duration-200 relative ${isCollapsed ? 'justify-center' : ''} ${
                  activeView === item.id
                    ? 'bg-primary/10 text-primary font-bold'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                }`}
              >
                {activeView === item.id && !isCollapsed && <div className="absolute left-0 top-1 bottom-1 w-1 bg-primary rounded-r-full"></div>}
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!isCollapsed && <span className="text-sm">{item.label}</span>}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="border-t">
         {!isCollapsed && (
            <div className="text-xs text-center space-y-1 text-muted-foreground p-4">
                <p className="font-semibold text-foreground">Tech Stack</p>
                <p>React + Gemini API + TailwindCSS</p>
                <p className="pt-2">&copy; 2024 Jules</p>
            </div>
        )}
         <div className="p-2">
            <button onClick={() => setIsNavCollapsed(!isNavCollapsed)} className="w-full flex items-center justify-center p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground">
                {isNavCollapsed ? <ChevronDoubleRightIcon className="w-5 h-5" /> : <ChevronDoubleLeftIcon className="w-5 h-5" />}
            </button>
        </div>
      </div>
    </nav>
  );

  if (!authToken) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <SettingsProvider>
      <DndProvider backend={HTML5Backend}>
        <div className="flex h-screen bg-background text-foreground font-sans">
          {/* Mobile Menu Overlay */}
          {isMobile && isMobileMenuOpen && (
            <div className="fixed inset-0 bg-black/60 z-50" onClick={() => setIsMobileMenuOpen(false)}>
              <div className="w-64 h-full" onClick={e => e.stopPropagation()}>
                  <NavigationMenu isCollapsed={false} />
              </div>
            </div>
          )}

          {/* Desktop Navigation */}
          {!isMobile && <NavigationMenu isCollapsed={isNavCollapsed} />}

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col overflow-hidden">
              <header className="flex-shrink-0 bg-card/80 backdrop-blur-md h-[65px] px-6 flex justify-between items-center border-b z-10">
                  <div className="flex items-center">
                      {isMobile && (
                          <button onClick={() => setIsMobileMenuOpen(true)} className="mr-4 p-2 text-muted-foreground hover:text-foreground">
                              <MenuIcon className="w-6 h-6" />
                          </button>
                      )}
                      <h2 className="text-xl font-bold">{activeNavItem?.label}</h2>
                  </div>
                  <div className="flex items-center space-x-4">
                      <button className="text-muted-foreground hover:text-foreground relative p-2 rounded-full hover:bg-accent">
                          <BellIcon className="w-6 h-6" />
                          <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-destructive rounded-full border-2 border-card"></span>
                      </button>
                       <div className="w-px h-6 bg-border"></div>
                      <button className="flex items-center space-x-2 text-muted-foreground hover:text-foreground p-1 rounded-full hover:bg-accent">
                          <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="User" className="w-8 h-8 rounded-full" />
                           {!isNavCollapsed && !isMobile && <span className="text-sm font-semibold">J. Doe</span>}
                      </button>
                  </div>
              </header>
              <main className="flex-1 overflow-y-auto">
                {renderContent()}
              </main>
          </div>

        </div>
      </DndProvider>
    </SettingsProvider>
  );
};

export default App;
