import sqlite3
import re

conn = sqlite3.connect("travel_platform.db")
c = conn.cursor()

c.execute("SELECT id, name, state, popularity_rank, is_hub FROM cities")
all_cities = c.fetchall()

clean_by_state = {}
for cid, name, state, rank, is_hub in all_cities:
    has_num = bool(re.search(r'\d+$', name))
    words = name.split()
    has_suffix = len(words) >= 2 and words[-1] in [
        'Patti', 'Pattinam', 'Cheri', 'Palayam', 'Kottai', 'Ganj', 'Kheda', 
        'Gaon', 'Katte', 'Peta', 'Halli', 'Chowk', 'Bazaar', 'Puram', 'Nagar', 'Giri', 'Palli'
    ]
    if not has_num and not has_suffix:
        clean_by_state.setdefault(state, []).append((cid, name))

print(f"Total States/UTs with clean cities: {len(clean_by_state)}")
for state, c_list in sorted(clean_by_state.items()):
    print(f" - {state} ({len(c_list)} cities): {[c[1] for c in c_list]}")
