def test_product_flow(client):
    # Login as Admin
    login_res = client.post("/auth/login", json={"email": "testadmin@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Category
    cat_res = client.post("/categories", json={"name": "Audio", "description": "Sound devices"}, headers=headers)
    assert cat_res.status_code in [201, 409]
    cat_id = 1

    # Create Product
    prod_payload = {
        "sku": "AUDIO-TEST-001",
        "barcode": "999888777111",
        "name": "Bass Boosted Speaker",
        "category_id": cat_id,
        "unit": "Piece",
        "cost_price": 1000.0,
        "selling_price": 1500.0,
        "reorder_level": 5,
        "reorder_quantity": 20
    }
    prod_res = client.post("/products", json=prod_payload, headers=headers)
    assert prod_res.status_code == 201
    assert prod_res.json()["data"]["sku"] == "AUDIO-TEST-001"
