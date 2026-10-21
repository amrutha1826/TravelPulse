import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

conn = sqlite3.connect('travel_platform.db')
c = conn.cursor()

sample_cities = [
    # East
    ('CCU', 'Kolkata'), ('CTY_00099', 'Darjeeling'), ('CTY_00123', 'Puri'), ('CTY_00130', 'Gaya'),
    # North
    ('ATQ', 'Amritsar'), ('LKO', 'Lucknow'), ('CTY_00051', 'Ayodhya'), ('CTY_00153', 'Rishikesh'),
    ('CTY_00145', 'Shimla'), ('CTY_00146', 'Manali'), ('CTY_00177', 'Srinagar'), ('CTY_00186', 'Leh'),
    # West
    ('AMD', 'Ahmedabad'), ('CTY_00079', 'Udaipur'), ('CTY_00080', 'Jodhpur'), ('CTY_00081', 'Jaisalmer'),
    ('PNQ', 'Pune'), ('CTY_00182', 'Goa (Panaji)'),
    # Middle / Central
    ('BHO', 'Bhopal'), ('IDR', 'Indore'), ('CTY_00090', 'Gwalior'), ('CTY_00093', 'Khajuraho'), ('CTY_00092', 'Ujjain'),
    # North-East
    ('GAU', 'Guwahati'), ('CTY_00166', 'Kaziranga'), ('CTY_00192', 'Shillong'), ('CTY_00202', 'Gangtok'), ('CTY_00190', 'Tawang')
]

print("==================================================================")
print("VERIFYING PAN-INDIA REAL PLACES ACROSS ALL REGIONS")
print("==================================================================")

for cid, cname in sample_cities:
    c.execute("SELECT name, category FROM places WHERE city_id = ? ORDER BY id", (cid,))
    rows = c.fetchall()
    print(f"\n{cname} ({cid}):")
    for r in rows:
        print(f"  * {r[0]} [{r[1]}]")
