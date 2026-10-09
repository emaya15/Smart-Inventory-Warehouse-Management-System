def test_sales_order_flow(client):
    login_res = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    cust_payload = {
        "customer_code": "CUST-SO-TEST",
        "name": "Mega Store",
        "email": "mega@store.com",
        "phone": "8888888888",
        "address": "Mumbai",
        "credit_limit": 100000.0
    }
    client.post("/customers", json=cust_payload, headers=headers)

    so_payload = {
        "customer_id": 1,
        "warehouse_id": 1,
        "items": [{"product_id": 1, "quantity": 2}]
    }
    r = client.post("/sales-orders", json=so_payload, headers=headers)
    assert r.status_code == 201
