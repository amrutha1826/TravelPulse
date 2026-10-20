import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.transport_service import TransportSearchService

ts = TransportSearchService()

pairs = [
    ('CTY_00009', 'CTY_00014', 'Thanjavur', 'Rameswaram'),
    ('CTY_00009', 'MAA', 'Thanjavur', 'Chennai'),
    ('CTY_00014', 'MAA', 'Rameswaram', 'Chennai'),
    ('CTY_00009', 'IXM', 'Thanjavur', 'Madurai'),
    ('CTY_00009', 'CJB', 'Thanjavur', 'Coimbatore'),
    ('CTY_00014', 'IXM', 'Rameswaram', 'Madurai'),
    ('CTY_00014', 'BLR', 'Rameswaram', 'Bengaluru'),
    ('CTY_00009', 'CTY_00023', 'Thanjavur', 'Kumbakonam'),
    ('CTY_00008', 'MAA', 'Vellore', 'Chennai'),
    ('CTY_AP_KDP', 'CTY_00014', 'Kadapa', 'Rameswaram')
]

print("=== Systematic City Pair Verification ===")
for orig_id, dest_id, o_name, d_name in pairs:
    res = ts.search_routes(origin_city_id=orig_id, dest_city_id=dest_id)
    print(f"\n{o_name} -> {d_name}:")
    print(f"  Total routes: {res.get('total_count')}")
    print(f"  Direct routes: {len(res.get('direct_routes', []))}")
    print(f"  Multi-hop routes: {len(res.get('multihop_routes', []))}")
    rec = res.get('recommended_route')
    if rec:
        print(f"  Recommended: {rec.get('route_title')}")
        print(f"  Reason: {rec.get('reasoning')}")
