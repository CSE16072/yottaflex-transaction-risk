\# YottaFlex Transaction Risk Intelligence



\## Project Overview



YottaFlex Transaction Risk Intelligence is a three-tier application designed to monitor financial transactions, identify suspicious activities, prioritize risk, and support analyst case management.



\## Architecture



The application uses three layers:



1\. \*\*Database:\*\* SQLite relational database.

2\. \*\*Backend:\*\* Python and FastAPI REST API.

3\. \*\*Frontend:\*\* React, Vite, and JavaScript dashboard.



The frontend communicates with the database through the backend API.



\## Key Features



\- Synthetic financial data generation using a fixed random seed.

\- Customer, account, merchant, device, and transaction management.

\- Explainable transaction risk scoring.

\- Risk alerts and case management.

\- Transfer reconciliation.

\- Analyst actions and audit history.

\- Dashboard for monitoring transactions, alerts, and cases.

\- Data validation and automated backend tests.



\## Dataset



The generated dataset includes:



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



A separate ground-truth dataset contains five planted anomaly types.



\## Risk Detection



The risk engine considers:

\- High transaction amounts

\- New devices

\- High transaction frequency

\- Dormant account reactivation

\- High-risk merchants



Risk levels are classified as LOW, MEDIUM, or HIGH.



\## Running the Application



\### Backend



Open a terminal in the `backend` directory and activate the virtual environment:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



Start the API:



```powershell

uvicorn app.main:app --reload

```



API documentation: http://127.0.0.1:8000/docs



\### Frontend



Open another terminal in the `frontend` directory:



```powershell

npm install

npm run dev

```



Frontend: http://localhost:5173/



\## Testing



From the backend directory:



```powershell

python -m pytest tests -v

```



The current automated backend test result is 12 passed.



\## Documentation



Additional documentation is available in the `docs` directory:

\- architecture.md

\- source\_manifest.md

\- validation\_report.md

\- data\_dictionary.md



\## Technology Stack



Python, FastAPI, SQLite, React, Vite, JavaScript, Pandas, and Pytest.



\## Project



YottaFlex Transaction Risk Intelligence — Hackathon Submission.

