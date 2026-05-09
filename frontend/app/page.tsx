"use client";

import { useState, useEffect, useRef } from "react";
import { Activity, TrendingUp, Users, AlertTriangle, Settings, Brain, Network, RefreshCw, Loader2, Globe, Info, FileText, Sparkles, Plus, Trash2, Download, Book, Lock, Mail, Key, LogOut, Bell, Check, ThumbsUp, ThumbsDown, Filter, ChevronDown, Server, Cloud, Database, DatabaseZap } from "lucide-react";
import AICopilot from "./components/AICopilot";
import Sidebar from "./components/Sidebar";
import Modal from "./components/Modal";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Brush, BarChart, Bar } from 'recharts';
import { LanguageProvider, useLanguage, THEME_COLORS } from "@/lib/i18n";
import { fetchMLMetrics, fetchChurnScores, fetchSegments, triggerTraining, fetchRevenueTrend, fetchSummary, suggestRules, generateReport, fetchRules, deleteRule, login, fetchNotifications, markNotificationRead, triggerDemoNotifications, clearNotifications, fetchRecommendation, triggerRecommendationCampaign, fetchConversions, fetchCohorts, sendRecommendationFeedback } from "@/lib/api";


function KPICard({ title, value, icon: Icon, trend, color, t, granularity, details, lang }: any) {
  const [isFlipped, setIsFlipped] = useState(false);

  const getPeriodLabel = () => {
    switch (granularity) {
      case 'year': return t('granularity.year');
      case 'month': return t('granularity.month');
      case 'week': return t('granularity.week');
      case 'day': return t('granularity.day');
      default: return t('granularity.month');
    }
  };

  const handleAIClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    const query = lang === 'fr' 
      ? `Donne-moi une interprétation détaillée de la métrique "${title}" (${value}). Quelles sont les implications pour le business ?`
      : `Give me a detailed interpretation of the "${title}" metric (${value}). What are the business implications?`;
    window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
  };

  const isRevenue = title.toLowerCase().includes('revenu') || title.toLowerCase().includes('revenue');

  return (
    <div className="perspective-2000 h-36 w-full group/card">
      <div 
        className={`flip-card-inner ${isFlipped ? 'flipped' : ''} cursor-pointer`}
        onClick={() => setIsFlipped(!isFlipped)}
      >
        {/* Front */}
        <div className="flip-card-front glass-panel p-4 flex flex-col justify-between group-hover/card:border-primary/50 transition-all overflow-hidden absolute w-full h-full backface-hidden">
          <div className="flex justify-between items-start">
            <div className="flex-1 min-w-0 pr-2">
              <p className="text-[10px] uppercase font-bold text-foreground/40 tracking-widest mb-1 whitespace-normal break-words" title={title}>
                {title}
              </p>
              <h3 className="text-xl font-black text-foreground tracking-tight whitespace-nowrap">
                {value}
              </h3>
            </div>
            <div className="flex flex-col items-end gap-1.5 shrink-0">
              <div className={`p-2 rounded-xl bg-gradient-to-br from-white/10 to-transparent border border-card-border text-${color} shadow-inner`}>
                <Icon size={18} />
              </div>
              <button 
                onClick={handleAIClick}
                className="p-1.5 rounded-lg bg-primary/10 text-primary opacity-0 group-hover/card:opacity-100 hover:bg-primary hover:text-white transition-all shadow-lg shadow-primary/20"
                title="Ask AI"
              >
                <Sparkles size={12} />
              </button>
            </div>
          </div>

          {trend !== undefined && (
            <div className="flex items-center gap-2 mt-auto">
              <div className={`flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold ${trend > 0 ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
                <TrendingUp size={10} className={trend < 0 ? 'rotate-180' : ''} />
                {Math.abs(trend)}%
              </div>
              <span className="text-[11px] text-foreground/30 font-medium lowercase italic whitespace-nowrap">{t('dash.vsLastMonth')}</span>
            </div>
          )}
        </div>

        {/* Back */}
        <div className="flip-card-back glass-panel border-primary/20 bg-primary/5 p-4 flex flex-col justify-center relative overflow-hidden">
          <Sparkles className="absolute -right-2 -bottom-2 text-primary/10 w-12 h-12" />
          <p className="text-[10px] uppercase font-bold text-primary mb-2 tracking-widest">{t('dash.detailContext')}</p>
          
          {isRevenue && details ? (
            <div className="space-y-1 w-full">
              {Object.entries(details).map(([plan, data]: [string, any]) => (
                <div key={plan} className="flex justify-between text-[10px] text-foreground/90">
                  <span className="capitalize">{plan} ({data.count} users)</span>
                  <span className="font-bold">${data.revenue.toLocaleString()}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[13px] text-foreground/90 leading-snug font-medium text-center">
              {title.toLowerCase().includes('revenu') || title.toLowerCase().includes('revenue') ? t('dash.revenueDesc') :
               title.toLowerCase().includes('user') ? t('dash.usersDesc') :
               title.toLowerCase().includes('engagement') ? t('dash.engagementDesc') :
               title.toLowerCase().includes('churn') ? t('dash.churnDesc') :
               t('dash.cardDetail').replace('{title}', title).replace('{period}', getPeriodLabel())}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function KPISkeleton() {
  return (
    <div className="glass-panel p-6 flex items-start justify-between">
      <div className="space-y-3 w-1/2">
        <div className="h-4 w-20 skeleton" />
        <div className="h-8 w-32 skeleton" />
      </div>
      <div className="w-12 h-12 rounded-2xl skeleton" />
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="glass-panel p-6 h-80 flex flex-col gap-4">
      <div className="flex justify-between">
        <div className="h-6 w-40 skeleton" />
        <div className="h-6 w-20 skeleton" />
      </div>
      <div className="flex-1 w-full skeleton" />
    </div>
  );
}

function DashboardView() {
  const { t, lang, theme } = useLanguage();
  const colors = THEME_COLORS[theme] || THEME_COLORS.midnight;
  const [granularity, setGranularity] = useState<'year' | 'month' | 'week' | 'day'>('month');
  const [trendData, setTrendData] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [segments, setSegments] = useState<any[]>([]);
  const [conversions, setConversions] = useState<any>(null);
  const [loadingTrend, setLoadingTrend] = useState(true);
  const [report, setReport] = useState<string | null>(null);

  useEffect(() => {
    fetchSummary().then(setSummary).catch(() => {});
    fetchSegments().then(data => Array.isArray(data) ? setSegments(data) : setSegments([])).catch(() => {});
    fetchConversions().then(setConversions).catch(() => {});
  }, []);

  useEffect(() => {
    setLoadingTrend(true);
    fetchRevenueTrend(granularity)
      .then(data => Array.isArray(data) ? setTrendData(data) : setTrendData([]))
      .catch(() => setTrendData([]))
      .finally(() => setLoadingTrend(false));
  }, [granularity]);

  const handleGenerateReport = async () => {
    const res = await generateReport();
    setReport(res.report);
  };

  return (
    <div className="space-y-6">
          <header className="flex justify-between items-end mb-8 shrink-0">
            <div>
              <h1 className="text-3xl font-bold mb-2">{t('dash.overview')}</h1>
              <p className="text-foreground/60">{t('dash.subtitle')}</p>
            </div>
            <div className="flex space-x-3">
              <button onClick={handleGenerateReport} className="glass-button px-4 py-2 text-sm font-medium rounded-lg text-primary-foreground flex items-center gap-2">
                <FileText size={16} /> {t('dash.genReport')}
              </button>
            </div>
          </header>

          {report && (
            <div className="glass-panel p-6 border-primary/30 bg-primary/5 animate-in slide-in-from-top duration-500 shrink-0">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold flex items-center gap-2"><Sparkles className="text-primary" /> {t('dash.reportGenerated')}</h3>
                <button onClick={() => setReport(null)} className="text-foreground/40 hover:text-primary">{t('dash.close')}</button>
              </div>
              <pre className="whitespace-pre-wrap text-sm text-foreground/80 font-mono bg-black/20 p-4 rounded-lg">{report}</pre>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 shrink-0">
            {!summary ? (
              <>
                <KPISkeleton /> <KPISkeleton /> <KPISkeleton /> <KPISkeleton />
              </>
            ) : (
              <>
                <KPICard title={t('dash.revenue')} value={summary?.total_revenue || "—"} icon={TrendingUp} trend={+12.5} color="success" t={t} granularity={granularity} details={summary?.revenue_breakdown} lang={lang} />
                <KPICard title={t('dash.users')} value={summary?.active_users || "—"} icon={Users} trend={+5.2} color="primary" t={t} granularity={granularity} lang={lang} />
                <KPICard title={t('dash.engagement')} value={summary?.engagement_score || "—"} icon={Activity} trend={+1.2} color="secondary" t={t} granularity={granularity} lang={lang} />
                <KPICard title={t('dash.churn')} value={summary?.churn_rate || "—"} icon={AlertTriangle} trend={-2.4} color="danger" t={t} granularity={granularity} lang={lang} />
              </>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 shrink-0">
             {/* Live Events Feed */}
             <div className="lg:col-span-1 glass-panel p-4 flex flex-col h-64">
                <div className="flex items-center justify-between mb-4">
                   <h3 className="text-xs font-bold uppercase text-foreground/40 tracking-widest flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-success animate-pulse" /> {t('dash.liveActivity')}
                   </h3>
                   <span className="text-[10px] font-mono text-success">{t('dash.realtime')}</span>
                </div>
                <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-2">
                   {[
                      { user: 'usr_812', event: 'Feature: Analytics', time: '2s ago', color: 'primary' },
                      { user: 'usr_443', event: 'Plan Upgrade: Pro', time: '14s ago', color: 'success' },
                      { user: 'usr_902', event: 'Session Start', time: '1m ago', color: 'secondary' },
                      { user: 'usr_112', event: 'Feature: Copilot', time: '3m ago', color: 'primary' },
                      { user: 'usr_665', event: 'Feature: Export', time: '5m ago', color: 'primary' },
                   ].map((log, i) => (
                      <div key={i} className="flex items-center justify-between text-[11px] p-2 rounded-lg bg-foreground/5 border border-card-border hover:border-primary/30 transition-colors">
                         <div className="flex items-center gap-2">
                            <div className={`w-1.5 h-1.5 rounded-full bg-${log.color}`} />
                            <span className="font-bold text-foreground/80">{log.user}</span>
                            <span className="text-foreground/40">{log.event}</span>
                         </div>
                         <span className="text-[9px] opacity-30">{log.time}</span>
                      </div>
                   ))}
                </div>
             </div>

             {/* ML & Retention Quick Cards */}
             <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4 h-64">
                <div className="glass-panel p-4 flex flex-col justify-between bg-primary/5 border-primary/20">
                   <div className="flex justify-between items-start">
                      <div className="group relative">
                        <p className="text-[10px] uppercase font-bold text-foreground/40 tracking-widest mb-1 flex items-center gap-1">
                          {t('ml.accuracy')}
                          <Info size={10} className="cursor-help text-foreground/20 group-hover:text-primary transition-colors" />
                        </p>
                        <div className="absolute top-full left-0 mt-2 w-48 p-2 bg-popover text-[10px] text-popover-foreground rounded-lg opacity-0 group-hover:opacity-100 transition-all pointer-events-none z-50 normal-case font-normal border border-card-border backdrop-blur-xl shadow-xl">
                          {t('ml.accuracyDesc')}
                        </div>
                        <h4 className="text-2xl font-bold text-foreground text-glow">75.5%</h4>
                      </div>
                      <div className="p-2 bg-primary/20 rounded-lg text-primary"><Brain size={20}/></div>
                   </div>
                   <div className="space-y-2">
                      <div className="flex justify-between text-[10px] font-bold">
                         <span className="text-foreground/40 uppercase">{t('ml.modelHealth')}</span>
                         <span className="text-success">{t('ml.excellent')}</span>
                      </div>
                      <div className="w-full bg-foreground/5 h-1.5 rounded-full overflow-hidden">
                         <div className="bg-primary h-full w-[75.5%] animate-pulse" />
                      </div>
                   </div>
                </div>
                <div className="glass-panel p-4 flex flex-col justify-between bg-success/5 border-success/20">
                   <div className="flex justify-between items-start">
                      <div className="group relative">
                        <p className="text-[10px] uppercase font-bold text-foreground/40 tracking-widest mb-1 flex items-center gap-1">
                          Average Retention
                          <Info size={10} className="cursor-help text-foreground/20 group-hover:text-primary transition-colors" />
                        </p>
                        <div className="absolute top-full left-0 mt-2 w-48 p-2 bg-popover text-[10px] text-popover-foreground rounded-lg opacity-0 group-hover:opacity-100 transition-all pointer-events-none z-50 normal-case font-normal border border-card-border backdrop-blur-xl shadow-xl">
                          {t('ret.avgDesc')}
                        </div>
                        <h4 className="text-2xl font-bold text-foreground text-glow">64.2%</h4>
                      </div>
                      <div className="p-2 bg-success/20 rounded-lg text-success"><RefreshCw size={20}/></div>
                   </div>
                   <div className="space-y-2">
                      <div className="flex justify-between text-[10px] font-bold">
                         <span className="text-foreground/40 uppercase">{t('ret.w1Trend')}</span>
                         <span className="text-success">↑ 4.2%</span>
                      </div>
                      <div className="flex gap-1 h-8 items-end">
                         {[30, 45, 35, 55, 48, 62, 58, 70, 64].map((h, i) => (
                            <div 
                              key={i} 
                              className="flex-1 bg-success/30 rounded-t-sm hover:bg-success transition-colors cursor-pointer" 
                              style={{ height: `${h}%` }} 
                              onClick={() => {
                                const query = lang === 'fr' 
                                  ? `Analyse ce point de rétention de ${h}%. Comment se compare-t-il à la moyenne ?`
                                  : `Analyze this retention point of ${h}%. How does it compare to the average?`;
                                window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
                              }}
                            />
                         ))}
                      </div>
                   </div>
                </div>
             </div>
          </div>

          {loadingTrend ? (
            <ChartSkeleton />
          ) : (
            <div className="glass-panel p-6 animate-in fade-in duration-500 shrink-0">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-semibold">{t('dash.revTrend')}</h3>
                <div className="flex bg-foreground/5 rounded-lg p-1">
                  {(['year', 'month', 'week', 'day'] as const).map(g => (
                    <button 
                      key={g} 
                      onClick={() => setGranularity(g)}
                      className={`px-3 py-1 text-xs rounded-md capitalize transition-colors ${granularity === g ? 'bg-primary text-primary-foreground shadow' : 'text-foreground/60 hover:text-foreground'}`}
                    >
                      {t(`granularity.${g}`)}
                    </button>
                  ))}
                </div>
              </div>
              <div className="h-72 w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData}>
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={colors.primary} stopOpacity={0.3}/>
                        <stop offset="95%" stopColor={colors.primary} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--foreground-rgb), 0.1)" vertical={false} />
                    <XAxis dataKey="name" stroke="rgba(var(--foreground-rgb), 0.3)" tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 10}} axisLine={false} tickLine={false} />
                    <YAxis 
                      stroke="rgba(var(--foreground-rgb), 0.3)" 
                      tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 10}} 
                      axisLine={false} 
                      tickLine={false}
                      tickFormatter={(val) => new Intl.NumberFormat().format(val)}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--card-border)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                      itemStyle={{ color: 'var(--foreground)' }}
                      formatter={(value: any) => [new Intl.NumberFormat().format(value), t('dash.revenue')]}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="revenue" 
                      stroke={colors.primary} 
                      strokeWidth={3} 
                      fillOpacity={1} 
                      fill="url(#colorRevenue)" 
                      className="cursor-pointer"
                      onClick={(data: any) => {
                        if (data && data.activePayload && data.activePayload[0]) {
                          const item = data.activePayload[0].payload;
                          const query = lang === 'fr' 
                            ? `Explique-moi la tendance des revenus pour ${item.name}. Pourquoi avons-nous ${item.revenue} ?`
                            : `Explain the revenue trend for ${item.name}. Why do we have ${item.revenue}?`;
                          window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
                        }
                      }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 shrink-0">
            <div className="glass-panel p-6">
              <h3 className="font-semibold mb-6">{t('dash.userSeg')}</h3>
              <div className="h-64 w-full flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={segments.map(s => ({
                        name: (s.name || '').replace('_', ' '),
                        value: s.count,
                        color: ({
                          power_user: colors.primary,
                          casual: colors.secondary,
                          at_risk: '#f59e0b',
                          dormant: '#ef4444'
                        } as any)[s.name] || '#64748b'
                      }))}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                      className="cursor-pointer outline-none"
                      onClick={(data) => {
                        const name = data.name;
                        const query = lang === 'fr' 
                          ? `Donne-moi une analyse détaillée du segment ${name}. Quelles sont les actions recommandées ?`
                          : `Give me a detailed analysis of the ${name} segment. What are the recommended actions?`;
                        window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
                      }}
                    >
                      {segments.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={({
                          power_user: colors.primary,
                          casual: colors.secondary,
                          at_risk: '#f59e0b',
                          dormant: '#ef4444'
                        } as any)[entry.name] || '#64748b'} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--card-border)', borderRadius: '8px' }}
                      itemStyle={{ color: 'var(--foreground)' }}
                      formatter={(value: any) => new Intl.NumberFormat().format(value)}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-panel p-6">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold">{t('dash.conversionRate')}</h3>
                  <div className="group relative">
                    <Info className="w-4 h-4 text-foreground/40 cursor-help" />
                    <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover:block w-64 p-2 text-xs bg-background text-foreground rounded border border-card-border z-10 text-center shadow-lg">
                      {lang === 'fr' 
                        ? "Calculé selon le % d'utilisateurs avec un plan payant (Pro, Enterprise) sur l'ensemble des utilisateurs actifs (Base GCP)."
                        : "Calculated as the % of users with a paid plan (Pro, Enterprise) out of all active users (GCP Data)."}
                    </div>
                  </div>
                </div>
                <div className="text-2xl font-bold text-success">{conversions?.rate}%</div>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={conversions?.history || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--foreground-rgb), 0.1)" vertical={false} />
                    <XAxis dataKey="month" stroke="rgba(var(--foreground-rgb), 0.3)" tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 10}} />
                    <YAxis stroke="rgba(var(--foreground-rgb), 0.3)" tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 10}} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--card-border)', borderRadius: '8px' }}
                      itemStyle={{ color: 'var(--foreground)' }}
                      formatter={(value: any) => new Intl.NumberFormat().format(value)}
                    />
                    <Bar 
                      dataKey="rate" 
                      fill="#10b981" 
                      radius={[4, 4, 0, 0]} 
                      className="cursor-pointer"
                      onClick={(data: any) => {
                        const query = lang === 'fr' 
                          ? `Analyse le taux de conversion de ${data.month} (${data.rate}%). Est-ce une bonne performance ?`
                          : `Analyze the conversion rate for ${data.month} (${data.rate}%). Is this a good performance?`;
                        window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
                      }}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
    </div>
  );
}

function SegmentsView() {
  const { t, theme } = useLanguage();
  const colors = THEME_COLORS[theme] || THEME_COLORS.midnight;
  const [segments, setSegments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const SEGMENT_COLORS: Record<string, string> = {
    power_user: colors.primary,
    casual:     colors.secondary,
    at_risk:    '#f59e0b',
    dormant:    '#ef4444',
  };

  useEffect(() => {
    fetchSegments()
      .then(data => Array.isArray(data) ? setSegments(data) : setSegments([]))
      .catch(() => setSegments([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('seg.title')}</h1>
          <p className="text-foreground/60">{t('seg.subtitle')}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {segments.map((seg, idx) => (
          <div key={seg?.name || idx} className="glass-panel p-6 border-l-4 flex flex-col justify-between" style={{ borderLeftColor: SEGMENT_COLORS[seg?.name] || colors.primary }}>
            <div>
          <h1 className="text-3xl font-bold mb-2">{t('seg.title')}</h1>
          <p className="text-foreground/60">{t('seg.subtitle')}</p>
        </div>
            <div className="mt-4 pt-4 border-t border-card-border flex items-center justify-between">
              <span className="text-[10px] text-foreground/40 uppercase font-bold tracking-tighter">Distribution</span>
              <span className="text-xs font-mono text-primary">{(seg?.percentage || 0).toFixed(1)}%</span>
            </div>
          </div>
        ))}
      </div>

      <div className="glass-panel overflow-visible">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-foreground/5 border-b border-card-border">
              <th className="p-4 text-xs font-bold uppercase text-foreground/60">Segment</th>
              <th className="p-4 text-xs font-bold uppercase text-foreground/60">Count</th>
              <th className="p-4 text-xs font-bold uppercase text-foreground/60 group relative">
                <div className="flex items-center gap-1">
                  Avg Score
                  <Info size={12} className="cursor-help text-foreground/40 group-hover:text-primary transition-colors" />
                </div>
                <div className="absolute top-full left-0 mt-2 w-56 p-3 bg-popover text-[11px] text-popover-foreground rounded-xl opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none z-50 normal-case font-normal border border-card-border backdrop-blur-xl shadow-2xl translate-y-1 group-hover:translate-y-0">
                  <p className="font-bold mb-1 text-primary">{t('seg.avgScoreTitle')}</p>
                  {t('seg.avgScoreDesc')}
                </div>
              </th>
              <th className="p-4 text-xs font-bold uppercase text-foreground/60 group relative">
                <div className="flex items-center gap-1">
                  Inactivity
                  <Info size={12} className="cursor-help text-foreground/40 group-hover:text-primary transition-colors" />
                </div>
                <div className="absolute top-full left-0 mt-2 w-56 p-3 bg-popover text-[11px] text-popover-foreground rounded-xl opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none z-50 normal-case font-normal border border-card-border backdrop-blur-xl shadow-2xl translate-y-1 group-hover:translate-y-0">
                  <p className="font-bold mb-1 text-primary">{t('seg.inactivityTitle')}</p>
                  {t('seg.inactivityDesc')}
                </div>
              </th>
              <th className="p-4 text-xs font-bold uppercase text-foreground/60">Status</th>
            </tr>
          </thead>
          <tbody>
            {segments.map((seg, idx) => (
              <tr key={seg?.name || idx} className="border-b border-card-border hover:bg-foreground/5 transition-colors">
                <td className="p-4 font-medium capitalize group relative cursor-help">
                  {(seg?.name || 'unknown').replace('_', ' ')}
                  <div className="absolute left-0 bottom-full mb-2 w-48 p-2 bg-popover text-[10px] text-popover-foreground rounded-lg opacity-0 group-hover:opacity-100 transition-all pointer-events-none z-50 normal-case font-normal border border-card-border backdrop-blur-xl shadow-xl">
                    {t(`seg.desc.${seg?.name}`)}
                  </div>
                </td>
                <td className="p-4">{seg?.count || 0}</td>
                <td className="p-4">{(seg?.avg_score || 0).toFixed(1)}/100</td>
                <td className="p-4">{(seg?.avg_churn_days || 0).toFixed(1)} days</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${(seg?.avg_score || 0) > 70 ? 'bg-success/20 text-success' : 'bg-warning/20 text-warning'}`}>
                    {(seg?.avg_score || 0) > 70 ? t('ml.healthy') : t('ml.monitor')}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}



function MLView() {
  const { t, lang } = useLanguage();
  const [metrics, setMetrics] = useState<any>(null);
  const [churnScores, setChurnScores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMLMetrics().then(setMetrics).catch(() => {});
    fetchChurnScores()
      .then(data => Array.isArray(data) ? setChurnScores(data) : setChurnScores([]))
      .catch(() => setChurnScores([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2 text-foreground">{t('ml.title')}</h1>
          <p className="text-foreground/60">{t('ml.subtitle')}</p>
        </div>
        <button onClick={() => triggerTraining()} className="glass-button px-4 py-2 rounded-lg flex items-center gap-2">
          <RefreshCw size={18} /> {t('ml.retrain')}
        </button>
      </div>

      <div className="glass-panel p-6 bg-foreground/5 border border-card-border mb-6">
        <h3 className="font-bold text-foreground mb-2 flex items-center gap-2">
          <Brain size={18} className="text-primary" /> {t('ml.trainingTitle')}
        </h3>
        <p className="text-sm text-foreground/80 leading-relaxed">
          {t('ml.trainingDesc')}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6">
          <p className="text-sm font-medium text-foreground/60 mb-1">XGBoost Accuracy</p>
          <h3 className="text-2xl font-bold text-foreground">{((metrics?.xgboost?.accuracy || 0) * 100).toFixed(1)}%</h3>
          <p className="text-[10px] text-foreground/40 mt-1 leading-tight">{t('ml.accuracyDesc')}</p>
          <div className="w-full bg-foreground/5 h-2 rounded-full mt-3 overflow-hidden">
            <div className="bg-success h-full transition-all" style={{ width: `${((metrics?.xgboost?.accuracy || 0) * 100)}%` }} />
          </div>
        </div>
        <div className="glass-panel p-6">
           <p className="text-sm font-medium text-foreground/60 mb-1">{t('ml.silhouette')}</p>
           <h3 className="text-2xl font-bold text-foreground">{(metrics?.kmeans?.silhouette || 0).toFixed(3)}</h3>
           <p className="text-[10px] text-foreground/40 mt-1 leading-tight">{t('ml.silhouetteDesc')}</p>
         </div>
        <div className="glass-panel p-6">
          <p className="text-sm font-medium text-foreground/60 mb-1">Last Trained</p>
          <h3 className="text-lg font-bold text-foreground">{metrics?.last_trained || "Just now"}</h3>
          <p className="text-xs text-success mt-2 flex items-center gap-1"><Activity size={12} /> Model Healthy</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <div className="mb-6">
            <h3 className="font-semibold">{t('ml.churnPred')}</h3>
            <p className="text-[10px] text-foreground/40 mt-1">{t('ml.churnPredDesc')}</p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={churnScores.slice(0, 20)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--foreground-rgb), 0.1)" vertical={false} />
                <XAxis dataKey="user_id" tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 8}} stroke="rgba(var(--foreground-rgb), 0.3)" interval="preserveStartEnd" />
                <YAxis stroke="rgba(var(--foreground-rgb), 0.3)" tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 10}} width={30} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--card-border)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                  itemStyle={{ color: 'var(--foreground)' }}
                  cursor={{fill: 'var(--foreground)', fillOpacity: 0.05}}
                  formatter={(value: any) => `${(Number(value) * 100).toFixed(1)}%`}
                />
                <Bar 
                  dataKey="churn_score" 
                  radius={[6, 6, 0, 0]} 
                  className="cursor-pointer transition-all duration-300 hover:opacity-80"
                  onClick={(data: any) => {
                    const query = lang === 'fr'
                      ? `Analyse le score de churn pour l'utilisateur ${data.user_id}. Pourquoi est-il de ${(data.churn_score * 100).toFixed(1)}% ?`
                      : `Analyze the churn score for user ${data.user_id}. Why is it ${(data.churn_score * 100).toFixed(1)}%?`;
                    window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
                  }}
                >
                  {churnScores.slice(0, 20).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.churn_score > 0.7 ? '#ef4444' : entry.churn_score > 0.4 ? '#f59e0b' : '#10b981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-6">
          <div className="mb-6">
            <h3 className="font-semibold">{t('ml.featureImportance')}</h3>
            <p className="text-[10px] text-foreground/40 mt-1">{t('ml.featureImportanceDesc')}</p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={
                  metrics?.xgboost?.feature_importance 
                    ? Object.entries(metrics.xgboost.feature_importance)
                        .map(([name, value]) => ({ 
                          name: name.replace(/_/g, ' ').replace('min', '').trim(), 
                          value: value as number 
                        }))
                        .sort((a, b) => b.value - a.value)
                    : []
                } 
                layout="vertical"
                margin={{ left: 30, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--foreground-rgb), 0.1)" horizontal={false} />
                <XAxis type="number" stroke="rgba(var(--foreground-rgb), 0.3)" tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 10}} />
                <YAxis dataKey="name" type="category" stroke="rgba(var(--foreground-rgb), 0.3)" tick={{fill: 'rgba(var(--foreground-rgb), 0.6)', fontSize: 10}} width={100} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--card-border)', borderRadius: '12px', backdropFilter: 'blur(10px)' }}
                  itemStyle={{ color: 'var(--foreground)' }}
                  formatter={(value: any) => (value as number).toFixed(4)}
                />
                <Bar 
                  dataKey="value" 
                  fill="var(--primary)" 
                  radius={[0, 6, 6, 0]} 
                  className="cursor-pointer transition-all duration-300 hover:opacity-80"
                  onClick={(data: any) => {
                    const query = lang === 'fr'
                      ? `Explique l'importance de la variable "${data.name}" dans le modèle XGBoost. Comment influence-t-elle la probabilité de churn ?`
                      : `Explain the importance of the "${data.name}" feature in the XGBoost model. How does it influence churn probability?`;
                    window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
                  }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {churnScores.length > 0 && <RecommendationSection userId={churnScores[0].user_id} />}
    </div>
  );
}

function RecommendationSection({ userId }: { userId: string }) {
  const { t, lang } = useLanguage();
  const [rec, setRec] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [triggered, setTriggered] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [feedback, setFeedback] = useState<boolean | null>(null);

  useEffect(() => {
    fetchRecommendation(userId, lang)
      .then(setRec)
      .finally(() => setLoading(false));
  }, [userId, lang]);

  const handleTrigger = async () => {
    if (!rec) return;
    setTriggering(true);
    try {
      const res = await triggerRecommendationCampaign(userId, rec.feature);
      if (res.status === 'success') {
        setTriggered(true);
      }
    } catch (e) {}
    setTriggering(false);
  };

  const handleFeedback = async (isHelpful: boolean) => {
    if (!rec || feedback !== null) return;
    try {
      await sendRecommendationFeedback(userId, rec.feature, isHelpful);
      setFeedback(isHelpful);
    } catch (e) {}
  };

  if (loading) return <div className="glass-panel p-6 animate-pulse bg-foreground/5 h-32" />;
  if (!rec) return null;

  return (
    <div className="glass-panel p-6 border-l-4 border-primary bg-primary/5 animate-in slide-in-from-right duration-500 relative overflow-hidden">
      {/* Background Decorative Sparkle */}
      <Sparkles className="absolute -right-4 -top-4 text-primary/10 w-24 h-24 rotate-12" />
      
      <div className="flex items-center justify-between mb-4 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/20 rounded-lg text-primary">
            <Sparkles size={20} />
          </div>
          <div>
            <h3 className="font-bold text-foreground">{t('seg.recommendation')}</h3>
            <p className="text-xs text-foreground/60">{t('seg.suggested')} for User {userId.slice(0, 8)}...</p>
          </div>
        </div>
        
        {/* Feedback Buttons */}
        <div className="flex items-center gap-2">
          <button 
            onClick={() => handleFeedback(true)}
            className={`p-2 rounded-lg transition-all ${feedback === true ? 'bg-success text-white' : 'bg-foreground/5 text-foreground/40 hover:text-success hover:bg-success/10'}`}
            disabled={feedback !== null}
          >
            <ThumbsUp size={16} />
          </button>
          <button 
            onClick={() => handleFeedback(false)}
            className={`p-2 rounded-lg transition-all ${feedback === false ? 'bg-danger text-white' : 'bg-foreground/5 text-foreground/40 hover:text-danger hover:bg-danger/10'}`}
            disabled={feedback !== null}
          >
            <ThumbsDown size={16} />
          </button>
        </div>
      </div>

      <div className="bg-foreground/5 p-4 rounded-xl border border-card-border relative z-10">
        <p className="text-sm text-foreground italic leading-relaxed">
          "{rec.message}"
        </p>
        <div className="mt-4 flex items-center justify-between">
          <span className="text-[10px] uppercase font-bold text-primary tracking-widest flex items-center gap-1">
            <Activity size={10} /> Feature: {rec.feature}
          </span>
          <button 
            onClick={handleTrigger}
            disabled={triggered || triggering}
            className={`text-[10px] font-bold text-white px-4 py-2 rounded-lg transition-all flex items-center gap-2 shadow-lg ${
              triggered ? 'bg-success shadow-success/20' : 'bg-primary hover:bg-primary/80 shadow-primary/20'
            } disabled:opacity-70`}
          >
            {triggering ? <Loader2 size={12} className="animate-spin" /> : triggered ? <Check size={12} /> : null}
            {triggered ? t('dec.campaignSent') : t('dec.triggerCampaign')}
          </button>
        </div>
      </div>
    </div>
  );
}

function DecisionEngineView() {
  const { t, lang } = useLanguage();
  const [rules, setRules] = useState<any[]>([]);
  const [suggesting, setSuggesting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [ruleToDelete, setRuleToDelete] = useState<number | null>(null);

  const loadRules = async () => {
    setLoading(true);
    try {
      const data = await fetchRules(lang);
      if (Array.isArray(data)) setRules(data);
    } catch (e) {}
    setLoading(false);
  };

  useEffect(() => {
    loadRules();
  }, [lang]);

  const handleAISuggest = async () => {
    setSuggesting(true);
    try {
      const res = await suggestRules(lang);
      if (res.status === "ok" || res.added > 0) {
        await loadRules();
      } else if (res.detail) {
        alert(`Erreur IA : ${res.detail}`);
      }
    } catch (e: any) {
      alert(`Erreur : ${e?.message || "Impossible de contacter l'IA"}`);
    }
    setSuggesting(false);
  };

  const handleTestAlerts = async () => {
    await triggerDemoNotifications();
  };

  const handleDelete = async (id: number) => {
    await deleteRule(id);
    loadRules();
    setRuleToDelete(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('dec.title')}</h1>
          <p className="text-foreground/60">{t('dec.subtitle')}</p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={handleTestAlerts} 
            className="glass-button px-4 py-2 rounded-lg flex items-center gap-2 border-success/30 text-success hover:bg-success/10"
          >
            <Bell size={18} /> {t('dec.testAlert')}
          </button>
          <button 
            onClick={handleAISuggest} 
            disabled={suggesting}
            className="glass-button px-4 py-2 rounded-lg flex items-center gap-2 bg-primary/20 text-white"
          >
            {suggesting ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
            {t('dec.suggestAI')}
          </button>
        </div>
      </div>

      <div className="glass-panel p-6 min-h-[400px] flex flex-col">
        <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
          <Network className="text-primary" size={20} /> {t('dec.activeRules')}
        </h3>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="animate-spin text-primary" size={48} />
          </div>
        ) : rules.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-foreground/40 italic">
             <p className="mb-2 text-center">{t('rules.noRules')}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {rules.map((rule) => (
              <div key={rule.id} className="p-6 bg-foreground/5 border border-card-border rounded-2xl flex items-center justify-between group">
                <div className="flex-1 pr-8">
                  <h4 className="text-foreground font-bold mb-1 text-lg">{rule.name}</h4>
                  <p className="text-foreground/60 text-sm leading-relaxed">{rule.description}</p>
                </div>
                <div className="flex items-center gap-4">
                   <span className="px-3 py-1 rounded-full text-[10px] font-bold uppercase bg-success/20 text-success border border-success/30">
                    {t('dec.enabled')}
                  </span>
                  <button 
                    onClick={() => setRuleToDelete(rule.id)}
                    className="p-2 text-foreground/20 hover:text-danger hover:bg-danger/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <button className="mt-8 flex items-center gap-2 text-primary hover:text-white transition-colors text-sm font-bold w-fit">
          <Plus size={18} /> {t('dec.addRule')}
        </button>

        <Modal 
          isOpen={ruleToDelete !== null}
          onClose={() => setRuleToDelete(null)}
          onConfirm={() => ruleToDelete && handleDelete(ruleToDelete)}
          title={t('dec.deleteTitle')}
          message={t('dec.deleteMsg')}
          confirmText={t('dec.deleteConfirm')}
          cancelText={t('dash.cancel')}
          type="danger"
        />
      </div>
    </div>
  );
}

function ProjectView() {
  const { t } = useLanguage();
  return (
    <div className="max-w-5xl space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-4xl font-bold text-foreground mb-4">{t('project.title')}</h1>
        <p className="text-xl text-foreground/60">{t('project.subtitle')}</p>
      </header>

      {/* Mission Section */}
      <section className="glass-panel p-8 border-primary/20 bg-primary/5">
        <h3 className="text-2xl font-bold text-primary mb-4 flex items-center gap-3">
          <Globe size={28}/> {t('project.vision')}
        </h3>
        <p className="text-lg text-foreground/80 leading-relaxed max-w-4xl mb-8">
          {t('project.visionDesc')}
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div className="bg-slate-800/50 p-6 rounded-xl border border-card-border">
            <h4 className="text-lg font-bold mb-2 text-amber-400">{t('project.saasTitle')}</h4>
            <p className="text-sm text-foreground/80 leading-relaxed">{t('project.saasDesc')}</p>
          </div>
          <div className="bg-slate-800/50 p-6 rounded-xl border border-card-border">
            <h4 className="text-lg font-bold mb-2 text-blue-400">{t('project.whatTitle')}</h4>
            <p className="text-sm text-foreground/80 leading-relaxed">{t('project.whatDesc')}</p>
          </div>
          <div className="bg-slate-800/50 p-6 rounded-xl border border-card-border">
            <h4 className="text-lg font-bold mb-2 text-emerald-400">{t('project.howTitle')}</h4>
            <p className="text-sm text-foreground/80 leading-relaxed">{t('project.howDesc')}</p>
          </div>
          <div className="bg-slate-800/50 p-6 rounded-xl border border-card-border">
            <h4 className="text-lg font-bold mb-2 text-purple-400">{t('project.whyTitle')}</h4>
            <p className="text-sm text-foreground/80 leading-relaxed">{t('project.whyDesc')}</p>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="space-y-6">
        <h3 className="text-2xl font-bold text-foreground flex items-center gap-3">
          <Network size={28} className="text-secondary"/> {t('project.modulesTitle')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((num) => (
            <div key={num} className="glass-panel p-6">
              <div className="w-10 h-10 rounded-xl bg-foreground/5 flex items-center justify-center text-primary font-bold mb-4">
                0{num}
              </div>
              <h4 className="text-lg font-bold text-foreground mb-2">{t(`project.module${num}`)}</h4>
              <p className="text-sm text-foreground/60 leading-relaxed">{t(`project.module${num}Desc`)}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Infrastructure Section */}
      <section className="space-y-6">
        <h3 className="text-2xl font-bold text-foreground flex items-center gap-3">
          <Server size={28} className="text-success"/> {t('project.infraTitle')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-panel p-6 border-t-2 border-t-[#4285F4]">
             <h4 className="font-bold text-foreground mb-2 flex items-center gap-2"><Cloud size={18} className="text-[#4285F4]"/> Google Cloud Run</h4>
             <p className="text-sm text-foreground/60">{t('project.cloudRunDesc')}</p>
          </div>
          <div className="glass-panel p-6 border-t-2 border-t-[#336791]">
             <h4 className="font-bold text-foreground mb-2 flex items-center gap-2"><Database size={18} className="text-[#336791]"/> Cloud SQL (PostgreSQL)</h4>
             <p className="text-sm text-foreground/60">{t('project.dbDesc')}</p>
          </div>
          <div className="glass-panel p-6 border-t-2 border-t-primary">
             <h4 className="font-bold text-foreground mb-2 flex items-center gap-2"><DatabaseZap size={18} className="text-primary"/> {t('project.dataSeedTitle')}</h4>
             <p className="text-sm text-foreground/60">{t('project.dataSeedDesc')}</p>
          </div>
        </div>
      </section>

      {/* Bottom Grid: Tech & Glossary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Tech Stack */}
        <section className="glass-panel p-6">
          <h3 className="text-xl font-bold text-foreground mb-6 flex items-center gap-2">
            <Settings size={20} className="text-foreground/40"/> {t('project.tech')}
          </h3>
          <p className="text-sm text-foreground/60 mb-6">{t('project.techList')}</p>
          <div className="flex flex-wrap gap-3">
            {['FastAPI', 'Python', 'XGBoost', 'K-Means', 'Next.js 14', 'PostgreSQL', 'OpenAI GPT-4o'].map(tech => (
              <span key={tech} className="px-3 py-1.5 rounded-lg bg-foreground/5 border border-card-border text-xs font-medium text-foreground/80">
                {tech}
              </span>
            ))}
          </div>
        </section>

        {/* Glossary Quick View */}
        <section className="glass-panel p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Book size={20} className="text-foreground/40"/> {t('project.lexicon')}
          </h3>
          <div className="space-y-4">
            {['churn', 'engagement', 'breadth'].map(key => (
              <div key={key}>
                <p className="text-sm font-bold text-white">{t(`project.lex.${key}`)}</p>
                <p className="text-xs text-foreground/60">{t(`project.lex.${key}Desc`)}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Data Strategy */}
      <section className="p-6 bg-foreground/5 rounded-2xl border border-card-border flex items-center gap-6">
        <div className="p-4 bg-primary/10 rounded-2xl text-primary shrink-0">
          <Activity size={32} />
        </div>
        <div>
          <h4 className="font-bold text-white mb-1">{t('project.dataSource')}</h4>
          <p className="text-sm text-foreground/60">{t('project.originDesc')}</p>
        </div>
      </section>
    </div>
  );
}

function RetentionView() {
  const { t, lang } = useLanguage();
  const [cohorts, setCohorts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCohorts, setSelectedCohorts] = useState<string[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchCohorts()
      .then(data => Array.isArray(data) ? setCohorts(data) : setCohorts([]))
      .catch(() => setCohorts([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getHeatmapColor = (value: number) => {
    if (value === 100) return 'bg-primary';
    if (value >= 80) return 'bg-primary/80';
    if (value >= 60) return 'bg-primary/60';
    if (value >= 40) return 'bg-primary/40';
    if (value >= 20) return 'bg-primary/20';
    return 'bg-foreground/5';
  };

  const filteredCohorts = selectedCohorts.length > 0 
    ? cohorts.filter(c => selectedCohorts.includes(c.cohort)) 
    : cohorts;

  const avgW1 = filteredCohorts.length > 0 
    ? filteredCohorts.reduce((acc, c) => acc + (c.retention[1] || 0), 0) / filteredCohorts.length 
    : 0;
  
  const bestCohort = filteredCohorts.length > 0
    ? [...filteredCohorts].sort((a, b) => (b.retention[4] || 0) - (a.retention[4] || 0))[0]
    : null;

  const toggleCohort = (cohort: string) => {
    if (selectedCohorts.includes(cohort)) {
      setSelectedCohorts(selectedCohorts.filter(c => c !== cohort));
    } else {
      setSelectedCohorts([...selectedCohorts, cohort]);
    }
  };

  return (
    <div className="space-y-8 pb-20">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold mb-2">{t('ret.title')}</h1>
          <p className="text-foreground/60">{t('ret.subtitle')}</p>
        </div>

        <div className="relative" ref={dropdownRef}>
          <button 
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="glass-button px-4 py-2 text-sm flex items-center gap-3 font-bold border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all"
          >
            <Filter size={16} className={selectedCohorts.length > 0 ? "text-primary" : "text-foreground/40"} />
            {selectedCohorts.length === 0 ? (lang === 'fr' ? 'Toutes les cohortes' : 'All Cohorts') : `${selectedCohorts.length} ${lang === 'fr' ? 'sélectionnées' : 'selected'}`}
            <ChevronDown size={14} className={`transition-transform duration-300 ${isDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {isDropdownOpen && (
            <div className="absolute top-full right-0 mt-2 w-64 glass-panel p-2 shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-200">
              <div className="p-2 border-b border-card-border flex justify-between items-center mb-1">
                 <span className="text-[10px] uppercase font-bold text-foreground/40 tracking-widest">{lang === 'fr' ? 'SÉLECTION' : 'SELECT COHORTS'}</span>
                 <div className="flex gap-3">
                   <button 
                     onClick={() => setSelectedCohorts(cohorts.map(c => c.cohort))} 
                     className="text-[9px] text-primary hover:text-white uppercase font-bold transition-colors"
                   >
                     {lang === 'fr' ? 'Tout' : 'All'}
                   </button>
                   {selectedCohorts.length > 0 && (
                     <button 
                       onClick={() => setSelectedCohorts([])} 
                       className="text-[9px] text-foreground/40 hover:text-danger uppercase font-bold transition-colors"
                     >
                       {lang === 'fr' ? 'Vider' : 'Clear'}
                     </button>
                   )}
                 </div>
              </div>
              <div className="max-h-64 overflow-y-auto custom-scrollbar p-1">
                {cohorts.map(c => (
                  <label 
                    key={c.cohort} 
                    className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all hover:bg-foreground/5 group ${selectedCohorts.includes(c.cohort) ? 'bg-primary/5' : ''}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded border flex items-center justify-center transition-all ${selectedCohorts.includes(c.cohort) ? 'bg-primary border-primary' : 'border-card-border bg-foreground/5 group-hover:border-white/30'}`}>
                        {selectedCohorts.includes(c.cohort) && <Check size={10} className="text-white" />}
                      </div>
                      <span className={`text-sm ${selectedCohorts.includes(c.cohort) ? 'text-primary font-bold underline decoration-primary/30 underline-offset-4' : 'text-foreground/60'}`}>{c.cohort}</span>
                    </div>
                    <span className="text-[10px] font-mono text-foreground/30">{c.size} users</span>
                    <input 
                      type="checkbox" 
                      className="hidden"
                      checked={selectedCohorts.includes(c.cohort)}
                      onChange={() => toggleCohort(c.cohort)}
                    />
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {!loading && cohorts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in duration-500">
          <div 
            className="glass-panel p-6 border-l-4 border-success"
            onClick={() => {
              const query = lang === 'fr' 
                ? `Analyse mon taux de rétention moyen en semaine 1 (${avgW1.toFixed(1)}%). Est-ce un bon score pour un SaaS ?`
                : `Analyze my average Week 1 retention rate (${avgW1.toFixed(1)}%). Is this a good score for a SaaS?`;
              window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
            }}
          >
            <div className="flex justify-between items-start">
              <p className="text-[10px] uppercase font-bold text-foreground/40 mb-1 tracking-widest">{t('ret.avgW1')}</p>
            </div>
            <h3 className="text-3xl font-bold text-foreground">{avgW1.toFixed(1)}%</h3>
            <p className="text-[10px] text-success mt-2 font-bold">↑ {t('dash.vsLastMonth')}</p>
          </div>

          <div 
            className="glass-panel p-6 border-l-4 border-primary"
            onClick={() => {
              const query = lang === 'fr' 
                ? `Pourquoi la cohorte ${bestCohort?.cohort} est-elle la plus performante avec ${bestCohort?.size} utilisateurs ?`
                : `Why is cohort ${bestCohort?.cohort} performing the best with ${bestCohort?.size} users?`;
              window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
            }}
          >
            <div className="flex justify-between items-start">
              <p className="text-[10px] uppercase font-bold text-foreground/40 mb-1 tracking-widest">{t('ret.bestCohort')}</p>
              <Sparkles size={12} className="text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <h3 className="text-3xl font-bold text-foreground">{bestCohort?.cohort || "—"}</h3>
            <p className="text-[10px] text-primary mt-2 font-bold">{bestCohort?.size} users</p>
          </div>

          <div 
            className="glass-panel p-6 border-l-4 border-secondary cursor-pointer hover:border-secondary/50 hover:bg-secondary/5 transition-all group"
            onClick={() => {
              const query = lang === 'fr' 
                ? `Explique-moi comment lire cette analyse de cohorte et quelles sont les colonnes les plus importantes.`
                : `Explain how to read this cohort analysis and which columns are the most important.`;
              window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
            }}
          >
            <div className="flex justify-between items-start">
              <p className="text-[10px] uppercase font-bold text-foreground/40 mb-1 tracking-widest">{t('ret.howTo')}</p>
              <Sparkles size={12} className="text-secondary opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <p className="text-[11px] text-white/70 leading-relaxed mt-2">{t('ret.howToDesc')}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex-1 flex items-center justify-center min-h-[400px]">
          <Loader2 className="animate-spin text-primary" size={48} />
        </div>
      ) : filteredCohorts.length === 0 ? (
        <div className="glass-panel p-12 text-center text-foreground/40 italic">
          {cohorts.length === 0 ? t('ret.empty') : (lang === 'fr' ? 'Aucune cohorte ne correspond à votre sélection.' : 'No cohorts match your selection.')}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="glass-panel overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="bg-foreground/5 border-b border-card-border">
                  <th className="p-4 text-xs font-bold uppercase text-foreground/60">Cohorte</th>
                  <th className="p-4 text-xs font-bold uppercase text-foreground/60">{t('ret.size')}</th>
                  {[0, 1, 2, 3, 4, 5, 6, 7, 8].map(w => (
                    <th key={w} className="p-4 text-xs font-bold uppercase text-foreground/60 text-center">
                      {t('ret.week')} {w}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredCohorts.map((c, idx) => (
                  <tr key={c.cohort || idx} className="border-b border-card-border hover:bg-foreground/5 transition-colors">
                    <td className="p-4 font-mono text-sm font-bold text-white/90">{c.cohort}</td>
                    <td className="p-4 text-sm font-medium text-foreground/40">{c.size}</td>
                    {Array.from({ length: 9 }).map((_, wIndex) => {
                      const value = c.retention[wIndex];
                      const isAvailable = value !== undefined;
                      return (
                        <td key={wIndex} className="p-1">
                          <div 
                            className={`h-12 w-full rounded-lg flex items-center justify-center text-xs font-bold transition-all hover:scale-105 cursor-pointer ${isAvailable ? getHeatmapColor(value) : 'opacity-5'}`}
                            onClick={() => {
                              if (!isAvailable) return;
                              const query = lang === 'fr' 
                                ? `Analyse la rétention de la cohorte ${c.cohort} à la semaine ${wIndex}. Nous sommes à ${Math.round(value)}%, est-ce une performance normale ou une anomalie ?`
                                : `Analyze the retention for cohort ${c.cohort} at week ${wIndex}. We are at ${Math.round(value)}%, is this a normal performance or an anomaly?`;
                              window.dispatchEvent(new CustomEvent('insightforge-query', { detail: query }));
                            }}
                          >
                            {isAvailable ? `${Math.round(value)}%` : '—'}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-panel p-6 bg-primary/5 border-primary/20">
              <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles size={16} className="text-primary" /> {t('ret.insights')}
              </h4>
              <ul className="space-y-3">
                <li className="flex items-start gap-3 text-xs text-foreground/80 leading-relaxed">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                  {t('ret.insight1')}
                </li>
                <li className="flex items-start gap-3 text-xs text-foreground/80 leading-relaxed">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                  {t('ret.insight2')}
                </li>
              </ul>
            </div>
            
            <div className="glass-panel p-6 flex flex-col justify-center items-center text-center">
              <p className="text-xs text-foreground/60 mb-4">{t('copilot.reasoning')}</p>
              <button 
                onClick={() => window.dispatchEvent(new CustomEvent('insightforge-query', { detail: lang === 'fr' ? 'Analyse ma rétention globale et suggère 3 actions prioritaires.' : 'Analyze my overall retention and suggest 3 priority actions.' }))}
                className="glass-button px-6 py-2 rounded-xl text-sm font-bold flex items-center gap-2 bg-primary/20 text-white"
              >
                <Brain size={18} /> {t('dec.suggestAI')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SettingsView() {
  const { t, theme, setTheme } = useLanguage();
  
  const themes = [
    { id: 'midnight', color: 'bg-[#007db8]' },
    { id: 'ocean', color: 'bg-[#0ea5e9]' },
    { id: 'emerald', color: 'bg-[#10b981]' },
    { id: 'corporate', color: 'bg-[#3b82f6]' },
    { id: 'academic', color: 'bg-[#475569]' },
    { id: 'corporate-light', color: 'bg-[#2563eb]' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
      <h1 className="text-4xl font-bold text-foreground">{t('nav.settings')}</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Profile Section */}
        <div className="glass-panel p-8">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
            <Users size={20} className="text-primary" /> {t('set.profile')}
          </h3>
          <div className="space-y-6">
            <div className="flex items-center gap-4 p-4 bg-foreground/5 rounded-2xl border border-card-border">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-2xl font-bold text-white shadow-xl shadow-primary/20">
                JD
              </div>
              <div>
                <p className="text-lg font-bold text-foreground">John Doe</p>
                <p className="text-sm text-foreground/40">{t('set.admin')}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <button className="glass-button py-3 rounded-xl text-sm font-bold">{t('set.edit')}</button>
              <button className="glass-button py-3 rounded-xl text-sm font-bold bg-danger/10 text-danger border-danger/20 hover:bg-danger hover:text-white transition-all">
                {t('set.delete')}
              </button>
            </div>
          </div>
        </div>

        {/* Appearance Section */}
        <div className="glass-panel p-8">
          <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
            <Globe size={20} className="text-primary" /> {t('set.theme')}
          </h3>
          <p className="text-sm text-foreground/40 mb-8">{t('set.themeDesc')}</p>
          
          <div className="grid grid-cols-1 gap-3">
            {themes.map((th) => (
              <button
                key={th.id}
                onClick={() => setTheme(th.id)}
                className={`flex items-center justify-between p-4 rounded-2xl border transition-all group ${
                  theme === th.id 
                    ? 'bg-primary/10 border-primary shadow-lg shadow-primary/10' 
                    : 'bg-foreground/5 border-card-border hover:border-white/20'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full ${th.color} shadow-lg group-hover:scale-110 transition-transform`} />
                  <span className={`font-bold transition-colors ${theme === th.id ? 'text-foreground' : 'text-foreground/60'}`}>
                    {t(`theme.${th.id}`)}
                  </span>
                </div>
                {theme === th.id && (
                  <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center animate-in zoom-in duration-300">
                    <Check size={14} className="text-white" />
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function LoginView({ onLogin }: { onLogin: () => void }) {
  const { t } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await login(email, password);
      if (res.access_token) {
        localStorage.setItem('if_token', res.access_token);
        onLogin();
      } else {
        setError(t('login.error'));
      }
    } catch (e) {
      setError("Server Error");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass-panel p-8 w-full max-w-md animate-in fade-in zoom-in duration-300">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-primary/20">
            <Lock className="text-primary" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-2">{t('login.title')}</h1>
          <p className="text-foreground/60">{t('login.subtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs uppercase font-bold text-foreground/80 mb-2 block">{t('login.email')}</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-foreground/60" size={18} />
              <input 
                type="email" required
                value={email} onChange={e => setEmail(e.target.value)}
                className="w-full bg-black/5 dark:bg-foreground/5 border border-black/20 dark:border-white/20 rounded-lg py-3 pl-10 pr-4 text-foreground focus:outline-none focus:border-primary/50 transition-colors"
                placeholder="admin@acme.com"
              />
            </div>
          </div>

          <div>
            <label className="text-xs uppercase font-bold text-foreground/80 mb-2 block">{t('login.password')}</label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 text-foreground/60" size={18} />
              <input 
                type="password" required
                value={password} onChange={e => setPassword(e.target.value)}
                className="w-full bg-black/5 dark:bg-foreground/5 border border-black/20 dark:border-white/20 rounded-lg py-3 pl-10 pr-4 text-foreground focus:outline-none focus:border-primary/50 transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && <p className="text-danger text-sm text-center font-medium bg-danger/10 py-2 rounded border border-danger/20">{error}</p>}

          <button 
            type="submit" 
            disabled={loading}
            className="glass-button w-full py-3 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 mt-6"
          >
            {loading ? <Loader2 size={20} className="animate-spin" /> : <Lock size={20} />}
            {t('login.button')}
          </button>
        </form>
        <p className="text-[10px] text-center mt-6 text-foreground/60 italic">{t('login.demo')}</p>
      </div>
    </div>
  );
}

export default function Home() {
  const [auth, setAuth] = useState(false);
  const [init, setInit] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('if_token');
    if (token) setAuth(true);
    setInit(true);
  }, []);

  if (!init) return null;

  return (
    <LanguageProvider>
      <HomeContent auth={auth} setAuth={setAuth} />
    </LanguageProvider>
  );
}

function HomeContent({ auth, setAuth }: { auth: boolean, setAuth: (v: boolean) => void }) {
  const { theme } = useLanguage();

  useEffect(() => {
    // Sync theme to root and body for maximum compatibility
    const themeClass = theme === 'midnight' ? '' : `theme-${theme}`;
    
    // Cleanup old theme classes
    ['theme-ocean', 'theme-emerald', 'theme-corporate', 'theme-cyberpunk', 'theme-mckinsey', 'theme-academic', 'theme-corporate-light'].forEach(c => {
      document.documentElement.classList.remove(c);
      document.body.classList.remove(c);
    });

    if (themeClass) {
      document.documentElement.classList.add(themeClass);
      document.body.classList.add(themeClass);
    }
  }, [theme]);

  return (
    <main className="min-h-screen">
      {!auth ? (
        <LoginView onLogin={() => setAuth(true)} />
      ) : (
        <AppContent onLogout={() => { localStorage.removeItem('if_token'); setAuth(false); }} />
      )}
    </main>
  );
}

function AppContent({ onLogout }: { onLogout: () => void }) {
  const { t, lang, theme } = useLanguage();
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
      case "ml": return <MLView />;
      case "decision": return <DecisionEngineView />;
      case "retention": return <RetentionView />;
      case "project": return <ProjectView />;
      case "settings": return <SettingsView />;
      default: return <DashboardView />;
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden relative w-full">
      <Sidebar activeView={currentView} onViewChange={handleViewChange} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <header className="h-16 flex items-center justify-between px-8 border-b border-card-border bg-background/50 backdrop-blur-md z-10 shrink-0">
          <div className="flex items-center gap-4">
             <h2 className="text-foreground/40 text-xs font-bold uppercase tracking-widest">{t('nav.' + currentView)}</h2>
          </div>
          <div className="flex items-center gap-6">
            <NotificationBell />
            <div className="h-4 w-px bg-white/10" />
            <button 
              onClick={onLogout}
              className="text-foreground/40 hover:text-danger flex items-center gap-2 text-sm transition-colors group"
            >
              <LogOut size={18} className="group-hover:translate-x-1 transition-transform" />
              {t('nav.signOut')}
            </button>
          </div>
        </header>
        
        <div className="flex-1 flex overflow-hidden p-8 gap-8">
          {/* Main Content Area */}
          <main className={`flex-1 overflow-y-auto custom-scrollbar transition-all duration-300 transform ${animateState === 'in' ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}`}>
            <div className="max-w-[1200px] mx-auto pb-20">
              {renderView()}
            </div>
          </main>

          {/* Persistent AI Copilot Sidebar */}
          <aside className="w-[400px] hidden xl:block shrink-0 h-full animate-in slide-in-from-right duration-500">
            <AICopilot />
          </aside>
        </div>
      </div>
    </div>
  );
}

function NotificationBell() {
  const { t } = useLanguage();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [show, setShow] = useState(false);
  const [showClearModal, setShowClearModal] = useState(false);
  const unreadCount = notifications.filter(n => !n.read).length;
  const dropdownRef = useRef<HTMLDivElement>(null);
  const bellRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
        bellRef.current && !bellRef.current.contains(event.target as Node)
      ) {
        setShow(false);
      }
    };

    if (show) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [show]);

  const load = () => {
    fetchNotifications().then(data => {
      if (Array.isArray(data)) setNotifications(data);
    });
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const handleRead = async (id: number) => {
    await markNotificationRead(id);
    load();
  };

  const handleClearAll = async () => {
    await clearNotifications();
    load();
  };

  return (
    <div className="relative">
      <button 
        ref={bellRef}
        onClick={() => setShow(!show)}
        className="relative p-2 text-foreground/60 hover:text-white transition-colors"
      >
        <Bell size={20} className={unreadCount > 0 ? 'animate-bounce' : ''} />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-danger text-white text-[10px] font-bold rounded-full flex items-center justify-center border-2 border-background">
            {unreadCount}
          </span>
        )}
      </button>

      {show && (
        <div ref={dropdownRef} className="absolute right-0 mt-4 w-80 glass-panel p-0 overflow-hidden animate-in fade-in slide-in-from-top-4 duration-300 z-50">
          <div className="p-4 border-b border-card-border flex justify-between items-center bg-foreground/5">
            <div className="flex items-center gap-3">
              <h4 className="font-bold text-sm">{t('notif.title')}</h4>
              <span className="text-[10px] bg-primary/20 text-primary px-2 py-0.5 rounded-full font-bold">{unreadCount} {t('notif.new')}</span>
            </div>
            {notifications.length > 0 && (
              <button 
                onClick={() => setShowClearModal(true)}
                className="text-foreground/40 hover:text-danger transition-colors p-1"
                title={t('notif.clearConfirm')}
              >
                <Trash2 size={14} />
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto custom-scrollbar">
            {notifications.length === 0 ? (
              <p className="p-8 text-center text-sm text-foreground/40 italic">{t('notif.empty')}</p>
            ) : (
              notifications.map(n => (
                <div key={n.id} className={`p-4 border-b border-card-border hover:bg-foreground/5 transition-colors ${!n.read ? 'bg-primary/5' : ''}`}>
                  <div className="flex justify-between items-start mb-1">
                    <p className={`text-xs font-bold ${n.type === 'danger' ? 'text-danger' : n.type === 'success' ? 'text-success' : 'text-white'}`}>{n.title}</p>
                    {!n.read && <button onClick={() => handleRead(n.id)} className="text-primary hover:text-white transition-colors"><Check size={14} /></button>}
                  </div>
                  <p className="text-[11px] text-foreground/60 leading-relaxed">{n.message}</p>
                  <p className="text-[9px] text-foreground/30 mt-2">{new Date(n.created_at).toLocaleTimeString()}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
      
      <Modal 
        isOpen={showClearModal}
        onClose={() => setShowClearModal(false)}
        onConfirm={handleClearAll}
        title={t('notif.clearTitle')}
        message={t('notif.clearMsg')}
        confirmText={t('notif.clearConfirm')}
        cancelText={t('dash.cancel')}
        type="danger"
      />
    </div>
  );
}
