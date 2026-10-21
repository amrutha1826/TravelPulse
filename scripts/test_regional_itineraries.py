import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database.db_manager import DatabaseManager
from engine.rag_service import RAGService
from engine.itinerary_service import ItineraryPlanningService

db = DatabaseManager('travel_platform.db')
rag = RAGService(db)
itin = ItineraryPlanningService(db, rag)

test_cities = [
    ('CTY_00009', 'Thanjavur'),
    ('CTY_00014', 'Rameswaram'),
    ('CTY_AP_KDP', 'Kadapa'),
    ('CTY_TN_TKS', 'Tenkasi')
]

for cid, cname in test_cities:
    plan = itin.generate_itinerary(destination_city_id=cid, num_days=1)
    day1 = plan.get(1, {})
    acts = day1.get('activities', [])
    print(f"=== {cname} Itinerary (Day 1) ===")
    print("Theme:", day1.get('theme_title'))
    print("Activity Count:", len(acts))
    for a in acts[:3]:
        poi = a.get('poi', {})
        rev = a.get('review_summary', {})
        print(f"  - {poi.get('name')} [{poi.get('category')}]")
        pros = rev.get('pros', [])
        if pros:
            print(f"    Grounded Quote: {pros[0]}")
    print()
