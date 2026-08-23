from pydantic import BaseModel, Field

class Station(BaseModel):
    name: str
    code: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

class Train(BaseModel):
    id: str
    number: str
    name: str
    origin: Station
    destination: Station
    departure: str
    arrival: str
    duration_minutes: int = Field(gt=0)
    classes: list[str]
    availability: str
    fare: int = Field(gt=0)

