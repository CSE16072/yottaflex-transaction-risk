# System Architecture – YottaFlex Transaction Risk Intelligence

## 1. Overview
YottaFlex Transaction Risk Intelligence is a transaction monitoring and fraud-risk investigation platform built using a three-tier architecture.

## 2. Architecture

### Database Layer
- SQLite relational database.
- Stores customers, accounts, merchants, devices, transactions, transfer links, risk rules, alerts, cases, case-alert relationships and analyst actions.
- Primary keys and foreign keys maintain referential integrity.

### Backend Layer
- Python and FastAPI.
- Provides REST APIs for dashboard metrics, transactions, alerts, cases and risk scoring.
- Applies explainable rule-based risk scoring.
- Supports case updates and analyst actions.

### Frontend Layer
- React and Vite.
- Displays dashboard metrics, transactions, alerts and case management.
- Communicates with the backend through REST APIs.

## 3. Data Flow
1. Synthetic data is generated using a fixed random seed.
2. Data is stored in the SQLite database.
3. The backend retrieves and processes database records.
4. Risk scoring identifies suspicious activity.
5. Alerts and cases are presented in the frontend.
6. Analysts can review and update cases.

## 4. Security and Integrity
- Foreign key constraints are enabled.
- API requests are separated from direct database access.
- Ground-truth anomaly labels are kept separate from operational data.

## 5. Technology Stack
- Python 3.12
- FastAPI
- SQLite
- React
- Vite
- JavaScript
- Pytest