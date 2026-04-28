from app.models.trip_request import TripRequest
from app.models.trip_plan import TripPlan
from app.extensions import db
from app.services.llm_service import generate_itinerary
from app.utils.parser import parse_itinerary

def create_trip(data):
    destination = data["destination"]
    duration = data["duration_days"]
    people = data["num_people"]
    budget = data["budget"]

    prompt = f"""
    Buat itinerary perjalanan ke {destination} selama {duration} hari untuk {people} orang dengan budget {budget}.
    Format JSON:
    [
      {{
        "day": 1,
        "activity": "...",
        "estimated_cost": "...",
        "tips": "..."
      }}
    ]
    """

    try:
        # Memanggil AI
        result = generate_itinerary(prompt)
        
        if isinstance(result, dict) and "itinerary" in result:
            parsed = result["itinerary"]
        else:
            parsed = parse_itinerary(result)

        # Simpan ke Database
        trip_request = TripRequest(
            destination=destination,
            duration_days=duration,
            budget=budget 
        )
        db.session.add(trip_request)
        db.session.commit()

        for item in parsed:
            plan = TripPlan(
                day=item.get("day"),
                activity=item.get("activity"),
                estimated_cost=item.get("estimated_cost"),
                tips=item.get("tips"),
                request_id=trip_request.id
            )
            db.session.add(plan)
        db.session.commit()

        # Berhasil! Kirim kembali ke browser
        return {
            "status": "success",
            "data": {
                "id": trip_request.id,
                "destination": destination,
                "duration_days": duration,
                "budget": budget,
                "itinerary": parsed
            }
        }

    except Exception as e:
        # Jika ada error, kirim status error ke browser
        return {
            "status": "error",
            "error": str(e)
        }


def get_all_trips():
    trips = TripRequest.query.all()
    return [
        {
            "id": t.id,
            "destination": t.destination,
            "duration_days": t.duration_days,
            "budget": t.budget
        }
        for t in trips
    ]


def get_trip_detail(trip_id):
    request = TripRequest.query.get(trip_id)
    plans = TripPlan.query.filter_by(request_id=trip_id).all()

    itinerary_list = [
        {
            "day": p.day,
            "activity": p.activity,
            "estimated_cost": p.estimated_cost,
            "tips": p.tips
        }
        for p in plans
    ]

    return {
        "destination": request.destination if request else "Unknown",
        "duration_days": request.duration_days if request else 0,
        "itinerary": itinerary_list
    }