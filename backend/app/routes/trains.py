from starlette.responses import JSONResponse
from ..providers.csv_provider import train_rows, train_view

async def all_trains(request): return await search(request)

async def search(request):
    query = request.query_params
    filters = {"origin": query.get("origin"), "destination": query.get("destination"), "train_number": query.get("train_number"), "availability": query.get("availability"), "class": query.get("class"), "sort_by": query.get("sort_by")}
    if query.get("max_fare") is not None: filters["max_fare"] = float(query["max_fare"])
    if query.get("max_duration") is not None: filters["max_duration"] = float(query["max_duration"])
    return JSONResponse({"trains": [train_view(row) for row in train_rows(filters)], "data_notice": "Synthetic CSV prototype data"})
