def test_register_creates_user_and_returns_token(client):
    response = client.post("/api/auth/register", json={"username": "novo_usuario", "password": "senha123"})
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_seeds_default_categories_for_new_user(client):
    reg = client.post("/api/auth/register", json={"username": "comcategorias", "password": "senha123"})
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cats = client.get("/api/categories", headers=headers)
    assert cats.status_code == 200
    names = [c["name"] for c in cats.json()]
    assert "Alimentação" in names
    assert "Salário" in names
    assert len(names) >= 8

def test_register_duplicate_username_fails(client):
    client.post("/api/auth/register", json={"username": "duplicado", "password": "senha123"})
    response = client.post("/api/auth/register", json={"username": "duplicado", "password": "outrasenha"})
    assert response.status_code == 400

def test_register_duplicate_username_case_insensitive(client):
    client.post("/api/auth/register", json={"username": "CaseUser", "password": "senha123"})
    response = client.post("/api/auth/register", json={"username": "caseuser", "password": "outrasenha"})
    assert response.status_code == 400

def test_register_short_password_rejected(client):
    response = client.post("/api/auth/register", json={"username": "senhacurta", "password": "123"})
    assert response.status_code == 422

def test_login_success(client):
    client.post("/api/auth/register", json={"username": "loginuser", "password": "senha123"})
    response = client.post("/api/auth/login", json={"username": "loginuser", "password": "senha123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={"username": "loginuser2", "password": "senha123"})
    response = client.post("/api/auth/login", json={"username": "loginuser2", "password": "senhaerrada"})
    assert response.status_code == 401

def test_login_unknown_user_fails(client):
    response = client.post("/api/auth/login", json={"username": "naoexiste", "password": "senha123"})
    assert response.status_code == 401

def test_me_returns_authenticated_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_me_without_token_fails(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_protected_routes_require_token(client):
    assert client.get("/api/categories").status_code == 401
    assert client.get("/api/transactions").status_code == 401
    assert client.get("/api/summary").status_code == 401

def test_invalid_token_rejected(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer token-invalido"})
    assert response.status_code == 401
