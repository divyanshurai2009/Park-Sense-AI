"""
booking.py — Slot Booking Blueprint
====================================
Completely independent module. No imports from app.py.
Registers two API endpoints:
  POST /book      — reserve a slot
  GET  /bookings  — list all bookings
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

booking_bp = Blueprint("booking", __name__)

# In-memory store: { slot_number (int): { "user": str, "time": str } }
_bookings: dict = {}


@booking_bp.route("/book", methods=["POST"])
def book_slot():
    """
    POST /book
    Body (JSON): { "slot": 5, "user": "Alice" }
    Returns 200 on success, 400 on bad input, 409 if already booked.
    """
    data = request.get_json(silent=True) or {}

    slot = data.get("slot")
    user = (data.get("user") or "").strip()

    if not slot or not isinstance(slot, int) or slot < 1 or slot > 30:
        return jsonify({"error": "Invalid slot number (must be 1–30)"}), 400

    if not user:
        return jsonify({"error": "User name is required"}), 400

    if slot in _bookings:
        existing = _bookings[slot]
        return jsonify({
            "error": f"Slot {slot} is already booked by {existing['user']}"
        }), 409

    _bookings[slot] = {
        "slot": slot,
        "user": user,
        "time": datetime.now().strftime("%H:%M:%S")
    }

    return jsonify({
        "success": True,
        "message": f"Slot {slot} booked for {user}",
        "booking": _bookings[slot]
    }), 200


@booking_bp.route("/bookings", methods=["GET"])
def get_bookings():
    """
    GET /bookings
    Returns list of all current bookings.
    """
    return jsonify({
        "count": len(_bookings),
        "bookings": list(_bookings.values())
    }), 200


@booking_bp.route("/cancel", methods=["POST"])
def cancel_booking():
    """
    POST /cancel
    Body (JSON): { "slot": 5 }
    Cancels an existing booking.
    """
    data = request.get_json(silent=True) or {}
    slot = data.get("slot")

    if not slot or slot not in _bookings:
        return jsonify({"error": "No booking found for that slot"}), 404

    removed = _bookings.pop(slot)
    return jsonify({
        "success": True,
        "message": f"Booking for slot {removed['slot']} by {removed['user']} cancelled"
    }), 200
