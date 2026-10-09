def test_register_and_login(client):
    reg_payload = {
        "email": "testadmin@example.com",
        "password": "Password123!",
        "full_name": "Test Administrator",
        "role": "ADMIN"
    }
    r = client.post("/auth/register", json=reg_payload)
    assert r.status_code == 201

    login_payload = {
        "email": "testadmin@example.com",
        "password": "Password123!"
    }
    r2 = client.post("/auth/login", json=login_payload)
    assert r2.status_code == 200
    assert "access_token" in r2.json()

def test_login_invalid_password(client):
    login_payload = {
        "email": "testadmin@example.com",
        "password": "WrongPassword"
    }
    r = client.post("/auth/login", json=login_payload)
    assert r.status_code == 401
