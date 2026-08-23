import uuid
from ..schemas.journey import JourneyRequest
from ..providers.csv_provider import train_rows, train_view, transport_rows, transport_view, route_row
from ..services.recommendation_service import recommend

JOURNEY_CACHE = {}

async def plan_journey(request: JourneyRequest):
    train_source = next((row for row in train_rows({}) if row["train_number"] == request.train_id), None)
    if not train_source:
        raise ValueError("Train not found in synthetic dataset")
    train = train_view(train_source)
    destination_name = train["destination"]["name"]
    if request.destination_station.lower() != destination_name.lower():
        raise ValueError("Selected destination station does not match the train")
    options = [transport_view(row) for row in transport_rows(destination_name, request.final_destination.name)]
    if not options:
        raise ValueError("No synthetic transport options found for this destination")
    for option in options:
        fare = option["estimated_fare"]
        fare_score = max(0, 1 - fare["min"] / 250)
        time_score = max(0, 1 - option["estimated_duration_minutes"] / 60)
        availability_score = 1 if option["availability"].lower() == "available" else .35
        option["score"] = round(fare_score * .35 + time_score * .4 + availability_score * .25, 3)
    recommendation = recommend(options)
    route = route_row(destination_name, request.final_destination.name)
    if route:
        recommendation = {**recommendation, "mode": route["recommended_mode"].lower(), "label": route["recommended_mode"], "why": [route["recommendation_reason"]]}
    selected = next((option for option in options if option["mode"] == recommendation["mode"]), max(options, key=lambda option: option["score"]))
    journey_id = uuid.uuid4().hex[:10]
    total = {"min": train["fare"] + selected["estimated_fare"]["min"], "max": train["fare"] + selected["estimated_fare"]["max"], "currency": "INR", "status": "ESTIMATED"}
    response = {"journey_id": journey_id, "train": train, "origin": train["origin"], "destination_station": train["destination"], "final_destination": request.final_destination.model_dump(), "transport_options": options, "recommendation": recommendation, "route_segments": [{"label": "Train journey", "mode": "train", "duration_minutes": train["duration_minutes"], "distance_km": 0, "fare": {"min": train["fare"], "max": train["fare"], "currency": "INR", "status": "CALCULATED"}}, {"label": "Last-mile to final destination", "mode": selected["mode"], "duration_minutes": selected["estimated_duration_minutes"], "distance_km": selected["distance_km"], "fare": selected["estimated_fare"]}], "total_estimated_time_minutes": train["duration_minutes"] + selected["estimated_duration_minutes"], "total_estimated_cost": total, "data_notice": "Synthetic CSV prototype data. Fares and availability are estimates, not live IRCTC data."}
    JOURNEY_CACHE[journey_id] = response
    return response

def get_journey(journey_id):
    return JOURNEY_CACHE.get(journey_id)
