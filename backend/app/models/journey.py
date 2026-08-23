from dataclasses import dataclass

@dataclass
class JourneyRecord:
    id: str
    train_id: str
    final_destination: str

