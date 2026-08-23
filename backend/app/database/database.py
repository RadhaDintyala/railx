import sqlite3
from pathlib import Path
from ..config import settings

DB_PATH = Path(__file__).resolve().parents[2] / "ircts.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if settings.database_url.startswith("postgresql"):
        return
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS stations (code TEXT PRIMARY KEY, name TEXT NOT NULL, latitude REAL, longitude REAL);
        CREATE TABLE IF NOT EXISTS trains (id TEXT PRIMARY KEY, number TEXT, name TEXT, origin_code TEXT, destination_code TEXT, departure TEXT, arrival TEXT, duration_minutes INTEGER, classes TEXT, availability TEXT, fare INTEGER);
        CREATE TABLE IF NOT EXISTS journeys (id TEXT PRIMARY KEY, train_id TEXT, final_destination TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS transport_options (journey_id TEXT, mode TEXT, distance_km REAL, fare_min INTEGER, fare_max INTEGER, duration_minutes INTEGER);
        CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE, phone TEXT, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
        count = conn.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
        if count == 0:
            stations = [
                ("MAS", "Chennai Central", 13.0827, 80.2707),
                ("BZA", "Vijayawada Junction", 16.5178, 80.6480),
                ("SC", "Secunderabad Junction", 17.4399, 78.4983),
                ("SBC", "KSR Bengaluru City", 12.9784, 77.5707),
            ]
            conn.executemany("INSERT INTO stations VALUES (?,?,?,?)", stations)
            trains = [
                ("12603", "12603", "Charminar Express", "MAS", "BZA", "06:10", "13:35", 445, "SL,3A,2A", "AVAILABLE", 685),
                ("12864", "12864", "Chennai–Howrah Mail", "MAS", "BZA", "16:15", "23:55", 460, "SL,3A,2A,1A", "RAC 12", 740),
                ("12608", "12608", "Lalbagh Express", "MAS", "SBC", "15:35", "21:45", 370, "CC,2S", "AVAILABLE", 520),
                ("12760", "12760", "Charminar SF Express", "SC", "BZA", "18:25", "23:10", 285, "SL,3A,2A", "WL 04", 460),
            ]
            conn.executemany("INSERT INTO trains VALUES (?,?,?,?,?,?,?,?,?,?,?)", trains)

