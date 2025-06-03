def test_create_get_item(test_client, item_payload):
    # Create the item
    response = test_client.post("/items", json=item_payload)
    assert response.status_code == 201
    response_json = response.json()

    # Get the created item
    response = test_client.get(f"/items/{response_json["id"]}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["owner_id"] == 1
    assert response_json["name"] == item_payload["name"]
    assert response_json["price"] == item_payload["price"]
