import sqlite3

conn = sqlite3.connect("travel_platform.db")
c = conn.cursor()

print("--- CITIES INVESTIGATION ---")
c.execute("SELECT COUNT(*) FROM cities")
print("Total cities count:", c.fetchone()[0])

c.execute("SELECT id, name, state, is_hub, popularity_rank FROM cities WHERE name IN ('Chennai', 'Bengaluru', 'Bangalore', 'Nellore')")
print("Target cities:", c.fetchall())

c.execute("SELECT COUNT(*) FROM cities WHERE name LIKE '% Patti%' OR name LIKE '% Pattinam%' OR name LIKE '% Cheri%' OR name LIKE '% Palayam%' OR name LIKE '% Puram %' OR name LIKE '% Kottai%'")
print("Synthetic / noise suffix cities count:", c.fetchone()[0])

c.execute("SELECT id, name FROM cities WHERE name LIKE '%Nellore%'")
print("Nellore entries in cities:", c.fetchall())

print("\n--- PLACES INVESTIGATION ---")
c.execute("SELECT COUNT(*) FROM places")
print("Total places count:", c.fetchone()[0])

c.execute("SELECT city_id, name, category FROM places WHERE city_id IN ('MAA', 'BLR') LIMIT 10")
print("Sample places in MAA / BLR:", c.fetchall())

print("\n--- SCHEDULES INVESTIGATION ---")
c.execute("SELECT COUNT(*) FROM schedules")
print("Total schedules count:", c.fetchone()[0])

c.execute("SELECT transport_mode, COUNT(*) FROM schedules GROUP BY transport_mode")
print("Schedules by mode:", c.fetchall())

c.execute("SELECT DISTINCT origin_city_id, dest_city_id FROM schedules LIMIT 10")
print("Sample origin/dest pairs in schedules:", c.fetchall())

# Look for BLR / MAA schedules
c.execute("SELECT COUNT(*) FROM schedules WHERE origin_city_id = 'BLR' AND dest_city_id = 'MAA'")
print("Direct BLR -> MAA schedules count:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM schedules WHERE origin_city_id = 'MAA' AND dest_city_id = 'BLR'")
print("Direct MAA -> BLR schedules count:", c.fetchone()[0])

# Look for schedules by city names
c.execute("""
    SELECT s.id, s.origin_city_id, c1.name, s.dest_city_id, c2.name, s.transport_mode 
    FROM schedules s
    JOIN cities c1 ON s.origin_city_id = c1.id
    JOIN cities c2 ON s.dest_city_id = c2.id
    WHERE (c1.name LIKE '%Chennai%' AND c2.name LIKE '%Bengaluru%')
       OR (c1.name LIKE '%Chennai%' AND c2.name LIKE '%Bangalore%')
       OR (c1.name LIKE '%Bengaluru%' AND c2.name LIKE '%Chennai%')
    LIMIT 10
""")
print("Schedules connecting Chennai and Bengaluru by city name:", c.fetchall())
