# Source Manifest – YottaFlex Transaction Risk Intelligence

## 1. Data Source
All project records are synthetically generated. No real customer or financial information is used.

## 2. Data Generation
- Generator: `backend/app/services/generator.py`
- Random seed: `20261022`
- Database: `database/yottaflex_risk.db`
- Schema: `database/schema.sql`
- Ground truth: `data/ground_truth.csv`

## 3. Generated Dataset

| Entity | Record Count |
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

## 4. Ground Truth
Five planted anomaly categories are maintained separately from operational data:
1. Transaction on a closed account.
2. Negative balance beyond overdraft.
3. Mismatched transfer legs.
4. Alert without a triggering transaction.
5. Case disposition preceding its alert.

## 5. Reproducibility
The generator uses a fixed random seed (`20261022`) to support repeatable synthetic data generation.

## 6. Data Usage
The generated dataset is used for database validation, risk scoring, alert investigation, case management and dashboard reporting.