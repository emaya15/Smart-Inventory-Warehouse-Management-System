def test_create_warehouse(client):
    login_res = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    wh_payload = {
        "warehouse_code": "WH-TEST-01",
        "name": "Test Depot",
        "city": "Chennai",
        "address": "OMR Tech Park",
        "capacity": 10000
    }
    r = client.post("/warehouses", json=wh_payload, headers=headers)
    assert r.status_code == 201
    assert r.json()["data"]["warehouse_code"] == "WH-TEST-01"
