
from app.services.risk_engine import calculate_risk_score


def test_low_risk_transaction():
    result = calculate_risk_score(amount=1000)

    assert result["risk_score"] == 0
    assert result["risk_level"] == "LOW"


def test_high_amount_risk():
    result = calculate_risk_score(amount=75000)

    assert result["risk_score"] == 25
    assert "High transaction amount" in result["reasons"]


def test_new_device_risk():
    result = calculate_risk_score(
        amount=1000,
        is_new_device=True
    )

    assert result["risk_score"] == 20
    assert result["risk_level"] == "LOW"


def test_high_velocity_risk():
    result = calculate_risk_score(
        amount=1000,
        transactions_last_hour=6
    )

    assert result["risk_score"] == 25


def test_high_risk_classification():
    result = calculate_risk_score(
        amount=75000,
        is_new_device=True,
        transactions_last_hour=6,
        is_high_risk_merchant=True
    )

    assert result["risk_score"] == 80
    assert result["risk_level"] == "HIGH"


def test_score_never_exceeds_100():
    result = calculate_risk_score(
        amount=100000,
        is_new_device=True,
        transactions_last_hour=10,
        is_dormant_account=True,
        is_high_risk_merchant=True
    )

    assert result["risk_score"] <= 100
