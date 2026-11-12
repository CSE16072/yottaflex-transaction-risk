
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from app.database import get_connection
from app.services.risk_engine import calculate_risk_score


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

SEED = 20261022

CUSTOMER_COUNT = 5000
ACCOUNT_COUNT = 7000
MERCHANT_COUNT = 100
DEVICE_COUNT = 2000
TRANSACTION_COUNT = 100000
ALERT_COUNT = 1000

START_DATE = datetime(2026, 1, 1)

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
GROUND_TRUTH_FILE = DATA_DIR / "ground_truth.csv"

FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Ananya", "Arjun",
    "Sneha", "Rohan", "Kavya", "Vikram", "Meera"
]

LAST_NAMES = [
    "Sharma", "Reddy", "Patel", "Kumar", "Rao",
    "Gupta", "Singh", "Verma", "Das", "Nair"
]

MERCHANT_CATEGORIES = [
    "GROCERY", "RETAIL", "TRAVEL", "FOOD",
    "FUEL", "E_COMMERCE", "ENTERTAINMENT",
    "HEALTHCARE", "CRYPTO", "GAMBLING"
]

HIGH_RISK_CATEGORIES = {"CRYPTO", "GAMBLING"}


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def random_date():
    return START_DATE + timedelta(
        minutes=random.randint(10 * 24 * 60, 330 * 24 * 60)
    )


def date_string(value):
    return value.isoformat(timespec="seconds")


def risk_level(score):
    if score >= 85:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def clear_database(connection):
    tables = [
        "analyst_actions",
        "case_alerts",
        "cases",
        "alerts",
        "transfer_links",
        "transactions",
        "devices",
        "merchants",
        "risk_rules",
        "accounts",
        "customers"
    ]

    for table in tables:
        connection.execute(f"DELETE FROM {table}")


# --------------------------------------------------
# 3. CUSTOMERS
# --------------------------------------------------

def generate_customers(connection):
    rows = []

    for i in range(1, CUSTOMER_COUNT + 1):
        rows.append((
            f"CUS-{i:06d}",
            f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            f"customer{i}@example.com",
            f"9{random.randint(100000000, 999999999)}",
            random.choices(
                ["ACTIVE", "INACTIVE", "SUSPENDED"],
                weights=[90, 7, 3]
            )[0],
            date_string(START_DATE)
        ))

    connection.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
        rows
    )

    return [row[0] for row in rows]


# --------------------------------------------------
# 4. ACCOUNTS
# --------------------------------------------------

def generate_accounts(connection, customer_ids):
    rows = []
    account_info = {}

    for i in range(1, ACCOUNT_COUNT + 1):
        account_id = f"ACC-{i:06d}"
        customer_id = random.choice(customer_ids)
        opening_balance = round(random.uniform(2000000, 5000000), 2)

        account_info[account_id] = {
            "customer_id": customer_id,
            "opening_balance": opening_balance,
            "balance": opening_balance,
            "overdraft_limit": 0.0,
            "status": "ACTIVE",
            "opened_at": START_DATE,
            "closed_at": None
        }

        rows.append((
            account_id,
            customer_id,
            random.choice(["SAVINGS", "CURRENT"]),
            opening_balance,
            0.0,
            "ACTIVE",
            date_string(START_DATE),
            None
        ))

    connection.executemany(
        "INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows
    )

    return account_info


# --------------------------------------------------
# 5. MERCHANTS
# --------------------------------------------------

def generate_merchants(connection):
    rows = []
    merchant_info = {}

    for i in range(1, MERCHANT_COUNT + 1):
        merchant_id = f"MER-{i:04d}"
        category = random.choice(MERCHANT_CATEGORIES)

        merchant_info[merchant_id] = {
            "category": category
        }

        rows.append((
            merchant_id,
            f"Merchant {i}",
            category,
            random.choice(["IN", "US", "UK", "SG"])
        ))

    connection.executemany(
        "INSERT INTO merchants VALUES (?, ?, ?, ?)",
        rows
    )

    return merchant_info


# --------------------------------------------------
# 6. DEVICES
# --------------------------------------------------

def generate_devices(connection, customer_ids):
    rows = []
    device_info = {}
    devices_by_customer = {}

    for i in range(1, DEVICE_COUNT + 1):
        device_id = f"DEV-{i:05d}"
        customer_id = random.choice(customer_ids)

        device_info[device_id] = customer_id
        devices_by_customer.setdefault(customer_id, []).append(device_id)

        rows.append((
            device_id,
            customer_id,
            random.choice(["MOBILE", "DESKTOP", "TABLET"]),
            date_string(START_DATE),
            date_string(START_DATE + timedelta(days=365)),
            "ACTIVE"
        ))

    connection.executemany(
        "INSERT INTO devices VALUES (?, ?, ?, ?, ?, ?)",
        rows
    )

    return device_info, devices_by_customer


# --------------------------------------------------
# 7. RISK RULES
# --------------------------------------------------

def generate_risk_rules(connection):
    rules = [
        ("RULE-001", "High Amount",
         "Transaction amount is unusually high", 25),

        ("RULE-002", "New Device",
         "Transaction uses a device not previously used by the customer", 20),

        ("RULE-003", "High Velocity",
         "Multiple transactions occurred within one hour", 25),

        ("RULE-004", "Dormant Account",
         "Account became active after a long period of inactivity", 20),

        ("RULE-005", "High Risk Merchant",
         "Transaction involves a high-risk merchant category", 10)
    ]

    for rule_id, name, description, weight in rules:
        connection.execute(
            """
            INSERT INTO risk_rules
            VALUES (?, ?, ?, ?, 'ACTIVE', ?, NULL)
            """,
            (
                rule_id,
                name,
                description,
                weight,
                date_string(START_DATE)
            )
        )


# --------------------------------------------------
# 8. TRANSACTION EVENT CREATION
# --------------------------------------------------

def generate_transactions(
    connection,
    account_info,
    merchant_info,
    devices_by_customer
):
    events_by_account = {
        account_id: []
        for account_id in account_info
    }

    account_ids = list(account_info)
    normal_accounts = account_ids[2:]

    transaction_number = 1
    normal_count = TRANSACTION_COUNT - 202

    def add_event(
        account_id,
        transaction_type,
        amount,
        timestamp,
        merchant_id=None,
        device_id=None,
        transfer_direction=None
    ):
        nonlocal transaction_number

        transaction_id = f"TXN-2026-{transaction_number:08d}"
        transaction_number += 1

        events_by_account[account_id].append({
            "id": transaction_id,
            "type": transaction_type,
            "amount": round(amount, 2),
            "time": timestamp,
            "merchant": merchant_id,
            "device": device_id,
            "transfer_direction": transfer_direction
        })

        return transaction_id

    # Velocity pattern: six transactions within one hour.
    velocity_account = normal_accounts[0]
    velocity_customer = account_info[velocity_account]["customer_id"]
    velocity_devices = devices_by_customer.get(velocity_customer, [])

    for i in range(6):
        device_id = random.choice(velocity_devices) if velocity_devices else None

        add_event(
            velocity_account,
            "DEBIT",
            random.uniform(5000, 12000),
            START_DATE + timedelta(days=50, minutes=i * 5),
            random.choice(list(merchant_info)),
            device_id
        )

    # Dormant account pattern: first activity after a long inactive period.
    dormant_account = normal_accounts[1]
    dormant_customer = account_info[dormant_account]["customer_id"]
    dormant_devices = devices_by_customer.get(dormant_customer, [])

    dormant_device = (
        random.choice(dormant_devices)
        if dormant_devices else None
    )

    add_event(
        dormant_account,
        "DEBIT",
        75000,
        START_DATE + timedelta(days=300),
        random.choice(list(merchant_info)),
        dormant_device
    )

    # Generate the remaining normal transactions.
    available_accounts = normal_accounts[2:]

    for _ in range(normal_count - 7):
        account_id = random.choice(available_accounts)
        customer_id = account_info[account_id]["customer_id"]

        customer_devices = devices_by_customer.get(customer_id, [])
        device_id = (
            random.choice(customer_devices)
            if customer_devices else None
        )

        merchant_id = random.choice(list(merchant_info))

        if random.random() < 0.05:
            amount = random.uniform(50000, 150000)
        else:
            amount = random.uniform(100, 25000)

        transaction_type = random.choices(
            ["DEBIT", "CREDIT"],
            weights=[75, 25]
        )[0]

        add_event(
            account_id,
            transaction_type,
            amount,
            random_date(),
            merchant_id,
            device_id
        )

    # Create 100 transfer pairs (200 transaction legs).
    transfer_links = []

    circular_accounts = normal_accounts[2:5]

    for i in range(100):
        if i < 3:
            source_id = circular_accounts[i]
            destination_id = circular_accounts[(i + 1) % 3]
        else:
            source_id = random.choice(available_accounts)
            destination_id = random.choice(available_accounts)

            while destination_id == source_id:
                destination_id = random.choice(available_accounts)

        amount = round(random.uniform(500, 15000), 2)
        timestamp = random_date()

        debit_id = add_event(
            source_id,
            "TRANSFER",
            amount,
            timestamp,
            transfer_direction="DEBIT"
        )

        credit_id = add_event(
            destination_id,
            "TRANSFER",
            amount,
            timestamp,
            transfer_direction="CREDIT"
        )

        transfer_links.append((
            f"TL-{i + 1:06d}",
            debit_id,
            credit_id,
            source_id,
            destination_id,
            amount,
            "MATCHED"
        ))

    # Anomaly 1: transaction after account closure.
    closed_account_id = account_ids[0]
    closed_account = account_info[closed_account_id]

    closed_account["status"] = "CLOSED"
    closed_account["closed_at"] = START_DATE + timedelta(days=100)

    closed_transaction_id = add_event(
        closed_account_id,
        "DEBIT",
        100,
        START_DATE + timedelta(days=200)
    )

    # Anomaly 2: negative balance without overdraft.
    negative_account_id = account_ids[1]
    negative_account = account_info[negative_account_id]

    negative_account["opening_balance"] = 100.0
    negative_account["overdraft_limit"] = 0.0

    negative_transaction_id = add_event(
        negative_account_id,
        "DEBIT",
        500,
        START_DATE + timedelta(days=201)
    )

    # Process transactions chronologically for each account.
    transactions = []
    scored_records = []

    last_transaction_by_account = {}
    first_device_use = {}
    recent_transactions = {}

    for account_id, events in events_by_account.items():
        account = account_info[account_id]
        balance = account["opening_balance"]

        events.sort(key=lambda item: (item["time"], item["id"]))

        for event in events:
            timestamp = event["time"]
            amount = event["amount"]

            before = round(balance, 2)

            if event["type"] == "CREDIT":
                balance += amount
            elif (
                event["type"] == "TRANSFER"
                and event["transfer_direction"] == "CREDIT"
            ):
                balance += amount
            else:
                balance -= amount

            after = round(balance, 2)

            customer_id = account["customer_id"]
            device_id = event["device"]

            # Derive new-device status from actual transaction history.
            device_key = (customer_id, device_id)
            is_new_device = (
                device_id is not None
                and device_key not in first_device_use
            )

            if device_id is not None:
                first_device_use[device_key] = timestamp

            # Derive transaction velocity from previous transactions.
            previous_times = recent_transactions.setdefault(account_id, [])

            previous_times = [
                previous_time
                for previous_time in previous_times
                if timestamp - previous_time <= timedelta(hours=1)
            ]

            transactions_last_hour = len(previous_times)
            previous_times.append(timestamp)
            recent_transactions[account_id] = previous_times

            # Derive dormant status from account activity history.
            last_time = last_transaction_by_account.get(account_id)

            if last_time is None:
                dormant = (
                    timestamp - account["opened_at"]
                    >= timedelta(days=90)
                )
            else:
                dormant = (
                    timestamp - last_time
                    >= timedelta(days=90)
                )

            last_transaction_by_account[account_id] = timestamp

            merchant_id = event["merchant"]

            is_high_risk_merchant = (
                merchant_id is not None
                and merchant_info[merchant_id]["category"]
                in HIGH_RISK_CATEGORIES
            )

            # Calculate score from the actual transaction features.
            result = calculate_risk_score(
                amount=amount,
                is_new_device=is_new_device,
                transactions_last_hour=transactions_last_hour,
                is_dormant_account=dormant,
                is_high_risk_merchant=is_high_risk_merchant
            )

            transaction = (
                event["id"],
                account_id,
                merchant_id,
                device_id,
                event["type"],
                amount,
                date_string(timestamp),
                "COMPLETED",
                "INR",
                before,
                after
            )

            transactions.append(transaction)

            scored_records.append({
                "transaction": transaction,
                "customer_id": customer_id,
                "score": result["risk_score"],
                "level": risk_level(result["risk_score"]),
                "reasons": result["reasons"],
                "timestamp": timestamp
            })

        account["balance"] = round(balance, 2)

    # Update final account balances and lifecycle states.
    for account_id, account in account_info.items():
        connection.execute(
            """
            UPDATE accounts
            SET balance = ?, account_status = ?, closed_at = ?
            WHERE account_id = ?
            """,
            (
                account["balance"],
                account["status"],
                date_string(account["closed_at"])
                if account["closed_at"] else None,
                account_id
            )
        )

    connection.executemany(
        """
        INSERT INTO transactions
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        transactions
    )

    # Plant transfer reconciliation anomaly.
    first_link = list(transfer_links[0])
    first_link[5] = round(first_link[5] + 250, 2)
    first_link[6] = "MISMATCHED"
    transfer_links[0] = tuple(first_link)

    connection.executemany(
        "INSERT INTO transfer_links VALUES (?, ?, ?, ?, ?, ?, ?)",
        transfer_links
    )

    anomaly_ids = {
        "closed_transaction": closed_transaction_id,
        "negative_transaction": negative_transaction_id
    }

    return transactions, transfer_links, scored_records, anomaly_ids


# --------------------------------------------------
# 9. ALERTS, CASES AND ANALYST ACTIONS
# --------------------------------------------------

def generate_alerts_and_cases(
    connection,
    customer_ids,
    scored_records
):
    alerts = []
    cases = []
    case_alerts = []
    actions = []
    ground_truth = []

    # Select transactions with actual risk indicators.
    candidates = [
        record for record in scored_records
        if record["score"] > 0
    ]

    if len(candidates) < ALERT_COUNT - 1:
        raise ValueError(
            "Not enough risk-triggering transactions to create alerts."
        )

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    selected = candidates[:ALERT_COUNT - 1]

    rule_map = {
        "High transaction amount": "RULE-001",
        "Transaction from a new device": "RULE-002",
        "Unusually high transaction frequency": "RULE-003",
        "Dormant account reactivated": "RULE-004",
        "High-risk merchant": "RULE-005"
    }

    for i, record in enumerate(selected, 1):
        transaction = record["transaction"]
        reasons = record["reasons"]

        triggering_rule = next(
            (
                rule_map[reason]
                for reason in reasons
                if reason in rule_map
            ),
            None
        )

        if triggering_rule is None:
            continue

        alert_id = f"ALT-2026-{i:06d}"

        alerts.append((
            alert_id,
            transaction[0],
            record["customer_id"],
            triggering_rule,
            record["score"],
            record["level"],
            "OPEN",
            transaction[6]
        ))

    # Ensure the expected alert count.
    if len(alerts) != ALERT_COUNT - 1:
        raise ValueError(
            "Alert count mismatch. Review risk-rule mapping."
        )

    # Anomaly 4: alert without a triggering transaction.
    missing_alert_id = f"ALT-2026-{ALERT_COUNT:06d}"
    missing_customer = customer_ids[2]
    missing_time = date_string(START_DATE + timedelta(days=250))

    alerts.append((
        missing_alert_id,
        None,
        missing_customer,
        "RULE-001",
        75,
        "HIGH",
        "OPEN",
        missing_time
    ))

    connection.executemany(
        "INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        alerts
    )

    # Create one case for each alert.
    for i, alert in enumerate(alerts, 1):
        alert_id = alert[0]
        customer_id = alert[2]
        alert_time = datetime.fromisoformat(alert[7])

        case_id = f"CASE-2026-{i:06d}"
        case_time = alert_time - timedelta(hours=1)

        status = "OPEN"
        disposition = None
        disposition_at = None

        # Represent false positives in the synthetic dataset.
        if i % 10 == 0:
            status = "RESOLVED"
            disposition = "FALSE_POSITIVE"
            disposition_at = date_string(
                alert_time + timedelta(hours=2)
            )

        cases.append((
            case_id,
            customer_id,
            status,
            alert[5],
            date_string(case_time),
            disposition,
            disposition_at
        ))

        case_alerts.append((
            case_id,
            alert_id,
            date_string(alert_time)
        ))

        actions.append((
            f"ACT-{i:06d}",
            case_id,
            f"ANALYST-{(i % 10) + 1:03d}",
            "REVIEW",
            "Synthetic analyst review action",
            date_string(alert_time + timedelta(minutes=30))
        ))

    # Anomaly 5: case disposition before alert creation.
    anomaly_case_index = 4

    bad_case = list(cases[anomaly_case_index])
    bad_alert_time = datetime.fromisoformat(
        alerts[anomaly_case_index][7]
    )

    bad_case[2] = "RESOLVED"
    bad_case[5] = "FALSE_POSITIVE"
    bad_case[6] = date_string(
        bad_alert_time - timedelta(days=1)
    )

    cases[anomaly_case_index] = tuple(bad_case)

    connection.executemany(
        "INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?)",
        cases
    )

    connection.executemany(
        "INSERT INTO case_alerts VALUES (?, ?, ?)",
        case_alerts
    )

    connection.executemany(
        "INSERT INTO analyst_actions VALUES (?, ?, ?, ?, ?, ?)",
        actions
    )

    ground_truth.extend([
        (
            "ANOM-001",
            "CLOSED_ACCOUNT_TRANSACTION",
            "Transaction occurred after account closure",
            "TXN-2026-00099999"
        ),
        (
            "ANOM-002",
            "NEGATIVE_BALANCE_WITHOUT_OVERDRAFT",
            "Negative balance with zero overdraft limit",
            "TXN-2026-00100000"
        ),
        (
            "ANOM-003",
            "TRANSFER_RECONCILIATION_MISMATCH",
            "Transfer link amount differs from transaction legs",
            "TL-000001"
        ),
        (
            "ANOM-004",
            "ALERT_WITHOUT_TRANSACTION",
            "Alert does not reference a triggering transaction",
            missing_alert_id
        ),
        (
            "ANOM-005",
            "CASE_DISPOSITION_PRECEDES_ALERT",
            "Case disposition timestamp precedes alert creation",
            cases[anomaly_case_index][0]
        )
    ])

    return ground_truth


# --------------------------------------------------
# 10. SAVE GROUND TRUTH LABELS
# --------------------------------------------------

def save_ground_truth(rows):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        GROUND_TRUTH_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "anomaly_id",
            "anomaly_type",
            "description",
            "affected_record_id"
        ])

        writer.writerows(rows)


# --------------------------------------------------
# 11. MAIN GENERATION FUNCTION
# --------------------------------------------------

def generate_dataset():
    random.seed(SEED)

    connection = get_connection()

    try:
        print("Clearing previous synthetic data...")
        connection.execute("PRAGMA foreign_keys = ON")
        clear_database(connection)

        print("Generating customers...")
        customers = generate_customers(connection)

        print("Generating accounts...")
        accounts = generate_accounts(connection, customers)

        print("Generating merchants...")
        merchants = generate_merchants(connection)

        print("Generating devices...")
        device_info, devices_by_customer = generate_devices(
            connection,
            customers
        )

        print("Generating risk rules...")
        generate_risk_rules(connection)

        print("Generating transactions...")
        transactions, transfers, scored_records, anomaly_ids = (
            generate_transactions(
                connection,
                accounts,
                merchants,
                devices_by_customer
            )
        )

        print("Generating alerts and cases...")
        ground_truth = generate_alerts_and_cases(
            connection,
            customers,
            scored_records
        )

        print("Committing database records...")
        connection.commit()

        print("Saving ground truth...")
        save_ground_truth(ground_truth)

        print("\nDATA GENERATION COMPLETED")
        print("-------------------------")
        print("Customers:", len(customers))
        print("Accounts:", len(accounts))
        print("Merchants:", len(merchants))
        print("Devices:", len(device_info))
        print("Transactions:", len(transactions))
        print("Transfer links:", len(transfers))
        print("Alerts:", ALERT_COUNT)
        print("Labelled anomalies:", len(ground_truth))
        print("Ground truth:", GROUND_TRUTH_FILE)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_dataset()
