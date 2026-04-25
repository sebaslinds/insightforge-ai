import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const SENTINEL_API_BASE_URL =
  import.meta.env.VITE_SENTINEL_API_BASE_URL || "http://localhost:8001";
const EXAMPLE_QUESTIONS = [
  "Top products by revenue",
  "Revenue by category",
  "Which products have the lowest revenue?",
];
const EXAMPLE_SERIES = "10, 12, 11, 13, 100, 12, 11, 200, 9";

function App() {
  const [activeModule, setActiveModule] = useState("overview");

  return (
    <main className="app-shell">
      <section className="workspace">
        <header className="platform-header">
          <div>
            <p className="eyebrow">InsightForge AI</p>
            <h1>Data intelligence workspace</h1>
          </div>
          <nav className="module-tabs" aria-label="InsightForge modules">
            <button
              type="button"
              className={activeModule === "overview" ? "active" : ""}
              onClick={() => setActiveModule("overview")}
            >
              Overview
            </button>
            <button
              type="button"
              className={activeModule === "bi" ? "active" : ""}
              onClick={() => setActiveModule("bi")}
            >
              BI Copilot
            </button>
            <button
              type="button"
              className={activeModule === "sentinel" ? "active" : ""}
              onClick={() => setActiveModule("sentinel")}
            >
              Data Sentinel
            </button>
          </nav>
        </header>

        {activeModule === "overview" && <PlatformOverview setActiveModule={setActiveModule} />}
        {activeModule === "bi" && <BiCopilot />}
        {activeModule === "sentinel" && <DataSentinel />}

        <footer className="footer">Powered by Gemini, FastAPI, Scikit-learn, and Recharts.</footer>
      </section>
    </main>
  );
}

function PlatformOverview({ setActiveModule }) {
  const [services, setServices] = useState({
    bi: { label: "BI Copilot API", status: "checking" },
    sentinel: { label: "Data Sentinel API", status: "checking" },
  });

  useEffect(() => {
    let isMounted = true;

    async function checkService(key, url) {
      try {
        const response = await fetch(`${url}/health`);
        if (!response.ok) {
          throw new Error("Health check failed.");
        }
        if (isMounted) {
          setServices((current) => ({
            ...current,
            [key]: { ...current[key], status: "online" },
          }));
        }
      } catch {
        if (isMounted) {
          setServices((current) => ({
            ...current,
            [key]: { ...current[key], status: "offline" },
          }));
        }
      }
    }

    checkService("bi", API_BASE_URL);
    checkService("sentinel", SENTINEL_API_BASE_URL);

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <section className="module-view">
      <header className="module-header">
        <div>
          <p className="eyebrow">Platform Overview</p>
          <h2>One workspace for data exploration and monitoring</h2>
        </div>
      </header>

      <div className="overview-grid">
        <ServiceCard
          title="BI Copilot"
          description="Ask business questions, generate read-only SQL, and turn sales data into charts and insights."
          status={services.bi.status}
          docsUrl={`${API_BASE_URL}/docs`}
          onOpen={() => setActiveModule("bi")}
        />
        <ServiceCard
          title="Data Sentinel"
          description="Scan numeric signals for unusual values using Isolation Forest anomaly detection."
          status={services.sentinel.status}
          docsUrl={`${SENTINEL_API_BASE_URL}/docs`}
          onOpen={() => setActiveModule("sentinel")}
        />
      </div>

      <section className="panel workflow-panel">
        <div className="panel-header">
          <h2>Platform Flow</h2>
        </div>
        <div className="workflow-steps">
          <div>
            <span>1</span>
            <p>Explore sales performance with natural language questions.</p>
          </div>
          <div>
            <span>2</span>
            <p>Review generated SQL, tables, charts, and AI insight.</p>
          </div>
          <div>
            <span>3</span>
            <p>Monitor numeric signals and flag anomalous values.</p>
          </div>
        </div>
      </section>
    </section>
  );
}

function ServiceCard({ title, description, status, docsUrl, onOpen }) {
  return (
    <section className="panel service-card">
      <div className="service-topline">
        <h2>{title}</h2>
        <span className={`status-pill ${status}`}>{formatStatus(status)}</span>
      </div>
      <p>{description}</p>
      <div className="service-actions">
        <button type="button" onClick={onOpen}>
          Open
        </button>
        <a href={docsUrl} target="_blank" rel="noreferrer">
          API Docs
        </a>
      </div>
    </section>
  );
}

function BiCopilot() {
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
    <section className="module-view">
      <header className="module-header">
        <div>
          <p className="eyebrow">BI Copilot</p>
          <h2>Ask questions about e-commerce sales</h2>
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
    </section>
  );
}

function DataSentinel() {
  const [series, setSeries] = useState(EXAMPLE_SERIES);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const parsedSeries = useMemo(() => parseSentinelInput(series), [series]);
  const chartData = useMemo(
    () => {
      if (result?.series?.length) {
        return result.series.map((point) => ({
          index: point.index,
          label: point.timestamp || String(point.index),
          value: point.value,
          anomaly: point.is_anomaly ? point.value : null,
          anomaly_score: point.anomaly_score,
          threshold: result.threshold,
          status: point.is_anomaly ? "anomaly" : "normal",
        }));
      }

      return parsedSeries.map((point, index) => ({
        index: index + 1,
        label: point.timestamp || String(index + 1),
        value: getPointValue(point),
        anomaly: null,
        anomaly_score: null,
        threshold: 0,
        status: "pending",
      }));
    },
    [parsedSeries, result],
  );

  async function detectAnomalies(event) {
    event.preventDefault();

    if (!parsedSeries.length) {
      setError("Enter at least one numeric value.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${SENTINEL_API_BASE_URL}/detect`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ data: parsedSeries }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail || "Unable to detect anomalies.");
      }

      setResult(payload);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="module-view">
      <header className="module-header">
        <div>
          <p className="eyebrow sentinel">Data Sentinel</p>
          <h2>Detect unusual values in a numeric series</h2>
        </div>
      </header>

      <form className="sentinel-form" onSubmit={detectAnomalies}>
        <label htmlFor="series-input">Numeric series or timestamp,value rows</label>
        <textarea
          id="series-input"
          value={series}
          onChange={(event) => setSeries(event.target.value)}
          rows={4}
        />
        <div className="form-actions">
          <button type="button" onClick={() => setSeries(EXAMPLE_SERIES)} disabled={isLoading}>
            Example
          </button>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Scanning..." : "Detect"}
          </button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="results" aria-live="polite">
          <section className="insight-panel sentinel-summary">
            <span>Anomaly Summary</span>
            <p>
              {result.anomalies.length
                ? `${result.anomalies.length} anomalous value${
                    result.anomalies.length > 1 ? "s" : ""
                  } detected: ${result.anomalies.map(formatAnomalyLabel).join(", ")}.`
                : "No anomalous values were detected."}
            </p>
            <p>{result.explanation}</p>
          </section>

          <div className="visual-grid">
            <section className="panel">
              <div className="panel-header">
                <h2>Signal</h2>
              </div>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="label" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="anomaly"
                      stroke="#dc2626"
                      strokeWidth={0}
                      dot={{ r: 6, fill: "#dc2626", strokeWidth: 0 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>Anomaly Scores</h2>
              </div>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="label" />
                    <YAxis />
                    <Tooltip />
                    <ReferenceLine y={result.threshold} stroke="#dc2626" strokeDasharray="4 4" />
                    <Line
                      type="monotone"
                      dataKey="anomaly_score"
                      stroke="#047857"
                      strokeWidth={3}
                      dot={{ r: 3 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>

          <section className="panel">
            <div className="panel-header">
              <h2>Scored Values</h2>
            </div>
            <DataTable
              rows={chartData.map((row) => ({
                index: row.index,
                timestamp: row.label,
                value: row.value,
                anomaly_score:
                  row.anomaly_score === null ? "pending" : Number(row.anomaly_score).toFixed(6),
                status: row.status,
              }))}
            />
          </section>
        </section>
      )}
    </section>
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

function formatAnomalyLabel(anomaly) {
  const value = Number(anomaly.value).toString();
  return anomaly.timestamp ? `${value} at ${anomaly.timestamp}` : value;
}

function getPointValue(point) {
  return typeof point === "number" ? point : point.value;
}

function parseSentinelInput(value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return [];
  }

  const lines = trimmed
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const timestampRows = lines
    .map((line) => line.split(",").map((part) => part.trim()))
    .filter((parts) => parts.length === 2 && !Number.isFinite(Number(parts[0])));

  if (timestampRows.length === lines.length) {
    return timestampRows
      .map(([timestamp, rawValue]) => ({ timestamp, value: Number(rawValue) }))
      .filter((point) => Number.isFinite(point.value));
  }

  return trimmed
    .split(/[\s,;]+/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map(Number)
    .filter((item) => Number.isFinite(item));
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

function formatStatus(status) {
  if (status === "online") {
    return "Online";
  }
  if (status === "offline") {
    return "Offline";
  }
  return "Checking";
}

createRoot(document.getElementById("root")).render(<App />);
