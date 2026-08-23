from starlette.responses import JSONResponse
from ..providers.csv_provider import station_rows

async def all_stations(request): return JSONResponse({"stations": station_rows(request.query_params.get("q", "")), "data_notice": "Synthetic CSV prototype data"})
async def search(request): return await all_stations(request)
