import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

@pytest.mark.asyncio
async def test_search_and_plan():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        trains = await client.get('/api/trains/search?origin=Chennai&destination=Vijayawada')
        assert trains.status_code == 200
        train = trains.json()['trains'][0]
        result = await client.post('/api/journey/plan', json={
            'origin':'Chennai','train_id':train['id'],'destination_station':train['destination']['name'],
            'final_destination':{'name':'Andhra Loyola College','latitude':16.503,'longitude':80.653}
        })
    assert result.status_code == 201
    body = result.json()
    assert body['recommendation']['mode'] in {'auto','cab','bike','bus','walk'}
    assert all(option['estimated_fare']['status'] == 'ESTIMATED' for option in body['transport_options'])

@pytest.mark.asyncio
async def test_invalid_coordinates():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post('/api/journey/plan', json={'origin':'Chennai','train_id':'12603','destination_station':'Vijayawada Junction','final_destination':{'name':'Bad','latitude':99,'longitude':80}})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_csv_filters_and_transport_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        trains = await client.get('/api/trains/search?origin=Chennai%20Central&max_fare=500&sort_by=fare')
        transport = await client.get('/api/transport/options?station=Vijayawada%20Junction&final_destination=Andhra%20Loyola%20College&max_fare=150&sort_by=duration')
    assert trains.status_code == 200
    assert all(item['fare'] <= 500 for item in trains.json()['trains'])
    assert transport.status_code == 200
    assert all(item['estimated_fare']['max'] <= 150 for item in transport.json()['options'])

@pytest.mark.asyncio
async def test_authentication_lifecycle_uses_the_authenticated_token(monkeypatch):
    from app.routes import auth
    users = {}

    def find_user(email):
        return users.get(email)

    def create_user(user):
        users[user["email"]] = user

    monkeypatch.setattr(auth, "_find_user", find_user)
    monkeypatch.setattr(auth, "_create_user", create_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        invalid = await client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
        signup = await client.post("/api/auth/signup", json={"name": "QA User", "email": "qa@example.com", "password": "correct-password"})
        token = signup.json()["token"]
        me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        login = await client.post("/api/auth/login", json={"email": "qa@example.com", "password": "correct-password"})

    assert invalid.status_code == 401
    assert signup.status_code == 200
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "qa@example.com"
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_invalid_numeric_filters_return_validation_errors():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        bad_fare = await client.get("/api/trains/search?max_fare=not-a-number")
        bad_duration = await client.get("/api/trains/search?max_duration=NaN")
        bad_distance = await client.get("/api/transport/options?max_distance=-1")
        no_transport = await client.get("/api/transport/options?station=Unknown&final_destination=Unknown")

    assert bad_fare.status_code == 400
    assert "max_fare" in bad_fare.json()["error"]
    assert bad_duration.status_code == 400
    assert bad_distance.status_code == 400
    assert "max_distance" in bad_distance.json()["error"]
    assert no_transport.status_code == 404