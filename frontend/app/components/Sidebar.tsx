import { LayoutDashboard, MessageSquare, Users, Settings, Brain, Network, Globe, Info, Calendar } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export default function Sidebar({ activeView, onViewChange }: SidebarProps) {
  const { t, lang, setLang } = useLanguage();

  const navItems = [
    { id: 'dashboard', label: t('nav.dashboard'), icon: LayoutDashboard },
    { id: 'segments', label: t('nav.segments'), icon: Users },
    { id: 'ml', label: t('nav.ml'), icon: Brain },
    { id: 'decision', label: t('nav.decision'), icon: Network },
    { id: 'retention', label: t('nav.retention') || 'Retention', icon: Calendar },
    { id: 'project',  label: t('nav.project') || 'Project Info', icon: Info },
  ];

  return (
    <aside className="w-64 glass-panel m-4 flex flex-col justify-between hidden md:flex shrink-0 relative overflow-hidden">
      <div className="p-6">
        <h2 
          className="text-2xl font-bold bg-clip-text text-transparent mb-8 cursor-pointer" 
          style={{ backgroundImage: 'linear-gradient(to right, var(--primary), var(--secondary))' }}
          onClick={() => onViewChange('dashboard')}
        >
          InsightForge
        </h2>
        
        <nav className="space-y-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`w-full flex items-center space-x-3 transition-all p-3 rounded-xl ${
                  isActive 
                    ? 'text-primary-foreground shadow-lg scale-105' 
                    : 'text-foreground/80 hover:text-primary hover:bg-primary/10 hover:scale-105'
                }`}
                style={isActive ? { backgroundColor: 'var(--primary)', boxShadow: '0 10px 15px -3px rgba(var(--primary-rgb), 0.2)' } : {}}
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
          className="w-full flex items-center justify-between transition-all p-3 rounded-xl text-foreground/80 hover:text-primary hover:bg-primary/10 hover:scale-105 border border-white/5"
        >
          <div className="flex items-center space-x-3">
            <Globe size={20} />
            <span className="font-medium">{t('nav.langLabel')}</span>
          </div>
          <span className="text-xs uppercase font-bold bg-white/10 px-2 py-1 rounded">{lang}</span>
        </button>

        <button
          onClick={() => onViewChange('settings')}
          className={`w-full flex items-center space-x-3 transition-all p-3 rounded-xl ${
            activeView === 'settings'
              ? 'text-primary-foreground shadow-lg scale-105' 
              : 'text-foreground/80 hover:text-primary hover:bg-primary/10 hover:scale-105'
          }`}
          style={activeView === 'settings' ? { backgroundColor: 'var(--primary)', boxShadow: '0 10px 15px -3px rgba(var(--primary-rgb), 0.2)' } : {}}
        >
          <Settings size={20} />
          <span className="font-medium">{t('nav.settings')}</span>
        </button>
      </div>
    </aside>
  );
}
