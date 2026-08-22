def test_summary_balance_and_recents(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    # Base reference date: 2026-08-22
    # Add transaction 5 days ago (2026-08-17) -> Should affect balance, NOT recent
    client.post("/api/transactions", json={
        "description": "Antiga",
        "type": "despesa",
        "amount": 100.0,
        "category_id": cat_id,
        "date_time": "2026-08-17T12:00:00"
    }, headers=auth_headers)

    # Add transaction 2 days ago (2026-08-20) -> Should affect balance AND be in recent
    client.post("/api/transactions", json={
        "description": "Recente 1",
        "type": "despesa",
        "amount": 50.0,
        "category_id": cat_id,
        "date_time": "2026-08-20T12:00:00"
    }, headers=auth_headers)

    # Add transaction today (2026-08-22) -> Should affect balance AND be in recent
    client.post("/api/transactions", json={
        "description": "Salário",
        "type": "receita",
        "amount": 1000.0,
        "category_id": cat_id,
        "date_time": "2026-08-22T08:00:00"
    }, headers=auth_headers)

    summary = client.get("/api/summary?base_date=2026-08-22", headers=auth_headers).json()

    # Total income = 1000, Total expense = 150 -> Balance = 850
    assert summary["total_income"] == 1000.0
    assert summary["total_expense"] == 150.0
    assert summary["current_balance"] == 850.0

    # Recent transactions: only 2026-08-20 and 2026-08-22 (2 transactions)
    assert len(summary["recent_transactions"]) == 2
    descriptions = [t["description"] for t in summary["recent_transactions"]]
    assert "Salário" in descriptions
    assert "Recente 1" in descriptions
    assert "Antiga" not in descriptions

def test_summary_requires_authentication(client):
    assert client.get("/api/summary").status_code == 401

def test_summary_is_isolated_between_users(client, auth_headers, second_user_headers):
    cats_a = client.get("/api/categories", headers=auth_headers).json()
    cats_b = client.get("/api/categories", headers=second_user_headers).json()

    client.post("/api/transactions", json={
        "description": "Receita A",
        "type": "receita",
        "amount": 300.0,
        "category_id": cats_a[0]["id"],
        "date_time": "2026-08-22T08:00:00"
    }, headers=auth_headers)

    client.post("/api/transactions", json={
        "description": "Receita B",
        "type": "receita",
        "amount": 900.0,
        "category_id": cats_b[0]["id"],
        "date_time": "2026-08-22T08:00:00"
    }, headers=second_user_headers)

    summary_a = client.get("/api/summary?base_date=2026-08-22", headers=auth_headers).json()
    summary_b = client.get("/api/summary?base_date=2026-08-22", headers=second_user_headers).json()

    assert summary_a["total_income"] == 300.0
    assert summary_b["total_income"] == 900.0
