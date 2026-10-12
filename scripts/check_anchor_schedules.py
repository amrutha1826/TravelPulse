import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3

conn = sqlite3.connect("travel_platform.db")
c = conn.cursor()

# Get all clean city IDs from anchor data
from database.generate_1k_cities import STATE_ANCHOR_DATA
clean_names = set()
for st, d in STATE_ANCHOR_DATA.items():
    for anchor in d["anchors"]:
        clean_names.add(anchor[0])

c.execute("SELECT id, name FROM cities")
clean_ids = set()
for cid, name in c.fetchall():
    if name in clean_names:
        clean_ids.add(cid)

print(f"Total matched clean city IDs: {len(clean_ids)}")

c.execute("SELECT COUNT(*) FROM schedules WHERE origin_city_id IN ({seq}) AND dest_city_id IN ({seq})".format(
    seq=",".join([f"'{cid}'" for cid in clean_ids])
))
count_schedules = c.fetchone()[0]
print(f"Schedules directly between clean anchor cities: {count_schedules}")

# Sample routes
c.execute("""
    SELECT s.transport_mode, COUNT(*) 
    FROM schedules s 
    WHERE s.origin_city_id IN ({seq}) AND s.dest_city_id IN ({seq})
    GROUP BY s.transport_mode
""".format(seq=",".join([f"'{cid}'" for cid in clean_ids])))
print("Clean anchor schedules by mode:", c.fetchall())
