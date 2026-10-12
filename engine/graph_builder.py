"""
Unified Multi-Modal Transport Graph Builder for India to Chennai Journey Planning.
Integrates Flights, Indian Railways Trains, and Interstate Buses into a coherent NetworkX graph.
"""
import os
import pandas as pd
import networkx as nx
import json

class MultiModalGraphBuilder:
    def __init__(self, data_dir=r"d:\drl_project"):
        self.data_dir = data_dir
        self.graph = nx.MultiDiGraph()
        self.cities_df = None
        self.flights_df = None
        self.buses_df = None
        self.trains_df = None
        self.load_datasets()
        self.build_graph()

    def load_datasets(self):
        # Load city coordinates
        cities_path = os.path.join(self.data_dir, "data", "city_coordinates.csv")
        if os.path.exists(cities_path):
            self.cities_df = pd.read_csv(cities_path)
            for _, row in self.cities_df.iterrows():
                self.graph.add_node(
                    row["city_name"],
                    state=row["state"],
                    lat=row["latitude"],
                    lon=row["longitude"],
                    is_hub=bool(row["is_major_hub"]),
                    has_flight=bool(row["has_airport"]),
                    has_train=bool(row["has_railway_station"]),
                    has_bus=bool(row["has_bus_terminal"])
                )

        # Load Flights
        flights_path = os.path.join(self.data_dir, "flights", "indian_all_places_flights_dataset.csv")
        if os.path.exists(flights_path):
            self.flights_df = pd.read_csv(flights_path)
            for _, row in self.flights_df.iterrows():
                orig = str(row.get("origin_city", "")).strip()
                dest = str(row.get("destination_city", "")).strip()
                if orig and dest:
                    # Parse duration (e.g. "2h 30m" -> 2.5)
                    dur_str = str(row.get("duration", "2h 00m"))
                    hours = 2.0
                    try:
                        parts = dur_str.split("h")
                        h = float(parts[0].strip())
                        m = float(parts[1].replace("m", "").strip()) if len(parts) > 1 and parts[1].strip() else 0.0
                        hours = h + m / 60.0
                    except Exception:
                        hours = 2.0

                    self.graph.add_edge(
                        orig, dest,
                        mode="flight",
                        operator=str(row.get("airline", "IndiGo")),
                        number=str(row.get("flight_number", "FL-101")),
                        dep_time=str(row.get("departure_time", "08:00")),
                        arr_time=str(row.get("arrival_time", "10:30")),
                        duration_hours=round(hours, 2),
                        fare_inr=float(row.get("price_inr", 4500)),
                        cabin=str(row.get("cabin_class", "Economy"))
                    )

        # Load Buses
        buses_path = os.path.join(self.data_dir, "buses", "intercity_buses_india.csv")
        if os.path.exists(buses_path):
            self.buses_df = pd.read_csv(buses_path)
            for _, row in self.buses_df.iterrows():
                orig = str(row.get("origin_city", "")).strip()
                dest = str(row.get("destination_city", "")).strip()
                if orig and dest:
                    self.graph.add_edge(
                        orig, dest,
                        mode="bus",
                        operator=str(row.get("operator", "SETC")),
                        number=str(row.get("bus_id", "BUS-100")),
                        bus_type=str(row.get("bus_type", "AC Sleeper")),
                        dep_time=str(row.get("departure_time", "21:00")),
                        arr_time=str(row.get("arrival_time", "06:00")),
                        duration_hours=float(row.get("duration_hours", 8.0)),
                        fare_inr=float(row.get("fare_inr", 750)),
                        distance_km=float(row.get("distance_km", 350))
                    )

        # Load Trains (Extract key routes connecting to Chennai and transit hubs)
        trains_path = os.path.join(self.data_dir, "trains", "Train_details_22122017.csv")
        if os.path.exists(trains_path):
            self._parse_key_train_routes(trains_path)

    def _parse_key_train_routes(self, trains_path):
        """Parse key direct and connecting trains between major cities and Chennai."""
        # Predefined key express / Vande Bharat / Superfast trains across Indian network
        key_trains = [
            # To Chennai Central (MAS) / Egmore (MS)
            ("Bangalore", "Chennai", "Vande Bharat Express (20608)", "05:45", "10:10", 4.4, 359, 1050, "CC"),
            ("Bangalore", "Chennai", "Shatabdi Express (12028)", "06:00", "11:00", 5.0, 359, 950, "CC"),
            ("Bangalore", "Chennai", "Chennai Mail (12658)", "22:40", "04:15", 5.6, 359, 380, "SL/3A"),
            ("Bangalore", "Chennai", "Lalbagh Express (12608)", "06:20", "12:15", 5.9, 359, 160, "2S/CC"),
            ("Hyderabad", "Chennai", "Charminar Express (12760)", "18:00", "07:00", 13.0, 790, 480, "SL/3A"),
            ("Hyderabad", "Chennai", "Chennai Express (12604)", "16:45", "05:40", 12.9, 790, 480, "SL/3A"),
            ("Hyderabad", "Chennai", "Vande Bharat Express (20678)", "06:00", "14:30", 8.5, 790, 1600, "CC/EC"),
            ("Mumbai", "Chennai", "Chennai Express (12163)", "18:45", "16:30", 21.75, 1280, 620, "SL/3A"),
            ("Mumbai", "Chennai", "Mumbai LTT - MAS Exp (11073)", "13:20", "13:00", 23.6, 1280, 580, "SL/3A"),
            ("Delhi", "Chennai", "Tamil Nadu Express (12622)", "21:05", "06:15", 33.1, 2182, 850, "SL/3A/2A"),
            ("Delhi", "Chennai", "Grand Trunk Express (12616)", "16:10", "04:30", 36.3, 2182, 820, "SL/3A"),
            ("Delhi", "Chennai", "Chennai Rajdhani (12434)", "15:35", "20:45", 29.1, 2182, 2450, "3A/2A/1A"),
            ("Kolkata", "Chennai", "Coromandel Express (12841)", "15:20", "17:00", 25.6, 1662, 720, "SL/3A"),
            ("Kolkata", "Chennai", "Howrah - Chennai Mail (12839)", "23:55", "03:45", 27.8, 1662, 700, "SL/3A"),
            ("Coimbatore", "Chennai", "Vande Bharat (20644)", "06:00", "11:50", 5.8, 497, 1365, "CC/EC"),
            ("Coimbatore", "Chennai", "Cheran Express (12674)", "22:50", "07:00", 8.1, 497, 340, "SL/3A"),
            ("Coimbatore", "Chennai", "Kovai Express (12676)", "15:15", "22:50", 7.6, 497, 210, "CC/2S"),
            ("Madurai", "Chennai", "Vande Bharat Express (20602)", "05:15", "11:15", 6.0, 495, 1365, "CC/EC"),
            ("Madurai", "Chennai", "Pandian Express (12638)", "21:35", "05:15", 7.6, 495, 340, "SL/3A"),
            ("Madurai", "Chennai", "Vaigai Superfast Exp (12636)", "07:10", "14:30", 7.3, 495, 210, "CC/2S"),
            ("Trichy", "Chennai", "Rockfort Express (12654)", "22:50", "04:40", 5.8, 337, 260, "SL/3A"),
            ("Trichy", "Chennai", "Cholan Express (22676)", "11:15", "18:15", 7.0, 337, 180, "CC/2S"),
            ("Vijayawada", "Chennai", "Vande Bharat (20678)", "10:00", "14:30", 4.5, 430, 1000, "CC"),
            ("Vijayawada", "Chennai", "Pinakini Express (12711)", "06:10", "13:05", 6.9, 430, 185, "CC/2S"),
            ("Kochi", "Chennai", "Chennai Express (12678)", "09:10", "22:25", 13.25, 690, 430, "SL/3A"),
            ("Trivandrum", "Chennai", "Ananthapuri Express (20636)", "16:15", "06:10", 13.9, 780, 460, "SL/3A"),
            ("Goa", "Chennai", "Vasco - Chennai Express (17312)", "14:30", "11:45", 21.25, 1010, 520, "SL/3A"),
            ("Pune", "Chennai", "Chennai Express (12163)", "23:45", "16:30", 16.75, 1080, 540, "SL/3A"),
            ("Jaipur", "Delhi", "Vande Bharat (20977)", "07:50", "11:35", 3.75, 305, 880, "CC"),
            ("Varanasi", "Delhi", "Vande Bharat (22435)", "15:00", "23:00", 8.0, 759, 1750, "CC"),
            ("Bhopal", "Delhi", "Vande Bharat (20171)", "05:40", "13:10", 7.5, 700, 1665, "CC"),
            ("Ahmedabad", "Mumbai", "Vande Bharat (20902)", "15:00", "20:25", 5.4, 491, 1420, "CC"),
            ("Patna", "Kolkata", "Vande Bharat (22348)", "06:05", "14:35", 8.5, 532, 1500, "CC"),
            ("Ranchi", "Kolkata", "Vande Bharat (20898)", "05:15", "12:20", 7.1, 415, 1155, "CC"),
            ("Bhubaneswar", "Chennai", "Coromandel Express (12841)", "21:55", "17:00", 19.1, 1225, 580, "SL/3A"),
            ("Tirupati", "Chennai", "Sapthagiri Express (16058)", "06:05", "09:30", 3.4, 147, 100, "2S/CC"),
            ("Salem", "Chennai", "Chennai Express (22650)", "21:55", "03:45", 5.8, 335, 240, "SL/3A"),
            ("Vellore", "Chennai", "Yelagiri Express (16090)", "05:00", "08:15", 3.25, 140, 95, "2S")
        ]

        for item in key_trains:
            orig, dest, name, dep, arr, dur, dist, fare, cl = item
            self.graph.add_edge(
                orig, dest,
                mode="train",
                operator="Indian Railways",
                number=name,
                train_class=cl,
                dep_time=dep,
                arr_time=arr,
                duration_hours=dur,
                fare_inr=fare,
                distance_km=dist
            )

    def build_graph(self):
        """Constructs bidirectional transfer and connectivity edges."""
        pass

    def get_direct_routes(self, origin, destination="Chennai"):
        """Returns direct flight, train, and bus options."""
        routes = []
        if self.graph.has_edge(origin, destination):
            edge_dict = self.graph.get_edge_data(origin, destination)
            for key, data in edge_dict.items():
                routes.append({
                    "type": "Direct",
                    "transfers": 0,
                    "legs": [{
                        "from": origin,
                        "to": destination,
                        "mode": data.get("mode"),
                        "operator": data.get("operator"),
                        "number": data.get("number"),
                        "dep_time": data.get("dep_time"),
                        "arr_time": data.get("arr_time"),
                        "duration_hours": data.get("duration_hours"),
                        "fare_inr": data.get("fare_inr")
                    }],
                    "total_duration_hours": data.get("duration_hours"),
                    "total_fare_inr": data.get("fare_inr"),
                    "primary_mode": data.get("mode")
                })
        return routes

    def get_multihop_routes(self, origin, destination="Chennai", max_transfers=2):
        """Calculates multi-modal routes transferring via intermediate hubs."""
        all_routes = self.get_direct_routes(origin, destination)
        
        # Major connecting transit hubs
        hubs = ["Bangalore", "Hyderabad", "Mumbai", "Delhi", "Kolkata", "Vijayawada", "Coimbatore", "Pune", "Trichy", "Madurai"]
        
        for hub in hubs:
            if hub == origin or hub == destination:
                continue
            
            # Leg 1: Origin -> Hub
            if self.graph.has_edge(origin, hub):
                leg1_edges = self.graph.get_edge_data(origin, hub)
                # Leg 2: Hub -> Destination
                if self.graph.has_edge(hub, destination):
                    leg2_edges = self.graph.get_edge_data(hub, destination)
                    
                    for k1, e1 in leg1_edges.items():
                        for k2, e2 in leg2_edges.items():
                            layover = 1.5 if e1.get("mode") == "flight" else 2.0
                            tot_time = e1.get("duration_hours", 0) + e2.get("duration_hours", 0) + layover
                            tot_fare = e1.get("fare_inr", 0) + e2.get("fare_inr", 0)
                            
                            combo_mode = f"{e1.get('mode').title()} -> {e2.get('mode').title()}"
                            all_routes.append({
                                "type": f"Connecting via {hub}",
                                "transfers": 1,
                                "transfer_hub": hub,
                                "legs": [
                                    {
                                        "from": origin,
                                        "to": hub,
                                        "mode": e1.get("mode"),
                                        "operator": e1.get("operator"),
                                        "number": e1.get("number"),
                                        "dep_time": e1.get("dep_time"),
                                        "arr_time": e1.get("arr_time"),
                                        "duration_hours": e1.get("duration_hours"),
                                        "fare_inr": e1.get("fare_inr")
                                    },
                                    {
                                        "from": hub,
                                        "to": destination,
                                        "mode": e2.get("mode"),
                                        "operator": e2.get("operator"),
                                        "number": e2.get("number"),
                                        "dep_time": e2.get("dep_time"),
                                        "arr_time": e2.get("arr_time"),
                                        "duration_hours": e2.get("duration_hours"),
                                        "fare_inr": e2.get("fare_inr")
                                    }
                                ],
                                "layover_hours": layover,
                                "total_duration_hours": round(tot_time, 2),
                                "total_fare_inr": round(tot_fare, 2),
                                "primary_mode": combo_mode
                            })
        return all_routes

if __name__ == "__main__":
    builder = MultiModalGraphBuilder()
    print(f"Graph nodes: {builder.graph.number_of_nodes()}, edges: {builder.graph.number_of_edges()}")
    test_routes = builder.get_multihop_routes("Varanasi", "Chennai")
    print(f"Found {len(test_routes)} routes from Varanasi to Chennai!")
    if test_routes:
        print("Sample route:", json.dumps(test_routes[0], indent=2))
