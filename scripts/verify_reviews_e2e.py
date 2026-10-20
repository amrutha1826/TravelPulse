import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import DatabaseManager
from engine.rag_service import RAGService
from engine.transport_service import TransportSearchService
from engine.itinerary_service import ItineraryPlanningService
from engine.hotel_service import HotelSearchService

db = DatabaseManager('travel_platform.db')
rag = RAGService(db)
ts = TransportSearchService(db, rag)
itin = ItineraryPlanningService(db, rag)
htl = HotelSearchService(db)

print("==================================================================")
print("1. VERIFYING TRANSPORT REVIEWS (Thanjavur -> Rameswaram Direct Trains)")
print("==================================================================")
t_res = ts.search_routes(origin_city_id='CTY_00009', dest_city_id='CTY_00014', limit=5)
direct = t_res.get('direct_routes', [])
print(f"Total Direct Trains: {len(direct)}")
for idx, r in enumerate(direct[:3]):
    srv = r.get('service_number')
    rev_sum = r.get('review_summary', {})
    print(f"\n--- Train #{idx+1}: {srv} ---")
    print("Summary:", rev_sum.get('summary'))
    print("Top Pro:", rev_sum.get('pros', ['N/A'])[0] if rev_sum.get('pros') else 'N/A')

print("\n==================================================================")
print("2. VERIFYING ITINERARY REVIEWS (Thanjavur Itinerary)")
print("==================================================================")
i_res = itin.generate_itinerary(destination_city_id='CTY_00009', num_days=1)
day1 = i_res.get(1, {})
print("Theme:", day1.get('theme_title'))
for act in day1.get('activities', []):
    poi = act.get('poi', {})
    p_rev = act.get('review_summary', {})
    print(f"\nActivity: {poi.get('name')} ({poi.get('category')})")
    print("Review Summary:", p_rev.get('summary'))
    if p_rev.get('pros'):
        print("Grounded Quote:", p_rev['pros'][0])

print("\n==================================================================")
print("3. VERIFYING HOTEL REVIEWS (Rameswaram Hotels)")
print("==================================================================")
h_res = htl.search_hotels(city_id='CTY_00014', limit=3)
for h in h_res:
    h_rev = rag.generate_grounded_review_summary('hotel', h['id'], h['name'])
    print(f"\nHotel: {h['name']} ({h.get('category')})")
    print("Summary:", h_rev.get('summary'))
    if h_rev.get('pros'):
        print("Verified Quote:", h_rev['pros'][0])
