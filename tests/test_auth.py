# tests/test_auth.py
def test_register_and_login(client):
    # Register
    resp = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "user"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user"]["username"] == "testuser"

    # Login
    resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
