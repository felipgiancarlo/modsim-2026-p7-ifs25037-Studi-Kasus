from app.models.trip_request import TripRequest
from app.models.trip_plan import TripPlan
from app.extensions import db
from app.services.llm_service import generate_itinerary
from app.utils.parser import parse_itinerary

def create_trip(data):
    # Mengambil data dari payload JSON
    destination = data["destination"]
    duration = data["duration_days"]
    people = data["num_people"]
    budget = data["budget"]

    # Prompt dikirim ke LLM
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

    # Mendapatkan hasil dari AI dan parsing menjadi list Python
    result = generate_itinerary(prompt)
    
    # Jika generate_itinerary sudah mengembalikan objek (hasil json.loads), 
    # kita pastikan mengambil bagian itinerary-nya
    if isinstance(result, dict) and "itinerary" in result:
        parsed = result["itinerary"]
    else:
        parsed = parse_itinerary(result)

    # Simpan Request Utama ke Database
    trip_request = TripRequest(
        destination=destination,
        duration_days=duration,
        # Pastikan kolom num_people ada di model TripRequest, 
        # jika tidak ada, baris ini bisa dihapus/disesuaikan
        budget=budget 
    )
    db.session.add(trip_request)
    db.session.commit()

    # Simpan Detail Rencana (Plans) ke Database
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

    # --- MODIFIKASI PENTING UNTUK FRONTEND ---
    # Kita bungkus dalam key "data" dan label "itinerary" 
    # agar JavaScript tidak lagi kena error 'forEach'
    return {
        "status": "success",
        "data": {
            "id": trip_request.id,
            "destination": destination,
            "duration_days": duration,
            "budget": budget,
            "itinerary": parsed  # Frontend mencari label ini
        }
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
    # Mengambil request untuk mendapatkan nama destinasi
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

    # Return dalam format yang sama agar fungsi detail di web juga jalan
    return {
        "destination": request.destination if request else "Unknown",
        "duration_days": request.duration_days if request else 0,
        "itinerary": itinerary_list
    }