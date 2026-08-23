def test_create_and_get_transaction(client, auth_headers):
    # Get a category
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    payload = {
        "description": "Almoço no restaurante",
        "type": "despesa",
        "amount": 45.50,
        "category_id": cat_id,
        "date_time": "2026-08-20T12:30:00",
        "repeat_monthly": False
    }

    create_res = client.post("/api/transactions", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    tx = create_res.json()
    assert tx["description"] == "Almoço no restaurante"
    assert tx["amount"] == 45.50
    assert tx["type"] == "despesa"

    # Get single transaction
    get_res = client.get(f"/api/transactions/{tx['id']}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == tx["id"]

def test_filter_transactions_by_date_and_type(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    # Insert transactions
    client.post("/api/transactions", json={
        "description": "Mercado Julho",
        "type": "despesa",
        "amount": 100.0,
        "category_id": cat_id,
        "date_time": "2026-07-15T10:00:00"
    }, headers=auth_headers)
    client.post("/api/transactions", json={
        "description": "Mercado Agosto",
        "type": "despesa",
        "amount": 200.0,
        "category_id": cat_id,
        "date_time": "2026-08-10T10:00:00"
    }, headers=auth_headers)
    client.post("/api/transactions", json={
        "description": "Salário Agosto",
        "type": "receita",
        "amount": 5000.0,
        "category_id": cat_id,
        "date_time": "2026-08-05T09:00:00"
    }, headers=auth_headers)

    # Filter by August date range
    res_aug = client.get("/api/transactions?start_date=2026-08-01&end_date=2026-08-31", headers=auth_headers).json()
    assert len(res_aug) == 2

    # Filter by Despesa in August
    res_desp = client.get("/api/transactions?start_date=2026-08-01&end_date=2026-08-31&type=despesa", headers=auth_headers).json()
    assert len(res_desp) == 1
    assert res_desp[0]["description"] == "Mercado Agosto"

    # Filter by Receita in August
    res_rec = client.get("/api/transactions?start_date=2026-08-01&end_date=2026-08-31&type=receita", headers=auth_headers).json()
    assert len(res_rec) == 1
    assert res_rec[0]["description"] == "Salário Agosto"

def test_update_and_delete_transaction(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    created = client.post("/api/transactions", json={
        "description": "Cinema",
        "type": "despesa",
        "amount": 30.0,
        "category_id": cat_id,
        "date_time": "2026-08-18T20:00:00"
    }, headers=auth_headers).json()

    tx_id = created["id"]

    # Update
    up_res = client.put(f"/api/transactions/{tx_id}", json={
        "amount": 35.0,
        "description": "Cinema IMAX"
    }, headers=auth_headers)
    assert up_res.status_code == 200
    assert up_res.json()["amount"] == 35.0
    assert up_res.json()["description"] == "Cinema IMAX"

    # Delete
    del_res = client.delete(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify deleted
    assert client.get(f"/api/transactions/{tx_id}", headers=auth_headers).status_code == 404

def test_cannot_create_transaction_with_other_users_category(client, auth_headers, second_user_headers):
    # Category belongs to user B; user A must not be able to use it
    other_categories = client.get("/api/categories", headers=second_user_headers).json()
    other_cat_id = other_categories[0]["id"]

    res = client.post("/api/transactions", json={
        "description": "Tentativa inválida",
        "type": "despesa",
        "amount": 10.0,
        "category_id": other_cat_id,
        "date_time": "2026-08-20T10:00:00"
    }, headers=auth_headers)
    assert res.status_code == 400

def test_transactions_are_isolated_between_users(client, auth_headers, second_user_headers):
    cats_a = client.get("/api/categories", headers=auth_headers).json()
    cats_b = client.get("/api/categories", headers=second_user_headers).json()

    client.post("/api/transactions", json={
        "description": "Gasto do usuário A",
        "type": "despesa",
        "amount": 50.0,
        "category_id": cats_a[0]["id"],
        "date_time": "2026-08-20T10:00:00"
    }, headers=auth_headers)

    client.post("/api/transactions", json={
        "description": "Gasto do usuário B",
        "type": "despesa",
        "amount": 75.0,
        "category_id": cats_b[0]["id"],
        "date_time": "2026-08-20T11:00:00"
    }, headers=second_user_headers)

    txs_a = client.get("/api/transactions", headers=auth_headers).json()
    txs_b = client.get("/api/transactions", headers=second_user_headers).json()

    descriptions_a = [t["description"] for t in txs_a]
    descriptions_b = [t["description"] for t in txs_b]

    assert "Gasto do usuário A" in descriptions_a
    assert "Gasto do usuário A" not in descriptions_b
    assert "Gasto do usuário B" in descriptions_b
    assert "Gasto do usuário B" not in descriptions_a

def test_user_cannot_access_another_users_transaction_by_id(client, auth_headers, second_user_headers):
    cats_a = client.get("/api/categories", headers=auth_headers).json()
    created = client.post("/api/transactions", json={
        "description": "Privado do usuário A",
        "type": "despesa",
        "amount": 20.0,
        "category_id": cats_a[0]["id"],
        "date_time": "2026-08-20T10:00:00"
    }, headers=auth_headers).json()
    tx_id = created["id"]

    assert client.get(f"/api/transactions/{tx_id}", headers=second_user_headers).status_code == 404
    assert client.put(f"/api/transactions/{tx_id}", json={"amount": 999.0}, headers=second_user_headers).status_code == 404
    assert client.delete(f"/api/transactions/{tx_id}", headers=second_user_headers).status_code == 404
