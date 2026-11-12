
from typing import Optional


def calculate_risk_score(
    amount: float,
    is_new_device: bool = False,
    transactions_last_hour: int = 0,
    is_dormant_account: bool = False,
    is_high_risk_merchant: bool = False
):
    """
    Calculate transaction risk using explainable rules.
    """

    score = 0
    reasons = []

    # Rule 1: High transaction amount
    if amount >= 50000:
        score += 25
        reasons.append("High transaction amount")

    # Rule 2: New device
    if is_new_device:
        score += 20
        reasons.append("Transaction from a new device")

    # Rule 3: High transaction velocity
    if transactions_last_hour >= 5:
        score += 25
        reasons.append("Unusually high transaction frequency")

    # Rule 4: Dormant account activity
    if is_dormant_account:
        score += 20
        reasons.append("Dormant account reactivated")

    # Rule 5: High-risk merchant
    if is_high_risk_merchant:
        score += 10
        reasons.append("High-risk merchant")

    # Keep score between 0 and 100
    score = min(score, 100)

    # Determine risk level
    if score >= 70:
        risk_level = "HIGH"
    elif score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons
    }


if __name__ == "__main__":

    result = calculate_risk_score(
        amount=75000,
        is_new_device=True,
        transactions_last_hour=6,
        is_dormant_account=False,
        is_high_risk_merchant=True
    )

    print("Risk Assessment:")
    print(result)
