import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.generate_1k_cities import STATE_ANCHOR_DATA

tn_anchors = [a[0] for a in STATE_ANCHOR_DATA["Tamil Nadu"]["anchors"]]
ap_anchors = [a[0] for a in STATE_ANCHOR_DATA["Andhra Pradesh"]["anchors"]]

print(f"Tamil Nadu ({len(tn_anchors)}): {tn_anchors}")
print(f"Andhra Pradesh ({len(ap_anchors)}): {ap_anchors}")
