class TransitProvider:
    async def options(self, distance_km: float):
        return ["bus", "auto", "cab", "bike", "walk"] if distance_km < 15 else ["bus", "cab", "auto"]

