def test_purchase_order_flow(client):
    login_res = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "Password123!"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    sup_payload = {
        "supplier_code": "SUP-TEST-PO",
        "name": "Global Components",
        "email": "global@sup.com",
        "phone": "9999999999",
        "gst_number": "33ABCDE1234F1Z5",
        "address": "Delhi, India",
        "lead_time_days": 2
    }
    client.post("/suppliers", json=sup_payload, headers=headers)

    po_payload = {
        "supplier_id": 1,
        "warehouse_id": 1,
        "items": [{"product_id": 1, "quantity_ordered": 20, "unit_cost": 1000.0}]
    }
    r = client.post("/purchase-orders", json=po_payload, headers=headers)
    assert r.status_code == 201
    po_id = r.json()["data"]["id"]

    r_app = client.put(f"/purchase-orders/{po_id}/approve", headers=headers)
    assert r_app.status_code == 200
