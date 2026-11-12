
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard_endpoint():
    response = client.get("/api/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 5000
    assert data["total_accounts"] == 7000
    assert data["total_transactions"] == 100000
    assert data["total_alerts"] == 1000


def test_transactions_endpoint():
    response = client.get("/api/transactions?limit=5")

    assert response.status_code == 200
    assert len(response.json()) <= 5


def test_alerts_endpoint():
    response = client.get("/api/alerts?limit=5")

    assert response.status_code == 200
    assert len(response.json()) <= 5


def test_cases_endpoint():
    response = client.get("/api/cases?limit=5")

    assert response.status_code == 200
    assert len(response.json()) <= 5


def test_risk_scoring_endpoint():
    response = client.post(
        "/api/risk/score",
        json={
            "amount": 75000,
            "is_new_device": True,
            "transactions_last_hour": 6,
            "is_dormant_account": False,
            "is_high_risk_merchant": True
        }
    )

    assert response.status_code == 200
    assert response.json()["risk_score"] == 80
    assert response.json()["risk_level"] == "HIGH"


def test_transfer_reconciliation_endpoint():
    response = client.get("/api/transfers?limit=100")

    assert response.status_code == 200

    transfers = response.json()

    assert isinstance(transfers, list)
    assert len(transfers) > 0

    for transfer in transfers:
        assert "amounts_match" in transfer
        assert "computed_reconciliation_status" in transfer

    assert any(
        transfer["computed_reconciliation_status"] == "MISMATCHED"
        for transfer in transfers
    )


def test_case_audit_history_endpoint():
    cases_response = client.get("/api/cases?limit=1")

    assert cases_response.status_code == 200

    cases = cases_response.json()

    assert len(cases) > 0

    case_id = cases[0]["case_id"]

    response = client.get(
        f"/api/cases/{case_id}/actions?limit=100"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
