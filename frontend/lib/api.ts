export const askAI = async (question: string, language: string = 'en') => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ask/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, language }),
  });
  if (!response.ok) throw new Error('Ask API error');
  return response.json();
};

export const fetchMLMetrics = async () => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ml/metrics`);
  if (!response.ok) throw new Error('ML metrics error');
  return response.json();
};

export const fetchChurnScores = async () => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ml/churn-scores`);
  if (!response.ok) throw new Error('Churn scores error');
  return response.json();
};

export const fetchSegments = async () => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ml/segments`);
  if (!response.ok) throw new Error('Segments error');
  return response.json();
};

export const triggerTraining = async () => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/ml/train`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Training error');
  return response.json();
};
