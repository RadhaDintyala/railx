def recommend(options):
    ranked = sorted(options, key=lambda o: o["score"], reverse=True)
    best = ranked[0]
    mode_labels = {"cab": "Cab", "auto": "Auto", "bike": "Bike taxi", "bus": "Bus", "walk": "Walk"}
    reasons = ["Direct route", "Balanced time and fare"]
    if best["mode"] == min(options, key=lambda x: x["estimated_duration_minutes"])["mode"]: reasons[0] = "Fastest"
    if best["mode"] == min(options, key=lambda x: x["estimated_fare"]["min"])["mode"]: reasons[1] = "Best value"
    return {"mode": best["mode"], "label": mode_labels[best["mode"]], "why": reasons, "score": best["score"]}

