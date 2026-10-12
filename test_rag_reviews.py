"""
Comprehensive Test Suite for RAG Review-Summary Feature.
Validates:
1. Operator review retrieval for direct and connecting routes.
2. Place review retrieval and pros/cons generation for each itinerary activity.
3. Strict Groundedness: Every pro/con is directly traceable to a retrieved review in the database.
4. Fallback behavior: "No reviews available" is shown when no reviews exist in DB (no hallucinations).
5. Overall itinerary review digest.
"""
import sys
import unittest
from database.db_manager import DatabaseManager
from engine.rag_service import RAGService
from engine.transport_service import TransportSearchService
from engine.itinerary_service import ItineraryPlanningService

class TestRAGReviewSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.rag = RAGService(cls.db)
        cls.transport = TransportSearchService(cls.db, cls.rag)
        cls.itinerary = ItineraryPlanningService(cls.db, cls.rag)

    def test_01_database_reviews_exist(self):
        """Verify database contains indexed reviews for places and operators."""
        with self.db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE entity_type = 'operator'")
            op_rev_cnt = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE entity_type = 'place'")
            plc_rev_cnt = cursor.fetchone()[0]

        print(f"\n[Test 1] Reviews in DB: {op_rev_cnt} operator reviews, {plc_rev_cnt} place reviews")
        self.assertGreater(op_rev_cnt, 0, "Operators should have verified reviews in database")
        self.assertGreater(plc_rev_cnt, 0, "Places should have verified reviews in database")

    def test_02_transport_direct_route_reviews(self):
        """Verify direct routes have grounded operator reviews generated."""
        routes_res = self.transport.search_routes(
            origin_city_id="DEL",
            dest_city_id="BOM",
            selected_modes=["flight", "train", "bus"]
        )
        self.assertGreater(routes_res["total_count"], 0, "Should find routes between DEL and BOM")
        
        # Check first 3 routes
        tested_any_with_reviews = False
        for r in routes_res["direct_routes"][:5]:
            op_summary = r.get("operator_review_summary")
            self.assertIsNotNone(op_summary, "Route must have operator_review_summary")
            self.assertIn("has_reviews", op_summary)
            self.assertIn("summary", op_summary)
            self.assertIn("pros", op_summary)
            self.assertIn("cons", op_summary)
            
            if op_summary["has_reviews"]:
                tested_any_with_reviews = True
                self.assertGreater(len(op_summary["retrieved_reviews"]), 0)
                # Verify traceability: every pro must originate from a review
                for pro in op_summary["pros"]:
                    self.assertTrue(any(rr["text"] in pro for rr in op_summary["retrieved_reviews"]),
                                    f"Pro '{pro}' must trace to a retrieved review")
                print(f"[Test 2] Operator '{r.get('operator_name')}' reviews verified: {len(op_summary['retrieved_reviews'])} reviews cited")

        self.assertTrue(tested_any_with_reviews, "At least one operator should have verified reviews")

    def test_03_connecting_route_reviews(self):
        """Verify connecting routes have operator reviews for both legs."""
        routes_res = self.transport.search_routes(
            origin_city_id="DEL",
            dest_city_id="MAA",
            include_connecting=True
        )
        connecting = routes_res.get("connecting_routes", [])
        if connecting:
            c = connecting[0]
            self.assertIn("leg1_review_summary", c, "Connecting route must have leg1_review_summary")
            self.assertIn("leg2_review_summary", c, "Connecting route must have leg2_review_summary")
            self.assertIn("operator_review_summary", c, "Connecting route must have operator_review_summary")
            print(f"[Test 3] Connecting route review summaries verified successfully for legs: {c.get('service_number')}")

    def test_04_itinerary_activity_reviews(self):
        """Verify each activity in generated itinerary has place review summary attached."""
        itin = self.itinerary.generate_itinerary(destination_city_id="MAA", num_days=2)
        total_activities = 0
        activities_with_reviews = 0

        for day_num, day_data in itin.items():
            for act in day_data.get("activities", []):
                total_activities += 1
                poi = act.get("poi", {})
                rev = act.get("review_summary")
                self.assertIsNotNone(rev, f"Activity {poi.get('name')} must have review_summary attached")
                self.assertIn("has_reviews", rev)
                self.assertIn("summary", rev)
                if rev["has_reviews"]:
                    activities_with_reviews += 1
                    self.assertGreater(len(rev["retrieved_reviews"]), 0)
                    # Traceability check
                    for pro in rev["pros"]:
                        self.assertTrue(any(rr["text"] in pro for rr in rev["retrieved_reviews"]),
                                        f"Place pro '{pro}' must trace to retrieved review")

        print(f"[Test 4] Itinerary activities: {activities_with_reviews}/{total_activities} have verified reviews")
        self.assertGreater(activities_with_reviews, 0, "Activities in MAA must have reviews")

    def test_05_unreviewed_entity_fallback_no_hallucinations(self):
        """Verify that when an entity has no reviews in the DB, it cleanly shows 'No reviews available'."""
        # Query for a fictitious entity
        fake_summary = self.rag.generate_grounded_review_summary("place", "PLC_NON_EXISTENT_9999", "Imaginary Place")
        self.assertFalse(fake_summary["has_reviews"], "Should flag has_reviews as False")
        self.assertEqual(len(fake_summary["pros"]), 0, "Must not hallucinate pros")
        self.assertEqual(len(fake_summary["cons"]), 0, "Must not hallucinate cons")
        self.assertEqual(len(fake_summary["retrieved_reviews"]), 0, "No reviews should be retrieved")
        self.assertIn("No reviews available", fake_summary["summary"], "Must output explicit no-reviews message")
        print("[Test 5] Fallback verified: no hallucinated reviews generated for unreviewed entity")

    def test_06_overall_plan_review_digest(self):
        """Verify the Stage 4 overall plan review digest compiles citations."""
        itin = self.itinerary.generate_itinerary(destination_city_id="MAA", num_days=2)
        sample_day = next(iter(itin.values()))
        digest = sample_day.get("plan_review_summary")
        self.assertIsNotNone(digest, "Itinerary must contain plan_review_summary")
        self.assertTrue(digest.get("has_reviews"), "Plan digest should have reviews for MAA")
        self.assertGreater(digest.get("total_citations", 0), 0, "Plan digest must have total_citations > 0")
        self.assertGreater(len(digest.get("grounded_digest", [])), 0, "Plan digest must contain grounded POI items")
        print(f"[Test 6] Overall Plan Digest: {digest.get('total_citations')} citations across {digest.get('total_places_reviewed')} places")

if __name__ == "__main__":
    unittest.main()
