from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Geo Schemas ---
class CityPreview(BaseModel):
    id: str
    name: str
    state: str
    is_hub: int = 0
    latitude: float
    longitude: float

class PlacePreview(BaseModel):
    id: str
    name: str
    category: str
    rating: float = 4.5
    entry_fee_inr: float = 0.0

# --- Transport Schemas ---
class TransportSearchRequest(BaseModel):
    origin_city_id: str
    dest_city_id: str
    selected_modes: Optional[List[str]] = Field(default=["flight", "train", "bus", "cab"])
    max_price: Optional[float] = None
    departure_window: Optional[List[str]] = None # ["06:00", "12:00"]
    selected_operators: Optional[List[str]] = None
    sort_by: str = "cheapest" # cheapest, fastest, earliest, best_value
    include_connecting: bool = True
    free_text_query: Optional[str] = None
    limit: int = 50

# --- Itinerary Schemas ---
class ItineraryGenerateRequest(BaseModel):
    destination_city_id: str
    num_days: int = 3
    pace: str = "Moderate" # Relaxed, Moderate, Packed
    categories: Optional[List[str]] = None
    budget_per_day: float = 3500.0
    daily_start_time: str = "09:00"
    daily_end_time: str = "21:00"
    day_time_windows: Optional[Dict[str, List[str]]] = None # {"1": ["09:00", "21:00"]}
    free_text_query: Optional[str] = None

class ItineraryRegenDayRequest(BaseModel):
    current_itinerary: Dict[str, Any]
    destination_city_id: str
    day_num: int
    pace: str = "Moderate"
    categories: Optional[List[str]] = None
    daily_start_time: Optional[str] = None
    daily_end_time: Optional[str] = None

class ItinerarySwapActivityRequest(BaseModel):
    current_itinerary: Dict[str, Any]
    day_num: int
    activity_idx: int
    new_place_id: str

# --- Hotel Schemas ---
class HotelSearchRequest(BaseModel):
    city_id: str
    category: Optional[str] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    sort_by: str = "rating"
    limit: int = 50

# --- Booking Schemas ---
class BookingCreateRequest(BaseModel):
    user_name: str
    user_email: str
    user_phone: str
    booking_type: str = "full_trip"
    item_details: Dict[str, Any]
    total_amount: float
