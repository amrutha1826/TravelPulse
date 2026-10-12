import sqlite3

conn = sqlite3.connect("travel_platform.db")
c = conn.cursor()

c.execute("SELECT id, name, state, granularity_level FROM cities WHERE name LIKE '%Nellore%'")
cities = c.fetchall()
print(f"Nellore query in cities ({len(cities)} matches):", cities)

c.execute("SELECT id, name, category, rating FROM places WHERE city_id = 'CTY_00118'")
places = c.fetchall()
print(f"\nNellore places ({len(places)} total):")
for p in places:
    print(" -", p)
