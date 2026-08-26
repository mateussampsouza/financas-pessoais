def test_create_and_get_transaction(client, auth_headers):
    # Get a category
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    payload = {
        "description": "Almoço no restaurante",
        "type": "despesa",
        "amount": 45.50,
        "category_id": cat_id,
        "date_time": "2026-08-20T12:30:00"
    }

    create_res = client.post("/api/transactions", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    tx = create_res.json()
    assert tx["description"] == "Almoço no restaurante"
    assert tx["amount"] == 45.50
    assert tx["type"] == "despesa"
    assert tx["recurrence"] == "nunca"
    assert tx["recurrence_quantity"] is None
    assert tx["recurrence_installment"] is None
    assert tx["recurrence_group_id"] is None

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


def _series(client, auth_headers, group_id):
    txs = client.get("/api/transactions", headers=auth_headers).json()
    return sorted((t for t in txs if t["recurrence_group_id"] == group_id), key=lambda t: t["date_time"])


def test_daily_recurrence_creates_past_and_future_occurrences(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    # quantidade=5, parcela=4 -> 3 occurrences before this date, 1 after
    created = client.post("/api/transactions", json={
        "description": "Assinatura Streaming",
        "type": "despesa",
        "amount": 19.90,
        "category_id": cat_id,
        "date_time": "2026-01-10T12:00:00",
        "recurrence": "diaria",
        "recurrence_quantity": 5,
        "recurrence_installment": 4
    }, headers=auth_headers).json()

    assert created["recurrence_installment"] == 4
    series = _series(client, auth_headers, created["recurrence_group_id"])
    assert len(series) == 5
    assert [t["date_time"][:10] for t in series] == [
        "2026-01-07", "2026-01-08", "2026-01-09", "2026-01-10", "2026-01-11"
    ]
    assert all(t["recurrence"] == "diaria" and t["recurrence_quantity"] == 5 for t in series)
    assert [t["recurrence_installment"] for t in series] == [1, 2, 3, 4, 5]


def test_weekly_recurrence_keeps_same_weekday(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    created = client.post("/api/transactions", json={
        "description": "Feira",
        "type": "despesa",
        "amount": 80.0,
        "category_id": cat_id,
        "date_time": "2026-01-10T12:00:00",
        "recurrence": "semanal",
        "recurrence_quantity": 4,
        "recurrence_installment": 1
    }, headers=auth_headers).json()

    series = _series(client, auth_headers, created["recurrence_group_id"])
    assert [t["date_time"][:10] for t in series] == [
        "2026-01-10", "2026-01-17", "2026-01-24", "2026-01-31"
    ]


def test_monthly_recurrence_clamps_day_across_short_months(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    created = client.post("/api/transactions", json={
        "description": "Aluguel",
        "type": "despesa",
        "amount": 1500.0,
        "category_id": cat_id,
        "date_time": "2026-01-31T09:00:00",
        "recurrence": "mensal",
        "recurrence_quantity": 3,
        "recurrence_installment": 1
    }, headers=auth_headers).json()

    series = _series(client, auth_headers, created["recurrence_group_id"])
    # Feb has no 31st, so it clamps to the last day of the month.
    assert [t["date_time"][:10] for t in series] == ["2026-01-31", "2026-02-28", "2026-03-31"]


def test_recurrence_requires_quantity_and_installment(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    res = client.post("/api/transactions", json={
        "description": "Sem quantidade",
        "type": "despesa",
        "amount": 10.0,
        "category_id": cat_id,
        "date_time": "2026-01-10T12:00:00",
        "recurrence": "mensal"
    }, headers=auth_headers)
    assert res.status_code == 422


def test_recurrence_installment_cannot_exceed_quantity(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    res = client.post("/api/transactions", json={
        "description": "Parcela inválida",
        "type": "despesa",
        "amount": 10.0,
        "category_id": cat_id,
        "date_time": "2026-01-10T12:00:00",
        "recurrence": "mensal",
        "recurrence_quantity": 3,
        "recurrence_installment": 4
    }, headers=auth_headers)
    assert res.status_code == 422


def test_editing_one_occurrence_does_not_affect_the_rest_of_the_series(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    created = client.post("/api/transactions", json={
        "description": "Academia",
        "type": "despesa",
        "amount": 100.0,
        "category_id": cat_id,
        "date_time": "2026-01-10T12:00:00",
        "recurrence": "mensal",
        "recurrence_quantity": 3,
        "recurrence_installment": 1
    }, headers=auth_headers).json()
    group_id = created["recurrence_group_id"]

    before = _series(client, auth_headers, group_id)
    target_id = before[1]["id"]  # the February occurrence

    up_res = client.put(f"/api/transactions/{target_id}", json={
        "amount": 150.0,
        "description": "Academia (mensalidade promocional)"
    }, headers=auth_headers)
    assert up_res.status_code == 200
    updated = up_res.json()
    # recurrence metadata is untouched by the update payload/endpoint
    assert updated["recurrence"] == "mensal"
    assert updated["recurrence_quantity"] == 3
    assert updated["recurrence_installment"] == 2

    after = _series(client, auth_headers, group_id)
    assert after[0]["amount"] == 100.0
    assert after[0]["description"] == "Academia"
    assert after[1]["amount"] == 150.0
    assert after[1]["description"] == "Academia (mensalidade promocional)"
    assert after[2]["amount"] == 100.0
    assert after[2]["description"] == "Academia"


def test_delete_only_removes_single_occurrence(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    created = client.post("/api/transactions", json={
        "description": "Curso Online",
        "type": "despesa",
        "amount": 50.0,
        "category_id": cat_id,
        "date_time": "2026-01-10T12:00:00",
        "recurrence": "diaria",
        "recurrence_quantity": 3,
        "recurrence_installment": 2
    }, headers=auth_headers).json()
    group_id = created["recurrence_group_id"]
    series = _series(client, auth_headers, group_id)
    assert len(series) == 3

    del_res = client.delete(f"/api/transactions/{series[1]['id']}?mode=only", headers=auth_headers)
    assert del_res.status_code == 204

    remaining = _series(client, auth_headers, group_id)
    assert len(remaining) == 2
    assert [t["id"] for t in remaining] == [series[0]["id"], series[2]["id"]]


def test_delete_following_removes_this_and_later_but_keeps_earlier(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    created = client.post("/api/transactions", json={
        "description": "Mensalidade Escola",
        "type": "despesa",
        "amount": 300.0,
        "category_id": cat_id,
        "date_time": "2026-01-10T12:00:00",
        "recurrence": "mensal",
        "recurrence_quantity": 5,
        "recurrence_installment": 2
    }, headers=auth_headers).json()
    group_id = created["recurrence_group_id"]
    series = _series(client, auth_headers, group_id)
    assert len(series) == 5

    # Delete from the 3rd occurrence onward
    del_res = client.delete(f"/api/transactions/{series[2]['id']}?mode=following", headers=auth_headers)
    assert del_res.status_code == 204

    remaining = _series(client, auth_headers, group_id)
    assert [t["id"] for t in remaining] == [series[0]["id"], series[1]["id"]]
