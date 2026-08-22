def test_get_default_categories(client, auth_headers):
    response = client.get("/api/categories", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8
    names = [c["name"] for c in data]
    assert "Alimentação" in names
    assert "Salário" in names

def test_create_category(client, auth_headers):
    payload = {
        "name": "Academia",
        "icon": "heart-pulse",
        "color": "#10b981"
    }
    response = client.post("/api/categories", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Academia"
    assert data["id"] is not None

def test_create_duplicate_category(client, auth_headers):
    payload = {
        "name": "Alimentação",
        "icon": "utensils",
        "color": "#ef4444"
    }
    response = client.post("/api/categories", json=payload, headers=auth_headers)
    assert response.status_code == 400

def test_update_category(client, auth_headers):
    # Create first
    created = client.post("/api/categories", json={"name": "Pets", "icon": "tag", "color": "#f97316"}, headers=auth_headers).json()
    cat_id = created["id"]

    response = client.put(
        f"/api/categories/{cat_id}",
        json={"name": "Animais", "icon": "heart-pulse", "color": "#06b6d4"},
        headers=auth_headers
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Animais"
    assert updated["color"] == "#06b6d4"

def test_delete_category(client, auth_headers):
    created = client.post("/api/categories", json={"name": "Streaming", "icon": "tv", "color": "#8b5cf6"}, headers=auth_headers).json()
    cat_id = created["id"]

    del_resp = client.delete(f"/api/categories/{cat_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/categories/{cat_id}", headers=auth_headers)
    assert get_resp.status_code == 404

def test_delete_category_with_linked_transactions_is_blocked(client, auth_headers):
    categories = client.get("/api/categories", headers=auth_headers).json()
    cat_id = categories[0]["id"]

    # Link a transaction to this category
    client.post("/api/transactions", json={
        "description": "Compra vinculada",
        "type": "despesa",
        "amount": 25.0,
        "category_id": cat_id,
        "date_time": "2026-08-20T10:00:00"
    }, headers=auth_headers)

    del_resp = client.delete(f"/api/categories/{cat_id}", headers=auth_headers)
    assert del_resp.status_code == 400
    assert "transações vinculadas" in del_resp.json()["detail"]

    # Category must still exist
    get_resp = client.get(f"/api/categories/{cat_id}", headers=auth_headers)
    assert get_resp.status_code == 200

def test_categories_are_isolated_between_users(client, auth_headers, second_user_headers):
    # User A creates a custom category
    client.post("/api/categories", json={"name": "ViagemExclusivaA", "icon": "plane", "color": "#3b82f6"}, headers=auth_headers)

    user_a_names = [c["name"] for c in client.get("/api/categories", headers=auth_headers).json()]
    user_b_names = [c["name"] for c in client.get("/api/categories", headers=second_user_headers).json()]

    assert "ViagemExclusivaA" in user_a_names
    assert "ViagemExclusivaA" not in user_b_names

def test_user_cannot_access_another_users_category_by_id(client, auth_headers, second_user_headers):
    created = client.post(
        "/api/categories", json={"name": "SoDoUsuarioA", "icon": "tag", "color": "#64748b"}, headers=auth_headers
    ).json()
    cat_id = created["id"]

    # User B cannot fetch, update, or delete user A's category
    assert client.get(f"/api/categories/{cat_id}", headers=second_user_headers).status_code == 404
    assert client.put(f"/api/categories/{cat_id}", json={"name": "Hackeado"}, headers=second_user_headers).status_code == 404
    assert client.delete(f"/api/categories/{cat_id}", headers=second_user_headers).status_code == 404
