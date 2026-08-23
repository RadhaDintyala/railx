from dataclasses import dataclass
@dataclass
class TrainRecord:
    id: str
    number: str
    name: str
    origin: str
    destination: str
    departure: str
    arrival: str
    duration_minutes: int
    classes: list[str]
    availability: str
    fare: int
