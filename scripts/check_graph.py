import sqlite3

conn = sqlite3.connect("travel_platform.db")
c = conn.cursor()

c.execute("""
    SELECT s.id, s.origin_city_id, c1.name, s.dest_city_id, c2.name, s.transport_mode 
    FROM schedules s 
    JOIN cities c1 ON s.origin_city_id = c1.id 
    JOIN cities c2 ON s.dest_city_id = c2.id 
    WHERE s.origin_city_id = 'CTY_00118' OR s.dest_city_id = 'CTY_00118'
""")
print("Nellore schedules:", c.fetchall())
