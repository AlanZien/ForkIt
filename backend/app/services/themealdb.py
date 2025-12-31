"""TheMealDB API client for POC phase."""

import httpx

from app.config import settings


class TheMealDBClient:
    """Client for TheMealDB API."""

    def __init__(self) -> None:
        self.base_url = settings.themealdb_base_url

    async def search_by_name(self, name: str) -> dict:
        """Search meals by name."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/search.php", params={"s": name})
            return response.json()

    async def get_by_id(self, meal_id: str) -> dict:
        """Get meal by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/lookup.php", params={"i": meal_id}
            )
            return response.json()

    async def get_random(self) -> dict:
        """Get a random meal."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/random.php")
            return response.json()

    async def list_categories(self) -> dict:
        """List all meal categories."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/categories.php")
            return response.json()

    async def filter_by_category(self, category: str) -> dict:
        """Filter meals by category."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/filter.php", params={"c": category})
            return response.json()


themealdb_client = TheMealDBClient()
