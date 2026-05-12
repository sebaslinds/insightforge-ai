const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Gestion du token
const getAuthHeader = () => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('if_token');
    if (token) return { 'Authorization': `Bearer ${token}` };
  }
  return {};
};

const fetchWithAuth = async (url: string, options: any = {}) => {
  const headers = {
    ...options.headers,
    ...getAuthHeader(),
  };
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('if_token');
      window.location.reload(); // Force le retour au login
    }
  }
  return res.json();
};

export const login = async (email: string, pass: string) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', pass);

  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
};

export const askAI = async (question: string, language: string = 'en') => {
  return fetchWithAuth(`${API_URL}/ask/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, language }),
  });
};

export const fetchMLMetrics = () => fetchWithAuth(`${API_URL}/ml/metrics`);
export const fetchChurnScores = () => fetchWithAuth(`${API_URL}/ml/churn-scores`);
export const fetchChurnDistribution = () => fetchWithAuth(`${API_URL}/ml/churn-distribution`);
export const fetchSegments = () => fetchWithAuth(`${API_URL}/ml/segments`);
export const triggerTraining = () => fetchWithAuth(`${API_URL}/ml/train`, { method: 'POST' });
export const fetchRevenueTrend = (g = "month") => fetchWithAuth(`${API_URL}/analytics/revenue-trend?granularity=${g}`);
export const fetchSummary = (g = "month") => fetchWithAuth(`${API_URL}/analytics/summary?granularity=${g}`);
export const fetchRules = (lang: string = "en") => fetchWithAuth(`${API_URL}/analytics/rules?lang=${lang}`);
export const suggestRules = (l = "en") => fetchWithAuth(`${API_URL}/analytics/suggest-rules?lang=${l}`, { method: 'POST' });
export const deleteRule = (id: number) => fetchWithAuth(`${API_URL}/analytics/rules/${id}`, { method: 'DELETE' });
export const generateReport = (lang: string = "en") => fetchWithAuth(`${API_URL}/analytics/generate-report?lang=${lang}`);
export const fetchConversions = () => fetchWithAuth(`${API_URL}/analytics/conversions`);

// Notifications
export const fetchNotifications = () => fetchWithAuth(`${API_URL}/notifications`);
export const markNotificationRead = (id: number) => fetchWithAuth(`${API_URL}/notifications/${id}/read`, { method: 'POST' });
export const clearNotifications = () => fetchWithAuth(`${API_URL}/notifications`, { method: 'DELETE' });
export const triggerDemoNotifications = () => fetchWithAuth(`${API_URL}/notifications/trigger-demo`, { method: 'POST' });
export const fetchRecommendation = (userId: string, lang: string = 'en') => fetchWithAuth(`${API_URL}/ml/recommendations/${userId}?lang=${lang}`);
export const triggerRecommendationCampaign = (userId: string, feature: string) => fetchWithAuth(`${API_URL}/ml/recommendations/trigger`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, feature }),
});

export const fetchCohorts = () => fetchWithAuth(`${API_URL}/analytics/cohorts`);

export const sendRecommendationFeedback = (userId: string, feature: string, isHelpful: boolean) => fetchWithAuth(`${API_URL}/ml/recommendations/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, feature, is_helpful: isHelpful }),
});
