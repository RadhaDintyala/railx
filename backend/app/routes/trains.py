import math

from starlette.responses import JSONResponse
from ..providers.csv_provider import train_rows, train_view


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


async def all_trains(request):
    return await search(request)


async def search(request):
    query = request.query_params
    filters = {"origin": query.get("origin"), "destination": query.get("destination"), "train_number": query.get("train_number"), "availability": query.get("availability"), "class": query.get("class"), "sort_by": query.get("sort_by")}
    for name in ("max_fare", "max_duration"):
        value, error = _number(query, name)
        if error:
            return error
        if value is not None:
            filters[name] = value
    return JSONResponse({"trains": [train_view(row) for row in train_rows(filters)], "data_notice": "Synthetic CSV prototype data"})