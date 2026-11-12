
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.database import get_connection
from app.services.risk_engine import calculate_risk_score


app = FastAPI(
    title="YottaFlex Transaction Risk Intelligence",
    description="Transaction risk monitoring and case management API",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RiskRequest(BaseModel):
    amount: float = Field(gt=0)
    is_new_device: bool = False
    transactions_last_hour: int = Field(default=0, ge=0)
    is_dormant_account: bool = False
    is_high_risk_merchant: bool = False


class CaseUpdateRequest(BaseModel):
    status: str
    disposition: Optional[str] = None
    comments: Optional[str] = None


class AnalystActionRequest(BaseModel):
    analyst_id: str = Field(min_length=1)
    action_type: str = Field(min_length=1)
    comments: Optional[str] = None


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
def home():
    return {
        "message": "YottaFlex Transaction Risk Intelligence API",
        "documentation": "/docs"
    }


@app.get("/api/health")
def health():
    return {"status": "healthy", "message": "Backend is running"}


@app.get("/api/dashboard")
def dashboard():
    connection = get_connection()

    try:
        result = {
            "total_customers": connection.execute(
                "SELECT COUNT(*) FROM customers"
            ).fetchone()[0],

            "total_accounts": connection.execute(
                "SELECT COUNT(*) FROM accounts"
            ).fetchone()[0],

            "total_transactions": connection.execute(
                "SELECT COUNT(*) FROM transactions"
            ).fetchone()[0],

            "total_alerts": connection.execute(
                "SELECT COUNT(*) FROM alerts"
            ).fetchone()[0],

            "open_alerts": connection.execute(
                "SELECT COUNT(*) FROM alerts WHERE alert_status = 'OPEN'"
            ).fetchone()[0],

            "open_cases": connection.execute(
                """
                SELECT COUNT(*) FROM cases
                WHERE case_status IN ('OPEN', 'INVESTIGATING')
                """
            ).fetchone()[0]
        }

        return result

    finally:
        connection.close()


@app.get("/api/transactions")
def get_transactions(limit: int = Query(default=100, ge=1, le=500)):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                t.transaction_id,
                t.account_id,
                a.customer_id,
                c.full_name AS customer_name,
                t.merchant_id,
                m.merchant_name,
                t.amount,
                t.currency,
                t.transaction_type,
                t.transaction_status,
                t.transaction_timestamp,
                t.balance_before,
                t.balance_after
            FROM transactions t
            LEFT JOIN accounts a ON t.account_id = a.account_id
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            LEFT JOIN merchants m ON t.merchant_id = m.merchant_id
            ORDER BY t.transaction_timestamp DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


@app.get("/api/alerts")
def get_alerts(limit: int = Query(default=100, ge=1, le=500)):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                a.alert_id,
                a.customer_id,
                a.transaction_id,
                a.risk_score,
                a.risk_level,
                a.alert_status,
                a.created_at,
                r.rule_name,
                r.rule_description
            FROM alerts a
            LEFT JOIN risk_rules r ON a.rule_id = r.rule_id
            ORDER BY a.risk_score DESC, a.created_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        results = []

        for row in rows:
            item = dict(row)
            item["explanation"] = item.pop("rule_description", None)
            results.append(item)

        return results

    finally:
        connection.close()


@app.get("/api/cases")
def get_cases(limit: int = Query(default=100, ge=1, le=500)):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                case_id,
                customer_id,
                case_status,
                priority,
                disposition,
                created_at,
                disposition_at
            FROM cases
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# TRANSFER RECONCILIATION
@app.get("/api/transfers")
def get_transfers(limit: int = Query(default=100, ge=1, le=500)):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                tl.transfer_link_id,
                tl.debit_transaction_id,
                tl.credit_transaction_id,
                tl.source_account_id,
                tl.destination_account_id,
                tl.transfer_amount,
                tl.reconciliation_status,

                debit.amount AS debit_amount,
                debit.transaction_status AS debit_status,

                credit.amount AS credit_amount,
                credit.transaction_status AS credit_status

            FROM transfer_links tl

            LEFT JOIN transactions debit
                ON tl.debit_transaction_id = debit.transaction_id

            LEFT JOIN transactions credit
                ON tl.credit_transaction_id = credit.transaction_id

            ORDER BY tl.transfer_link_id
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        results = []

        for row in rows:
            item = dict(row)

            debit_amount = item["debit_amount"]
            credit_amount = item["credit_amount"]
            transfer_amount = item["transfer_amount"]

            amounts_match = (
                debit_amount is not None
                and credit_amount is not None
                and transfer_amount is not None
                and abs(abs(debit_amount) - transfer_amount) <= 0.01
                and abs(credit_amount - transfer_amount) <= 0.01
            )

            item["amounts_match"] = amounts_match

            if debit_amount is not None and credit_amount is not None:
                item["amount_difference"] = round(
                    abs(debit_amount) - abs(credit_amount), 2
                )
            else:
                item["amount_difference"] = None

            item["computed_reconciliation_status"] = (
                "MATCHED" if amounts_match else "MISMATCHED"
            )

            results.append(item)

        return results

    finally:
        connection.close()


# UPDATE CASE AND AUTOMATICALLY RECORD AUDIT HISTORY
@app.patch("/api/cases/{case_id}")
def update_case(case_id: str, request: CaseUpdateRequest):
    connection = get_connection()

    try:
        existing = connection.execute(
            """
            SELECT case_id, case_status, disposition
            FROM cases
            WHERE case_id = ?
            """,
            (case_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(status_code=404, detail="Case not found")

        timestamp = utc_now()

        connection.execute(
            """
            UPDATE cases
            SET case_status = ?,
                disposition = COALESCE(?, disposition),
                disposition_at = CASE
                    WHEN ? IS NOT NULL THEN ?
                    ELSE disposition_at
                END
            WHERE case_id = ?
            """,
            (
                request.status,
                request.disposition,
                request.disposition,
                timestamp,
                case_id
            )
        )

        action_id = "ACT-" + uuid.uuid4().hex[:12].upper()

        audit_notes = request.comments or (
            f"Case status changed from {existing['case_status']} "
            f"to {request.status}. "
            f"Disposition: {request.disposition or existing['disposition'] or 'Not specified'}"
        )

        connection.execute(
            """
            INSERT INTO analyst_actions (
                action_id,
                case_id,
                analyst_id,
                action_type,
                action_notes,
                action_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                action_id,
                case_id,
                "dashboard-user",
                "CASE_UPDATED",
                audit_notes,
                timestamp
            )
        )

        connection.commit()

        return {
            "message": "Case updated and audit history recorded",
            "case_id": case_id,
            "status": request.status,
            "action_id": action_id
        }

    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        connection.close()


# VIEW AUDIT HISTORY FOR A CASE
@app.get("/api/cases/{case_id}/actions")
def get_case_actions(
    case_id: str,
    limit: int = Query(default=100, ge=1, le=500)
):
    connection = get_connection()

    try:
        existing = connection.execute(
            "SELECT case_id FROM cases WHERE case_id = ?",
            (case_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(status_code=404, detail="Case not found")

        rows = connection.execute(
            """
            SELECT
                action_id,
                case_id,
                analyst_id,
                action_type,
                action_notes,
                action_timestamp
            FROM analyst_actions
            WHERE case_id = ?
            ORDER BY action_timestamp DESC
            LIMIT ?
            """,
            (case_id, limit)
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# MANUALLY ADD AN ANALYST ACTION
@app.post("/api/cases/{case_id}/actions")
def add_analyst_action(
    case_id: str,
    request: AnalystActionRequest
):
    connection = get_connection()

    try:
        existing = connection.execute(
            "SELECT case_id FROM cases WHERE case_id = ?",
            (case_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(status_code=404, detail="Case not found")

        action_id = "ACT-" + uuid.uuid4().hex[:12].upper()

        connection.execute(
            """
            INSERT INTO analyst_actions (
                action_id,
                case_id,
                analyst_id,
                action_type,
                action_notes,
                action_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                action_id,
                case_id,
                request.analyst_id,
                request.action_type,
                request.comments,
                utc_now()
            )
        )

        connection.commit()

        return {
            "message": "Analyst action recorded",
            "action_id": action_id,
            "case_id": case_id
        }

    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        connection.close()


@app.post("/api/risk/score")
def score_transaction(request: RiskRequest):
    result = calculate_risk_score(
        amount=request.amount,
        is_new_device=request.is_new_device,
        transactions_last_hour=request.transactions_last_hour,
        is_dormant_account=request.is_dormant_account,
        is_high_risk_merchant=request.is_high_risk_merchant
    )

    return result
