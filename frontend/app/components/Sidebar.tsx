import { LayoutDashboard, MessageSquare, Users, Settings, Brain, Network, Globe } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

interface SidebarProps {
  currentView: string;
  setCurrentView: (view: string) => void;
}

export default function Sidebar({ currentView, setCurrentView }: SidebarProps) {
  const { t, lang, setLang } = useLanguage();

  const navItems = [
    { id: 'dashboard', label: t('nav.dashboard'), icon: LayoutDashboard },
    { id: 'segments', label: t('nav.segments'), icon: Users },
    { id: 'copilot', label: t('nav.copilot'), icon: MessageSquare },
    { id: 'ml', label: t('nav.ml'), icon: Brain },
    { id: 'decision', label: t('nav.decision'), icon: Network },
  ];

  return (
    <aside className="w-64 glass-panel m-4 flex flex-col justify-between hidden md:flex shrink-0 relative overflow-hidden">
      <div className="p-6">
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary mb-8 cursor-pointer" onClick={() => setCurrentView('dashboard')}>
          InsightForge
        </h2>
        
        <nav className="space-y-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`w-full flex items-center space-x-3 transition-all p-3 rounded-xl ${
                  isActive 
                    ? 'bg-primary text-white shadow-lg shadow-primary/20 scale-105' 
                    : 'text-foreground/80 hover:text-white hover:bg-white/5 hover:scale-105'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
      
      <div className="p-6 space-y-4">
        <button
          onClick={() => setLang(lang === 'en' ? 'fr' : 'en')}
          className="w-full flex items-center justify-between transition-all p-3 rounded-xl text-foreground/80 hover:text-white hover:bg-white/5 hover:scale-105 border border-white/5"
        >
          <div className="flex items-center space-x-3">
            <Globe size={20} />
            <span className="font-medium">Language</span>
          </div>
          <span className="text-xs uppercase font-bold bg-white/10 px-2 py-1 rounded">{lang}</span>
        </button>

        <button
          onClick={() => setCurrentView('settings')}
          className={`w-full flex items-center space-x-3 transition-all p-3 rounded-xl ${
            currentView === 'settings'
              ? 'bg-primary text-white shadow-lg shadow-primary/20 scale-105' 
              : 'text-foreground/80 hover:text-white hover:bg-white/5 hover:scale-105'
          }`}
        >
          <Settings size={20} />
          <span className="font-medium">{t('nav.settings')}</span>
        </button>
      </div>
    </aside>
  );
}
