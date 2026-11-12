
from app.database import get_connection

connection = get_connection()

expected_counts = {
    "customers": 5000,
    "accounts": 7000,
    "merchants": 100,
    "devices": 2000,
    "transactions": 100000,
    "transfer_links": 100,
    "risk_rules": 5,
    "alerts": 1000,
    "cases": 1000,
    "case_alerts": 1000,
    "analyst_actions": 1000
}

print("\nDATABASE COUNT VALIDATION")
print("=" * 40)

all_passed = True

for table, expected in expected_counts.items():
    actual = connection.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    passed = actual == expected
    print(f"{table}: {actual} | Expected: {expected} | {'PASS' if passed else 'FAIL'}")

    if not passed:
        all_passed = False

print("\nFOREIGN KEY VALIDATION")
print("=" * 40)

foreign_key_errors = connection.execute(
    "PRAGMA foreign_key_check"
).fetchall()

print("Foreign key errors:", len(foreign_key_errors))

if foreign_key_errors:
    all_passed = False
    for error in foreign_key_errors:
        print(tuple(error))

print("\nPLANTED ANOMALY VALIDATION")
print("=" * 40)

checks = {
    "Closed account transaction": """
        SELECT COUNT(*)
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE a.account_status = 'CLOSED'
        AND t.transaction_timestamp > a.closed_at
    """,

    "Negative balance without overdraft": """
        SELECT COUNT(*)
        FROM accounts
        WHERE balance < -overdraft_limit
    """,

    "Mismatched transfer": """
        SELECT COUNT(*)
        FROM transfer_links
        WHERE reconciliation_status = 'MISMATCHED'
    """,

    "Alert without transaction": """
        SELECT COUNT(*)
        FROM alerts
        WHERE transaction_id IS NULL
    """,

    "Case disposition before alert": """
        SELECT COUNT(*)
        FROM cases c
        JOIN case_alerts ca ON c.case_id = ca.case_id
        JOIN alerts a ON ca.alert_id = a.alert_id
        WHERE c.disposition_at < a.created_at
    """
}

for name, query in checks.items():
    count = connection.execute(query).fetchone()[0]
    passed = count >= 1

    print(f"{name}: {count} | {'PASS' if passed else 'FAIL'}")

    if not passed:
        all_passed = False

connection.close()

print("\nFINAL RESULT")
print("=" * 40)
print("ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED")
