"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

export type Language = 'en' | 'fr';

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: string) => string;
}

export const LanguageContext = createContext<LanguageContextType>({} as LanguageContextType);

export const translations: Record<Language, Record<string, string>> = {
  en: {
    'nav.dashboard': 'Dashboard',
    'nav.segments': 'Segments',
    'nav.copilot': 'Copilot',
    'nav.ml': 'ML Models',
    'nav.decision': 'Decision Engine',
    'nav.settings': 'Settings',
    
    'dash.overview': 'Overview',
    'dash.subtitle': 'InsightForge AI Analytics Dashboard',
    'dash.last30': 'Last 30 Days',
    'dash.genReport': 'Generate Report',
    'dash.revenue': 'Total Revenue',
    'dash.users': 'Active Users',
    'dash.engagement': 'Engagement Score',
    'dash.churn': 'Churn Risk',
    'dash.vsLastMonth': 'vs last month',
    'dash.revTrend': 'Revenue Trend',
    'dash.userSeg': 'User Segmentation',
    'granularity.year': 'Year',
    'granularity.month': 'Month',
    'granularity.week': 'Week',
    'granularity.day': 'Day',
    
    'ml.title': 'ML Models',
    'ml.subtitle': 'Manage XGBoost and K-Means models.',
    'ml.churn': 'Churn Predictor (XGBoost)',
    'ml.accuracy': 'Accuracy',
    'ml.lastTrained': 'Last Trained',
    'ml.status': 'Status',
    'ml.active': 'Active',
    'ml.retrain': 'Retrain Model',
    'ml.seg': 'Segmentation (K-Means)',
    'ml.clusters': 'Clusters',
    'ml.silhouette': 'Silhouette Score',
    'ml.update': 'Update Clusters',
    
    'dec.title': 'Decision Engine config',
    'dec.subtitle': 'Configure rules and automation triggers.',
    'dec.activeRules': 'Active Rules',
    'dec.highAnomaly': 'High Anomaly Alert',
    'dec.highAnomalyDesc': 'Triggers Slack alert when anomaly confidence > 0.8',
    'dec.lowRev': 'Low Revenue Recommendation',
    'dec.lowRevDesc': 'Logs a recommendation if daily revenue drops below $1000',
    'dec.enabled': 'Enabled',
    'dec.addRule': 'Add New Rule',
    
    'copilot.title': 'AI Copilot Fullscreen',
    'copilot.subtitle': 'Chat directly with the Decision Engine.',
    'copilot.header': 'Decision Copilot',
    'copilot.you': 'You',
    'copilot.ai': 'InsightForge AI',
    'copilot.decisions': 'Engine Decisions',
    'copilot.actions': 'Automated Actions',
    'copilot.suggested': 'Suggested follow-ups:',
    'copilot.reasoning': 'Engine reasoning...',
    'copilot.placeholder': 'Type your command or question...',
    
    'seg.title': 'User Segments',
    'seg.subtitle': 'Detailed view of your user clusters.',
    'seg.explorer': 'Segment Explorer',
    'seg.explorerDesc': 'Select a segment to view detailed user lists and ML insights.',
    'seg.load': 'Load Segment Data',
    
    'set.title': 'Settings',
    'set.subtitle': 'Manage application preferences.',
    'set.config': 'Configuration',
    'set.configDesc': 'API Keys, integrations and general settings go here.'
  },
  fr: {
    'nav.dashboard': 'Tableau de bord',
    'nav.segments': 'Segments',
    'nav.copilot': 'Copilote',
    'nav.ml': 'Modèles ML',
    'nav.decision': 'Moteur de décision',
    'nav.settings': 'Paramètres',
    
    'dash.overview': 'Vue d\'ensemble',
    'dash.subtitle': 'Tableau de bord analytique InsightForge AI',
    'dash.last30': '30 derniers jours',
    'dash.genReport': 'Générer le rapport',
    'dash.revenue': 'Revenus totaux',
    'dash.users': 'Utilisateurs actifs',
    'dash.engagement': 'Score d\'engagement',
    'dash.churn': 'Risque d\'attrition',
    'dash.vsLastMonth': 'vs mois dernier',
    'dash.revTrend': 'Tendance des revenus',
    'dash.userSeg': 'Segmentation',
    'granularity.year': 'Année',
    'granularity.month': 'Mois',
    'granularity.week': 'Semaine',
    'granularity.day': 'Jour',
    
    'ml.title': 'Modèles d\'apprentissage',
    'ml.subtitle': 'Gérer les modèles XGBoost et K-Means.',
    'ml.churn': 'Prédiction d\'attrition',
    'ml.accuracy': 'Précision',
    'ml.lastTrained': 'Dernier entraînement',
    'ml.status': 'Statut',
    'ml.active': 'Actif',
    'ml.retrain': 'Réentraîner le modèle',
    'ml.seg': 'Segmentation',
    'ml.clusters': 'Clusters',
    'ml.silhouette': 'Score de Silhouette',
    'ml.update': 'Mettre à jour',
    
    'dec.title': 'Configuration Moteur Décision',
    'dec.subtitle': 'Configurer les règles et déclencheurs.',
    'dec.activeRules': 'Règles actives',
    'dec.highAnomaly': 'Alerte d\'anomalie élevée',
    'dec.highAnomalyDesc': 'Envoie une alerte Slack si confiance > 0.8',
    'dec.lowRev': 'Alerte revenus faibles',
    'dec.lowRevDesc': 'Journalise une recommandation si revenus < 1000$',
    'dec.enabled': 'Activé',
    'dec.addRule': 'Ajouter une règle',
    
    'copilot.title': 'Copilote IA',
    'copilot.subtitle': 'Discutez directement avec le moteur de décision.',
    'copilot.header': 'Copilote de décision',
    'copilot.you': 'Vous',
    'copilot.ai': 'IA InsightForge',
    'copilot.decisions': 'Décisions du moteur',
    'copilot.actions': 'Actions automatisées',
    'copilot.suggested': 'Suivis suggérés:',
    'copilot.reasoning': 'Raisonnement...',
    'copilot.placeholder': 'Tapez votre commande ou question...',
    
    'seg.title': 'Segments Utilisateurs',
    'seg.subtitle': 'Vue détaillée de vos clusters utilisateurs.',
    'seg.explorer': 'Explorateur de segments',
    'seg.explorerDesc': 'Sélectionnez un segment pour voir les détails.',
    'seg.load': 'Charger les données',
    
    'set.title': 'Paramètres',
    'set.subtitle': 'Gérer les préférences de l\'application.',
    'set.config': 'Configuration',
    'set.configDesc': 'Clés API, intégrations et paramètres.'
  }
};

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Language>('en');
  
  const t = (key: string) => {
    return translations[lang][key] || key;
  };
  
  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
