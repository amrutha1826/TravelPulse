"""
Database Manager for TravelPulse - Next-Gen Autonomous Trip & Transit Platform.
Provides high-performance, indexed, parameterized SQL queries, caching, review retrieval, and multi-leg route matching.
"""
import sqlite3
import json
import math
import os
import uuid
from datetime import datetime, time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "travel_platform.db")

def get_db_connection(db_path=None):
    """Returns a SQLite connection with dict-like row access and foreign keys enabled."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH

    def get_connection(self):
        return get_db_connection(self.db_path)

    def get_db_connection(self):
        return get_db_connection(self.db_path)

    def get_states(self):
        """Retrieves all distinct states and union territories sorted alphabetically."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT state FROM cities WHERE state IS NOT NULL AND state != '' ORDER BY state ASC")
            return [row["state"] for row in cursor.fetchall()]

    def get_cities(self, state=None, search=None, limit=None):
        """
        Retrieves all legitimate cities/districts deduplicated by name.
        Filtered to city/district_hq granularity level, with optional state and search keyword filtering.
        """
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            conditions = ["(granularity_level IN ('district_hq', 'city', 'town') OR granularity_level IS NULL)"]
            params = []

            if state:
                conditions.append("state = ? COLLATE NOCASE")
                params.append(state)

            if search and search.strip():
                conditions.append("name LIKE ? COLLATE NOCASE")
                params.append(f"%{search.strip()}%")

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            query = f"""
                SELECT id, name, state, country, code, latitude, longitude, is_hub, MIN(popularity_rank) AS popularity_rank, tags, granularity_level
                FROM cities
                {where_clause}
                GROUP BY name
                ORDER BY popularity_rank ASC, name ASC
            """
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_cities_by_state(self, state_name, search=None):
        """
        Retrieves all cities strictly within a given state, deduplicated at the DB level (GROUP BY name),
        filtered to city/district_hq granularity level.
        """
        return self.get_cities(state=state_name, search=search)

    def search_places(self, query_text, city_id=None, limit=25):
        """Searches authentic places and landmarks by keyword in name, category, or famous_for."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.*, c.name AS city_name, c.state AS city_state 
                FROM places p
                JOIN cities c ON p.city_id = c.id
                WHERE (p.name LIKE ? OR p.category LIKE ? OR p.famous_for LIKE ? OR p.description LIKE ?)
            """
            kw = f"%{query_text.strip()}%"
            params = [kw, kw, kw, kw]
            if city_id:
                query += " AND p.city_id = ?"
                params.append(city_id)
            query += " ORDER BY p.rating DESC, p.num_reviews DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_city_places_preview(self, city_id, limit=6):
        """
        Retrieves a formatted list of top place names and categories within a city
        for place-level granularity previews.
        """
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, category, sub_category, rating
                FROM places
                WHERE city_id = ?
                ORDER BY rating DESC, num_reviews DESC
                LIMIT ?
            """, (city_id, limit))
            places = [dict(row) for row in cursor.fetchall()]
            return places

    def get_city_by_id(self, city_id):
        """Retrieves a city record by ID or Name."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cities WHERE id = ? OR name = ? COLLATE NOCASE", (city_id, city_id))
            row = cursor.fetchone()
            return dict(row) if row else None


    def search_direct_transport(
        self,
        origin_city_id,
        dest_city_id,
        modes=None,
        max_price=None,
        departure_window=None, # (start_time_str, end_time_str) e.g. ("06:00", "12:00")
        operators=None,
        sort_by="cheapest", # cheapest, fastest, earliest, best_value
        limit=50,
        offset=0
    ):
        """
        Executes strict, indexed multi-modal transport search (Stage 1: SQL Filter).
        Strictly enforces selected modes (zero leakage of unselected modes).
        """
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    s.id AS schedule_id,
                    s.origin_city_id,
                    c_orig.name AS origin_city_name,
                    s.dest_city_id,
                    c_dest.name AS dest_city_name,
                    s.transport_mode,
                    s.route_type,
                    s.service_number,
                    s.departure_time,
                    s.arrival_time,
                    s.duration_hours,
                    s.distance_km,
                    s.stops_count,
                    s.via_city_id,
                    s.amenities_json,
                    s.carbon_kg,
                    op.id AS operator_id,
                    op.name AS operator_name,
                    op.code AS operator_code,
                    op.rating AS operator_rating,
                    op.logo_emoji,
                    f.id AS fare_id,
                    f.seat_class,
                    f.base_fare_inr,
                    f.tax_inr,
                    f.service_fee_inr,
                    f.total_fare_inr,
                    f.baggage_allowance_kg,
                    f.is_refundable,
                    f.available_seats
                FROM schedules s
                JOIN cities c_orig ON s.origin_city_id = c_orig.id
                JOIN cities c_dest ON s.dest_city_id = c_dest.id
                JOIN operators op ON s.operator_id = op.id
                JOIN fares f ON f.schedule_id = s.id
                WHERE s.origin_city_id = ? AND s.dest_city_id = ?
            """
            params = [origin_city_id, dest_city_id]

            # 1. Strict Transport Modes Filter (MANDATORY REQUIREMENT - STAGE 1 SQL FILTER)
            if modes is not None:
                if len(modes) == 0:
                    # If modes list is explicitly empty, return 0 results
                    return []
                normalized_modes = [m.lower().strip() for m in modes]
                placeholders = ",".join(["?"] * len(normalized_modes))
                query += f" AND LOWER(s.transport_mode) IN ({placeholders})"
                params.extend(normalized_modes)

            # 2. Price Filter
            if max_price is not None and max_price > 0:
                query += " AND f.total_fare_inr <= ?"
                params.append(max_price)

            # 3. Departure Window Filter
            if departure_window and len(departure_window) == 2:
                start_t, end_t = departure_window
                if start_t <= end_t:
                    query += " AND s.departure_time >= ? AND s.departure_time <= ?"
                    params.extend([start_t, end_t])
                else:
                    # Overnight window e.g. 21:00 to 06:00
                    query += " AND (s.departure_time >= ? OR s.departure_time <= ?)"
                    params.extend([start_t, end_t])

            # 4. Operator Filter
            if operators and len(operators) > 0:
                placeholders = ",".join(["?"] * len(operators))
                query += f" AND op.name IN ({placeholders})"
                params.extend(operators)

            # 5. Sorting
            if sort_by == "cheapest":
                query += " ORDER BY f.total_fare_inr ASC, s.duration_hours ASC"
            elif sort_by == "fastest":
                query += " ORDER BY s.duration_hours ASC, f.total_fare_inr ASC"
            elif sort_by == "earliest":
                query += " ORDER BY s.departure_time ASC, f.total_fare_inr ASC"
            elif sort_by == "best_value":
                query += " ORDER BY (f.total_fare_inr * 0.5 + s.duration_hours * 250 - op.rating * 200) ASC"
            else:
                query += " ORDER BY f.total_fare_inr ASC"

            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                try:
                    d["amenities"] = json.loads(d.get("amenities_json", "[]"))
                except Exception:
                    d["amenities"] = []
                results.append(d)
            return results

    def search_connecting_transport(
        self,
        origin_city_id,
        dest_city_id,
        modes=None,
        max_price=None,
        limit=20
    ):
        """
        Finds 2-leg connecting multi-modal journeys (e.g., Train -> Bus or Flight -> Cab)
        when no direct options exist or as alternative options.
        """
        if modes is not None and len(modes) == 0:
            return []
            
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            normalized_modes = [m.lower().strip() for m in (modes or ["flight", "train", "bus", "cab"])]
            placeholders1 = ",".join(["?"] * len(normalized_modes))
            placeholders2 = ",".join(["?"] * len(normalized_modes))
            
            query = f"""
                SELECT 
                    s1.id AS leg1_id,
                    s1.transport_mode AS leg1_mode,
                    s1.service_number AS leg1_service,
                    s1.departure_time AS leg1_departure,
                    s1.arrival_time AS leg1_arrival,
                    s1.duration_hours AS leg1_duration,
                    op1.id AS leg1_operator_id,
                    op1.code AS leg1_operator_code,
                    op1.name AS leg1_operator,
                    op1.logo_emoji AS leg1_emoji,
                    f1.total_fare_inr AS leg1_fare,
                    
                    c_hub.id AS hub_city_id,
                    c_hub.name AS hub_city_name,
                    
                    s2.id AS leg2_id,
                    s2.transport_mode AS leg2_mode,
                    s2.service_number AS leg2_service,
                    s2.departure_time AS leg2_departure,
                    s2.arrival_time AS leg2_arrival,
                    s2.duration_hours AS leg2_duration,
                    op2.id AS leg2_operator_id,
                    op2.code AS leg2_operator_code,
                    op2.name AS leg2_operator,
                    op2.logo_emoji AS leg2_emoji,
                    f2.total_fare_inr AS leg2_fare,
                    
                    (s1.duration_hours + 2.0 + s2.duration_hours) AS total_duration_hours,
                    (f1.total_fare_inr + f2.total_fare_inr) AS total_fare_inr,
                    (s1.distance_km + s2.distance_km) AS total_distance_km,
                    (s1.carbon_kg + s2.carbon_kg) AS total_carbon_kg
                    
                FROM schedules s1
                JOIN fares f1 ON f1.schedule_id = s1.id
                JOIN operators op1 ON s1.operator_id = op1.id
                JOIN cities c_hub ON s1.dest_city_id = c_hub.id
                
                JOIN schedules s2 ON s2.origin_city_id = c_hub.id
                JOIN fares f2 ON f2.schedule_id = s2.id
                JOIN operators op2 ON s2.operator_id = op2.id
                
                WHERE s1.origin_city_id = ?
                  AND s2.dest_city_id = ?
                  AND s1.dest_city_id != s1.origin_city_id
                  AND s2.dest_city_id != s2.origin_city_id
                  AND LOWER(s1.transport_mode) IN ({placeholders1})
                  AND LOWER(s2.transport_mode) IN ({placeholders2})
            """
            
            params = [origin_city_id, dest_city_id] + normalized_modes + normalized_modes
            
            if max_price is not None and max_price > 0:
                query += " AND (f1.total_fare_inr + f2.total_fare_inr) <= ?"
                params.append(max_price)
                
            query += " ORDER BY total_duration_hours ASC, total_fare_inr ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            connecting_routes = []
            for row in cursor.fetchall():
                d = dict(row)
                route_obj = {
                    "schedule_id": f"{d['leg1_id']}+{d['leg2_id']}",
                    "route_type": "Connecting",
                    "origin_city_id": origin_city_id,
                    "dest_city_id": dest_city_id,
                    "transport_mode": f"{d['leg1_mode'].title()} + {d['leg2_mode'].title()}",
                    "service_number": f"{d['leg1_service']} / {d['leg2_service']}",
                    "departure_time": d["leg1_departure"],
                    "arrival_time": d["leg2_arrival"],
                    "duration_hours": round(d["total_duration_hours"], 1),
                    "distance_km": round(d["total_distance_km"], 1),
                    "total_fare_inr": round(d["total_fare_inr"], 2),
                    "base_fare_inr": round(d["total_fare_inr"] * 0.85, 2),
                    "tax_inr": round(d["total_fare_inr"] * 0.15, 2),
                    "service_fee_inr": 150.0,
                    "operator_name": f"{d['leg1_operator']} ➔ {d['leg2_operator']}",
                    "logo_emoji": f"{d['leg1_emoji']} {d['leg2_emoji']}",
                    "operator_rating": 4.5,
                    "stops_count": 1,
                    "via_city_name": d["hub_city_name"],
                    "is_refundable": 1,
                    "available_seats": 20,
                    "carbon_kg": round(d["total_carbon_kg"], 1),
                    "legs": [
                        {
                            "leg_num": 1,
                            "mode": d["leg1_mode"],
                            "service": d["leg1_service"],
                            "operator": d["leg1_operator"],
                            "departure": d["leg1_departure"],
                            "arrival": d["leg1_arrival"],
                            "duration": d["leg1_duration"],
                            "fare": d["leg1_fare"]
                        },
                        {
                            "leg_num": 2,
                            "mode": d["leg2_mode"],
                            "service": d["leg2_service"],
                            "operator": d["leg2_operator"],
                            "departure": d["leg2_departure"],
                            "arrival": d["leg2_arrival"],
                            "duration": d["leg2_duration"],
                            "fare": d["leg2_fare"],
                            "layover_hours": 2.0
                        }
                    ]
                }
                connecting_routes.append(route_obj)
            return connecting_routes

    def get_places_for_city(self, city_id, categories=None, limit=100):
        """Retrieves attractions and places in a city matching optional category filters."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM places WHERE city_id = ?"
            params = [city_id]
            
            if categories and len(categories) > 0:
                placeholders = ",".join(["?"] * len(categories))
                query += f" AND category IN ({placeholders})"
                params.extend(categories)
                
            query += " ORDER BY rating DESC, num_reviews DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_all_places_for_indexing(self):
        """Retrieves top curated places across all cities for Vector Index building."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, c.name AS city_name, c.state AS city_state 
                FROM places p
                JOIN cities c ON p.city_id = c.id
                ORDER BY (p.city_id IN ('MAA', 'DEL', 'BOM', 'BLR', 'HYD', 'CCU', 'AMD', 'JAI', 'PNQ', 'GOI', 'COK')) DESC, p.rating DESC
                LIMIT 10000
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_all_routes_for_indexing(self):
        """Retrieves route descriptions and metadata for Vector Index building."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, c1.name AS origin_name, c2.name AS dest_name, op.name AS operator_name, f.total_fare_inr
                FROM schedules s
                JOIN cities c1 ON s.origin_city_id = c1.id
                JOIN cities c2 ON s.dest_city_id = c2.id
                JOIN operators op ON s.operator_id = op.id
                JOIN fares f ON f.schedule_id = s.id
                ORDER BY (c1.is_hub + c2.is_hub) DESC, s.route_type ASC
                LIMIT 10000
            """)
            return [dict(row) for row in cursor.fetchall()]



    def get_reviews_for_entity(self, entity_type, entity_id, limit=5, offset=0):
        """Retrieves verified ground-truth reviews for a specific place, operator, or hotel."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reviews 
                WHERE entity_type = ? AND entity_id = ? 
                ORDER BY rating DESC, id ASC LIMIT ? OFFSET ?
            """, (entity_type, entity_id, limit, offset))
            rows = [dict(row) for row in cursor.fetchall()]
            if not rows and offset > 0:
                cursor.execute("""
                    SELECT * FROM reviews 
                    WHERE entity_type = ? AND entity_id = ? 
                    ORDER BY rating DESC, id ASC LIMIT ? OFFSET 0
                """, (entity_type, entity_id, limit))
                rows = [dict(row) for row in cursor.fetchall()]
            return rows

    def get_reviews_for_entities(self, entity_ids, limit_per_entity=3):
        """Retrieves reviews for a batch of place/operator IDs."""
        if not entity_ids:
            return {}
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(entity_ids))
            cursor.execute(f"""
                SELECT * FROM reviews 
                WHERE entity_id IN ({placeholders})
                ORDER BY rating DESC
            """, list(entity_ids))
            rows = cursor.fetchall()
            reviews_map = {}
            for r in rows:
                d = dict(r)
                eid = d["entity_id"]
                if eid not in reviews_map:
                    reviews_map[eid] = []
                if len(reviews_map[eid]) < limit_per_entity:
                    reviews_map[eid].append(d)
            return reviews_map

    def search_hotels(
        self,
        city_id,
        category=None,
        max_price=None,
        min_rating=None,
        area=None,
        sort_by="rating",
        limit=50
    ):
        """Searches and ranks hotels with Agoda-style filters."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM hotels WHERE city_id = ?"
            params = [city_id]
            
            if category and category != "Any Tier":
                tier_clean = category.split()[0]
                query += " AND category LIKE ?"
                params.append(f"%{tier_clean}%")
                
            if max_price is not None and max_price > 0:
                query += " AND price_per_night_inr <= ?"
                params.append(max_price)
                
            if min_rating is not None and min_rating > 0:
                query += " AND rating >= ?"
                params.append(min_rating)
                
            if area and area != "Any Area":
                query += " AND (area LIKE ? OR zone LIKE ?)"
                params.extend([f"%{area}%", f"%{area}%"])
                
            if sort_by == "price_asc":
                query += " ORDER BY price_per_night_inr ASC"
            elif sort_by == "price_desc":
                query += " ORDER BY price_per_night_inr DESC"
            elif sort_by == "popularity":
                query += " ORDER BY num_reviews DESC, rating DESC"
            else:
                query += " ORDER BY rating DESC, price_per_night_inr ASC"
                
            query += " LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            hotels = []
            for row in cursor.fetchall():
                h = dict(row)
                try:
                    h["amenities"] = json.loads(h.get("amenities_json", "[]"))
                except Exception:
                    h["amenities"] = ["WiFi", "AC", "Breakfast Included"]
                hotels.append(h)
            return hotels

    def create_booking(self, user_name, user_email, user_phone, booking_type, item_details, total_amount):
        """Creates a confirmed booking record and returns a unique PNR reference."""
        booking_ref = f"TP-{uuid.uuid4().hex[:8].upper()}"
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (id, booking_reference, user_name, user_email, user_phone, booking_type, item_details_json, total_amount_inr, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')
            """, (
                str(uuid.uuid4()),
                booking_ref,
                user_name,
                user_email,
                user_phone,
                booking_type,
                json.dumps(item_details),
                total_amount
            ))
            conn.commit()
            return booking_ref

    def get_booking(self, booking_ref):
        """Retrieves booking record by PNR reference."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE booking_reference = ?", (booking_ref,))
            row = cursor.fetchone()
            if row:
                b = dict(row)
                b["item_details"] = json.loads(b["item_details_json"])
                return b
            return None
