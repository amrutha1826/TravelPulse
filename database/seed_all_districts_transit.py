"""
Seed Transit Network Schedules & Fares for All 21 District Headquarters.
Connects Kadapa, Anantapur, Chittoor, Ongole, Eluru, etc. to hubs (Tirupati, Chennai, Bengaluru, Vijayawada).
"""
import sys
import os
import sqlite3
import json
import random

DB_PATH = "d:/drl_project/travel_platform.db"

def haversine(lat1, lon1, lat2, lon2):
    import math
    R = 6371.0
    dlat = math.radians(lon2 - lon1) # note: using lat/lon diff
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, latitude, longitude FROM cities")
    cities = {r[0]: {"name": r[1], "lat": r[2], "lon": r[3]} for r in cursor.fetchall()}

    # Define key district corridor links (City A, City B)
    CORRIDORS = [
        # Kadapa corridors
        ("CTY_AP_KDP", "CTY_00115"), # Kadapa <-> Tirupati (140 km)
        ("CTY_AP_KDP", "MAA"),       # Kadapa <-> Chennai (260 km)
        ("CTY_AP_KDP", "BLR"),       # Kadapa <-> Bengaluru (280 km)
        ("CTY_AP_KDP", "CTY_00118"), # Kadapa <-> Nellore (160 km)
        ("CTY_AP_KDP", "CTY_AP_CTR"),# Kadapa <-> Chittoor (160 km)

        # Chittoor corridors
        ("CTY_AP_CTR", "CTY_00115"), # Chittoor <-> Tirupati (70 km)
        ("CTY_AP_CTR", "MAA"),       # Chittoor <-> Chennai (150 km)
        ("CTY_AP_CTR", "BLR"),       # Chittoor <-> Bengaluru (180 km)
        ("CTY_AP_CTR", "CJB"),       # Chittoor <-> Vellore/West

        # Tirupati <-> Chennai additional links
        ("CTY_00115", "MAA"),        # Tirupati <-> Chennai

        # Anantapur corridors
        ("CTY_AP_ATP", "BLR"),       # Anantapur <-> Bengaluru (210 km)
        ("CTY_AP_ATP", "CTY_00115"), # Anantapur <-> Tirupati (260 km)
        ("CTY_AP_ATP", "HYD"),       # Anantapur <-> Hyderabad (350 km)
        ("CTY_AP_ATP", "CTY_AP_KDP"),# Anantapur <-> Kadapa (140 km)

        # Ongole corridors
        ("CTY_AP_OGL", "CTY_00114"), # Ongole <-> Vijayawada (150 km)
        ("CTY_AP_OGL", "CTY_00118"), # Ongole <-> Nellore (130 km)
        ("CTY_AP_OGL", "MAA"),       # Ongole <-> Chennai (300 km)
        ("CTY_AP_OGL", "HYD"),       # Ongole <-> Hyderabad (320 km)

        # Eluru, Machilipatnam, Bhimavaram corridors
        ("CTY_AP_ELR", "CTY_00114"), # Eluru <-> Vijayawada (60 km)
        ("CTY_AP_ELR", "VTZ"),       # Eluru <-> Visakhapatnam (290 km)
        ("CTY_AP_MTM", "CTY_00114"), # Machilipatnam <-> Vijayawada (70 km)
        ("CTY_AP_BVM", "CTY_00114"), # Bhimavaram <-> Vijayawada (110 km)
        ("CTY_AP_NDL", "CTY_00115"), # Nandyal <-> Tirupati (230 km)
        ("CTY_AP_NDL", "HYD"),       # Nandyal <-> Hyderabad (300 km)
        ("CTY_AP_SKL", "VTZ"),       # Srikakulam <-> Visakhapatnam (110 km)
        ("CTY_AP_VZM", "VTZ"),       # Vizianagaram <-> Visakhapatnam (60 km)

        # Tamil Nadu District corridors
        ("CTY_TN_DHP", "BLR"),       # Dharmapuri <-> Bengaluru (140 km)
        ("CTY_TN_DHP", "CJB"),       # Dharmapuri <-> Coimbatore (190 km)
        ("CTY_TN_NMK", "MAA"),       # Namakkal <-> Chennai (380 km)
        ("CTY_TN_NMK", "CJB"),       # Namakkal <-> Coimbatore (160 km)
        ("CTY_TN_KRR", "TRZ"),       # Karur <-> Tiruchirappalli (80 km)
        ("CTY_TN_KRR", "CJB"),       # Karur <-> Coimbatore (130 km)
        ("CTY_TN_PDK", "TRZ"),       # Pudukkottai <-> Tiruchirappalli (55 km)
        ("CTY_TN_PDK", "IXM"),       # Pudukkottai <-> Madurai (100 km)
        ("CTY_TN_VNR", "IXM"),       # Virudhunagar <-> Madurai (50 km)
        ("CTY_TN_VNR", "MAA"),       # Virudhunagar <-> Chennai (510 km)
        ("CTY_TN_TKS", "IXM"),       # Tenkasi <-> Madurai (160 km)
        ("CTY_TN_THN", "IXM"),       # Theni <-> Madurai (75 km)
        ("CTY_TN_NGP", "TRZ"),       # Nagapattinam <-> Tiruchirappalli (140 km)
        ("CTY_TN_TVR", "TRZ"),       # Tiruvarur <-> Tiruchirappalli (110 km)
        ("CTY_TN_VLP", "MAA"),       # Viluppuram <-> Chennai (160 km)
        ("CTY_TN_VLP", "TRZ"),       # Viluppuram <-> Tiruchirappalli (170 km)
        ("CTY_TN_TVL", "MAA"),       # Tiruvallur <-> Chennai (45 km)
    ]

    schedule_tuples = []
    fare_tuples = []

    print("Generating bidirectional schedules for all corridors...")
    for orig_id, dest_id in CORRIDORS:
        if orig_id not in cities or dest_id not in cities:
            continue
        c1, c2 = cities[orig_id], cities[dest_id]
        dist = round(haversine(c1["lat"], c1["lon"], c2["lat"], c2["lon"]), 1)
        if dist < 15:
            dist = 40.0

        for direction in [(orig_id, dest_id), (dest_id, orig_id)]:
            u, v = direction
            u_name, v_name = cities[u]["name"], cities[v]["name"]

            # 1. TRAIN SCHEDULE (IRCTC Superfast / Express)
            train_speed = 65.0
            t_dur = round(dist / train_speed + 0.3, 1)
            t_sid = f"SCH_CORR_{u}_{v}_TRN"
            t_fare = max(110.0, round(dist * 0.95 + 40.0, 1))
            t_dep = "06:30" if u == orig_id else "15:45"
            t_arr = f"{(int(t_dep.split(':')[0]) + int(t_dur)) % 24:02d}:{(int(t_dep.split(':')[1]) + int((t_dur%1)*60)) % 60:02d}"

            schedule_tuples.append((
                t_sid, u, v, "OP_IR_SF", "train", "direct",
                f"{random.randint(12600, 17800)} {u_name}-{v_name} Express",
                t_dep, t_arr, t_dur, dist, 0, None,
                json.dumps(["Reserved Sleeper", "Pantry Onboard", "Charging Points"]),
                round(dist * 0.03, 1)
            ))
            t_tax = round(t_fare * 0.05, 2)
            t_tot = round(t_fare + t_tax + 35.0, 2)
            fare_tuples.append((
                f"FAR_{t_sid}_STD", t_sid, "Sleeper / 2S",
                t_fare, t_tax, 35.0, t_tot, 15.0, 1, 45
            ))

            # 2. BUS SCHEDULE (APSRTC / SETC / IntrCity SmartBus)
            b_op = "OP_BUS_SMART" if dist > 180 else "OP_BUS_SETC"
            bus_speed = 50.0
            b_dur = round(dist / bus_speed + 0.5, 1)
            b_sid = f"SCH_CORR_{u}_{v}_BUS"
            b_fare = max(150.0, round(dist * 1.6 + 60.0, 1))
            b_dep = "08:00" if u == orig_id else "18:30"
            b_arr = f"{(int(b_dep.split(':')[0]) + int(b_dur)) % 24:02d}:{(int(b_dep.split(':')[1]) + int((b_dur%1)*60)) % 60:02d}"

            schedule_tuples.append((
                b_sid, u, v, b_op, "bus", "direct",
                f"EXP-{u[:6]}-{v[:6]}",
                b_dep, b_arr, b_dur, dist, 1, None,
                json.dumps(["AC Pushback", "Live GPS", "Water Bottle"]),
                round(dist * 0.05, 1)
            ))
            b_tax = round(b_fare * 0.05, 2)
            b_tot = round(b_fare + b_tax + 40.0, 2)
            fare_tuples.append((
                f"FAR_{b_sid}_STD", b_sid, "AC Semi-Sleeper",
                b_fare, b_tax, 40.0, b_tot, 20.0, 1, 30
            ))

            # 3. CAB SCHEDULE (Uber Intercity / MakeMyTrip)
            c_sid = f"SCH_CORR_{u}_{v}_CAB"
            c_dur = round(dist / 60.0 + 0.2, 1)
            c_fare = max(1200.0, round(dist * 14.5 + 250.0, 1))
            c_dep = "07:15" if u == orig_id else "14:00"
            c_arr = f"{(int(c_dep.split(':')[0]) + int(c_dur)) % 24:02d}:{(int(c_dep.split(':')[1]) + int((c_dur%1)*60)) % 60:02d}"

            schedule_tuples.append((
                c_sid, u, v, "OP_CAB_UBER", "cab", "direct",
                f"UBER-OUT-{u[:5]}-{v[:5]}",
                c_dep, c_arr, c_dur, dist, 0, None,
                json.dumps(["AC Sedan", "Sanitized Car", "Doorstep Pickup"]),
                round(dist * 0.12, 1)
            ))
            c_tax = round(c_fare * 0.05, 2)
            c_tot = round(c_fare + c_tax + 100.0, 2)
            fare_tuples.append((
                f"FAR_{c_sid}_SED", c_sid, "Sedan 4-Seater",
                c_fare, c_tax, 100.0, c_tot, 30.0, 1, 4
            ))

    cursor.executemany("""
        INSERT OR REPLACE INTO schedules (id, origin_city_id, dest_city_id, operator_id, transport_mode, route_type,
            service_number, departure_time, arrival_time, duration_hours, distance_km, stops_count, via_city_id, amenities_json, carbon_kg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, schedule_tuples)

    cursor.executemany("""
        INSERT OR REPLACE INTO fares (id, schedule_id, seat_class, base_fare_inr, tax_inr, service_fee_inr, total_fare_inr, baggage_allowance_kg, is_refundable, available_seats)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fare_tuples)

    conn.commit()
    print(f"Successfully seeded {len(schedule_tuples)} schedules and {len(fare_tuples)} fares across all district corridors.")
    conn.close()

if __name__ == "__main__":
    main()
