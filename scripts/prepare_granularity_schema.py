import sqlite3
import re
import os

DB_PATH = "travel_platform.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Inspect current table counts
cursor.execute("SELECT COUNT(*) FROM cities")
print("Original cities count:", cursor.fetchone()[0])
cursor.execute("SELECT COUNT(*) FROM places")
print("Original places count:", cursor.fetchone()[0])

# 2. Add granularity_level column to cities if not exists
try:
    cursor.execute("ALTER TABLE cities ADD COLUMN granularity_level TEXT DEFAULT 'city'")
    conn.commit()
    print("Added column granularity_level to cities")
except sqlite3.OperationalError:
    print("Column granularity_level already exists")

# 3. Add place_type / granularity_level to places if not exists
try:
    cursor.execute("ALTER TABLE places ADD COLUMN granularity_level TEXT DEFAULT 'point_of_interest'")
    conn.commit()
    print("Added column granularity_level to places")
except sqlite3.OperationalError:
    print("Column granularity_level already exists in places")
