from starlette.responses import JSONResponse
from ..providers.csv_provider import transport_rows, transport_view, route_row

async def options(request):
    query = request.query_params
    station = query.get("station", "Vijayawada Junction")
    destination = query.get("final_destination", "Andhra Loyola College")
    filters = {"transport_mode": query.get("transport_mode"), "availability": query.get("availability"), "sort_by": query.get("sort_by")}
    for key in ("max_fare", "max_duration", "max_distance"):
        if query.get(key) is not None: filters[key] = float(query[key])
    rows = transport_rows(station, destination, filters)
    if not rows: return JSONResponse({"error": "No matching synthetic transport options found"}, status_code=404)
    return JSONResponse({"options": [transport_view(row) for row in rows], "route": route_row(station, destination), "data_notice": "Synthetic CSV prototype data; fares are estimated."})

async def estimate(request): return JSONResponse({"error": "Use /api/transport/options for CSV-backed estimates"}, status_code=400)
