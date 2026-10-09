def test_dashboard_report(client):
    login_res = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    r = client.get("/reports/dashboard", headers=headers)
    assert r.status_code == 200
    assert "total_products" in r.json()
