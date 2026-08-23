from ..utils.fare_estimator import estimate_fare

async def fare_for(mode, distance_km):
    return estimate_fare(mode, distance_km)

