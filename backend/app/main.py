from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route
from .config import settings
from .database.database import init_db
from .routes.trains import search, all_trains
from .routes.journey import plan, detail
from .routes.transport import options, estimate
from .routes.stations import all_stations, search as search_stations
from .routes.routes import all_routes
from .routes.auth import signup, login, me
from .database.postgres import initialize_postgres

async def homepage(request): return JSONResponse({"name": "IRCTC – Journey Redesign", "message": "Your journey doesn't end at the railway station."})
async def health(request): return JSONResponse({"status": "ok", "demo_mode": settings.demo_mode, "database_connected": getattr(request.app.state, "database_connected", False)})
async def startup():
    init_db()
    app.state.database_connected = await initialize_postgres()

init_db()

routes = [Route("/", homepage), Route("/api/health", health), Route("/api/auth/signup", signup, methods=["POST"]), Route("/api/auth/login", login, methods=["POST"]), Route("/api/auth/me", me), Route("/api/trains", all_trains), Route("/api/trains/search", search), Route("/api/stations", all_stations), Route("/api/stations/search", search_stations), Route("/api/routes", all_routes), Route("/api/journey/plan", plan, methods=["POST"]), Route("/api/journey/{journey_id}", detail), Route("/api/transport/options", options), Route("/api/transport/estimate", estimate, methods=["POST"])]
app = Starlette(debug=True, routes=routes, on_startup=[startup])
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])
