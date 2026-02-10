"""API tests for GET /api/counties."""

import pytest

pytestmark = pytest.mark.asyncio


class TestGetCounties:
    """Test the /api/counties endpoint."""

    async def test_returns_200(self, async_client):
        response = await async_client.get("/api/counties")
        assert response.status_code == 200

    async def test_response_has_data_key(self, async_client):
        response = await async_client.get("/api/counties")
        body = response.json()
        assert "data" in body

    async def test_returns_26_counties(self, async_client):
        response = await async_client.get("/api/counties")
        counties = response.json()["data"]
        assert len(counties) == 26

    async def test_each_county_has_correct_structure(self, async_client):
        response = await async_client.get("/api/counties")
        counties = response.json()["data"]
        for county in counties:
            assert "name" in county
            assert "lat" in county
            assert "lon" in county

    async def test_dublin_is_in_counties(self, async_client):
        response = await async_client.get("/api/counties")
        counties = response.json()["data"]
        dublin = [c for c in counties if c["name"] == "Dublin"]
        assert len(dublin) == 1
        assert abs(dublin[0]["lat"] - 53.3498) < 0.01
        assert abs(dublin[0]["lon"] - (-6.2603)) < 0.01

    async def test_response_content_type_is_json(self, async_client):
        response = await async_client.get("/api/counties")
        assert "application/json" in response.headers["content-type"]
