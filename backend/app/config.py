import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ircts.db")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    auth_secret: str = os.getenv("AUTH_SECRET", "ircts-prototype-change-this-secret")
    maps_api_key: str = os.getenv("MAPS_API_KEY", "")
    transit_api_key: str = os.getenv("TRANSIT_API_KEY", "")
    cab_api_key: str = os.getenv("CAB_API_KEY", "")
    transport_rates: dict = None

    def __post_init__(self):
        object.__setattr__(self, "transport_rates", {
            "auto": {"base": 35, "per_km": 15, "time_rate": 0.0, "speed": 24},
            "cab": {"base": 75, "per_km": 18, "time_rate": 0.0, "speed": 30},
            "bike": {"base": 25, "per_km": 9, "time_rate": 0.0, "speed": 28},
            "bus": {"base": 12, "per_km": 2.5, "time_rate": 0.0, "speed": 20},
            "walk": {"base": 0, "per_km": 0, "time_rate": 0.0, "speed": 5},
        })

settings = Settings()
