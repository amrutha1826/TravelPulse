import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3
import re

conn = sqlite3.connect("travel_platform.db")
c = conn.cursor()

from database.generate_1k_cities import STATE_ANCHOR_DATA
anchor_names = set()
for st, d in STATE_ANCHOR_DATA.items():
    for anchor in d["anchors"]:
        anchor_names.add(anchor[0])

c.execute("SELECT id, name FROM cities")
clean_ids = set()
for cid, name in c.fetchall():
    if name in anchor_names:
        clean_ids.add(cid)

print(f"Total clean city IDs: {len(clean_ids)}")

c.execute("SELECT COUNT(*) FROM places WHERE city_id IN ({seq})".format(
    seq=",".join([f"'{cid}'" for cid in clean_ids])
))
clean_places_count = c.fetchone()[0]
print(f"Places mapped to clean cities: {clean_places_count}")

c.execute("SELECT COUNT(*) FROM places WHERE city_id NOT IN ({seq})".format(
    seq=",".join([f"'{cid}'" for cid in clean_ids])
))
noise_places_count = c.fetchone()[0]
print(f"Places mapped to noisy/synthetic cities: {noise_places_count}")
