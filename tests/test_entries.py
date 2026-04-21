import pytest


@pytest.mark.asyncio
async def test_create_entry(client, auth_headers):
    """Тест создания заявки"""
    # Сначала создаём соревнование и swim_event
    comp_resp = await client.post("/competitions/", headers=auth_headers, json={
        "name": "Соревнование для заявок",
        "start_date": "2026-12-01T00:00:00",
        "end_date": "2026-12-03T00:00:00",
        "city": "Новосибирск",
        "status": "registration_open"
    })
    comp_id = comp_resp.json()["id"]
    
    # Создаём swim_event
    event_resp = await client.post("/swim-events/", headers=auth_headers, json={
        "competition_id": comp_id,
        "name": "50m Freestyle",
        "distance": 50,
        "stroke": "freestyle"
    })
    event_id = event_resp.json()["id"]
    
    # Создаём заявку
    response = await client.post("/entries/", headers=auth_headers, json={
        "competition_id": comp_id,
        "swim_event_id": event_id,
        "athlete_id": 1,
        "entry_time": 30.5,
        "status": "pending"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["entry_time"] == 30.5


@pytest.mark.asyncio
async def test_get_entries_by_competition(client, auth_headers):
    """Тест получения заявок по соревнованию"""
    response = await client.get("/entries/competition/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_entry_status(client, auth_headers):
    """Тест обновления статуса заявки"""
    response = await client.put("/entries/1", headers=auth_headers, json={"status": "confirmed"})
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_delete_entry(client, auth_headers):
    """Тест удаления заявки"""
    response = await client.delete("/entries/1", headers=auth_headers)
    assert response.status_code == 200
