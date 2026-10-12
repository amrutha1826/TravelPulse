from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from database.db_manager import DatabaseManager
from engine.rag_service import RAGService
from engine.transport_service import TransportSearchService
from backend.schemas import TransportSearchRequest

router = APIRouter(prefix="/api/transport", tags=["Transport & Transit"])

db = DatabaseManager()
rag = RAGService(db)
transport_service = TransportSearchService(db, rag)

@router.get("/operators")
def get_transport_operators():
    """Returns list of all available carriers and operators."""
    with db.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code, logo_emoji, rating FROM operators ORDER BY rating DESC")
        return [dict(row) for row in cursor.fetchall()]

@router.post("/search")
def search_transport(req: TransportSearchRequest):
    """
    Executes the strict 4-Stage Transport Pipeline:
      Stage 1: SQL Hard Constraint Filter (Transport modes isolation, price cap, departure windows)
      Stage 2: Vector Search (RAG semantic query scoring)
      Stage 3: DRL policy sorting and connecting multi-modal combinations
      Stage 4: Grounded Carrier Review Summary generation with verified traveler citations
    """
    departure_win = tuple(req.departure_window) if req.departure_window and len(req.departure_window) == 2 else None
    
    results = transport_service.search_routes(
        origin_city_id=req.origin_city_id,
        dest_city_id=req.dest_city_id,
        selected_modes=req.selected_modes,
        max_price=req.max_price,
        departure_window=departure_win,
        selected_operators=req.selected_operators,
        sort_by=req.sort_by,
        include_connecting=req.include_connecting,
        free_text_query=req.free_text_query,
        limit=req.limit
    )
    return results
