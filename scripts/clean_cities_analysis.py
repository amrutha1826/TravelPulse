import sqlite3
import re

conn = sqlite3.connect("travel_platform.db")
c = conn.cursor()

# Check how many cities have numbers or synthetic suffixes
c.execute("SELECT id, name, state, popularity_rank FROM cities")
all_cities = c.fetchall()

print(f"Total cities in DB: {len(all_cities)}")

# Find all suffix patterns
noisy = []
clean = []
for cid, name, state, rank in all_cities:
    # Pattern: ends with digit, or has synthetic subdivision words
    # Like 'Patti', 'Pattinam', 'Cheri', 'Palayam', 'Kottai', 'Ganj', 'Kheda', 'Gaon', 'Katte', 'Peta', 'Halli', 'Chowk', 'Bazaar'
    # combined with numbers or after anchor name
    has_num = bool(re.search(r'\d+$', name))
    if has_num:
        noisy.append((cid, name, state))
    else:
        # Check if it has space and one of the suffix words
        words = name.split()
        if len(words) >= 2 and words[-1] in [
            'Patti', 'Pattinam', 'Cheri', 'Palayam', 'Kottai', 'Ganj', 'Kheda', 
            'Gaon', 'Katte', 'Peta', 'Halli', 'Chowk', 'Bazaar', 'Puram', 'Nagar', 'Giri', 'Palli'
        ]:
            noisy.append((cid, name, state))
        else:
            clean.append((cid, name, state, rank))

print(f"Detected Noisy / Sub-village entries: {len(noisy)}")
print(f"Detected Clean City / Town entries: {len(clean)}")
print("\nSample Clean Cities (first 30):")
for r in clean[:30]:
    print(r)
