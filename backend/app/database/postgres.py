from sqlalchemy import MetaData, Table, Column, String, Integer, Float, Text, DateTime, select, func
from sqlalchemy import create_engine
from ..config import settings

_engine = None
_ready = False

metadata = MetaData()
stations = Table("stations", metadata, Column("station_id", String, primary_key=True), Column("station_name", String), Column("city", String), Column("state", String), Column("latitude", Float), Column("longitude", Float), Column("data_source", String))
trains = Table("trains", metadata, Column("train_number", String, primary_key=True), Column("train_name", String), Column("origin", String), Column("destination", String), Column("departure", String), Column("arrival", String), Column("duration", String), Column("classes", String), Column("availability", String), Column("fare", Integer), Column("data_source", String))
transport_options = Table("transport_options", metadata, Column("option_id", String, primary_key=True), Column("station", String), Column("final_destination", String), Column("mode", String), Column("distance_km", Float), Column("duration_min", Integer), Column("min_fare", Integer), Column("max_fare", Integer), Column("availability", String), Column("fare_type", String), Column("data_source", String))
routes = Table("routes", metadata, Column("route_id", String, primary_key=True), Column("station", String), Column("final_destination", String), Column("total_distance_km", Float), Column("recommended_mode", String), Column("estimated_total_time_min", Integer), Column("recommendation_reason", Text), Column("data_source", String))
users = Table("users", metadata, Column("id", String, primary_key=True), Column("name", String), Column("email", String, unique=True), Column("phone", String), Column("password_hash", String), Column("created_at", DateTime))

async def initialize_postgres():
    global _engine, _ready
    if not settings.database_url.startswith("postgresql"):
        return False
    url = settings.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if "sslmode=" not in url: url += "&sslmode=require" if "?" in url else "?sslmode=require"
    engine = create_engine(url, pool_pre_ping=True)
    try:
        metadata.create_all(engine)
        from ..providers.csv_provider import data
        with engine.begin() as conn:
            for table, key in ((stations, "stations"), (trains, "trains"), (transport_options, "transport_options"), (routes, "routes")):
                if conn.scalar(select(func.count()).select_from(table)) == 0:
                    rows = []
                    for source in data()[key]:
                        row = dict(source)
                        if table is trains:
                            row["fare"] = int(float(row["fare"]))
                            row["data_source"] = row.get("data_source", "Synthetic")
                        if table is stations:
                            row["latitude"], row["longitude"] = float(row["latitude"]), float(row["longitude"])
                        if table is transport_options:
                            row["distance_km"] = float(row["distance_km"])
                            row["duration_min"] = int(float(row["duration_min"]))
                            row["min_fare"] = int(float(row["min_fare"]))
                            row["max_fare"] = int(float(row["max_fare"]))
                        if table is routes:
                            row["total_distance_km"] = float(row["total_distance_km"])
                            row["estimated_total_time_min"] = int(float(row["estimated_total_time_min"]))
                        rows.append(row)
                    conn.execute(table.insert(), rows)
        _engine = engine
        _ready = True
        data.cache_clear()
        return True
    except Exception:
        engine.dispose()
        return False

def postgres_is_ready():
    return _ready

def postgres_data():
    if not _ready:
        return None
    with _engine.connect() as conn:
        return {
            "stations": [dict(row) for row in conn.execute(select(stations)).mappings()],
            "trains": [dict(row) for row in conn.execute(select(trains)).mappings()],
            "transport_options": [dict(row) for row in conn.execute(select(transport_options)).mappings()],
            "routes": [dict(row) for row in conn.execute(select(routes)).mappings()],
        }

def create_postgres_user(user):
    with _engine.begin() as conn:
        conn.execute(users.insert().values(**user))

def get_postgres_user(email):
    with _engine.connect() as conn:
        row = conn.execute(select(users).where(func.lower(users.c.email) == email.lower())).mappings().first()
        return dict(row) if row else None
