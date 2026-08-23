from ..services.fare_service import fare_for
from ..services.routing_service import get_routes
from ..utils.distance import haversine_km

async def build_options(station, destination):
    distance = max(1.2, haversine_km(station["latitude"], station["longitude"], destination.latitude, destination.longitude) * 1.18)
    modes, route = await get_routes(station["name"], destination.name, distance)
    speeds = {"auto": 24, "cab": 30, "bike": 28, "bus": 20, "walk": 5}
    options = []
    for mode in modes:
        fare = await fare_for(mode, distance)
        duration = max(6, round(distance / speeds[mode] * 60 + (4 if mode in {"bus", "auto"} else 2)))
        convenience = {"cab": 1.0, "auto": .86, "bike": .82, "bus": .68, "walk": .42}[mode]
        fare_score = max(0, 1 - fare["min"] / 500)
        time_score = max(0, 1 - duration / 90)
        score = round(fare_score * .35 + time_score * .35 + convenience * .30, 3)
        options.append({"mode": mode, "distance_km": distance, "estimated_fare": fare, "estimated_duration_minutes": duration, "availability": "AVAILABLE", "source": "distance_based_estimator", "route": route["route"], "score": score})
    return options

