"use client";

import { useState, useEffect } from "react";
import { Activity, TrendingUp, Users, AlertTriangle, Settings, Brain, Network, RefreshCw, Loader2 } from "lucide-react";
import AICopilot from "./components/AICopilot";
import Sidebar from "./components/Sidebar";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Brush, BarChart, Bar } from 'recharts';
import { LanguageProvider, useLanguage } from "@/lib/i18n";
import { fetchMLMetrics, fetchChurnScores, fetchSegments, triggerTraining } from "@/lib/api";

const mockDataSets = {
  year: [
    { name: '2020', revenue: 120000 },
    { name: '2021', revenue: 180000 },
    { name: '2022', revenue: 240000 },
    { name: '2023', revenue: 420000 },
    { name: '2024', revenue: 650000 },
  ],
  month: [
    { name: 'Jan 2024', revenue: 45000 },
    { name: 'Feb 2024', revenue: 52000 },
    { name: 'Mar 2024', revenue: 48000 },
    { name: 'Apr 2024', revenue: 61000 },
    { name: 'May 2024', revenue: 59000 },
    { name: 'Jun 2024', revenue: 75000 },
    { name: 'Jul 2024', revenue: 82000 },
  ],
  week: [
    { name: 'Week 1', revenue: 12000 },
    { name: 'Week 2', revenue: 15000 },
    { name: 'Week 3', revenue: 14500 },
    { name: 'Week 4', revenue: 18000 },
  ],
  day: [
    { name: 'Mon', revenue: 4000 },
    { name: 'Tue', revenue: 3000 },
    { name: 'Wed', revenue: 5000 },
    { name: 'Thu', revenue: 4500 },
    { name: 'Fri', revenue: 6000 },
    { name: 'Sat', revenue: 5500 },
    { name: 'Sun', revenue: 7000 },
  ]
};

const mockSegmentData = [
  { name: 'Power User', value: 400, color: '#8b5cf6' },
  { name: 'Casual', value: 800, color: '#3b82f6' },
  { name: 'At Risk', value: 300, color: '#f59e0b' },
  { name: 'Dormant', value: 500, color: '#ef4444' },
];

function KPICard({ title, value, icon: Icon, trend, color, t }: any) {
  return (
    <div className="glass-panel p-6 flex items-start justify-between hover:scale-[1.02] transition-transform duration-300">
      <div>
        <p className="text-sm text-foreground/60 mb-1">{title}</p>
        <h3 className="text-3xl font-bold">{value}</h3>
        {trend && (
          <p className={`text-xs mt-2 flex items-center space-x-1 ${trend > 0 ? 'text-success' : 'text-danger'}`}>
            <TrendingUp size={12} className={trend < 0 ? 'rotate-180' : ''} />
            <span>{Math.abs(trend)}% {t('dash.vsLastMonth')}</span>
          </p>
        )}
      </div>
      <div className={`p-3 rounded-xl bg-white/5 text-${color}`}>
        <Icon size={24} />
      </div>
    </div>
  );
}

function DashboardView() {
  const [granularity, setGranularity] = useState<'year' | 'month' | 'week' | 'day'>('month');
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('dash.overview')}</h1>
          <p className="text-foreground/60">{t('dash.subtitle')}</p>
        </div>
        <div className="flex space-x-3">
          <button className="glass-panel px-4 py-2 text-sm font-medium hover:bg-white/10 transition-colors">
            {t('dash.last30')}
          </button>
          <button className="glass-button px-4 py-2 text-sm font-medium rounded-lg text-white">
            {t('dash.genReport')}
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard title={t('dash.revenue')} value="$45,231" icon={TrendingUp} trend={+12.5} color="success" t={t} />
        <KPICard title={t('dash.users')} value="2,845" icon={Users} trend={+5.2} color="primary" t={t} />
        <KPICard title={t('dash.engagement')} value="78/100" icon={Activity} trend={+1.2} color="secondary" t={t} />
        <KPICard title={t('dash.churn')} value="14.2%" icon={AlertTriangle} trend={-2.4} color="danger" t={t} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-semibold">{t('dash.revTrend')}</h3>
              <div className="flex bg-white/5 rounded-lg p-1">
                {(['year', 'month', 'week', 'day'] as const).map(g => (
                  <button 
                    key={g} 
                    onClick={() => setGranularity(g)}
                    className={`px-3 py-1 text-xs rounded-md capitalize transition-colors ${granularity === g ? 'bg-primary text-white shadow' : 'text-foreground/60 hover:text-white'}`}
                  >
                    {t(`granularity.${g}`)}
                  </button>
                ))}
              </div>
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockDataSets[granularity]}>
                  <defs>
                    <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" tick={{fill: 'rgba(255,255,255,0.5)'}} axisLine={false} tickLine={false} />
                  <YAxis stroke="rgba(255,255,255,0.5)" tick={{fill: 'rgba(255,255,255,0.5)'}} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
                  <Brush 
                    dataKey="name" 
                    height={30} 
                    stroke="#8b5cf6" 
                    fill="rgba(30, 41, 59, 0.8)" 
                    travellerWidth={10}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel p-6">
            <h3 className="font-semibold mb-6">{t('dash.userSeg')}</h3>
            <div className="h-64 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={mockSegmentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {mockSegmentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="ml-8 space-y-3 flex-1">
                {mockSegmentData.map((segment) => (
                  <div key={segment.name} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: segment.color }} />
                      <span className="text-sm">{segment.name}</span>
                    </div>
                    <span className="font-semibold">{segment.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-1">
          <AICopilot />
        </div>
      </div>
    </div>
  );
}

function SegmentsView() {
  const { t } = useLanguage();
  const [segments, setSegments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const SEGMENT_COLORS: Record<string, string> = {
    power_user: '#8b5cf6',
    casual:     '#3b82f6',
    at_risk:    '#f59e0b',
    dormant:    '#ef4444',
  };

  useEffect(() => {
    fetchSegments()
      .then(setSegments)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold mb-2">{t('seg.title')}</h1>
      <p className="text-foreground/60 mb-8">{t('seg.subtitle')}</p>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <Loader2 className="animate-spin text-primary" size={32} />
        </div>
      ) : segments.length === 0 ? (
        <div className="glass-panel p-8 text-center">
          <Brain size={48} className="mx-auto mb-4 text-primary opacity-50" />
          <h2 className="text-xl font-semibold mb-2">Modèles non entraînés</h2>
          <p className="text-foreground/60">Lance d'abord l'entraînement depuis la section ML Models.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {segments.map((seg) => (
            <div key={seg.segment} className="glass-panel p-6 hover:scale-[1.02] transition-transform">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-4 h-4 rounded-full" style={{ backgroundColor: SEGMENT_COLORS[seg.segment] ?? '#666' }} />
                <h3 className="font-semibold capitalize">{seg.segment.replace('_', ' ')}</h3>
              </div>
              <p className="text-4xl font-bold mb-2">{seg.count}</p>
              <div className="space-y-1 text-sm text-foreground/60">
                <p>Engagement moy. : <span className="text-white font-medium">{Number(seg.avg_engagement).toFixed(1)}</span></p>
                <p>Inactivité moy. : <span className="text-white font-medium">{Number(seg.avg_churn_days).toFixed(0)}j</span></p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function CopilotView() {
  const { t } = useLanguage();
  return (
    <div className="space-y-6 h-full flex flex-col">
      <h1 className="text-3xl font-bold mb-2">{t('copilot.title')}</h1>
      <p className="text-foreground/60 mb-4">{t('copilot.subtitle')}</p>
      <div className="flex-1 min-h-[700px]">
        <AICopilot />
      </div>
    </div>
  );
}

function MLView() {
  const { t } = useLanguage();
  const [metrics, setMetrics] = useState<any>(null);
  const [churnData, setChurnData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);

  useEffect(() => {
    Promise.all([fetchMLMetrics(), fetchChurnScores()])
      .then(([m, c]) => { setMetrics(m); setChurnData(c.slice(0, 10)); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleTrain = async () => {
    setTraining(true);
    await triggerTraining();
    setTimeout(async () => {
      const [m, c] = await Promise.all([fetchMLMetrics(), fetchChurnScores()]);
      setMetrics(m); setChurnData(c.slice(0, 10)); setTraining(false);
    }, 8000);
  };

  const xgbStatus = metrics?.xgboost?.status === 'trained';
  const kmeansStatus = metrics?.kmeans?.status === 'trained';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('ml.title')}</h1>
          <p className="text-foreground/60">{t('ml.subtitle')}</p>
        </div>
        <button
          onClick={handleTrain}
          disabled={training}
          className="glass-button px-4 py-2 rounded-lg text-white text-sm flex items-center gap-2 disabled:opacity-50"
        >
          {training ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
          {training ? 'Training...' : t('ml.retrain')}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Brain className="text-primary" size={24} />
            <h3 className="text-xl font-semibold">{t('ml.churn')}</h3>
          </div>
          {loading ? (
            <div className="flex items-center justify-center h-20"><Loader2 className="animate-spin text-primary" /></div>
          ) : (
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm">
                <span className="text-foreground/60">{t('ml.accuracy')}</span>
                <span className="font-semibold">{xgbStatus ? `${(metrics.xgboost.accuracy * 100).toFixed(1)}%` : '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-foreground/60">{t('ml.status')}</span>
                <span className={`font-semibold ${xgbStatus ? 'text-success' : 'text-warning'}`}>
                  {xgbStatus ? t('ml.active') : 'Not trained'}
                </span>
              </div>
              {/* Progress bar accuracy */}
              {xgbStatus && (
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${metrics.xgboost.accuracy * 100}%` }} />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="glass-panel p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Users className="text-secondary" size={24} />
            <h3 className="text-xl font-semibold">{t('ml.seg')}</h3>
          </div>
          {loading ? (
            <div className="flex items-center justify-center h-20"><Loader2 className="animate-spin text-primary" /></div>
          ) : (
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm">
                <span className="text-foreground/60">{t('ml.clusters')}</span>
                <span className="font-semibold">4</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-foreground/60">{t('ml.silhouette')}</span>
                <span className="font-semibold">{kmeansStatus ? metrics.kmeans.silhouette : '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-foreground/60">{t('ml.status')}</span>
                <span className={`font-semibold ${kmeansStatus ? 'text-success' : 'text-warning'}`}>
                  {kmeansStatus ? t('ml.active') : 'Not trained'}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Top 10 churn risk users */}
      {churnData.length > 0 && (
        <div className="glass-panel p-6">
          <h3 className="font-semibold mb-4">Top 10 — Churn Risk</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={churnData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${(v*100).toFixed(0)}%`}
                  stroke="rgba(255,255,255,0.4)" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="user_id" width={80}
                  tickFormatter={(v) => v.slice(0, 8) + '…'}
                  stroke="rgba(255,255,255,0.4)" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  formatter={(v: number) => [`${(v*100).toFixed(1)}%`, 'Churn Score']}
                  contentStyle={{ backgroundColor: 'rgba(30,41,59,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}
                  itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="churn_score" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

function DecisionEngineView() {
  const { t } = useLanguage();
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold mb-2">{t('dec.title')}</h1>
      <p className="text-foreground/60 mb-8">{t('dec.subtitle')}</p>
      <div className="glass-panel p-6">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2"><Network className="text-primary" /> {t('dec.activeRules')}</h3>
        <ul className="space-y-4">
          <li className="p-4 rounded bg-white/5 border border-white/10 flex justify-between items-center">
            <div>
              <span className="font-semibold block mb-1">{t('dec.highAnomaly')}</span>
              <span className="text-sm text-foreground/60">{t('dec.highAnomalyDesc')}</span>
            </div>
            <span className="px-3 py-1 bg-success/20 text-success rounded-full text-xs font-medium">{t('dec.enabled')}</span>
          </li>
          <li className="p-4 rounded bg-white/5 border border-white/10 flex justify-between items-center">
            <div>
              <span className="font-semibold block mb-1">{t('dec.lowRev')}</span>
              <span className="text-sm text-foreground/60">{t('dec.lowRevDesc')}</span>
            </div>
            <span className="px-3 py-1 bg-success/20 text-success rounded-full text-xs font-medium">{t('dec.enabled')}</span>
          </li>
        </ul>
        <button className="glass-button mt-6 px-6 py-2 rounded-lg text-white text-sm">{t('dec.addRule')}</button>
      </div>
    </div>
  );
}

function SettingsView() {
  const { t } = useLanguage();
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold mb-2">{t('set.title')}</h1>
      <p className="text-foreground/60 mb-8">{t('set.subtitle')}</p>
      <div className="glass-panel p-8 text-center">
        <Settings size={48} className="mx-auto mb-4 text-primary opacity-50 animate-spin-slow" />
        <h2 className="text-xl font-semibold mb-2">{t('set.config')}</h2>
        <p className="text-foreground/60">{t('set.configDesc')}</p>
      </div>
    </div>
  );
}

function AppContent() {
  const [currentView, setCurrentView] = useState("dashboard");
  const [animateState, setAnimateState] = useState("in");

  const handleViewChange = (view: string) => {
    if (view === currentView) return;
    setAnimateState("out");
    setTimeout(() => {
      setCurrentView(view);
      setAnimateState("in");
    }, 300);
  };

  const renderView = () => {
    switch (currentView) {
      case "dashboard": return <DashboardView />;
      case "segments": return <SegmentsView />;
      case "copilot": return <CopilotView />;
      case "ml": return <MLView />;
      case "decision": return <DecisionEngineView />;
      case "settings": return <SettingsView />;
      default: return <DashboardView />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar currentView={currentView} setCurrentView={handleViewChange} />
      
      <main className="flex-1 overflow-y-auto p-6 md:p-8 relative">
        <div 
          className={`transition-all duration-300 transform ${
            animateState === "in" 
              ? "opacity-100 translate-y-0 scale-100" 
              : "opacity-0 translate-y-8 scale-[0.98]"
          } w-full max-w-7xl mx-auto`}
        >
          {renderView()}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}
