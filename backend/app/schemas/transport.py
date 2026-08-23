from enum import Enum
from pydantic import BaseModel, Field, model_validator

class FareStatus(str, Enum):
    LIVE = "LIVE"
    ESTIMATED = "ESTIMATED"
    CALCULATED = "CALCULATED"
    UNAVAILABLE = "UNAVAILABLE"

class FareEstimate(BaseModel):
    min: int = Field(ge=0)
    max: int = Field(ge=0)
    currency: str = "INR"
    status: FareStatus = FareStatus.ESTIMATED

    @model_validator(mode="after")
    def ordered(self):
        if self.max < self.min:
            raise ValueError("fare max must be >= min")
        return self

class Location(BaseModel):
    name: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

class TransportOption(BaseModel):
    mode: str
    distance_km: float = Field(ge=0)
    estimated_fare: FareEstimate
    estimated_duration_minutes: int = Field(gt=0)
    availability: str
    source: str
    route: str
    score: float | None = None

class Recommendation(BaseModel):
    mode: str
    label: str
    why: list[str]
    score: float

class RouteSegment(BaseModel):
    label: str
    mode: str
    duration_minutes: int = Field(ge=0)
    distance_km: float = Field(ge=0)
    fare: FareEstimate

