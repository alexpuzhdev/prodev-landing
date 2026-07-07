import time

import httpx

from . import config


class Backend:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=config.BACKEND_URL, timeout=10)
        self._cache: dict[str, tuple[float, object]] = {}

    async def _cached_get(self, path: str):
        now = time.monotonic()
        hit = self._cache.get(path)
        if hit and hit[0] > now:
            return hit[1]
        resp = await self._client.get(path)
        resp.raise_for_status()
        data = resp.json()
        self._cache[path] = (now + config.CACHE_TTL, data)
        return data

    async def texts(self) -> dict:
        return await self._cached_get("/api/content")

    async def text(self, key: str) -> str:
        data = await self.texts()
        row = data.get(key) or {}
        return row.get("ru") or key

    async def portfolio(self) -> list:
        resp = await self._client.get("/api/portfolio")
        resp.raise_for_status()
        return resp.json()

    async def image(self, image_path: str) -> bytes:
        resp = await self._client.get(image_path)
        resp.raise_for_status()
        return resp.content

    async def create_lead(self, payload: dict) -> bool:
        resp = await self._client.post(
            "/api/leads", json=payload, headers={"X-Service-Token": config.SERVICE_TOKEN}
        )
        return resp.status_code == 200


backend = Backend()
