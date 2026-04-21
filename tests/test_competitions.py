import pytest
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_create_competition(client, auth_headers):
    """Тест создания соревнования"""
    response = await client.post("/competitions/", 
        headers=auth_headers,
        json={
            "name": "Тестовое соревнование",
            "description": "Описание тестового соревнования",
            "start_date": "2026-06-01T00:00:00",
            "end_date": "2026-06-07T00:00:00",
            "venue": "Бассейн",
            "city": "Москва",
            "status": "draft",
            "max_participants": 100
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Тестовое соревнование"
    assert data["city"] == "Москва"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_competitions(client):
    """Тест получения списка соревнований"""
    response = await client.get("/competitions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_competition_by_id(client, auth_headers):
    """Тест получения соревнования по ID"""
    # Создаём соревнование
    create_resp = await client.post("/competitions/",
        headers=auth_headers,
        json={
            "name": "Соревнование для поиска",
            "start_date": "2026-07-01T00:00:00",
            "end_date": "2026-07-05T00:00:00",
            "city": "СПб",
            "status": "draft"
        }
    )
    comp_id = create_resp.json()["id"]
    
    # Получаем по ID
    response = await client.get(f"/competitions/{comp_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Соревнование для поиска"


@pytest.mark.asyncio
async def test_update_competition(client, auth_headers):
    """Тест обновления соревнования"""
    # Создаём
    create_resp = await client.post("/competitions/",
        headers=auth_headers,
        json={
            "name": "Для обновления",
            "start_date": "2026-08-01T00:00:00",
            "end_date": "2026-08-03T00:00:00",
            "city": "Казань",
            "status": "draft"
        }
    )
    comp_id = create_resp.json()["id"]
    
    # Обновляем
    response = await client.put(f"/competitions/{comp_id}",
        headers=auth_headers,
        json={"name": "Обновлённое название", "status": "ongoing"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Обновлённое название"
    assert response.json()["status"] == "ongoing"


@pytest.mark.asyncio
async def test_delete_competition(client, auth_headers):
    """Тест удаления соревнования"""
    create_resp = await client.post("/competitions/",
        headers=auth_headers,
        json={
            "name": "Для удаления",
            "start_date": "2026-09-01T00:00:00",
            "end_date": "2026-09-03T00:00:00",
            "city": "Екатеринбург",
            "status": "draft"
        }
    )
    comp_id = create_resp.json()["id"]
    
    response = await client.delete(f"/competitions/{comp_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Проверяем, что удалено
    get_resp = await client.get(f"/competitions/{comp_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_search_competitions(client, auth_headers):
    """Тест поиска соревнований"""
    # Создаём несколько соревнований
    await client.post("/competitions/", headers=auth_headers, json={
        "name": "Чемпионат Москвы",
        "start_date": "2026-10-01T00:00:00",
        "end_date": "2026-10-03T00:00:00",
        "city": "Москва",
        "status": "registration_open"
    })
    await client.post("/competitions/", headers=auth_headers, json={
        "name": "Кубок СПб",
        "start_date": "2026-11-01T00:00:00",
        "end_date": "2026-11-03T00:00:00",
        "city": "Санкт-Петербург",
        "status": "ongoing"
    })
    
    # Поиск по названию
    response = await client.get("/competitions/search?name=Москвы")
    assert response.status_code == 200
    html = response.text
    assert "Чемпионат Москвы" in html
    
    # Поиск по городу
    response = await client.get("/competitions/search?city=СПб")
    assert response.status_code == 200
    assert "Кубок СПб" in response.text
