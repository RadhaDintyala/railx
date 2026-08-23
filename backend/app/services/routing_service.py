import asyncio
from ..providers.maps_provider import MapsProvider
from ..providers.transit_provider import TransitProvider

async def get_routes(station, destination, distance_km):
    modes, route = await asyncio.gather(
        TransitProvider().options(distance_km),
        MapsProvider().route(station, destination, distance_km),
    )
    return modes, route

