from starlette.responses import JSONResponse
from pydantic import ValidationError
from ..schemas.journey import JourneyRequest
from ..services.journey_service import plan_journey, get_journey

async def detail(request):
    result = get_journey(request.path_params["journey_id"])
    if not result:
        return JSONResponse({"error": "Journey not found or expired from demo cache"}, status_code=404)
    return JSONResponse(result)

async def plan(request):
    try:
        payload = JourneyRequest.model_validate(await request.json())
        return JSONResponse(await plan_journey(payload), status_code=201)
    except ValidationError as e:
        return JSONResponse({"error": "Invalid journey request", "details": e.errors()}, status_code=400)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": f"Unable to plan journey: {e}"}, status_code=400)
