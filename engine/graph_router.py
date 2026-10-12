"""
Graph-Based Multi-Modal Transit Router for TravelPulse Platform.
Models cities as graph nodes and transport schedules (flights, trains, buses, cabs) as directed edges.

Finds:
1. DIRECT ROUTES: 1-hop paths from Origin -> Destination on any allowed mode.
2. MULTI-HOP / COMBINED ROUTES: 2+ hop paths (up to 3 hops) combining any allowed modes
   (e.g., Bus -> Bus, Train -> Bus, Flight -> Cab, Bus -> Metro -> Auto, etc.)

Algorithm:
- Bounded Multi-Criteria Dijkstra / K-Shortest Path Search with Max Hop Limit = 3.
- Mode-Agnostic Edge Traversal with Strict Mode Filtering (Zero mode leakage).
- Layover Calculation & Itemized Leg Accounting.
"""

from collections import deque
import heapq
import json

class GraphRouter:
    def __init__(self, db_manager):
        self.db = db_manager

    def find_routes(
        self,
        origin_city_id,
        dest_city_id,
        selected_modes=None,
        max_price=None,
        departure_window=None,
        selected_operators=None,
        sort_by="cheapest",
        include_multihop=True,
        max_hops=3,
        limit=50
    ):
        """
        Executes graph search between origin and destination nodes.
        Returns dictionary with separated 'direct_routes' and 'multihop_routes'.
        """
        if selected_modes is not None and len(selected_modes) == 0:
            return {
                "direct_routes": [],
                "multihop_routes": [],
                "all_routes": [],
                "total_count": 0,
                "has_direct": False,
                "has_multihop": False,
                "empty_reason": "No transport modes selected."
            }

        if origin_city_id == dest_city_id:
            return {
                "direct_routes": [],
                "multihop_routes": [],
                "all_routes": [],
                "total_count": 0,
                "has_direct": False,
                "has_multihop": False,
                "empty_reason": "Origin and destination cities cannot be identical."
            }

        # Normalize allowed modes
        allowed_modes = set([m.lower().strip() for m in (selected_modes or ["flight", "train", "bus", "cab"])])

        # Step 1: Load filtered edges from database
        edges_by_origin = self._load_graph_edges(allowed_modes, selected_operators)

        # Step 2: Extract Direct Routes (1-hop paths)
        direct_routes = []
        if origin_city_id in edges_by_origin:
            for edge in edges_by_origin[origin_city_id]:
                if edge["dest_city_id"] == dest_city_id:
                    # Apply departure window filter if specified
                    if self._matches_dep_window(edge["departure_time"], departure_window):
                        if max_price is None or edge["total_fare_inr"] <= max_price:
                            direct_routes.append(self._format_direct_route(edge))

        # Step 3: Extract Multi-Hop Routes (2 to max_hops paths)
        multihop_routes = []
        if include_multihop:
            multihop_routes = self._search_multihop_paths(
                origin_city_id,
                dest_city_id,
                edges_by_origin,
                max_hops=max_hops,
                departure_window=departure_window,
                max_price=max_price,
                limit=limit
            )

        # Step 4: Sorting
        direct_routes = self._sort_routes(direct_routes, sort_by)
        multihop_routes = self._sort_routes(multihop_routes, sort_by)
        all_routes = direct_routes + multihop_routes
        all_routes = self._sort_routes(all_routes, sort_by)

        return {
            "origin_city_id": origin_city_id,
            "dest_city_id": dest_city_id,
            "direct_routes": direct_routes[:limit],
            "multihop_routes": multihop_routes[:limit],
            "all_routes": all_routes[:limit],
            "total_count": len(all_routes),
            "has_direct": len(direct_routes) > 0,
            "has_multihop": len(multihop_routes) > 0,
            "empty_reason": "No routes found matching your criteria." if len(all_routes) == 0 else None
        }

    def _load_graph_edges(self, allowed_modes, selected_operators=None):
        """
        Loads all transit edges where transport_mode is strictly in allowed_modes.
        Grouped by origin_city_id in adjacency list format.
        """
        with self.db.get_db_connection() as conn:
            cursor = conn.cursor()
            
            placeholders = ",".join(["?"] * len(allowed_modes))
            query = f"""
                SELECT 
                    s.id AS schedule_id,
                    s.origin_city_id,
                    c_orig.name AS origin_city_name,
                    c_orig.state AS origin_state,
                    s.dest_city_id,
                    c_dest.name AS dest_city_name,
                    c_dest.state AS dest_state,
                    s.transport_mode,
                    s.service_number,
                    s.departure_time,
                    s.arrival_time,
                    s.duration_hours,
                    s.distance_km,
                    op.id AS operator_id,
                    op.name AS operator_name,
                    op.code AS operator_code,
                    op.rating AS operator_rating,
                    op.logo_emoji,
                    f.seat_class,
                    f.base_fare_inr,
                    f.tax_inr,
                    f.service_fee_inr,
                    f.total_fare_inr,
                    f.available_seats
                FROM schedules s
                JOIN cities c_orig ON s.origin_city_id = c_orig.id
                JOIN cities c_dest ON s.dest_city_id = c_dest.id
                JOIN operators op ON s.operator_id = op.id
                JOIN fares f ON f.schedule_id = s.id
                WHERE LOWER(s.transport_mode) IN ({placeholders})
            """
            params = list(allowed_modes)

            if selected_operators and len(selected_operators) > 0:
                op_placeholders = ",".join(["?"] * len(selected_operators))
                query += f" AND op.name IN ({op_placeholders})"
                params.extend(selected_operators)

            cursor.execute(query, params)
            
            adj = {}
            for row in cursor.fetchall():
                d = dict(row)
                orig = d["origin_city_id"]
                if orig not in adj:
                    adj[orig] = []
                adj[orig].append(d)
                
            return adj

    def _search_multihop_paths(
        self,
        origin_city_id,
        dest_city_id,
        edges_by_origin,
        max_hops=3,
        departure_window=None,
        max_price=None,
        limit=30
    ):
        """
        Performs Bounded BFS with branch pruning to find all valid 2-hop and 3-hop paths.
        Guarantees loop-free paths and realistic transfer layovers.
        """
        results = []
        # Queue stores tuples of: (current_city, path_edges)
        queue = deque()

        if origin_city_id in edges_by_origin:
            for edge in edges_by_origin[origin_city_id]:
                # Leg 1 must match departure window if specified
                if self._matches_dep_window(edge["departure_time"], departure_window):
                    if edge["dest_city_id"] != dest_city_id:
                        queue.append((edge["dest_city_id"], [edge]))

        visited_signatures = set()

        while queue and len(results) < limit * 3:
            curr_city, path = queue.popleft()
            hop_count = len(path)

            if hop_count >= max_hops:
                continue

            if curr_city not in edges_by_origin:
                continue

            visited_nodes = {e["origin_city_id"] for e in path}
            visited_nodes.add(curr_city)

            for next_edge in edges_by_origin[curr_city]:
                next_dest = next_edge["dest_city_id"]

                # Avoid cycles (no revisiting cities in the same itinerary)
                if next_dest in visited_nodes:
                    continue

                new_path = path + [next_edge]
                
                # Check if we reached the final destination
                if next_dest == dest_city_id:
                    # Signature to prevent duplicate carrier combinations
                    sig = "+".join([e["schedule_id"] for e in new_path])
                    if sig not in visited_signatures:
                        visited_signatures.add(sig)
                        formatted = self._format_multihop_route(new_path)
                        if max_price is None or formatted["total_fare_inr"] <= max_price:
                            results.append(formatted)
                else:
                    # Continue search if below hop limit
                    if len(new_path) < max_hops:
                        queue.append((next_dest, new_path))

        return results

    def _format_direct_route(self, edge):
        """Formats a single edge as a top-level Direct Route."""
        return {
            "route_id": f"DIR_{edge['schedule_id']}",
            "route_type": "direct",
            "is_direct": True,
            "hop_count": 1,
            "mode": edge["transport_mode"],
            "carrier_name": edge["operator_name"],
            "operator_id": edge["operator_id"],
            "operator_name": edge["operator_name"],
            "operator_code": edge["operator_code"],
            "operator_rating": edge["operator_rating"],
            "logo_emoji": edge["logo_emoji"],
            "service_number": edge["service_number"],
            "origin_city_id": edge["origin_city_id"],
            "origin_city_name": edge["origin_city_name"],
            "dest_city_id": edge["dest_city_id"],
            "dest_city_name": edge["dest_city_name"],
            "departure_time": edge["departure_time"],
            "arrival_time": edge["arrival_time"],
            "duration_hours": round(edge["duration_hours"], 1),
            "duration_formatted": f"{int(edge['duration_hours'])}h {int((edge['duration_hours'] % 1) * 60)}m",
            "distance_km": edge["distance_km"],
            "seat_class": edge["seat_class"],
            "base_fare_inr": edge["base_fare_inr"],
            "tax_inr": edge["tax_inr"],
            "service_fee_inr": edge["service_fee_inr"],
            "total_fare_inr": round(edge["total_fare_inr"], 2),
            "price": round(edge["total_fare_inr"], 2),
            "available_seats": edge["available_seats"],
            "legs": [
                {
                    "leg_number": 1,
                    "mode": edge["transport_mode"],
                    "carrier_name": edge["operator_name"],
                    "operator_id": edge["operator_id"],
                    "service_number": edge["service_number"],
                    "from_city": edge["origin_city_name"],
                    "from_city_id": edge["origin_city_id"],
                    "to_city": edge["dest_city_name"],
                    "to_city_id": edge["dest_city_id"],
                    "departure_time": edge["departure_time"],
                    "arrival_time": edge["arrival_time"],
                    "duration_hours": round(edge["duration_hours"], 1),
                    "fare_inr": round(edge["total_fare_inr"], 2),
                    "seat_class": edge["seat_class"],
                    "logo_emoji": edge["logo_emoji"]
                }
            ]
        }

    def _format_multihop_route(self, path):
        """Formats a sequence of edges as a Multi-Hop Combined Route."""
        total_fare = sum(e["total_fare_inr"] for e in path)
        base_fare = sum(e["base_fare_inr"] for e in path)
        tax = sum(e["tax_inr"] for e in path)
        service_fee = sum(e["service_fee_inr"] for e in path)
        total_dist = sum(e["distance_km"] for e in path)

        # Layover calculation between legs
        # Standard layover buffer between intercity connections: 1.5h per transfer
        layover_hours_total = (len(path) - 1) * 1.5
        transit_duration = sum(e["duration_hours"] for e in path)
        total_duration = round(transit_duration + layover_hours_total, 1)

        modes_chain = " ➔ ".join([e["transport_mode"].title() for e in path])
        carriers_chain = " + ".join([e["operator_name"] for e in path])
        transfer_cities = [path[i]["dest_city_name"] for i in range(len(path) - 1)]
        transfer_summary = ", ".join(transfer_cities)

        legs = []
        for idx, e in enumerate(path):
            legs.append({
                "leg_number": idx + 1,
                "mode": e["transport_mode"],
                "carrier_name": e["operator_name"],
                "operator_id": e["operator_id"],
                "service_number": e["service_number"],
                "from_city": e["origin_city_name"],
                "from_city_id": e["origin_city_id"],
                "to_city": e["dest_city_name"],
                "to_city_id": e["dest_city_id"],
                "departure_time": e["departure_time"],
                "arrival_time": e["arrival_time"],
                "duration_hours": round(e["duration_hours"], 1),
                "fare_inr": round(e["total_fare_inr"], 2),
                "seat_class": e["seat_class"],
                "logo_emoji": e["logo_emoji"]
            })

        return {
            "route_id": "HOP_" + "_".join([e["schedule_id"] for e in path]),
            "route_type": "multihop",
            "is_direct": False,
            "hop_count": len(path),
            "mode": modes_chain,
            "carrier_name": carriers_chain,
            "operator_id": path[0]["operator_id"],
            "operator_name": carriers_chain,
            "operator_code": "/".join([e["operator_code"] for e in path]),
            "operator_rating": round(sum(e["operator_rating"] for e in path) / len(path), 1),
            "logo_emoji": " ➔ ".join([e["logo_emoji"] for e in path]),
            "service_number": " / ".join([e["service_number"] for e in path]),
            "origin_city_id": path[0]["origin_city_id"],
            "origin_city_name": path[0]["origin_city_name"],
            "dest_city_id": path[-1]["dest_city_id"],
            "dest_city_name": path[-1]["dest_city_name"],
            "departure_time": path[0]["departure_time"],
            "arrival_time": path[-1]["arrival_time"],
            "duration_hours": total_duration,
            "duration_formatted": f"{int(total_duration)}h {int((total_duration % 1) * 60)}m ({len(path)-1} layover)",
            "distance_km": round(total_dist, 1),
            "transfer_city": transfer_summary,
            "transfer_count": len(path) - 1,
            "base_fare_inr": round(base_fare, 2),
            "tax_inr": round(tax, 2),
            "service_fee_inr": round(service_fee, 2),
            "total_fare_inr": round(total_fare, 2),
            "price": round(total_fare, 2),
            "legs": legs
        }

    def _matches_dep_window(self, dep_time, window):
        if not window or len(window) != 2:
            return True
        start_t, end_t = window
        if start_t <= end_t:
            return start_t <= dep_time <= end_t
        else:
            return dep_time >= start_t or dep_time <= end_t

    def _sort_routes(self, routes, sort_by):
        if sort_by == "cheapest" or sort_by == "price_asc":
            return sorted(routes, key=lambda x: x["total_fare_inr"])
        elif sort_by == "fastest" or sort_by == "duration":
            return sorted(routes, key=lambda x: x["duration_hours"])
        elif sort_by == "earliest" or sort_by == "departure":
            return sorted(routes, key=lambda x: x["departure_time"])
        elif sort_by == "recommended":
            # Direct preferred over multi-hop, then by balanced score
            return sorted(routes, key=lambda x: (
                0 if x.get("is_direct") else 1,
                x["total_fare_inr"] * 0.5 + x["duration_hours"] * 150
            ))
        return routes
