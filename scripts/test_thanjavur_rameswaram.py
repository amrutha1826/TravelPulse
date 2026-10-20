import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from engine.transport_service import TransportSearchService

ts = TransportSearchService()
res = ts.search_routes(origin_city_id='CTY_00009', dest_city_id='CTY_00014')

print("=== Thanjavur to Rameswaram Route Search ===")
print("Total routes found:", res.get('total_count'))
print("Has direct routes:", res.get('has_direct'))
print("Direct routes count:", len(res.get('direct_routes', [])))
print("Has multi-hop routes:", res.get('has_multihop'))

print("\n--- Direct Train Options ---")
for r in res.get('direct_routes', [])[:5]:
    print(f"Service: {r.get('service_number')} | Carrier: {r.get('carrier_name')} | Dep: {r.get('departure_time')} | Arr: {r.get('arrival_time')} | Dur: {r.get('duration_hours')}h | Fare: Rs {r.get('total_fare_inr')}")

rec = res.get('recommended_route')
if rec:
    print("\n--- DRL Recommended Route ---")
    print("Statement:", rec.get('statement'))
    print("DRL Metadata:", rec.get('drl_metadata'))
