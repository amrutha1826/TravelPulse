"""
Booking & Checkout Service for Agoda-Style Travel Platform.
Manages reservation checkouts, PNR creation, transparent price breakdowns, and voucher generation.
"""
from database.db_manager import DatabaseManager
import uuid
import json
from datetime import datetime

class BookingCheckoutService:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()

    def process_booking(
        self,
        user_name,
        user_email,
        user_phone,
        booking_type, # 'transport', 'hotel', 'complete_package'
        item_details,
        num_travelers=1
    ):
        """Processes booking and creates confirmed voucher with unique PNR."""
        base_amount = float(item_details.get("base_amount", item_details.get("total_fare_inr", item_details.get("price_per_night_inr", 0))))
        taxes = float(item_details.get("taxes", base_amount * 0.12))
        convenience_fee = 150.0
        total_amount = round((base_amount + taxes) * num_travelers + convenience_fee, 2)

        booking_payload = {
            "item_details": item_details,
            "num_travelers": num_travelers,
            "pricing": {
                "base_amount_per_person": base_amount,
                "taxes_and_fees": taxes,
                "convenience_fee": convenience_fee,
                "total_amount_inr": total_amount
            },
            "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        pnr = self.db.create_booking(
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            booking_type=booking_type,
            item_details=booking_payload,
            total_amount=total_amount
        )

        return {
            "booking_reference": pnr,
            "status": "Confirmed",
            "user_name": user_name,
            "user_email": user_email,
            "total_amount_inr": total_amount,
            "booking_details": booking_payload
        }
