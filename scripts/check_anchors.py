import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.generate_1k_cities import STATE_ANCHOR_DATA

total_anchors = 0
states_count = len(STATE_ANCHOR_DATA)
print(f"Total states in STATE_ANCHOR_DATA: {states_count}")

for state, d in STATE_ANCHOR_DATA.items():
    anchors = d.get("anchors", [])
    total_anchors += len(anchors)
    print(f" - {state}: {len(anchors)} anchor cities/districts (e.g. {[a[0] for a in anchors[:4]]})")

print(f"\nTotal anchor cities across all states: {total_anchors}")
