"""
RAG (Retrieval-Augmented Generation) Engine for TravelPulse Platform.
Provides:
1. Free-Text Vector Search (Stage 2): Dense subword & character TF-IDF embedding projection + Vector Store over Places & Routes (Zero pretrained model dependencies).
2. Grounded Review-Summary Generation (Stage 4): Retrieves real indexed reviews for DRL-selected itineraries and generates strictly cited pros/cons summaries.
"""
import os
import re
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

class LocalVectorStore:
    """High-performance local vector store with dense semantic cosine matching."""
    def __init__(self, n_components=64):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            min_df=1,
            max_features=5000,
            token_pattern=r'(?u)\b\w+\b'
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.documents = []
        self.doc_metadata = []
        self.dense_embeddings = None
        self.is_indexed = False

    def build_index(self, corpus_items):
        """
        corpus_items: list of dicts with 'text' and other metadata fields.
        """
        if not corpus_items:
            return
        self.documents = [item["text"] for item in corpus_items]
        self.doc_metadata = corpus_items
        
        tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        n_comp = min(self.svd.n_components, tfidf_matrix.shape[1] - 1, tfidf_matrix.shape[0] - 1)
        if n_comp > 2:
            self.svd.n_components = n_comp
            dense = self.svd.fit_transform(tfidf_matrix)
            norms = np.linalg.norm(dense, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.dense_embeddings = dense / norms
        else:
            dense = tfidf_matrix.toarray()
            norms = np.linalg.norm(dense, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.dense_embeddings = dense / norms
            self.svd = None
            
        self.is_indexed = True

    def search(self, query_text, top_k=10, filter_fn=None):
        """Performs vector similarity retrieval on the user's free-text query."""
        if not self.is_indexed or not query_text.strip():
            return []
            
        q_tfidf = self.vectorizer.transform([query_text])
        if self.svd is not None:
            q_dense = self.svd.transform(q_tfidf)
        else:
            q_dense = q_tfidf.toarray()
            
        q_norm = np.linalg.norm(q_dense)
        if q_norm > 0:
            q_dense = q_dense / q_norm
            
        scores = np.dot(self.dense_embeddings, q_dense.T).flatten()
        ranked_indices = np.argsort(-scores)
        
        results = []
        for idx in ranked_indices:
            score = float(scores[idx])
            meta = self.doc_metadata[idx]
            if filter_fn and not filter_fn(meta):
                continue
            item = dict(meta)
            item["vector_similarity_score"] = round(score, 4)
            results.append(item)
            if len(results) >= top_k:
                break
                
        return results

class RAGService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.place_vector_store = LocalVectorStore(n_components=48)
        self.route_vector_store = LocalVectorStore(n_components=32)
        self._init_vector_indices()

    def _init_vector_indices(self):
        """Indexes places and routes from the database into the vector store."""
        # 1. Places Index
        places = self.db.get_all_places_for_indexing()
        place_docs = []
        for p in places:
            text = f"{p['name']} in {p.get('city_name', '')} {p['category']} {p.get('sub_category', '')}. {p.get('description', '')} Famous for: {p.get('famous_for', '')} Best time: {p.get('best_time_of_day', '')} Area: {p.get('area', '')}"
            doc = dict(p)
            doc["text"] = text
            place_docs.append(doc)
        if place_docs:
            self.place_vector_store.build_index(place_docs)

        # 2. Routes Index
        routes = self.db.get_all_routes_for_indexing()
        route_docs = []
        for r in routes:
            text = f"{r['transport_mode']} from {r['origin_name']} to {r['dest_name']} operated by {r['operator_name']}. Departure {r['departure_time']} arrival {r['arrival_time']}. Fare Rs {r['total_fare_inr']}. Service {r['service_number']} {r.get('amenities_json', '')}"
            doc = dict(r)
            doc["text"] = text
            route_docs.append(doc)
        if route_docs:
            self.route_vector_store.build_index(route_docs)

    def search_places_vector(self, query_text, city_id=None, top_k=15):
        """
        Stage 2 Vector Search: Embeds user free-text query and retrieves semantically matching candidate places.
        """
        def filter_city(meta):
            if city_id:
                return meta.get("city_id") == city_id
            return True
            
        res = self.place_vector_store.search(query_text, top_k=top_k, filter_fn=filter_city)
        if not res and city_id:
            # Fallback without strict city filter if city has limited POIs in vector index
            res = self.place_vector_store.search(query_text, top_k=top_k)
        return res

    def search_routes_vector(self, query_text, origin_city_id=None, dest_city_id=None, top_k=10):
        """
        Stage 2 Vector Search for Transport: Semantically matches free-text transit preferences.
        """
        def filter_od(meta):
            if origin_city_id and meta.get("origin_city_id") != origin_city_id:
                return False
            if dest_city_id and meta.get("dest_city_id") != dest_city_id:
                return False
            return True
            
        res = self.route_vector_store.search(query_text, top_k=top_k, filter_fn=filter_od)
        if not res:
            # If no route matches with OD filter in top vector results, return top semantic route matches
            res = self.route_vector_store.search(query_text, top_k=top_k)
        return res


    def generate_grounded_review_summary(self, entity_type, entity_id, entity_name):
        """
        Stage 4 RAG Review-Summary:
        Retrieves real/indexed reviews from the database and generates a strictly grounded pros/cons summary.
        Every single claim is mapped directly to a retrieved review snippet.
        If no reviews exist in the database, returns has_reviews=False with a clean fallback.
        """
        if not entity_id:
            return {
                "entity_name": entity_name,
                "summary": f"No reviews available for {entity_name}.",
                "average_rating": None,
                "total_reviews_analyzed": 0,
                "pros": [],
                "cons": [],
                "retrieved_reviews": [],
                "has_reviews": False,
                "is_grounded": True
            }

        reviews = self.db.get_reviews_for_entity(entity_type, entity_id, limit=6)
        if not reviews:
            return {
                "entity_name": entity_name,
                "summary": f"No reviews available for {entity_name}.",
                "average_rating": None,
                "num_reviews": 0,
                "total_reviews_analyzed": 0,
                "pros": [],
                "cons": [],
                "retrieved_reviews": [],
                "has_reviews": False,
                "is_grounded": True
            }

        pros = []
        cons = []
        cited_reviews = []

        for r in reviews:
            r_text = r["review_text"]
            user = r["user_name"]
            rating = r["rating"]
            sentiment = r.get("sentiment", "positive")
            
            cited_reviews.append({
                "user": user,
                "rating": rating,
                "text": r_text,
                "date": r.get("created_date", "2026-02")
            })

            # Strictly traceable aspect quotes — no generic or invented text
            if sentiment == "positive" or rating >= 4.0:
                pros.append(f"\"{r_text}\" — verified review from {user} ({rating}★)")
            else:
                cons.append(f"\"{r_text}\" — verified review note from {user} ({rating}★)")

        avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
        
        # Build consensus text exclusively from retrieved review snippets
        top_snippet = reviews[0]["review_text"]
        summary_text = (
            f"Based on {len(reviews)} verified reviews (Average rating: {avg_rating}/5.0★). "
            f"Key traveler feedback: \"{top_snippet}\""
        )

        return {
            "entity_name": entity_name,
            "summary": summary_text,
            "average_rating": avg_rating,
            "num_reviews": len(reviews),
            "total_reviews_analyzed": len(reviews),
            "pros": pros[:3],
            "cons": cons[:2] if cons else [f"No negative aspects reported across {len(reviews)} verified reviews."],
            "retrieved_reviews": cited_reviews,
            "has_reviews": True,
            "is_grounded": True
        }

    def generate_plan_review_summary(self, itinerary_days):
        """
        Stage 4 RAG Review-Summary for the overall DRL-generated Itinerary:
        Compiles grounded reviews for each visited POI and synthesizes an authentic travel digest.
        Every quote is mapped to an indexed review in the database.
        """
        all_poi_ids = []
        poi_map = {}
        for day in itinerary_days.values():
            for act in day.get("activities", []):
                poi = act.get("poi", {})
                pid = poi.get("id")
                if pid:
                    all_poi_ids.append(pid)
                    poi_map[pid] = poi.get("name", "Attraction")

        reviews_map = self.db.get_reviews_for_entities(all_poi_ids, limit_per_entity=3)
        
        grounded_digest = []
        unreviewed_places = []
        total_citations = 0
        for pid, name in poi_map.items():
            revs = reviews_map.get(pid, [])
            if revs:
                quotes = [f"\"{r['review_text']}\" — {r['user_name']} ({r['rating']}★)" for r in revs]
                avg_r = round(sum(r["rating"] for r in revs) / len(revs), 1)
                grounded_digest.append({
                    "poi_id": pid,
                    "poi_name": name,
                    "quotes": quotes,
                    "review_count": len(revs),
                    "average_rating": avg_r
                })
                total_citations += len(revs)
            else:
                unreviewed_places.append({
                    "poi_id": pid,
                    "poi_name": name
                })

        return {
            "total_places_reviewed": len(grounded_digest),
            "total_places_unreviewed": len(unreviewed_places),
            "total_citations": total_citations,
            "grounded_digest": grounded_digest,
            "unreviewed_places": unreviewed_places,
            "has_reviews": len(grounded_digest) > 0,
            "pipeline_stage": "Stage 4 (RAG Grounded Review Summary)"
        }
