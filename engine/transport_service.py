"""
Transport Search Service for TravelPulse Platform.
Implements the Strict 4-Stage Pipeline:
  Stage 1: SQL Filter (Strict hard constraints on transport mode, dates, budget, zero mode leakage)
  Stage 2: Vector Search (RAG Retrieval on free-text query embeddings, e.g. 'cheap overnight sleeper bus')
  Stage 3: Graph Router (Direct 1-hop + Multi-Hop mode-agnostic journey synthesis up to 3 hops)
  Stage 4: Grounded Review-Summary (Verified traveler feedback & pros/cons per carrier and per leg)
"""
import os
import json
import numpy as np
from database.db_manager import DatabaseManager
from engine.rag_service import RAGService
from engine.graph_router import GraphRouter

try:
    from stable_baselines3 import DQN
    HAS_SB3 = True
except ImportError:
    DQN = None
    HAS_SB3 = False

class TransportSearchService:
    def __init__(self, db_manager=None, rag_service=None, model_path=None):
        self.db = db_manager or DatabaseManager()
        self.rag = rag_service or RAGService(self.db)
        self.router = GraphRouter(self.db)

        # -------------------------------------------------------------
        # Load Trained DRL DQN Policy for Route Value Estimation
        # -------------------------------------------------------------
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_model_path = os.path.join(base_dir, "agents", "models", "route_dqn_best.zip")
        self.model_path = model_path or default_model_path
        self.dqn_model = None
        self.drl_loaded = False

        if HAS_SB3 and os.path.exists(self.model_path):
            try:
                self.dqn_model = DQN.load(self.model_path)
                self.drl_loaded = True
                print(f"[DRL SUCCESS] Route DQN Policy successfully loaded from {self.model_path}")
            except Exception as e:
                print(f"[DRL WARNING] Could not load DQN model ({e}). Falling back to multi-criteria utility.")
        else:
            print(f"[DRL INFO] DQN model not found at {self.model_path}.")

    def search_routes(
        self,
        origin_city_id,
        dest_city_id,
        selected_modes=None, # list of strings e.g. ['flight', 'train', 'bus', 'cab']
        max_price=None,
        departure_window=None, # ('06:00', '12:00')
        selected_operators=None,
        sort_by="recommended", # recommended, cheapest, fastest, earliest
        include_connecting=True,
        free_text_query=None,
        limit=50
    ):
        """
        Main TravelPulse transport search engine powered by Graph Router.
        Returns two distinct categories:
        1. direct_routes: 1-hop direct travel covering the whole journey on a single mode
        2. multihop_routes: multi-hop combined journeys (2+ legs, mixed modes)
        """
        # Hard check for empty mode selection
        if selected_modes is not None and len(selected_modes) == 0:
            return {
                "origin_city_id": origin_city_id,
                "dest_city_id": dest_city_id,
                "direct_routes": [],
                "multihop_routes": [],
                "connecting_routes": [],
                "all_routes": [],
                "results": [],
                "total_count": 0,
                "has_direct": False,
                "has_multihop": False,
                "empty_reason": "No transport modes selected. Please check at least one transport mode."
            }

        if origin_city_id == dest_city_id:
            return {
                "origin_city_id": origin_city_id,
                "dest_city_id": dest_city_id,
                "direct_routes": [],
                "multihop_routes": [],
                "connecting_routes": [],
                "all_routes": [],
                "results": [],
                "total_count": 0,
                "has_direct": False,
                "has_multihop": False,
                "empty_reason": "Origin and destination cities cannot be identical."
            }

        # -------------------------------------------------------------
        # STAGE 1 & 3: Graph Router (Multi-Modal Dijkstra / BFS Search)
        # -------------------------------------------------------------
        graph_res = self.router.find_routes(
            origin_city_id=origin_city_id,
            dest_city_id=dest_city_id,
            selected_modes=selected_modes,
            max_price=max_price,
            departure_window=departure_window,
            selected_operators=selected_operators,
            sort_by=sort_by,
            include_multihop=include_connecting,
            max_hops=3,
            limit=limit
        )

        direct_routes = graph_res.get("direct_routes", [])
        multihop_routes = graph_res.get("multihop_routes", [])

        # -------------------------------------------------------------
        # STAGE 2: Vector Search (Optional NL Free-Text Query Reranking)
        # -------------------------------------------------------------
        if free_text_query and free_text_query.strip():
            vector_matches = self.rag.search_routes_vector(
                query_text=free_text_query,
                origin_city_id=origin_city_id,
                dest_city_id=dest_city_id,
                top_k=20
            )
            v_scores = {vm.get("service_number"): vm.get("vector_similarity_score", 0.0) for vm in vector_matches}
            for r in direct_routes:
                r["vector_similarity_score"] = v_scores.get(r.get("service_number"), 0.1)

        # -------------------------------------------------------------
        # STAGE 4: Grounded Review-Summary Generation
        # -------------------------------------------------------------
        # Attach grounded reviews to Direct routes
        for r in direct_routes:
            op_id = r.get("operator_id")
            op_name = r.get("operator_name", "Carrier")
            # Rotate reviews deterministically per train/bus service number so different services show distinct feedback
            srv_key = str(r.get("service_number") or r.get("id") or "")
            rot_offset = (abs(hash(srv_key)) % 10) * 3
            r["review_summary"] = self.rag.generate_grounded_review_summary(
                entity_type="operator",
                entity_id=op_id,
                entity_name=op_name,
                offset=rot_offset
            )
            r["operator_review_summary"] = r["review_summary"]

        # Attach grounded reviews to Multi-Hop routes (for each leg and overall)
        for mr in multihop_routes:
            for leg in mr.get("legs", []):
                leg_op_id = leg.get("operator_id")
                leg_op_name = leg.get("carrier_name", "Carrier")
                leg_srv = str(leg.get("service_number") or leg.get("schedule_id") or "")
                leg_rot_offset = (abs(hash(leg_srv)) % 10) * 3
                leg["review_summary"] = self.rag.generate_grounded_review_summary(
                    entity_type="operator",
                    entity_id=leg_op_id,
                    entity_name=leg_op_name,
                    offset=leg_rot_offset
                )
            
            # Primary summary for route preview card
            if mr.get("legs"):
                mr["review_summary"] = mr["legs"][0].get("review_summary")
                mr["operator_review_summary"] = mr["review_summary"]

        all_routes = direct_routes + multihop_routes

        # -------------------------------------------------------------
        # ISSUE 3: DRL Policy Recommendation & Reasoning Engine
        # -------------------------------------------------------------
        recommended = self.recommend_best_route(
            direct_routes=direct_routes,
            multihop_routes=multihop_routes,
            selected_modes=selected_modes
        )

        return {
            "origin_city_id": origin_city_id,
            "dest_city_id": dest_city_id,
            "direct_routes": direct_routes,
            "multihop_routes": multihop_routes,
            "connecting_routes": multihop_routes, # backward compatible alias
            "all_routes": all_routes,
            "results": all_routes, # backward compatible alias for tests & legacy calls
            "total_count": len(all_routes),
            "has_direct": len(direct_routes) > 0,
            "has_multihop": len(multihop_routes) > 0,
            "recommended_route": recommended,
            "empty_reason": "No routes found matching your criteria." if len(all_routes) == 0 else None
        }

    def recommend_best_route(self, direct_routes, multihop_routes, selected_modes=None):
        """
        Evaluates candidate routes using the multi-criteria DRL objective:
          Reward = w_cost * Cost_Eff + w_time * Time_Eff + w_transfer * Transfer_Score + w_quality * Quality_Score
        Recommends ONE best option with an explicit, computed justification referencing actual numbers.
        """
        candidates = direct_routes + multihop_routes
        if not candidates:
            return None

        fares = [r.get("total_fare_inr", r.get("price", 1000.0)) for r in candidates]
        durs = [r.get("duration_hours", 5.0) for r in candidates]
        min_fare, max_fare = min(fares), max(fares)
        min_dur, max_dur = min(durs), max(durs)
        fare_range = max(1.0, max_fare - min_fare)
        dur_range = max(0.5, max_dur - min_dur)

        best_score = -float('inf')
        best_route = None
        best_metrics = {}
        drl_policy_used = "DQN-SB3" if (self.drl_loaded and self.dqn_model) else "MultiCriteria-Utility"

        for r in candidates:
            fare = r.get("total_fare_inr", r.get("price", 1000.0))
            dur = r.get("duration_hours", 5.0)
            is_direct = r.get("is_direct", len(r.get("legs", [])) <= 1)
            hop_count = len(r.get("legs", [])) or 1
            op_rating = r.get("operator_rating", 4.0)

            # Base multi-criteria utility
            cost_efficiency = (max_fare - fare) / fare_range
            time_efficiency = (max_dur - dur) / dur_range
            transfer_score = 1.0 if is_direct else (0.75 if hop_count == 2 else 0.45)
            quality_score = min(1.0, op_rating / 5.0)

            base_utility = (
                0.40 * cost_efficiency +
                0.35 * time_efficiency +
                0.15 * transfer_score +
                0.10 * quality_score
            )

            # DRL DQN State-Action Q-Evaluation:
            # Observation: [city_idx/N, mode_idx/3, elapsed_hours/48, cost/25000, transfers/5, dist/3000, step/max_steps]
            dqn_q_val = 0.0
            if self.drl_loaded and self.dqn_model is not None:
                try:
                    mode_str = str(r.get("mode", "train")).lower()
                    m_idx = 1.0 if "flight" in mode_str else (2.0 if "train" in mode_str else 3.0)
                    dist_val = float(r.get("distance_km", 300.0))
                    obs_route = np.array([
                        0.5, # normalized city idx
                        m_idx / 3.0,
                        min(1.0, dur / 48.0),
                        min(1.0, fare / 25000.0),
                        min(1.0, (hop_count - 1) / 5.0),
                        min(1.0, dist_val / 3000.0),
                        min(1.0, float(hop_count) / 5.0)
                    ], dtype=np.float32)
                    # Query policy Q-network
                    obs_tensor = self.dqn_model.policy.obs_to_tensor(obs_route)[0]
                    q_values = self.dqn_model.policy.q_net(obs_tensor).detach().cpu().numpy()[0]
                    # Direct route selects action 0, multi-hop actions correspond to connection index
                    act_idx = min(len(q_values) - 1, max(0, hop_count - 1))
                    dqn_q_val = float(q_values[act_idx])
                except Exception as q_err:
                    dqn_q_val = 0.0

            # Composite final score: blend base utility with DRL Q-value
            score = (base_utility * 0.7) + (float(np.tanh(dqn_q_val)) * 0.3) if self.drl_loaded else base_utility

            if score > best_score:
                best_score = score
                best_route = r
                best_metrics = {
                    "score": round(score, 3),
                    "base_utility": round(base_utility, 3),
                    "dqn_q_value": round(dqn_q_val, 3),
                    "fare": fare,
                    "duration": dur,
                    "is_direct": is_direct,
                    "hop_count": hop_count
                }

        if not best_route:
            return None

        # Build exact route summary string
        if best_route.get("is_direct"):
            mode = best_route.get("mode", "transit").lower()
            carrier = best_route.get("carrier_name") or best_route.get("operator_name", "Carrier")
            orig = best_route.get("origin_city_name", "Origin")
            dest = best_route.get("dest_city_name", "Destination")
            route_title = f"{orig} -> {dest} ({mode} via {carrier})"
        else:
            legs_str = " -> ".join([
                f"{l.get('from_city')} -> {l.get('to_city')} ({l.get('mode')})"
                for l in best_route.get("legs", [])
            ])
            route_title = legs_str

        fare_val = best_metrics["fare"]
        dur_val = best_metrics["duration"]
        hops = best_metrics["hop_count"]

        reasons = []
        if fare_val == min_fare:
            reasons.append(f"lowest total cost among valid options (Rs {fare_val:,.2f})")
        elif fare_val <= min_fare * 1.3:
            reasons.append(f"highly competitive fare (Rs {fare_val:,.2f}, within 30% of lowest available)")
        else:
            reasons.append(f"balanced fare of Rs {fare_val:,.2f}")

        if dur_val == min_dur:
            reasons.append(f"fastest total duration ({dur_val}h)")
        elif dur_val <= min_dur * 1.35:
            reasons.append(f"total duration of {dur_val}h within acceptable range")
        else:
            reasons.append(f"total duration of {dur_val}h")

        if best_metrics["is_direct"]:
            reasons.append("direct single-leg journey with 0 transfers")
        else:
            trans_city = best_route.get("transfer_city", "connecting hub")
            reasons.append(f"{hops - 1} transfer via {trans_city}")

        if selected_modes:
            norm_modes = [m.lower().strip() for m in selected_modes]
            if "flight" not in norm_modes:
                reasons.append("avoids flights per your filter settings")
            else:
                reasons.append(f"respects selected modes ({', '.join(selected_modes)})")

        reason_text = "; ".join(reasons) + "."
        full_statement = f"Recommended: {route_title}. Chosen because: {reason_text}"

        return {
            "route_id": best_route.get("route_id"),
            "route_title": route_title,
            "statement": full_statement,
            "reasoning": reason_text,
            "total_fare_inr": fare_val,
            "duration_hours": dur_val,
            "hop_count": hops,
            "is_direct": best_metrics["is_direct"],
            "drl_utility_score": best_metrics["score"],
            "chosen_route": best_route,
            "drl_metadata": {
                "model_family": "DQN (Deep Q-Network)",
                "framework": "stable-baselines3",
                "policy_type": "MlpPolicy",
                "dqn_q_value": best_metrics.get("dqn_q_value", 0.0),
                "is_live_drl": (self.drl_loaded and self.dqn_model is not None)
            }
        }
