from flask import Blueprint, request, jsonify
from app.services.trip_services import create_trip, get_all_trips, get_trip_detail

trip_bp = Blueprint("trip", __name__)

@trip_bp.route("/trips/generate", methods=["POST"])
def generate_trip():
    data = request.json
    result = create_trip(data)
    return jsonify(result)


@trip_bp.route("/trips", methods=["GET"])
def get_trips():
    return jsonify(get_all_trips())


@trip_bp.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    return jsonify(get_trip_detail(trip_id))