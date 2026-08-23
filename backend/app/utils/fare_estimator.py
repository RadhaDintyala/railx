from ..config import settings

def estimate_fare(mode: str, distance_km: float):
    rate = settings.transport_rates[mode]
    raw = rate["base"] + distance_km * rate["per_km"]
    spread = max(5, raw * 0.12)
    return {"min": max(0, round(raw - spread)), "max": max(0, round(raw + spread)), "currency": "INR", "status": "ESTIMATED"}
