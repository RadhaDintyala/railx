from starlette.responses import JSONResponse
from ..providers.csv_provider import data

async def all_routes(request):
    query = request.query_params
    rows = data()["routes"]
    if query.get("station"): rows = [row for row in rows if row["station"].lower() == query["station"].lower()]
    if query.get("final_destination"): rows = [row for row in rows if row["final_destination"].lower() == query["final_destination"].lower()]
    return JSONResponse({"routes": rows, "data_notice": "Synthetic CSV prototype data"})
