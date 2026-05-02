"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, AlertTriangle, CheckCircle, Lightbulb } from "lucide-react";
import { askAI } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";

type Message = {
  id: string;
  role: "user" | "ai";
  content: string;
  decisions?: any[];
  executionResults?: any[];
  followUps?: string[];
};

export default function AICopilot() {
  const { t, lang } = useLanguage();
  
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
    <div className="flex flex-col h-full min-h-[600px] glass-panel overflow-hidden">
      <div className="p-4 border-b border-white/10 bg-white/5 flex items-center space-x-2">
        <Bot className="text-primary" size={24} />
        <h3 className="font-semibold text-lg">{t('copilot.header')}</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <div className={`max-w-[85%] rounded-2xl p-4 ${
              msg.role === "user" 
                ? "bg-primary text-white rounded-br-none" 
                : "bg-white/10 text-foreground rounded-bl-none"
            }`}>
              <div className="flex items-center space-x-2 mb-1 opacity-70 text-xs">
                {msg.role === "user" ? <User size={12} /> : <Bot size={12} />}
                <span>{msg.role === "user" ? t('copilot.you') : t('copilot.ai')}</span>
              </div>
              <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
              
              {msg.decisions && msg.decisions.length > 0 && (
                <div className="mt-4 space-y-2">
                  <div className="text-xs font-semibold opacity-70 uppercase tracking-wider">{t('copilot.decisions')}</div>
                  {msg.decisions.map((dec, idx) => (
                    <div key={idx} className={`p-2 rounded border text-xs flex items-start space-x-2 ${
                      dec.type === 'alert' ? 'bg-danger/10 border-danger/30 text-danger-foreground' : 'bg-warning/10 border-warning/30 text-warning-foreground'
                    }`}>
                      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                      <div>
                        <span className="font-semibold capitalize">{dec.type}:</span> {dec.message}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {msg.executionResults && msg.executionResults.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
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
                      className="text-xs px-3 py-1.5 rounded-full border border-primary/30 bg-primary/10 hover:bg-primary/20 text-primary-foreground transition-colors text-left"
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

      <div className="p-4 border-t border-white/10 bg-white/5">
        {messages.length === 1 && !isLoading && (
          <div className="mb-3 flex flex-wrap gap-2">
            {suggestedPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => sendQuery(prompt)}
                className="text-xs px-3 py-1.5 rounded-full border border-white/20 bg-white/5 hover:bg-white/10 transition-colors"
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
            className="w-full bg-white/10 border border-white/20 rounded-full py-3 pl-4 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white placeholder-white/40"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full glass-button text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
