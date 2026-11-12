
PRAGMA foreign_keys = ON;

-- 1. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    customer_status TEXT NOT NULL
        CHECK (customer_status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    created_at TEXT NOT NULL
);

-- 2. ACCOUNTS
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_type TEXT NOT NULL,
    balance REAL NOT NULL,
    overdraft_limit REAL NOT NULL DEFAULT 0,
    account_status TEXT NOT NULL
        CHECK (account_status IN ('ACTIVE', 'CLOSED', 'FROZEN')),
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CHECK (overdraft_limit >= 0)
);

-- 3. MERCHANTS
CREATE TABLE IF NOT EXISTS merchants (
    merchant_id TEXT PRIMARY KEY,
    merchant_name TEXT NOT NULL,
    merchant_category TEXT NOT NULL,
    country TEXT NOT NULL
);

-- 4. DEVICES
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    device_type TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    device_status TEXT NOT NULL
        CHECK (device_status IN ('ACTIVE', 'BLOCKED', 'RETIRED')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 5. TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    merchant_id TEXT,
    device_id TEXT,
    transaction_type TEXT NOT NULL
        CHECK (transaction_type IN ('DEBIT', 'CREDIT', 'TRANSFER')),
    amount REAL NOT NULL CHECK (amount > 0),
    transaction_timestamp TEXT NOT NULL,
    transaction_status TEXT NOT NULL
        CHECK (transaction_status IN ('COMPLETED', 'PENDING', 'FAILED', 'REVERSED')),
    currency TEXT NOT NULL DEFAULT 'INR',
    balance_before REAL NOT NULL,
    balance_after REAL NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- 6. TRANSFER LINKS
CREATE TABLE IF NOT EXISTS transfer_links (
    transfer_link_id TEXT PRIMARY KEY,
    debit_transaction_id TEXT NOT NULL,
    credit_transaction_id TEXT NOT NULL,
    source_account_id TEXT NOT NULL,
    destination_account_id TEXT NOT NULL,
    transfer_amount REAL NOT NULL CHECK (transfer_amount > 0),
    reconciliation_status TEXT NOT NULL
        CHECK (reconciliation_status IN ('MATCHED', 'MISMATCHED', 'PENDING')),
    FOREIGN KEY (debit_transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (credit_transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (source_account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (destination_account_id) REFERENCES accounts(account_id),
    CHECK (debit_transaction_id <> credit_transaction_id),
    CHECK (source_account_id <> destination_account_id)
);

-- 7. RISK RULES
CREATE TABLE IF NOT EXISTS risk_rules (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,
    rule_description TEXT NOT NULL,
    risk_weight INTEGER NOT NULL CHECK (risk_weight BETWEEN 1 AND 100),
    rule_status TEXT NOT NULL
        CHECK (rule_status IN ('ACTIVE', 'INACTIVE')),
    effective_from TEXT NOT NULL,
    effective_to TEXT
);

-- 8. ALERTS
CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    transaction_id TEXT,
    customer_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    risk_score REAL NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    risk_level TEXT NOT NULL
        CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    alert_status TEXT NOT NULL
        CHECK (alert_status IN ('OPEN', 'UNDER_REVIEW', 'CLOSED', 'ESCALATED')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (rule_id) REFERENCES risk_rules(rule_id)
);

-- 9. CASES
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    case_status TEXT NOT NULL
        CHECK (case_status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED')),
    priority TEXT NOT NULL
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    created_at TEXT NOT NULL,
    disposition TEXT,
    disposition_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 10. CASE ALERTS (MANY-TO-MANY BRIDGE)
CREATE TABLE IF NOT EXISTS case_alerts (
    case_id TEXT NOT NULL,
    alert_id TEXT NOT NULL,
    linked_at TEXT NOT NULL,
    PRIMARY KEY (case_id, alert_id),
    FOREIGN KEY (case_id) REFERENCES cases(case_id),
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id)
);

-- 11. ANALYST ACTIONS
CREATE TABLE IF NOT EXISTS analyst_actions (
    action_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    analyst_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_notes TEXT,
    action_timestamp TEXT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

-- INDEXES FOR FASTER QUERIES
CREATE INDEX IF NOT EXISTS idx_transactions_account
ON transactions(account_id);

CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
ON transactions(transaction_timestamp);

CREATE INDEX IF NOT EXISTS idx_alerts_customer
ON alerts(customer_id);

CREATE INDEX IF NOT EXISTS idx_alerts_status
ON alerts(alert_status);

CREATE INDEX IF NOT EXISTS idx_cases_status
ON cases(case_status);

CREATE INDEX IF NOT EXISTS idx_analyst_actions_case
ON analyst_actions(case_id);
