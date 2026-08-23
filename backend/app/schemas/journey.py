from pydantic import BaseModel, Field
from .train import Train, Station
from .transport import Location, TransportOption, Recommendation, RouteSegment, FareEstimate

class FinalDestination(Location):
    pass

class JourneyRequest(BaseModel):
    origin: str = Field(min_length=2, max_length=100)
    train_id: str = Field(min_length=1)
    destination_station: str = Field(min_length=2, max_length=100)
    final_destination: FinalDestination
    passengers: int = Field(default=1, ge=1, le=9)

class JourneyResponse(BaseModel):
    journey_id: str
    train: Train
    origin: Station
    destination_station: Station
    final_destination: FinalDestination
    transport_options: list[TransportOption]
    recommendation: Recommendation
    route_segments: list[RouteSegment]
    total_estimated_time_minutes: int
    total_estimated_cost: FareEstimate
    data_notice: str

