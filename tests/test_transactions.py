from datetime import datetime

def test_create_and_get_transaction(client):
    # Get a category
    categories = client.get("/api/categories").json()
    cat_id = categories[0]["id"]

    payload = {
        "description": "Almoço no restaurante",
        "type": "despesa",
        "amount": 45.50,
        "category_id": cat_id,
        "date_time": "2026-08-20T12:30:00",
        "repeat_monthly": False
    }

    create_res = client.post("/api/transactions", json=payload)
    assert create_res.status_code == 201
    tx = create_res.json()
    assert tx["description"] == "Almoço no restaurante"
    assert tx["amount"] == 45.50
    assert tx["type"] == "despesa"

    # Get single transaction
    get_res = client.get(f"/api/transactions/{tx['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == tx["id"]

def test_filter_transactions_by_date_and_type(client):
    categories = client.get("/api/categories").json()
    cat_id = categories[0]["id"]

    # Insert transactions
    client.post("/api/transactions", json={
        "description": "Mercado Julho",
        "type": "despesa",
        "amount": 100.0,
        "category_id": cat_id,
        "date_time": "2026-07-15T10:00:00"
    })
    client.post("/api/transactions", json={
        "description": "Mercado Agosto",
        "type": "despesa",
        "amount": 200.0,
        "category_id": cat_id,
        "date_time": "2026-08-10T10:00:00"
    })
    client.post("/api/transactions", json={
        "description": "Salário Agosto",
        "type": "receita",
        "amount": 5000.0,
        "category_id": cat_id,
        "date_time": "2026-08-05T09:00:00"
    })

    # Filter by August date range
    res_aug = client.get("/api/transactions?start_date=2026-08-01&end_date=2026-08-31").json()
    assert len(res_aug) == 2

    # Filter by Despesa in August
    res_desp = client.get("/api/transactions?start_date=2026-08-01&end_date=2026-08-31&type=despesa").json()
    assert len(res_desp) == 1
    assert res_desp[0]["description"] == "Mercado Agosto"

    # Filter by Receita in August
    res_rec = client.get("/api/transactions?start_date=2026-08-01&end_date=2026-08-31&type=receita").json()
    assert len(res_rec) == 1
    assert res_rec[0]["description"] == "Salário Agosto"

def test_update_and_delete_transaction(client):
    categories = client.get("/api/categories").json()
    cat_id = categories[0]["id"]

    created = client.post("/api/transactions", json={
        "description": "Cinema",
        "type": "despesa",
        "amount": 30.0,
        "category_id": cat_id,
        "date_time": "2026-08-18T20:00:00"
    }).json()

    tx_id = created["id"]

    # Update
    up_res = client.put(f"/api/transactions/{tx_id}", json={
        "amount": 35.0,
        "description": "Cinema IMAX"
    })
    assert up_res.status_code == 200
    assert up_res.json()["amount"] == 35.0
    assert up_res.json()["description"] == "Cinema IMAX"

    # Delete
    del_res = client.delete(f"/api/transactions/{tx_id}")
    assert del_res.status_code == 204

    # Verify deleted
    assert client.get(f"/api/transactions/{tx_id}").status_code == 404
