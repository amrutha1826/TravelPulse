from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from database.db_manager import DatabaseManager
from engine.hotel_service import HotelSearchService
from engine.rag_service import RAGService

router = APIRouter(prefix="/api/hotels", tags=["Hotels & Accommodations"])

db = DatabaseManager()
hotel_service = HotelSearchService(db)
rag = RAGService(db)

@router.get("/search")
def search_hotels(
    city_id: str,
    category: Optional[str] = Query(None, description="Hotel tier: Luxury, Standard, Budget, Hostel"),
    max_price: Optional[float] = Query(None, description="Max nightly price in INR"),
    min_rating: Optional[float] = Query(None, description="Minimum star rating"),
    sort_by: str = Query("rating", description="rating, price_asc, price_desc, popularity"),
    limit: int = Query(50, description="Max results")
):
    """Searches hotels with Agoda-style tier filters, ratings, and price caps."""
    cat = category if category and category != "Any Tier" else None
    results = hotel_service.search_hotels(
        city_id=city_id,
        category=cat,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        limit=limit
    )
    
    # Attach Stage 4 grounded TripAdvisor hotel reviews & normalize price
    for h in results:
        h["price_per_night"] = h.get("price_per_night_inr", h.get("price_per_night", 2500))
        h_rev = rag.generate_grounded_review_summary(
            entity_type="hotel",
            entity_id=h["id"],
            entity_name=h["name"]
        )
        h["review_summary"] = h_rev
        
    return results
