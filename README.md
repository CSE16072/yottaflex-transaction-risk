# YottaFlex Transaction Risk Intelligence

A three-tier financial transaction monitoring and risk intelligence application built with **Python, FastAPI, SQLite, React, and Vite**.

The application helps identify suspicious financial transactions, calculate explainable risk scores, reconcile transfers, and support analyst investigations through a centralized dashboard.

## Project Overview

YottaFlex Transaction Risk Intelligence provides a structured solution for monitoring financial activity and managing potential transaction risks.

### Architecture

The application follows a three-tier architecture:

| Layer | Technology | Responsibility |
|---|---|---|
| Database | SQLite | Stores customers, accounts, transactions, alerts, cases, and audit records |
| Backend | Python, FastAPI | Provides REST APIs, risk scoring, reconciliation, and case management |
| Frontend | React, Vite, JavaScript | Displays dashboards and enables analyst interactions |

**Architecture flow:**

Frontend → FastAPI Backend → SQLite Database

## Key Features

- **Transaction Monitoring:** Manages and displays financial transaction activity.
- **Risk Scoring:** Calculates explainable risk scores using configurable risk indicators.
- **Risk Classification:** Classifies transactions into LOW, MEDIUM, and HIGH risk levels.
- **Risk Alerts:** Supports monitoring and reviewing suspicious activities.
- **Case Management:** Supports case updates and analyst investigation workflows.
- **Transfer Reconciliation:** Compares transfer amounts against debit and credit transaction legs.
- **Audit History:** Preserves analyst actions and case update history.
- **Data Validation:** Checks generated records, foreign-key relationships, and planted anomalies.
- **Interactive Dashboard:** Provides an interface for reviewing transactions, alerts, and cases.

## Dataset

The project uses reproducible synthetic financial data generated with a fixed random seed (`20261022`).

| Entity | Records |
|---|---:|
| Customers | 5,000 |
| Accounts | 7,000 |
| Merchants | 100 |
| Devices | 2,000 |
| Transactions | 100,000 |
| Transfer Links | 100 |
| Risk Rules | 5 |
| Alerts | 1,000 |
| Cases | 1,000 |
| Case Alerts | 1,000 |
| Analyst Actions | 1,000 |

A separate ground-truth dataset contains five planted anomaly types:

1. Transaction on a closed account.
2. Negative balance beyond the permitted overdraft.
3. Mismatched transfer legs.
4. Alert without a triggering transaction.
5. Case disposition preceding its alert.

## Risk Scoring

The risk engine evaluates multiple indicators:

| Risk Indicator | Score Contribution |
|---|---:|
| High transaction amount | 25 |
| New device | 20 |
| High transaction frequency | 25 |
| Dormant account reactivation | 20 |
| High-risk merchant | 10 |

Risk classification:

- **LOW:** Score below 40
- **MEDIUM:** Score from 40 to 69
- **HIGH:** Score of 70 or above

The maximum risk score is capped at 100.

## Technology Stack

| Component | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Database | SQLite |
| Frontend Library | React |
| Frontend Build Tool | Vite |
| Frontend Language | JavaScript |
| Testing | Pytest |
| Data Generation | Python, Faker |

## Project Structure

```text
yottaflex-transaction-risk/
│
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── generator.py
│   │   │   └── risk_engine.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   ├── check_db.py
│   │   └── validate_data.py
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── index.html
│
├── database/
│   ├── schema.sql
│   └── yottaflex_risk.db
│
├── data/
│   └── ground_truth.csv
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── source_manifest.md
│   └── validation_report.md
│
├── .gitignore
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.12 or compatible version
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/CSE16072/yottaflex-transaction-risk.git
cd yottaflex-transaction-risk
```

### 2. Start the Backend

Open a terminal in the `backend` directory.

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

Backend URL: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

### 3. Start the Frontend

Open a separate terminal in the `frontend` directory.

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend URL: http://localhost:5173/

Keep both backend and frontend servers running while using the application.

## Testing

Run backend tests from the `backend` directory:

```bash
python -m pytest tests -v
```

**Latest recorded test result:** 12 passed, 0 failed.

Data validation can be run using:

```bash
python -m app.validate_data
```

## Documentation

Additional project documentation is available in the `docs/` directory:

- `architecture.md` — System architecture.
- `data_dictionary.md` — Database entities and descriptions.
- `source_manifest.md` — Data generation details and source information.
- `validation_report.md` — Data validation results.

## GitHub Repository

**Project Repository:**  
https://github.com/CSE16072/yottaflex-transaction-risk

---

**Project:** YottaFlex Transaction Risk Intelligence  
**Submission Type:** Hackathon Project  
**Architecture:** Three-Tier Application