
import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [cases, setCases] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [dashboardRes, transactionRes, alertRes, caseRes] =
        await Promise.all([
          fetch(`${API}/api/dashboard`),
          fetch(`${API}/api/transactions?limit=50`),
          fetch(`${API}/api/alerts?limit=50`),
          fetch(`${API}/api/cases?limit=50`),
        ]);

      if (
        !dashboardRes.ok ||
        !transactionRes.ok ||
        !alertRes.ok ||
        !caseRes.ok
      ) {
        throw new Error("The backend returned an error.");
      }

      const [dashboardData, transactionData, alertData, caseData] =
        await Promise.all([
          dashboardRes.json(),
          transactionRes.json(),
          alertRes.json(),
          caseRes.json(),
        ]);

      setDashboard(dashboardData);
      setTransactions(transactionData);
      setAlerts(alertData);
      setCases(caseData);
    } catch (err) {
      setError(
        "Unable to connect to the backend. Please check that the FastAPI server is running."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function updateCase(caseId, status) {
    try {
      const response = await fetch(`${API}/api/cases/${caseId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status,
          disposition: status === "RESOLVED" ? "RESOLVED" : null,
          comments: "Updated from risk monitoring dashboard",
        }),
      });

      if (!response.ok) {
        throw new Error("Case update failed");
      }

      await loadData();
    } catch (err) {
      alert("Unable to update this case. Please try again.");
    }
  }

  const money = (amount, currency = "INR") =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(Number(amount || 0));

  const date = (value) =>
    value ? new Date(value).toLocaleString("en-IN") : "—";

  const riskClass = (level) =>
    String(level || "low").toLowerCase();

  function Metric({ label, value, detail, color }) {
    return (
      <div className="metric-card">
        <div className="metric-top">
          <span>{label}</span>
          <span className={`metric-dot ${color}`} />
        </div>
        <div className="metric-value">
          {Number(value || 0).toLocaleString("en-IN")}
        </div>
        <div className="metric-detail">{detail}</div>
      </div>
    );
  }

  if (loading && !dashboard) {
    return <div className="loading-screen">Loading risk intelligence dashboard...</div>;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">Y</div>
          <div>
            <h2>YottaFlex</h2>
            <span>RISK INTELLIGENCE</span>
          </div>
        </div>

        <div className="nav-heading">WORKSPACE</div>

        <button
          className={activeTab === "overview" ? "nav-item active" : "nav-item"}
          onClick={() => setActiveTab("overview")}
        >
          <span>▦</span> Overview
        </button>

        <button
          className={activeTab === "transactions" ? "nav-item active" : "nav-item"}
          onClick={() => setActiveTab("transactions")}
        >
          <span>⇄</span> Transactions
        </button>

        <button
          className={activeTab === "alerts" ? "nav-item active" : "nav-item"}
          onClick={() => setActiveTab("alerts")}
        >
          <span>◉</span> Risk Alerts
          <span className="nav-count">{dashboard?.open_alerts || 0}</span>
        </button>

        <button
          className={activeTab === "cases" ? "nav-item active" : "nav-item"}
          onClick={() => setActiveTab("cases")}
        >
          <span>▤</span> Case Management
        </button>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="online-dot" />
            API connected
          </div>
          <span className="sidebar-version">Version 1.0.0</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="breadcrumb">Risk Intelligence / {activeTab}</div>
            <h1>
              {activeTab === "overview" && "Risk Overview"}
              {activeTab === "transactions" && "Transaction Monitoring"}
              {activeTab === "alerts" && "Risk Alerts"}
              {activeTab === "cases" && "Case Management"}
            </h1>
          </div>

          <div className="topbar-actions">
            <span className="live-indicator">
              <span className="online-dot" /> LIVE DATA
            </span>
            <button className="refresh-button" onClick={loadData}>
              ↻ Refresh
            </button>
          </div>
        </header>

        {error && <div className="error-banner">{error}</div>}

        {activeTab === "overview" && dashboard && (
          <>
            <section className="welcome-panel">
              <div>
                <div className="eyebrow">TRANSACTION RISK MONITORING</div>
                <h2>Financial activity. Clearer decisions.</h2>
                <p>
                  Monitor transactions, identify suspicious activity and
                  manage risk investigations from one workspace.
                </p>
              </div>
              <div className="welcome-symbol">◎</div>
            </section>

            <section className="metrics-grid">
              <Metric
                label="Total Customers"
                value={dashboard.total_customers}
                detail="Registered customers"
                color="blue"
              />
              <Metric
                label="Total Accounts"
                value={dashboard.total_accounts}
                detail="Monitored accounts"
                color="purple"
              />
              <Metric
                label="Transactions"
                value={dashboard.total_transactions}
                detail="Transactions recorded"
                color="green"
              />
              <Metric
                label="Total Alerts"
                value={dashboard.total_alerts}
                detail="Risk alerts generated"
                color="orange"
              />
              <Metric
                label="Open Alerts"
                value={dashboard.open_alerts}
                detail="Awaiting review"
                color="red"
              />
              <Metric
                label="Open Cases"
                value={dashboard.open_cases}
                detail="Open investigations"
                color="yellow"
              />
            </section>

            <section className="content-grid">
              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Recent Risk Alerts</h3>
                    <p>Highest risk scores first</p>
                  </div>
                  <button
                    className="text-button"
                    onClick={() => setActiveTab("alerts")}
                  >
                    View all →
                  </button>
                </div>

                {alerts.slice(0, 6).map((alert) => (
                  <div className="alert-row" key={alert.alert_id}>
                    <div>
                      <strong>{alert.alert_id}</strong>
                      <p>{alert.rule_name || alert.explanation || "Risk detected"}</p>
                    </div>
                    <div className="alert-score">
                      <span className={`risk-badge ${riskClass(alert.risk_level)}`}>
                        {alert.risk_level}
                      </span>
                      <strong>{alert.risk_score}/100</strong>
                    </div>
                  </div>
                ))}

                {alerts.length === 0 && <p className="empty-state">No alerts found.</p>}
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h3>Investigation Summary</h3>
                    <p>Case management snapshot</p>
                  </div>
                  <span className="summary-icon">▤</span>
                </div>

                <div className="summary-number">{cases.length}</div>
                <p className="summary-caption">Cases loaded</p>

                <div className="summary-line">
                  <span>Open cases</span>
                  <strong>{dashboard.open_cases}</strong>
                </div>
                <div className="summary-line">
                  <span>Open alerts</span>
                  <strong>{dashboard.open_alerts}</strong>
                </div>

                <button
                  className="primary-button full-button"
                  onClick={() => setActiveTab("cases")}
                >
                  Manage investigations →
                </button>
              </div>
            </section>

            <section className="panel table-panel">
              <div className="panel-heading">
                <div>
                  <h3>Latest Transactions</h3>
                  <p>Recent activity across monitored accounts</p>
                </div>
                <button
                  className="text-button"
                  onClick={() => setActiveTab("transactions")}
                >
                  View transactions →
                </button>
              </div>
              <TransactionTable
                transactions={transactions.slice(0, 8)}
                money={money}
                date={date}
              />
            </section>
          </>
        )}

        {activeTab === "transactions" && (
          <section className="panel table-panel">
            <div className="panel-heading">
              <div>
                <h3>Transaction Records</h3>
                <p>Showing up to 50 latest transactions</p>
              </div>
              <span className="record-count">{transactions.length} records</span>
            </div>
            <TransactionTable
              transactions={transactions}
              money={money}
              date={date}
            />
          </section>
        )}

        {activeTab === "alerts" && (
          <section className="panel table-panel">
            <div className="panel-heading">
              <div>
                <h3>Risk Alert Register</h3>
                <p>Risk scores and rule-based explanations</p>
              </div>
              <span className="record-count">{alerts.length} alerts</span>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Alert ID</th>
                    <th>Customer</th>
                    <th>Transaction</th>
                    <th>Risk score</th>
                    <th>Risk level</th>
                    <th>Rule / Explanation</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => (
                    <tr key={alert.alert_id}>
                      <td className="id-cell">{alert.alert_id}</td>
                      <td>{alert.customer_id}</td>
                      <td>{alert.transaction_id || "No transaction"}</td>
                      <td><strong>{alert.risk_score}/100</strong></td>
                      <td>
                        <span className={`risk-badge ${riskClass(alert.risk_level)}`}>
                          {alert.risk_level}
                        </span>
                      </td>
                      <td>{alert.rule_name || alert.explanation || "—"}</td>
                      <td>{alert.alert_status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {activeTab === "cases" && (
          <section className="panel table-panel">
            <div className="panel-heading">
              <div>
                <h3>Investigation Cases</h3>
                <p>Review and update case status</p>
              </div>
              <span className="record-count">{cases.length} cases</span>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Customer</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Disposition</th>
                    <th>Created</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {cases.map((item) => (
                    <tr key={item.case_id}>
                      <td className="id-cell">{item.case_id}</td>
                      <td>{item.customer_id}</td>
                      <td>
                        <span className={`risk-badge ${riskClass(item.priority)}`}>
                          {item.priority}
                        </span>
                      </td>
                      <td>{item.case_status}</td>
                      <td>{item.disposition || "Pending"}</td>
                      <td>{date(item.created_at)}</td>
                      <td>
                        {item.case_status !== "RESOLVED" &&
                        item.case_status !== "CLOSED" ? (
                          <button
                            className="resolve-button"
                            onClick={() => updateCase(item.case_id, "RESOLVED")}
                          >
                            Resolve
                          </button>
                        ) : (
                          <span className="resolved-label">Completed</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        <footer className="footer">
          <span>YottaFlex Transaction Risk Intelligence</span>
          <span>Synthetic demonstration data · Rule-based risk scoring</span>
        </footer>
      </main>
    </div>
  );
}

function TransactionTable({ transactions, money, date }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Transaction ID</th>
            <th>Customer</th>
            <th>Merchant</th>
            <th>Amount</th>
            <th>Type</th>
            <th>Status</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.transaction_id}>
              <td className="id-cell">{transaction.transaction_id}</td>
              <td>
                <strong>{transaction.customer_name || "Unknown"}</strong>
                <small>{transaction.customer_id}</small>
              </td>
              <td>{transaction.merchant_name || "—"}</td>
              <td className="amount-cell">
                {money(transaction.amount, transaction.currency || "INR")}
              </td>
              <td>{transaction.transaction_type}</td>
              <td>
                <span className="status-badge">
                  {transaction.transaction_status}
                </span>
              </td>
              <td>{date(transaction.transaction_timestamp)}</td>
            </tr>
          ))}
          {transactions.length === 0 && (
            <tr>
              <td colSpan="7" className="empty-state">
                No transactions found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
