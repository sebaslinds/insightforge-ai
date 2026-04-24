import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const EXAMPLE_QUESTIONS = [
  "Top products by revenue",
  "Revenue by category",
  "Which products have the lowest revenue?",
];

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const chartData = useMemo(() => {
    if (!result?.data || !result?.chart?.x || !result?.chart?.y) {
      return [];
    }

    return result.data
      .filter((row) => row[result.chart.x] !== undefined && row[result.chart.y] !== undefined)
      .map((row) => ({
        [result.chart.x]: String(row[result.chart.x]),
        [result.chart.y]: Number(row[result.chart.y]) || 0,
      }));
  }, [result]);

  async function askQuestion(questionToAsk = question) {
    const trimmedQuestion = questionToAsk.trim();

    if (!trimmedQuestion) {
      setError("Enter a question to analyze.");
      return;
    }

    setQuestion(trimmedQuestion);
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: trimmedQuestion }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Unable to get an answer.");
      }

      setResult(payload);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await askQuestion();
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <header className="header">
          <div>
            <p className="eyebrow">BI Copilot</p>
            <h1>Ask questions about e-commerce sales</h1>
          </div>
        </header>

        <form className="ask-form" onSubmit={handleSubmit}>
          <input
            aria-label="Business question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Show product revenue"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Analyzing..." : "Ask"}
          </button>
        </form>

        <div className="examples" aria-label="Example questions">
          {EXAMPLE_QUESTIONS.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => askQuestion(example)}
              disabled={isLoading}
            >
              {example}
            </button>
          ))}
        </div>

        {error && <p className="error">{error}</p>}

        {result && (
          <section className="results" aria-live="polite">
            <section className="insight-panel">
              <span>AI Insight</span>
              <p>{cleanInsight(result.insight)}</p>
            </section>

            <div className="sql-panel">
              <span>Generated SQL</span>
              <pre>{result.sql}</pre>
            </div>

            <div className="visual-grid">
              <section className="panel">
                <div className="panel-header">
                  <h2>{getChartTitle(result.chart)}</h2>
                </div>
                <div className="chart-wrap">
                  {chartData.length > 0 && result.chart?.type !== "table" ? (
                    <ChartRenderer chart={result.chart} data={chartData} />
                  ) : (
                    <p className="empty-state">No chartable fields returned.</p>
                  )}
                </div>
              </section>

              <section className="panel">
                <div className="panel-header">
                  <h2>Results</h2>
                </div>
                <DataTable rows={result.data} />
              </section>
            </div>
          </section>
        )}

        <footer className="footer">Powered by Gemini, FastAPI, PostgreSQL, and Recharts.</footer>
      </section>
    </main>
  );
}

function ChartRenderer({ chart, data }) {
  if (chart.type === "line") {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey={chart.x} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey={chart.y} stroke="#2563eb" strokeWidth={3} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 12, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey={chart.x} />
        <YAxis />
        <Tooltip />
        <Bar dataKey={chart.y} fill="#2563eb" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function getChartTitle(chart) {
  if (!chart || chart.type === "table") {
    return "Visualization";
  }

  return `${formatLabel(chart.y)} by ${formatLabel(chart.x)}`;
}

function formatLabel(value) {
  return value
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function cleanInsight(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/^\s*[-*]\s+/gm, "")
    .replace(/^\s*\d+\.\s+/gm, "")
    .trim();
}

function DataTable({ rows }) {
  if (!rows?.length) {
    return <p className="empty-state">No rows returned.</p>;
  }

  const columns = Object.keys(rows[0]);

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={`${row.product || "row"}-${rowIndex}`}>
              {columns.map((column) => (
                <td key={column}>{String(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
