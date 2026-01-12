import pytest

@pytest.mark.asyncio
async def test_create_and_list_items(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}

    r1 = await client.post("/items", json={"name": "A"}, headers=headers)
    assert r1.status_code == 201

    r2 = await client.get("/items", headers=headers)
    assert r2.status_code == 200
    body = r2.json()
    assert "items" in body
    assert len(body["items"]) >= 1
