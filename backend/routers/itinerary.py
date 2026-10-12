from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from database.db_manager import DatabaseManager
from engine.rag_service import RAGService
from engine.itinerary_service import ItineraryPlanningService
from engine.hotel_service import HotelSearchService
from backend.schemas import (
    ItineraryGenerateRequest,
    ItineraryRegenDayRequest,
    ItinerarySwapActivityRequest
)

router = APIRouter(prefix="/api/itinerary", tags=["Day-Wise Itinerary Planner (DRL + RAG)"])

db = DatabaseManager()
rag = RAGService(db)
itinerary_service = ItineraryPlanningService(db, rag)
hotel_service = HotelSearchService(db)

@router.get("/categories")
def get_itinerary_categories():
    """Returns standard tourist interest categories."""
    return [
        "Temples & Spiritual",
        "Heritage & History",
        "Beaches & Coastline",
        "Food, Messes & Cafes",
        "Shopping & Markets",
        "Parks & Nature",
        "Entertainment & Theme Parks"
    ]

@router.post("/generate")
def generate_itinerary(req: ItineraryGenerateRequest):
    """
    Executes the strict 4-Stage Itinerary Pipeline:
      Stage 1: SQL Filter (Destination city, categories, opening hours)
      Stage 2: Vector Search (Semantic query scoring against place corpus)
      Stage 3: DRL Policy (PPO sequential decision maker: rating, diversity, time windows, distance)
      Stage 4: Grounded Review-Summary (Real visitor feedback attached to each activity & entire plan)
    """
    # Auto-pick top hotel for city if not specified
    city_hotels = hotel_service.search_hotels(req.destination_city_id, limit=1)
    selected_hotel = city_hotels[0] if city_hotels else None

    # Convert string keys in day_time_windows to int keys if provided
    formatted_windows = None
    if req.day_time_windows:
        formatted_windows = {int(k): tuple(v) for k, v in req.day_time_windows.items() if len(v) == 2}

    day_plans = itinerary_service.generate_itinerary(
        destination_city_id=req.destination_city_id,
        num_days=req.num_days,
        pace=req.pace,
        categories=req.categories,
        budget_per_day=req.budget_per_day,
        selected_hotel=selected_hotel,
        daily_start_time=req.daily_start_time,
        daily_end_time=req.daily_end_time,
        day_time_windows=formatted_windows,
        free_text_query=req.free_text_query
    )
    return {
        "destination_city_id": req.destination_city_id,
        "selected_hotel": selected_hotel,
        "num_days": req.num_days,
        "day_plans": day_plans
    }

@router.post("/regenerate-day")
def regenerate_single_day(req: ItineraryRegenDayRequest):
    """Regenerates a single day by re-invoking the DRL policy while preserving other days."""
    city_hotels = hotel_service.search_hotels(req.destination_city_id, limit=1)
    selected_hotel = city_hotels[0] if city_hotels else None

    # Convert dict keys from string to int
    converted_itin = {int(k): v for k, v in req.current_itinerary.items()}

    updated_itin = itinerary_service.regenerate_single_day(
        current_itinerary=converted_itin,
        destination_city_id=req.destination_city_id,
        day_num=req.day_num,
        pace=req.pace,
        categories=req.categories,
        selected_hotel=selected_hotel,
        daily_start_time=req.daily_start_time,
        daily_end_time=req.daily_end_time
    )
    return {"day_plans": updated_itin}

@router.post("/swap-activity")
def swap_activity(req: ItinerarySwapActivityRequest):
    """Swaps an individual activity with a replacement place and updates Stage 4 review summaries."""
    converted_itin = {int(k): v for k, v in req.current_itinerary.items()}
    updated_itin = itinerary_service.swap_activity(
        current_itinerary=converted_itin,
        day_num=req.day_num,
        activity_idx=req.activity_idx,
        new_place_id=req.new_place_id
    )
    return {"day_plans": updated_itin}
