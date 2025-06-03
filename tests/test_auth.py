def test_create_get_user(test_client, user_payload):
    # Create the user
    response = test_client.post("/auth/register", json=user_payload)
    assert response.status_code == 201
    response_json = response.json()

    # Get the created user
    response = test_client.get(f"/users/{response_json["id"]}")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["first_name"] == user_payload["first_name"]
    assert response_json["email"] == user_payload["email"]
