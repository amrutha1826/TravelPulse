import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json

DB_PATH = "travel_platform.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Seeding realistic district-to-district connectivity for Nellore and South India corridor...")

# Operators available
cursor.execute("SELECT id, name, mode, code FROM operators")
ops = {r[2]: r[0] for r in cursor.fetchall()}

# Schedules to add: (orig_id, dest_id, mode, op_id, service_num, dep, arr, dur, dist, fare, seat_class)
NEW_SCHEDULES = [
    # Nellore <-> Chennai (175 km)
    ("CTY_00118", "MAA", "train", "OP_IR_SF", "12711 Pinakini Express", "06:15", "09:45", 3.5, 175.0, 180.0, "2S / CC"),
    ("MAA", "CTY_00118", "train", "OP_IR_SF", "12712 Pinakini Express", "14:10", "17:35", 3.4, 175.0, 180.0, "2S / CC"),
    ("CTY_00118", "MAA", "bus", "OP_BUS_SMART", "SMART-NLR-MAA", "07:30", "11:30", 4.0, 175.0, 350.0, "AC Sleeper"),
    ("MAA", "CTY_00118", "bus", "OP_BUS_SMART", "SMART-MAA-NLR", "18:00", "22:00", 4.0, 175.0, 350.0, "AC Sleeper"),
    ("CTY_00118", "MAA", "cab", "OP_CAB_UBER", "UBER-NLR-MAA", "08:00", "11:30", 3.5, 175.0, 2800.0, "Sedan AC"),
    ("MAA", "CTY_00118", "cab", "OP_CAB_UBER", "UBER-MAA-NLR", "15:00", "18:30", 3.5, 175.0, 2800.0, "Sedan AC"),

    # Nellore <-> Vijayawada (280 km)
    ("CTY_00118", "CTY_00114", "train", "OP_IR_VB", "20677 Vande Bharat", "07:45", "11:15", 3.5, 280.0, 950.0, "AC Chair Car"),
    ("CTY_00114", "CTY_00118", "train", "OP_IR_VB", "20678 Vande Bharat", "15:30", "19:00", 3.5, 280.0, 950.0, "AC Chair Car"),
    ("CTY_00118", "CTY_00114", "bus", "OP_BUS_SETC", "APSRTC-Garuda-NLR-BZA", "08:30", "14:00", 5.5, 280.0, 480.0, "AC Garuda"),
    ("CTY_00114", "CTY_00118", "bus", "OP_BUS_SETC", "APSRTC-Garuda-BZA-NLR", "16:00", "21:30", 5.5, 280.0, 480.0, "AC Garuda"),

    # Nellore <-> Tirupati (135 km)
    ("CTY_00118", "CTY_00115", "bus", "OP_BUS_SETC", "APSRTC-Saptagiri-NLR-TPTY", "06:00", "09:00", 3.0, 135.0, 220.0, "Express"),
    ("CTY_00115", "CTY_00118", "bus", "OP_BUS_SETC", "APSRTC-Saptagiri-TPTY-NLR", "17:00", "20:00", 3.0, 135.0, 220.0, "Express"),
    ("CTY_00118", "CTY_00115", "train", "OP_IR_SF", "17238 Express", "08:15", "11:00", 2.7, 135.0, 140.0, "Second Sitting"),
    ("CTY_00115", "CTY_00118", "train", "OP_IR_SF", "17237 Express", "16:45", "19:30", 2.7, 135.0, 140.0, "Second Sitting"),

    # Tirupati <-> Bengaluru (250 km)
    ("CTY_00115", "BLR", "train", "OP_IR_SF", "16220 TPTY-SBC Express", "05:30", "11:30", 6.0, 250.0, 240.0, "Sleeper / 3A"),
    ("BLR", "CTY_00115", "train", "OP_IR_SF", "16219 SBC-TPTY Express", "20:30", "02:30", 6.0, 250.0, 240.0, "Sleeper / 3A"),
    ("CTY_00115", "BLR", "bus", "OP_BUS_KSRTC", "KSRTC-Airavat-TPTY-BLR", "07:00", "12:00", 5.0, 250.0, 520.0, "Airavat Volvo"),
    ("BLR", "CTY_00115", "bus", "OP_BUS_KSRTC", "KSRTC-Airavat-BLR-TPTY", "14:00", "19:00", 5.0, 250.0, 520.0, "Airavat Volvo"),
]

for orig, dest, mode, op_id, srv_num, dep, arr, dur, dist, fare, seat_class in NEW_SCHEDULES:
    sid = f"SCH_CORR_{orig}_{dest}_{mode[:3].upper()}"
    cursor.execute("""
        INSERT OR REPLACE INTO schedules (id, origin_city_id, dest_city_id, operator_id, transport_mode, route_type,
            service_number, departure_time, arrival_time, duration_hours, distance_km, stops_count, via_city_id, amenities_json, carbon_kg)
        VALUES (?, ?, ?, ?, ?, 'direct', ?, ?, ?, ?, ?, 0, NULL, ?, ?)
    """, (sid, orig, dest, op_id, mode, srv_num, dep, arr, dur, dist, json.dumps(["WiFi", "Comfort Seating"]), round(dist * 0.05, 1)))

    fid = f"FAR_{sid}_STD"
    tax = round(fare * 0.05, 2)
    tot = round(fare + tax + 40.0, 2)
    cursor.execute("""
        INSERT OR REPLACE INTO fares (id, schedule_id, seat_class, base_fare_inr, tax_inr, service_fee_inr, total_fare_inr, baggage_allowance_kg, is_refundable, available_seats)
        VALUES (?, ?, ?, ?, ?, 40.0, ?, 15.0, 1, 30)
    """, (fid, sid, seat_class, fare, tax, tot))

conn.commit()
print("Seeded corridor schedules and fares successfully.")
