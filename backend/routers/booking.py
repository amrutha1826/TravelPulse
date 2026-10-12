from fastapi import APIRouter, HTTPException
from database.db_manager import DatabaseManager
from backend.schemas import BookingCreateRequest

router = APIRouter(prefix="/api/bookings", tags=["Bookings & Checkout"])
db = DatabaseManager()

@router.post("/create")
def create_booking(req: BookingCreateRequest):
    """Generates confirmed TravelPulse PNR and stores booking voucher in DB."""
    pnr = db.create_booking(
        user_name=req.user_name,
        user_email=req.user_email,
        user_phone=req.user_phone,
        booking_type=req.booking_type,
        item_details=req.item_details,
        total_amount=req.total_amount
    )
    return {
        "pnr": pnr,
        "status": "CONFIRMED",
        "total_amount": req.total_amount,
        "message": f"Booking successfully confirmed with PNR {pnr}."
    }
