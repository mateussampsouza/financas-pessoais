def test_get_default_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8
    names = [c["name"] for c in data]
    assert "Alimentação" in names
    assert "Salário" in names

def test_create_category(client):
    payload = {
        "name": "Academia",
        "icon": "heart-pulse",
        "color": "#10b981"
    }
    response = client.post("/api/categories", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Academia"
    assert data["id"] is not None

def test_create_duplicate_category(client):
    payload = {
        "name": "Alimentação",
        "icon": "utensils",
        "color": "#ef4444"
    }
    response = client.post("/api/categories", json=payload)
    assert response.status_code == 400

def test_update_category(client):
    # Create first
    created = client.post("/api/categories", json={"name": "Pets", "icon": "tag", "color": "#f97316"}).json()
    cat_id = created["id"]

    response = client.put(f"/api/categories/{cat_id}", json={"name": "Animais", "icon": "heart-pulse", "color": "#06b6d4"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Animais"
    assert updated["color"] == "#06b6d4"

def test_delete_category(client):
    created = client.post("/api/categories", json={"name": "Streaming", "icon": "tv", "color": "#8b5cf6"}).json()
    cat_id = created["id"]

    del_resp = client.delete(f"/api/categories/{cat_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/categories/{cat_id}")
    assert get_resp.status_code == 404
