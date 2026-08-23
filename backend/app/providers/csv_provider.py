import csv
from pathlib import Path
from functools import lru_cache

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

class CsvDataError(RuntimeError):
    pass

def _read(name, required):
    path = DATA_DIR / name
    if not path.exists():
        raise CsvDataError(f"Dataset missing: {name}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in required if column not in (reader.fieldnames or [])]
        if missing:
            raise CsvDataError(f"{name} is missing columns: {', '.join(missing)}")
        return [row for row in reader if any((value or "").strip() for value in row.values())]

def _number(value, field, row):
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise CsvDataError(f"Invalid {field} in row {row}: {value}") from exc

def _duration(value):
    if ":" in value:
        hours, minutes = value.split(":", 1)
        return int(hours) * 60 + int(minutes)
    return int(float(value))

@lru_cache(maxsize=1)
def data():
    from ..database.postgres import postgres_data
    cloud_data = postgres_data()
    if cloud_data is not None:
        return cloud_data
    stations = _read("stations.csv", ["station_id", "station_name", "city", "state", "latitude", "longitude"])
    trains = _read("trains.csv", ["train_number", "train_name", "origin", "destination", "departure", "arrival", "duration", "classes", "availability", "fare"])
    transports = _read("transport_options.csv", ["option_id", "station", "final_destination", "mode", "distance_km", "duration_min", "min_fare", "max_fare", "availability", "fare_type"])
    routes = _read("routes.csv", ["route_id", "station", "final_destination", "total_distance_km", "recommended_mode", "estimated_total_time_min", "recommendation_reason"])
    return {"stations": stations, "trains": trains, "transport_options": transports, "routes": routes}

def station_rows(query=""):
    query = query.lower().strip()
    return [row for row in data()["stations"] if not query or any(query in (row.get(key) or "").lower() for key in ("station_name", "city", "state"))]

def station(name):
    matches = station_rows(name)
    return next((row for row in matches if row["station_name"].lower() == name.lower()), matches[0] if matches else None)

def train_rows(filters=None):
    filters = filters or {}
    rows = data()["trains"]
    def matches(row):
        if filters.get("origin") and filters["origin"].lower() not in row["origin"].lower(): return False
        if filters.get("destination") and filters["destination"].lower() not in row["destination"].lower(): return False
        if filters.get("train_number") and filters["train_number"].lower() not in row["train_number"].lower(): return False
        if filters.get("availability") and row["availability"].lower() != filters["availability"].lower(): return False
        if filters.get("class") and filters["class"].lower() not in row["classes"].lower(): return False
        if filters.get("max_fare") is not None and _number(row["fare"], "fare", row["train_number"]) > filters["max_fare"]: return False
        if filters.get("max_duration") is not None and _duration(row["duration"]) > filters["max_duration"]: return False
        return True
    result = [row for row in rows if matches(row)]
    sort_by = filters.get("sort_by")
    if sort_by == "fare": result.sort(key=lambda r: _number(r["fare"], "fare", r["train_number"]))
    elif sort_by == "duration": result.sort(key=lambda r: _duration(r["duration"]))
    elif sort_by == "departure": result.sort(key=lambda r: r["departure"])
    return result

def train_view(row):
    origin = station(row["origin"]) or {"station_name": row["origin"], "station_id": ""}
    destination = station(row["destination"]) or {"station_name": row["destination"], "station_id": ""}
    return {"id": row["train_number"], "number": row["train_number"], "name": row["train_name"], "origin": {"name": origin["station_name"], "code": origin["station_id"], "latitude": float(origin.get("latitude", 0)), "longitude": float(origin.get("longitude", 0))}, "destination": {"name": destination["station_name"], "code": destination["station_id"], "latitude": float(destination.get("latitude", 0)), "longitude": float(destination.get("longitude", 0))}, "departure": row["departure"], "arrival": row["arrival"], "duration_minutes": _duration(row["duration"]), "classes": [item.strip() for item in row["classes"].split(",")], "availability": row["availability"], "fare": int(float(row["fare"])), "data_source": row.get("data_source", "Synthetic")}

def transport_rows(station_name, destination, filters=None):
    filters = filters or {}
    rows = [row for row in data()["transport_options"] if row["station"].lower() == station_name.lower() and row["final_destination"].lower() == destination.lower()]
    def matches(row):
        if filters.get("transport_mode") and row["mode"].lower() != filters["transport_mode"].lower(): return False
        if filters.get("availability") and row["availability"].lower() != filters["availability"].lower(): return False
        if filters.get("max_fare") is not None and float(row["max_fare"]) > filters["max_fare"]: return False
        if filters.get("max_duration") is not None and float(row["duration_min"]) > filters["max_duration"]: return False
        if filters.get("max_distance") is not None and float(row["distance_km"]) > filters["max_distance"]: return False
        return True
    rows = [row for row in rows if matches(row)]
    sort_by = filters.get("sort_by")
    if sort_by == "fare": rows.sort(key=lambda r: float(r["min_fare"]))
    elif sort_by == "duration": rows.sort(key=lambda r: float(r["duration_min"]))
    elif sort_by == "distance": rows.sort(key=lambda r: float(r["distance_km"]))
    return rows

def transport_view(row):
    return {"option_id": row["option_id"], "mode": row["mode"].lower(), "distance_km": float(row["distance_km"]), "estimated_fare": {"min": int(float(row["min_fare"])), "max": int(float(row["max_fare"])), "currency": "INR", "status": "ESTIMATED"}, "estimated_duration_minutes": int(float(row["duration_min"])), "availability": row["availability"], "source": row.get("data_source", "Synthetic"), "fare_type": row["fare_type"], "route": f"{row['station']} → {row['final_destination']}"}

def route_row(station_name, destination):
    return next((row for row in data()["routes"] if row["station"].lower() == station_name.lower() and row["final_destination"].lower() == destination.lower()), None)
