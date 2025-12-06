# tests/test_tasks.py
def get_token(client, username="user1", email="u1@example.com", password="password123", role="user"):
    # Register and login helper
    client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "role": role
    })
    resp = client.post("/auth/login", json={
        "username": username,
        "password": password
    })
    return resp.get_json()["access_token"]


def test_task_crud_for_user(client):
    token = get_token(client)

    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    resp = client.post("/tasks", json={
        "title": "Test Task",
        "description": "Test Description"
    }, headers=headers)
    assert resp.status_code == 201
    task = resp.get_json()
    task_id = task["id"]

    # Get task
    resp = client.get(f"/tasks/{task_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Test Task"

    # Update task
    resp = client.put(f"/tasks/{task_id}", json={
        "completed": True
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["completed"] is True

    # List tasks
    resp = client.get("/tasks?page=1&per_page=5", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] >= 1

    # Delete task
    resp = client.delete(f"/tasks/{task_id}", headers=headers)
    assert resp.status_code == 200
