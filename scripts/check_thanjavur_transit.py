import sqlite3

conn = sqlite3.connect('travel_platform.db')
c = conn.cursor()

c.execute("SELECT id, name FROM cities WHERE name LIKE '%Thanjavur%'")
print("Thanjavur Cities:", c.fetchall())

c.execute("""
    SELECT s.transport_mode, COUNT(*) 
    FROM schedules s 
    JOIN cities c1 ON s.origin_city_id = c1.id 
    WHERE c1.name LIKE '%Thanjavur%' 
    GROUP BY s.transport_mode
""")
print("Outbound from Thanjavur by mode:", c.fetchall())

c.execute("""
    SELECT c2.name, s.transport_mode, s.service_number 
    FROM schedules s 
    JOIN cities c1 ON s.origin_city_id = c1.id 
    JOIN cities c2 ON s.dest_city_id = c2.id 
    WHERE c1.name LIKE '%Thanjavur%'
    LIMIT 20
""")
print("Outbound connections from Thanjavur:", c.fetchall())
