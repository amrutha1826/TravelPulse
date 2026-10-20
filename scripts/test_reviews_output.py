import sqlite3

conn = sqlite3.connect('travel_platform.db')
c = conn.cursor()

print("--- Thanjavur Place Reviews ---")
c.execute("SELECT entity_name, user_name, rating, review_text FROM reviews WHERE entity_id LIKE '%CTY_00009_TEM_1%'")
for r in c.fetchall():
    print(f"[{r[2]}*] {r[1]} on {r[0]}:\n  \"{r[3]}\"\n")

print("\n--- Rameswaram Place Reviews ---")
c.execute("SELECT entity_name, user_name, rating, review_text FROM reviews WHERE entity_id LIKE '%CTY_00014_TEM_1%'")
for r in c.fetchall():
    print(f"[{r[2]}*] {r[1]} on {r[0]}:\n  \"{r[3]}\"\n")

print("\n--- Superfast Mail Express (IRCTC) Reviews ---")
c.execute("SELECT entity_name, user_name, rating, review_text FROM reviews WHERE entity_id='OP_IR_SF' LIMIT 3")
for r in c.fetchall():
    print(f"[{r[2]}*] {r[1]}:\n  \"{r[3]}\"\n")

print("\n--- KSRTC Bus Reviews ---")
c.execute("SELECT entity_name, user_name, rating, review_text FROM reviews WHERE entity_id='OP_BUS_KSRTC' LIMIT 3")
for r in c.fetchall():
    print(f"[{r[2]}*] {r[1]}:\n  \"{r[3]}\"\n")

print("\n--- Rameswaram Hotel Reviews ---")
c.execute("SELECT entity_name, user_name, rating, review_text FROM reviews WHERE entity_id LIKE '%CTY_00014%' LIMIT 3")
for r in c.fetchall():
    print(f"[{r[2]}*] {r[1]} on {r[0]}:\n  \"{r[3]}\"\n")
