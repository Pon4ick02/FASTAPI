import pytest
from httpx import AsyncClient, ASGITransport
from book import app


@pytest.mark.asyncio
async def test_get_all_books():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/all_books/")
        assert response.status_code == 200
        assert response.json() == [{"id": 1, "title": "Book 1", "author": "Author 1"}, {"id": 2, "title": "Book 2", "author": "Author 2"}]



@pytest.mark.asyncio
async def test_create_book():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/create_book", json={ "title": "Book 3", "author": "Author 3"})
        assert response.status_code == 200
        assert response.json() == {"id": 3, "title": "Book 3", "author": "Author 3"}


