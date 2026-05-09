"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, AlertTriangle, CheckCircle, Lightbulb, Target, BarChart as BarChartIcon, PieChart as PieChartIcon, Activity as ActivityIcon } from "lucide-react";
import { askAI } from "@/lib/api";
import { useLanguage, THEME_COLORS } from "@/lib/i18n";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

type Message = {
  id: string;
  role: "user" | "ai";
  content: string;
  decisions?: any[];
  executionResults?: any[];
  followUps?: string[];
};

function ChatVisualizer({ jsonStr }: { jsonStr: string }) {
  const { theme } = useLanguage();
  const colors = THEME_COLORS[theme] || THEME_COLORS.midnight;
  const [shouldRender, setShouldRender] = useState(false);

  useEffect(() => {
    // Delay rendering to allow chat animation to finish and container to have dimensions
    const timer = setTimeout(() => setShouldRender(true), 200);
    return () => clearTimeout(timer);
  }, []);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className={`theme-${theme} bg-background/95 backdrop-blur-md border border-card-border p-3 rounded-xl shadow-2xl z-50`}>
          <p className="text-foreground font-black mb-1 border-b border-foreground/20 pb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-primary text-sm font-bold flex justify-between gap-4">
              <span className="opacity-70">{entry.name}:</span>
              <span>{new Intl.NumberFormat().format(entry.value)}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  try {
    const data = JSON.parse(jsonStr);
    if (!data.type || !data.items || !Array.isArray(data.items) || data.items.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-[160px] text-foreground/40 text-xs gap-2">
          <BarChartIcon size={24} className="opacity-20" />
          <span>Données de visualisation non disponibles</span>
        </div>
      );
    }

    if (!shouldRender) {
      return <div className="h-[160px] w-full flex items-center justify-center"><Loader2 className="animate-spin text-primary/40" /></div>;
    }

    if (data.type === 'area') {
      const processedData = data.items.map((item: any) => ({
        ...item,
        value: Number(item.value)
      }));
      return (
        <div className="h-[160px] w-[260px] mx-auto relative">
          <ResponsiveContainer width="100%" height="100%" key={jsonStr}>
            <AreaChart data={processedData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="chatColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.primary} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={colors.primary} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--foreground-rgb), 0.1)" vertical={false} />
              <XAxis dataKey="name" stroke="rgba(var(--foreground-rgb), 0.2)" fontSize={10} tickLine={false} axisLine={false} tick={{fill: 'rgba(var(--foreground-rgb), 0.5)'}} />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="value" stroke={colors.primary} strokeWidth={2} fillOpacity={1} fill="url(#chatColor)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (data.type === 'pie') {
      const PIE_COLORS = [colors.primary || '#3b82f6', colors.secondary || '#10b981', '#f59e0b', '#ef4444', '#10b981'];
      const processedData = data.items.map((item: any) => ({
        ...item,
        value: Number(item.value)
      }));
      
      return (
        <div className="h-[160px] w-[260px] mx-auto relative">
          <ResponsiveContainer width="100%" height="100%" key={jsonStr}>
            <PieChart>
              <Pie
                data={processedData}
                cx="50%" cy="50%" innerRadius={40} outerRadius={60}
                paddingAngle={5} dataKey="value" stroke="none"
              >
                {processedData.map((_: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (data.type === 'bar') {
      const processedData = data.items.map((item: any) => ({
        ...item,
        value: Number(item.value)
      }));
      return (
        <div className="h-[160px] w-[260px] mx-auto relative">
          <ResponsiveContainer width="100%" height="100%" key={jsonStr}>
            <BarChart data={processedData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(var(--foreground-rgb), 0.1)" vertical={false} />
              <XAxis dataKey="name" stroke="rgba(var(--foreground-rgb), 0.2)" fontSize={10} tickLine={false} axisLine={false} tick={{fill: 'rgba(var(--foreground-rgb), 0.5)'}} />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill={colors.primary} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    return null;
  } catch (e) {
    return null;
  }
}

export default function AICopilot() {
  const { t, lang, theme } = useLanguage();
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "ai",
      content: lang === 'fr' 
        ? "Bonjour ! Je suis le Copilote IA InsightForge. Posez-moi des questions sur vos utilisateurs ou vos revenus."
        : "Hello! I am the InsightForge AI Copilot. Ask me anything about your users, revenue, or churn risk.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleExternalQuery = (event: CustomEvent) => {
      if (event.detail && typeof event.detail === 'string') {
        sendQuery(event.detail);
      }
    };
    window.addEventListener('insightforge-query' as any, handleExternalQuery);
    return () => window.removeEventListener('insightforge-query' as any, handleExternalQuery);
  }, []);

  useEffect(() => {
    setMessages(prev => {
      if (prev.length === 1 && prev[0].id === "1") {
        return [{
          ...prev[0],
          content: lang === 'fr' 
            ? "Bonjour ! Je suis le Copilote IA InsightForge. Posez-moi des questions sur vos utilisateurs ou vos revenus."
            : "Hello! I am the InsightForge AI Copilot. Ask me anything about your users, revenue, or churn risk."
        }];
      }
      return prev;
    });
  }, [lang]);

  const sendQuery = async (query: string) => {
    if (!query.trim()) return;

    const userMessage: Message = { id: Date.now().toString(), role: "user", content: query };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await askAI(userMessage.content, lang);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: response.explanation || "Query executed successfully.",
        decisions: response.decisions,
        executionResults: response.execution_results,
        followUps: response.follow_ups
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        content: "Sorry, I encountered an error connecting to the Decision Engine.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendQuery(input);
  };

  const suggestedPrompts = lang === 'fr' ? [
    "Quel est le risque d'attrition actuel pour les Power Users ?",
    "Montre-moi les utilisateurs avec un score d'engagement < 30.",
    "Quelles fonctionnalités sont les plus utilisées par les plans Enterprise ?"
  ] : [
    "What is the current churn risk for Power Users?",
    "Show me users with engagement score < 30.",
    "Which features are most used by Enterprise plans?"
  ];

  return (
    <div className="flex flex-col h-full glass-panel overflow-hidden">
      <div className="p-3 border-b border-card-border bg-foreground/5 flex items-center space-x-2">
        <Bot style={{ color: 'var(--primary)' }} size={20} />
        <h3 className="font-semibold text-base">{t('copilot.header')}</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-4 custom-scrollbar">
        {messages.map((msg, index) => (
          <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <div className={`max-w-[90%] rounded-2xl p-4 ${
              msg.role === "user" 
                ? "bg-primary text-primary-foreground rounded-br-none" 
                : "bg-foreground/10 text-foreground rounded-bl-none"
            }`}>
              <div className="flex items-center space-x-2 mb-1 opacity-70 text-xs">
                {msg.role === "user" ? <User size={12} /> : <Bot size={12} />}
                <span>{msg.role === "user" ? t('copilot.you') : t('copilot.ai')}</span>
              </div>
              
              <div className={`markdown-content text-sm leading-relaxed prose ${theme.includes('light') || theme === 'academic' ? '' : 'prose-invert'} prose-sm max-w-none`}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content.split('```json')[0]}</ReactMarkdown>
              </div>

              {msg.content.includes('```json') && (
                <div className="mt-4 bg-background/40 p-4 rounded-2xl border border-card-border w-full min-h-[180px] flex flex-col justify-center">
                  <ChatVisualizer jsonStr={msg.content.split('```json')[1].split('```')[0]} />
                </div>
              )}
              
              {msg.decisions && msg.decisions.length > 0 && (
                <div className="mt-4 space-y-2">
                  <div className="text-xs font-semibold opacity-70 uppercase tracking-wider">{t('copilot.decisions')}</div>
                  {msg.decisions.map((dec, idx) => (
                    <div key={idx} className={`p-2 rounded border text-xs flex items-start space-x-2 ${
                      dec.type === 'alert' ? 'bg-danger/10 border-danger/30 text-danger-foreground' : 'bg-warning/10 border-warning/30 text-warning-foreground'
                    }`}>
                      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                      <div className="flex-1">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-semibold capitalize">{dec.type}:</span>
                          {dec.confidence && (
                            <div className="flex items-center gap-1 text-[10px] font-bold text-white/40">
                              <Target size={10} /> {(dec.confidence * 100).toFixed(0)}%
                            </div>
                          )}
                        </div>
                        <p className="mb-2">{dec.message}</p>
                        {dec.confidence && (
                          <div className="w-full bg-black/20 h-1 rounded-full overflow-hidden">
                            <div 
                              className={`h-full transition-all duration-500 ${dec.type === 'alert' ? 'bg-danger' : 'bg-warning'}`}
                              style={{ width: `${dec.confidence * 100}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {msg.executionResults && msg.executionResults.length > 0 && (
                <div className="mt-3 pt-3 border-t border-card-border">
                  <div className="text-xs font-semibold opacity-70 uppercase tracking-wider mb-2">{t('copilot.actions')}</div>
                  {msg.executionResults.map((res, idx) => (
                    <div key={idx} className="flex items-center space-x-2 text-xs text-success">
                      <CheckCircle size={12} />
                      <span>{res.action.replace('_', ' ')} - <span className="uppercase font-semibold">{res.status}</span></span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {msg.role === "ai" && msg.followUps && msg.followUps.length > 0 && index === messages.length - 1 && (
              <div className="mt-3 space-y-2 pl-2">
                <div className="text-xs flex items-center space-x-1 text-foreground/60">
                  <Lightbulb size={12} />
                  <span>{t('copilot.suggested')}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {msg.followUps.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => sendQuery(prompt)}
                      className="text-sm px-3 py-1.5 rounded-full border border-primary/30 bg-primary/10 hover:bg-primary/20 text-primary transition-colors text-left font-medium"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white/10 rounded-2xl rounded-bl-none p-4 flex items-center space-x-2">
              <Loader2 className="animate-spin text-primary" size={16} />
              <span className="text-sm">{t('copilot.reasoning')}</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 border-t border-card-border bg-foreground/5">
        {messages.length === 1 && !isLoading && (
          <div className="mb-2 flex flex-wrap gap-2">
            {suggestedPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => sendQuery(prompt)}
                className="text-[10px] px-2.5 py-1 rounded-full border border-card-border bg-foreground/5 hover:bg-foreground/10 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        )}
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('copilot.placeholder')}
            className="w-full bg-foreground/5 border border-card-border rounded-xl py-2 pl-4 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-primary/50 text-foreground placeholder-foreground/40"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 p-1.5 rounded-lg bg-primary text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
}
