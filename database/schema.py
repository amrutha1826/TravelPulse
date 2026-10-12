"""
Database Schema DDL and Indexing for TravelPulse - Next-Gen Autonomous Trip & Transit Platform.
Includes Normalized Tables: Cities, Places, Operators, Schedules, Fares, Hotels, Reviews, and Bookings.
"""
import sqlite3
import os

SCHEMA_SQL = """
-- 1. Cities Table
CREATE TABLE IF NOT EXISTS cities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL,
    country TEXT DEFAULT 'India',
    code TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    is_hub INTEGER DEFAULT 0,
    popularity_rank INTEGER DEFAULT 50,
    tags TEXT
);

-- 2. Places / Tourist Attractions Table
CREATE TABLE IF NOT EXISTS places (
    id TEXT PRIMARY KEY,
    city_id TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    area TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    recommended_duration_hours REAL DEFAULT 2.0,
    open_time TEXT DEFAULT '09:00',
    close_time TEXT DEFAULT '18:00',
    entry_fee_inr REAL DEFAULT 0,
    best_time_of_day TEXT DEFAULT 'Morning',
    description TEXT,
    famous_for TEXT,
    rating REAL DEFAULT 4.5,
    num_reviews INTEGER DEFAULT 100,
    elderly_friendly INTEGER DEFAULT 1,
    wheelchair_accessible INTEGER DEFAULT 0,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- 3. Operators (Airlines, Railways, State & Private Bus networks, Cabs)
CREATE TABLE IF NOT EXISTS operators (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    mode TEXT NOT NULL,
    code TEXT,
    rating REAL DEFAULT 4.2,
    logo_emoji TEXT DEFAULT '🚀'
);

-- 4. Schedules (Multi-Modal Routes)
CREATE TABLE IF NOT EXISTS schedules (
    id TEXT PRIMARY KEY,
    origin_city_id TEXT NOT NULL,
    dest_city_id TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    transport_mode TEXT NOT NULL,
    route_type TEXT DEFAULT 'direct',
    service_number TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    duration_hours REAL NOT NULL,
    distance_km REAL NOT NULL,
    stops_count INTEGER DEFAULT 0,
    via_city_id TEXT,
    days_of_week TEXT DEFAULT 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
    amenities_json TEXT DEFAULT '[]',
    carbon_kg REAL DEFAULT 50.0,
    FOREIGN KEY (origin_city_id) REFERENCES cities(id),
    FOREIGN KEY (dest_city_id) REFERENCES cities(id),
    FOREIGN KEY (operator_id) REFERENCES operators(id)
);

-- 5. Fares & Seat Classes
CREATE TABLE IF NOT EXISTS fares (
    id TEXT PRIMARY KEY,
    schedule_id TEXT NOT NULL,
    seat_class TEXT NOT NULL,
    base_fare_inr REAL NOT NULL,
    tax_inr REAL NOT NULL,
    service_fee_inr REAL DEFAULT 150.0,
    total_fare_inr REAL NOT NULL,
    baggage_allowance_kg REAL DEFAULT 15.0,
    is_refundable INTEGER DEFAULT 1,
    available_seats INTEGER DEFAULT 45,
    FOREIGN KEY (schedule_id) REFERENCES schedules(id)
);

-- 6. Hotels & Accommodations
CREATE TABLE IF NOT EXISTS hotels (
    id TEXT PRIMARY KEY,
    city_id TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    area TEXT,
    zone TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    price_per_night_inr REAL NOT NULL,
    tax_per_night_inr REAL NOT NULL,
    rating REAL DEFAULT 4.5,
    num_reviews INTEGER DEFAULT 250,
    amenities_json TEXT DEFAULT '[]',
    check_in_time TEXT DEFAULT '14:00',
    check_out_time TEXT DEFAULT '11:00',
    image_url TEXT,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- 7. Reviews Table (Grounded RAG Knowledge Base)
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL, -- 'place', 'operator', 'hotel', 'route'
    entity_id TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    user_name TEXT NOT NULL,
    rating REAL NOT NULL,
    review_text TEXT NOT NULL,
    sentiment TEXT DEFAULT 'positive',
    aspects_json TEXT DEFAULT '[]',
    created_date TEXT DEFAULT '2026-01-15'
);

-- 8. Bookings & Reservations
CREATE TABLE IF NOT EXISTS bookings (
    id TEXT PRIMARY KEY,
    booking_reference TEXT UNIQUE NOT NULL,
    user_name TEXT NOT NULL,
    user_email TEXT NOT NULL,
    user_phone TEXT,
    booking_type TEXT NOT NULL,
    item_details_json TEXT NOT NULL,
    total_amount_inr REAL NOT NULL,
    status TEXT DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes (< 20ms lookup across 100,000+ rows)
CREATE INDEX IF NOT EXISTS idx_cities_name ON cities(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_cities_state ON cities(state);
CREATE INDEX IF NOT EXISTS idx_cities_coords ON cities(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_places_city_cat ON places(city_id, category);
CREATE INDEX IF NOT EXISTS idx_places_rating ON places(rating);
CREATE INDEX IF NOT EXISTS idx_schedules_od_mode ON schedules(origin_city_id, dest_city_id, transport_mode);
CREATE INDEX IF NOT EXISTS idx_schedules_mode_dep ON schedules(transport_mode, departure_time);
CREATE INDEX IF NOT EXISTS idx_fares_schedule_class ON fares(schedule_id, seat_class);
CREATE INDEX IF NOT EXISTS idx_fares_total ON fares(total_fare_inr);
CREATE INDEX IF NOT EXISTS idx_hotels_city_price ON hotels(city_id, price_per_night_inr);
CREATE INDEX IF NOT EXISTS idx_hotels_rating ON hotels(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_entity ON reviews(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
"""

def init_db(db_path="travel_platform.db", drop_existing=False):
    """Initializes the database schema with tables and indexes."""
    conn = sqlite3.connect(db_path)
    if drop_existing:
        cursor = conn.cursor()
        for tbl in ["bookings", "reviews", "hotels", "fares", "schedules", "operators", "places", "cities"]:
            cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
        conn.commit()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db(drop_existing=True)
    print("Schema initialized successfully with all tables and B-Tree indexes.")

