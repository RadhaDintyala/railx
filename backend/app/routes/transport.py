import math

from starlette.responses import JSONResponse
from ..providers.csv_provider import transport_rows, transport_view, route_row


def _number(query, name):
    value = query.get(name)
    if value is None:
        return None, None
    try:
        number = float(value)
    except ValueError:
        return None, JSONResponse({"error": f"{name} must be a number"}, status_code=400)
    if not math.isfinite(number) or number < 0:
        return None, JSONResponse({"error": f"{name} must be a finite, non-negative number"}, status_code=400)
    return number, None


async def options(request):
    query = request.query_params
    station = query.get("station", "Vijayawada Junction")
    destination = query.get("final_destination", "Andhra Loyola College")
    filters = {"transport_mode": query.get("transport_mode"), "availability": query.get("availability"), "sort_by": query.get("sort_by")}
    for name in ("max_fare", "max_duration", "max_distance"):
        value, error = _number(query, name)
        if error:
            return error
        if value is not None:
            filters[name] = value
    rows = transport_rows(station, destination, filters)
    if not rows:
        return JSONResponse({"error": "No matching synthetic transport options found"}, status_code=404)
    return JSONResponse({"options": [transport_view(row) for row in rows], "route": route_row(station, destination), "data_notice": "Synthetic CSV prototype data; fares are estimated."})


async def estimate(request):
    return JSONResponse({"error": "Use /api/transport/options for CSV-backed estimates"}, status_code=400)