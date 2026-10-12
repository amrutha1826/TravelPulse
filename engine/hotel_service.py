"""
Hotel Search & Comparison Service for Agoda-Style Travel Platform.
"""
from database.db_manager import DatabaseManager

class HotelSearchService:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()

    def search_hotels(
        self,
        city_id,
        category="Any Tier",
        max_price=None,
        min_rating=None,
        area="Any Area",
        sort_by="rating",
        limit=50
    ):
        """Searches and filters indexed hotels."""
        return self.db.search_hotels(
            city_id=city_id,
            category=category,
            max_price=max_price,
            min_rating=min_rating,
            area=area,
            sort_by=sort_by,
            limit=limit
        )
