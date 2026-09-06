from starlette import status


def _create_todo(client, title):
    return client.post("/todos", json={"title": title, "description": "desc", "complete": False})


def test_todos_cursor_pagination(client):
    for i in range(3):
        response = _create_todo(client, f"todo-{i}")
        assert response.status_code == status.HTTP_201_CREATED

    first_page = client.get("/todos", params={"limit": 2})
    assert first_page.status_code == status.HTTP_200_OK

    first_body = first_page.json()
    assert len(first_body["items"]) == 2
    assert first_body["next_cursor"] is not None
    assert [item["title"] for item in first_body["items"]] == ["todo-0", "todo-1"]

    second_page = client.get("/todos", params={"limit": 2, "cursor": first_body["next_cursor"]})
    second_body = second_page.json()
    assert len(second_body["items"]) == 1
    assert second_body["next_cursor"] is None
    assert second_body["items"][0]["title"] == "todo-2"


def test_todos_rate_limited_register(client):
    # Rate limit is per remote address; 4th register should be rejected (429)
    for i in range(3):
        response = client.post(
            "/auth/register",
            json={"email": f"user{i}@example.com", "username": f"user{i}", "password": "supersecret123"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    response = client.post(
        "/auth/register",
        json={"email": "blocked@example.com", "username": "blocked", "password": "supersecret123"},
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
