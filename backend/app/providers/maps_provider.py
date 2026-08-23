class MapsProvider:
    async def route(self, origin: str, destination: str, distance_km: float):
        return {"route": f"{origin} → {destination}", "source": "demo_route_provider"}

