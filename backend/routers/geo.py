from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from database.db_manager import DatabaseManager

router = APIRouter(prefix="/api/geo", tags=["Geography & Destination Picker"])
db = DatabaseManager()

@router.get("/states", response_model=List[str])
def get_all_states():
    """Returns distinct list of all states and union territories in India."""
    return db.get_states()

@router.get("/cities")
def get_cities(
    state: Optional[str] = Query(None, description="State to filter cities"),
    search: Optional[str] = Query(None, description="Optional search keyword for city name"),
    limit: int = Query(500, description="Max cities to retrieve")
):
    """
    Two-step selection: Returns legitimate district/city entities strictly scoped to
    the chosen state, filtered to city/district_hq granularity level, with optional search.
    """
    return db.get_cities(state=state, search=search, limit=limit)

@router.get("/cities/{city_id}")
def get_city_detail(city_id: str):
    """Fetches details for a specific city."""
    city = db.get_city_by_id(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@router.get("/cities/{city_id}/places")
def get_city_places(
    city_id: str,
    limit: int = Query(100, description="Max places to retrieve")
):
    """
    Returns specific attractions & places within the selected city (place-level granularity).
    """
    return db.get_places_for_city(city_id, limit=limit)

@router.get("/cities/{city_id}/places/preview")
def get_city_places_preview(
    city_id: str,
    limit: int = Query(4, description="Max preview places")
):
    """Returns top landmark places for a city preview badge."""
    return db.get_city_places_preview(city_id, limit=limit)

@router.get("/places/search")
def search_places(
    q: str = Query(..., description="Place name or category keyword"),
    city_id: Optional[str] = Query(None, description="Optional city ID filter"),
    limit: int = Query(25, description="Max search results")
):
    """
    Searches authentic attractions and landmarks across districts and places.
    Enables instant keyword filtering instead of scrolling.
    """
    return db.search_places(q, city_id=city_id, limit=limit)
