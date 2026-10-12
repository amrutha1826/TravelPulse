import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from engine.nlu_chatbot import CustomNLUReplanner
from engine.chatbot import TripState
from engine.graph_builder import MultiModalGraphBuilder
from engine.itinerary_optimizer import ChennaiItineraryOptimizer
from engine.hotel_recommender import HotelRecommender

def main():
    nlu = CustomNLUReplanner()
    graph_b = MultiModalGraphBuilder()
    itin_opt = ChennaiItineraryOptimizer()
    hotel_rec = HotelRecommender()
    
    trip = TripState(origin_city="Ahmedabad", num_days=3, pace="Moderate")
    trip.daily_itinerary = itin_opt.plan_itinerary(num_days=3)
    
    # Test user queries
    test_queries = [
        "bro i dont want to visit tirumala temple chane the itenirary",
        "switch morning flight to train",
        "change hotel to budget near mylapore",
        "replace museum on day 2 with a beach",
        "make day 1 more relaxed"
    ]
    
    for q in test_queries:
        print(f"\n==========================================")
        print(f"USER INPUT: '{q}'")
        res = nlu.process_query(q, trip, graph_b, itin_opt, hotel_rec)
        print(f"DETECTED INTENT: {res['intent']}")
        print(f"EXTRACTED ENTITIES: {res['entities']}")
        print(f"BOT RESPONSE:\n{res['reply']}")
        print(f"ACTION PERFORMED: {res['action_done']}")

if __name__ == "__main__":
    main()
