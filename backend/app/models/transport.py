from dataclasses import dataclass

@dataclass
class TransportRecord:
    mode: str
    distance_km: float
    fare_min: int
    fare_max: int
    duration_minutes: int

