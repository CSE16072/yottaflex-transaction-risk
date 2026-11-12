# Validation Report – YottaFlex Transaction Risk Intelligence

## 1. Database Validation

The generated database was checked against expected record counts.

| Entity | Expected Records | Result |
|---|---:|---|
| Customers | 5,000 | PASS |
| Accounts | 7,000 | PASS |
| Merchants | 100 | PASS |
| Devices | 2,000 | PASS |
| Transactions | 100,000 | PASS |
| Transfer Links | 100 | PASS |
| Risk Rules | 5 | PASS |
| Alerts | 1,000 | PASS |
| Cases | 1,000 | PASS |
| Case Alerts | 1,000 | PASS |
| Analyst Actions | 1,000 | PASS |

## 2. Integrity Validation
- Foreign key errors: 0
- All expected record counts passed.
- All five planted anomaly categories were detected.

## 3. Planted Anomaly Validation

| Anomaly | Detected |
|---|---|
| Transaction on closed account | PASS |
| Negative balance beyond overdraft | PASS |
| Mismatched transfer legs | PASS |
| Alert without triggering transaction | PASS |
| Case disposition preceding alert | PASS |

## 4. Automated Testing

Pytest results:

- API tests: 6 passed.
- Risk engine tests: 6 passed.
- Total: 12 passed.
- Failed tests: 0.

## 5. Frontend and Backend Verification
- FastAPI server started successfully.
- API health endpoint returned successfully.
- Dashboard metrics loaded from the backend.
- Transactions, risk alerts and case management pages were tested.
- Case resolution and dashboard refresh worked successfully.

## 6. Conclusion
The database validation, planted anomaly checks, automated tests and frontend-backend integration checks completed successfully.

The project demonstrates a working transaction risk monitoring and investigation application.