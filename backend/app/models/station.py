from dataclasses import dataclass

@dataclass
class StationRecord:
    code: str
    name: str
    latitude: float
    longitude: float

