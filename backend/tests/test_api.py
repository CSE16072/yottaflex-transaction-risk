
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
