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
