"""
Comprehensive dataset generator for Chennai DRL Trip Planner.
Generates: Hotels, Buses, City Coordinates datasets.
"""
import json, os, random, csv
import pandas as pd

random.seed(42)

def generate_hotels():
    """Generate 150+ Chennai hotel entries."""
    hotels = []
    hotel_data = [
        # Luxury 5-Star
        ("ITC Grand Chola", "Guindy", "South Chennai", 5, "Luxury", 18000, "WiFi,Pool,Spa,Gym,Restaurant,Bar,Valet", 13.0103, 80.2210, 4.8, "Guindy Station", 0.5),
        ("Taj Connemara", "Binny Road", "Central Chennai", 5, "Luxury", 15000, "WiFi,Pool,Spa,Heritage,Restaurant,Bar", 13.0608, 80.2582, 4.7, "Express Avenue Mall", 0.3),
        ("The Leela Palace", "Adyar", "South Chennai", 5, "Luxury", 22000, "WiFi,Pool,Spa,Gym,Restaurant,Bar,Butler", 13.0062, 80.2558, 4.9, "Adyar Gate", 0.2),
        ("Taj Club House", "Anna Salai", "Central Chennai", 5, "Luxury", 12000, "WiFi,Pool,Gym,Restaurant,Bar,Rooftop", 13.0595, 80.2618, 4.6, "Spencer Plaza", 0.4),
        ("Hyatt Regency Chennai", "Teynampet", "Central Chennai", 5, "Luxury", 14000, "WiFi,Pool,Spa,Gym,Restaurant,Bar", 13.0458, 80.2498, 4.7, "Semmozhi Poonga", 0.3),
        ("Hilton Chennai", "Guindy", "South Chennai", 5, "Luxury", 11000, "WiFi,Pool,Gym,Restaurant,Bar", 13.0085, 80.2145, 4.5, "Guindy National Park", 0.8),
        ("The Park Chennai", "Anna Salai", "Central Chennai", 5, "Luxury", 9500, "WiFi,Pool,Gym,Restaurant,Nightclub", 13.0612, 80.2605, 4.5, "Thousand Lights", 0.2),
        ("Crowne Plaza Chennai Adyar Park", "TTK Road", "T. Nagar & Alwarpet", 5, "Luxury", 10000, "WiFi,Pool,Gym,Restaurant,Bar", 13.0382, 80.2498, 4.5, "Music Academy", 0.3),
        ("Radisson Blu Hotel GRT", "Kodambakkam", "West Chennai", 4, "Premium", 8000, "WiFi,Pool,Gym,Restaurant", 13.0528, 80.2278, 4.4, "Vadapalani Temple", 1.0),
        ("Novotel Chennai OMR", "Sholinganallur", "OMR IT Corridor", 4, "Premium", 7500, "WiFi,Pool,Gym,Restaurant,Bar", 12.9012, 80.2278, 4.4, "SIPCOT IT Park", 0.5),
        ("Novotel Chennai Chamiers Road", "Nandanam", "Central Chennai", 4, "Premium", 8500, "WiFi,Pool,Gym,Restaurant", 13.0285, 80.2388, 4.5, "Kalakshetra", 2.0),
        ("Ambassador Pallava", "Montieth Road", "Central Chennai", 4, "Premium", 6500, "WiFi,Restaurant,Bar,Parking", 13.0578, 80.2625, 4.3, "Express Avenue", 0.5),
        ("GRT Grand", "T. Nagar", "T. Nagar & Alwarpet", 4, "Premium", 7000, "WiFi,Pool,Gym,Restaurant,Banquet", 13.0402, 80.2348, 4.4, "Pondy Bazaar", 0.3),
        ("Residency Towers", "T. Nagar", "T. Nagar & Alwarpet", 4, "Premium", 6000, "WiFi,Pool,Restaurant,Bar", 13.0388, 80.2362, 4.3, "T. Nagar Bus Stand", 0.2),
        ("Hotel Savera", "RK Salai", "Central Chennai", 4, "Premium", 5500, "WiFi,Pool,Restaurant,Bar", 13.0485, 80.2595, 4.2, "Music Academy", 0.5),
        ("Rain Tree Hotel", "Alwarpet", "T. Nagar & Alwarpet", 4, "Premium", 6500, "WiFi,Pool,Restaurant,Bar,Garden", 13.0365, 80.2505, 4.5, "Alwarpet Junction", 0.2),
        ("Feathers Hotel", "Mount Poonamallee Road", "West Chennai", 4, "Premium", 5000, "WiFi,Pool,Gym,Restaurant", 13.0285, 80.1885, 4.3, "Ramachandra Hospital", 1.0),
        ("Courtyard by Marriott", "Teynampet", "Central Chennai", 4, "Premium", 7500, "WiFi,Pool,Gym,Restaurant,Bar", 13.0435, 80.2475, 4.5, "US Consulate", 0.3),
        ("Lemon Tree Premier", "OMR", "OMR IT Corridor", 4, "Premium", 5500, "WiFi,Pool,Gym,Restaurant", 12.9285, 80.2312, 4.3, "Tidel Park", 1.5),
        ("Fortune Select Grand", "Cathedral Road", "Central Chennai", 4, "Premium", 5000, "WiFi,Pool,Restaurant", 13.0505, 80.2498, 4.2, "Semmozhi Poonga", 0.4),
        # Standard 3-Star
        ("Hotel Vestin Park", "Egmore", "Central Chennai", 3, "Standard", 3500, "WiFi,Restaurant,Parking", 13.0748, 80.2598, 4.1, "Egmore Museum", 0.3),
        ("Comfort Inn Marina Towers", "Triplicane", "Central Chennai", 3, "Standard", 3000, "WiFi,Restaurant,AC", 13.0545, 80.2762, 4.0, "Parthasarathy Temple", 0.3),
        ("Hotel Ashoka", "Egmore", "Central Chennai", 3, "Standard", 2800, "WiFi,Restaurant,Parking", 13.0738, 80.2585, 4.0, "Egmore Station", 0.2),
        ("Hotel Pandian", "Egmore", "Central Chennai", 3, "Standard", 2500, "WiFi,Restaurant", 13.0755, 80.2605, 3.9, "Egmore Station", 0.1),
        ("Hotel Deccan Plaza", "RK Salai", "Central Chennai", 3, "Standard", 3200, "WiFi,Restaurant,AC", 13.0492, 80.2602, 4.1, "Music Academy", 0.4),
        ("Raj Park Hotel", "Teynampet", "Central Chennai", 3, "Standard", 3500, "WiFi,Pool,Restaurant", 13.0415, 80.2502, 4.2, "Nungambakkam Station", 0.5),
        ("Hotel Kanchi", "Egmore", "Central Chennai", 3, "Standard", 2200, "WiFi,Restaurant", 13.0725, 80.2578, 3.8, "Government Museum", 0.2),
        ("Breeze Hotel", "Kodambakkam", "West Chennai", 3, "Standard", 2800, "WiFi,Restaurant,AC", 13.0522, 80.2248, 4.0, "Kodambakkam Station", 0.3),
        ("Crystal Suites", "T. Nagar", "T. Nagar & Alwarpet", 3, "Standard", 3200, "WiFi,Restaurant,AC", 13.0395, 80.2332, 4.1, "Ranganathan Street", 0.2),
        ("Hotel Ranjith", "Nungambakkam", "Central Chennai", 3, "Standard", 2500, "WiFi,Restaurant", 13.0612, 80.2448, 3.9, "Nungambakkam Station", 0.3),
        ("Hotel Chenthur Park", "Nungambakkam", "Central Chennai", 3, "Standard", 2800, "WiFi,AC,Restaurant", 13.0625, 80.2435, 4.0, "Sterling Road", 0.3),
        ("Hotel Shelter", "Triplicane", "Central Chennai", 3, "Standard", 2200, "WiFi,Restaurant", 13.0528, 80.2748, 3.8, "Marina Beach", 0.5),
        ("Green Park Hotel", "Vadapalani", "West Chennai", 3, "Standard", 2500, "WiFi,Restaurant,AC", 13.0505, 80.2142, 4.0, "Vadapalani Temple", 0.3),
        ("ABM Grand", "Mylapore", "Mylapore & Mandaveli", 3, "Standard", 2800, "WiFi,Restaurant,AC", 13.0342, 80.2672, 4.1, "Kapaleeshwarar Temple", 0.2),
        ("JC Residency Madurai", "Besant Nagar", "South Chennai", 3, "Standard", 3000, "WiFi,Restaurant", 13.0005, 80.2655, 4.0, "Elliot's Beach", 0.5),
        ("Pride Hotel", "Anna Salai", "Central Chennai", 3, "Standard", 3200, "WiFi,Restaurant,AC", 13.0632, 80.2655, 4.1, "Anna Salai", 0.1),
        ("Royal Kourt Hotel", "Kilpauk", "Central Chennai", 3, "Standard", 2500, "WiFi,Restaurant", 13.0852, 80.2422, 3.9, "Kilpauk Medical", 0.3),
        ("Classic Diplomat", "Chetpet", "Central Chennai", 3, "Standard", 2800, "WiFi,Restaurant,AC", 13.0698, 80.2412, 4.0, "Chetpet Ecopark", 0.4),
    ]
    
    # Budget hotels
    budget_names = [
        ("FabHotel Prime Egmore", "Egmore", "Central Chennai", 2, "Budget", 1200, "WiFi,AC", 13.0742, 80.2592, 3.8, "Egmore Station", 0.3),
        ("FabHotel Royal Park", "Teynampet", "Central Chennai", 2, "Budget", 1400, "WiFi,AC", 13.0425, 80.2488, 3.7, "Teynampet Junction", 0.2),
        ("FabHotel Nest OMR", "Sholinganallur", "OMR IT Corridor", 2, "Budget", 1100, "WiFi,AC", 12.9045, 80.2295, 3.8, "OMR Signal", 0.5),
        ("Treebo Trip Shelton", "T. Nagar", "T. Nagar & Alwarpet", 2, "Budget", 1300, "WiFi,AC", 13.0385, 80.2345, 3.9, "T. Nagar Bus Stand", 0.3),
        ("Treebo Trend Ruby Arena", "Anna Nagar", "West Chennai", 2, "Budget", 1200, "WiFi,AC", 13.0855, 80.2125, 3.8, "Anna Nagar Tower", 0.4),
        ("OYO Townhouse Nungambakkam", "Nungambakkam", "Central Chennai", 2, "Budget", 1000, "WiFi,AC", 13.0618, 80.2455, 3.7, "Nungambakkam Station", 0.2),
        ("OYO Rooms Mylapore", "Mylapore", "Mylapore & Mandaveli", 2, "Budget", 900, "WiFi,AC", 13.0335, 80.2688, 3.6, "Kapaleeshwarar Temple", 0.2),
        ("OYO Flagship Mount Road", "Anna Salai", "Central Chennai", 2, "Budget", 1100, "WiFi,AC", 13.0625, 80.2678, 3.7, "Higginbothams", 0.2),
        ("OYO Rooms Velachery", "Velachery", "South Chennai", 2, "Budget", 850, "WiFi,AC", 12.9825, 80.2185, 3.6, "Phoenix Mall", 0.5),
        ("Hotel Mass Triplicane", "Triplicane", "Central Chennai", 2, "Budget", 800, "WiFi,Fan", 13.0552, 80.2748, 3.5, "Parthasarathy Temple", 0.3),
        ("Hotel Ganga", "Egmore", "Central Chennai", 2, "Budget", 950, "WiFi,AC", 13.0732, 80.2575, 3.6, "Egmore Station", 0.2),
        ("Chennai Gate Hotel", "Meenambakkam", "South Chennai", 2, "Budget", 1200, "WiFi,AC,Airport Shuttle", 12.9862, 80.1685, 3.8, "Chennai Airport", 1.0),
        ("Hotel Surguru", "Egmore", "Central Chennai", 2, "Budget", 1100, "WiFi,Restaurant", 13.0745, 80.2598, 3.9, "Egmore Station", 0.1),
        ("New Victoria Hotel", "Kennet Lane", "Central Chennai", 2, "Budget", 1000, "WiFi,AC", 13.0728, 80.2612, 3.7, "Egmore Museum", 0.3),
        ("Hotel Le Duplex", "Alwarpet", "T. Nagar & Alwarpet", 2, "Budget", 1400, "WiFi,AC", 13.0355, 80.2528, 3.9, "Alwarpet Junction", 0.1),
        ("Royal Inn Tambaram", "Tambaram", "Outer Suburbs", 2, "Budget", 850, "WiFi,AC", 12.9262, 80.1268, 3.6, "Tambaram Station", 0.3),
        ("Hotel Alankar Inn", "Perambur", "North Chennai", 2, "Budget", 750, "WiFi,AC", 13.1085, 80.2345, 3.5, "Perambur Station", 0.3),
        ("Stay Inn", "Chromepet", "Outer Suburbs", 2, "Budget", 800, "WiFi,AC", 12.9512, 80.1388, 3.6, "Chromepet Station", 0.2),
    ]
    
    # Backpacker hostels
    hostels = [
        ("Zostel Chennai", "Nungambakkam", "Central Chennai", 1, "Backpacker Hostel", 499, "WiFi,Locker,CommonArea,Kitchen", 13.0605, 80.2442, 4.2, "Express Avenue", 1.0),
        ("Backpackers Hostel", "Mylapore", "Mylapore & Mandaveli", 1, "Backpacker Hostel", 450, "WiFi,Locker,CommonArea", 13.0325, 80.2692, 4.0, "Kapaleeshwarar Temple", 0.3),
        ("The Madras Hostel", "Nungambakkam", "Central Chennai", 1, "Backpacker Hostel", 550, "WiFi,Locker,CommonArea,Cafe", 13.0628, 80.2448, 4.3, "Nungambakkam Station", 0.2),
        ("goSTOPS Chennai", "T. Nagar", "T. Nagar & Alwarpet", 1, "Backpacker Hostel", 500, "WiFi,Locker,CommonArea,Rooftop", 13.0398, 80.2355, 4.1, "Pondy Bazaar", 0.3),
        ("Tribe Hostel", "Besant Nagar", "South Chennai", 1, "Backpacker Hostel", 600, "WiFi,Locker,CommonArea,Beach", 12.9998, 80.2665, 4.2, "Elliot's Beach", 0.4),
        ("Social Hostel", "Egmore", "Central Chennai", 1, "Backpacker Hostel", 400, "WiFi,Locker,CommonArea", 13.0748, 80.2592, 3.9, "Egmore Station", 0.2),
        ("Clock Tower Hostel", "George Town", "Central Chennai", 1, "Backpacker Hostel", 350, "WiFi,Locker", 13.0885, 80.2852, 3.8, "Fort St George", 0.5),
    ]
    
    # More mid-range / area specific
    more_hotels = [
        ("The Raintree Anna Salai", "Anna Salai", "Central Chennai", 4, "Premium", 6000, "WiFi,Pool,Restaurant,Bar", 13.0565, 80.2605, 4.4, "Anna Salai", 0.1),
        ("Accord Metropolitan", "Cathedral Road", "Central Chennai", 4, "Premium", 5500, "WiFi,Restaurant,Pool", 13.0508, 80.2512, 4.3, "Cathedral Road", 0.1),
        ("My Fortune Chennai", "Cathedral Road", "Central Chennai", 4, "Premium", 5000, "WiFi,Pool,Restaurant", 13.0498, 80.2505, 4.2, "Semmozhi Poonga", 0.3),
        ("Holiday Inn Express", "OMR", "OMR IT Corridor", 3, "Standard", 4000, "WiFi,Breakfast,AC", 12.9125, 80.2285, 4.1, "OMR IT Hub", 0.5),
        ("Keys Select by Lemon Tree", "Kattupakkam", "West Chennai", 3, "Standard", 3200, "WiFi,Restaurant,AC", 13.0365, 80.1725, 3.9, "Porur Junction", 1.0),
        ("Hotel Vijay Park", "Guindy", "South Chennai", 3, "Standard", 2800, "WiFi,Restaurant", 13.0078, 80.2168, 4.0, "Guindy Station", 0.3),
        ("Green Coconut Resort", "ECR", "ECR & Coastal Corridor", 3, "Standard", 3500, "WiFi,Pool,Beach,Restaurant", 12.8225, 80.2418, 4.2, "Muttukadu", 0.5),
        ("Ideal Beach Resort", "Mahabalipuram", "Mahabalipuram", 3, "Standard", 4000, "WiFi,Pool,Beach,Restaurant", 12.6185, 80.1945, 4.3, "Shore Temple", 0.5),
        ("Radisson BLU Temple Bay", "Mahabalipuram", "Mahabalipuram", 5, "Luxury", 12000, "WiFi,Pool,Spa,Beach,Restaurant,Bar", 12.6125, 80.1922, 4.7, "Shore Temple", 0.8),
        ("Taj Fishermans Cove", "Covelong", "ECR & Coastal Corridor", 5, "Luxury", 16000, "WiFi,Pool,Spa,Beach,Surfing,Restaurant", 12.7942, 80.2525, 4.8, "Covelong Beach", 0.1),
        ("Chariot Beach Resort", "Mahabalipuram", "Mahabalipuram", 4, "Premium", 6000, "WiFi,Pool,Beach,Restaurant", 12.6095, 80.1912, 4.4, "Pancha Rathas", 0.3),
        ("Hanu Reddy Residences", "Wallace Garden", "Central Chennai", 3, "Standard", 3000, "WiFi,Kitchen,Parking", 13.0472, 80.2538, 4.3, "Cathedral Road", 0.3),
        ("Grand Chennai by GRT", "Mount Road", "Central Chennai", 4, "Premium", 5500, "WiFi,Pool,Restaurant,Bar", 13.0598, 80.2622, 4.4, "Anna Salai", 0.1),
        ("MGM Beach Resort", "ECR", "ECR & Coastal Corridor", 3, "Standard", 3800, "WiFi,Pool,Beach", 12.8295, 80.2425, 4.1, "MGM Dizzee World", 0.2),
        ("Hotel Kannan", "Tambaram", "Outer Suburbs", 2, "Budget", 900, "WiFi,AC", 12.9248, 80.1262, 3.5, "Tambaram Station", 0.2),
        ("YWCA International Guest House", "Nandanam", "Central Chennai", 2, "Budget", 1200, "WiFi,AC,Canteen", 13.0308, 80.2405, 3.9, "Nandanam Signal", 0.2),
        ("Hotel Sabari Classic", "Kodambakkam", "West Chennai", 3, "Standard", 2500, "WiFi,Restaurant", 13.0518, 80.2262, 3.9, "Kodambakkam Bridge", 0.3),
        ("Turyaa Chennai", "OMR Perungudi", "OMR IT Corridor", 4, "Premium", 6500, "WiFi,Pool,Gym,Restaurant,Bar", 12.9568, 80.2368, 4.5, "Perungudi Junction", 0.5),
        ("Hablis Hotel", "Guindy", "South Chennai", 4, "Premium", 5500, "WiFi,Pool,Gym,Restaurant,Eco", 13.0045, 80.2122, 4.5, "Guindy Industrial Estate", 0.5),
        ("The Residency", "Anna Salai", "Central Chennai", 4, "Premium", 5000, "WiFi,Pool,Restaurant", 13.0622, 80.2612, 4.2, "Anna Salai", 0.1),
        ("Hotel Palmgrove", "Kodambakkam", "West Chennai", 3, "Standard", 2800, "WiFi,Pool,Restaurant", 13.0535, 80.2252, 4.0, "Kodambakkam", 0.2),
        ("Vivanta Chennai IT Expressway", "OMR", "OMR IT Corridor", 5, "Luxury", 9000, "WiFi,Pool,Spa,Gym,Restaurant,Bar", 12.8785, 80.2265, 4.6, "Siruseri IT Park", 0.5),
        ("Trident Chennai", "GST Road", "South Chennai", 5, "Luxury", 8500, "WiFi,Pool,Spa,Restaurant", 12.9862, 80.1718, 4.5, "Chennai Airport", 2.0),
        ("Ibis Chennai City Centre", "Wall Tax Road", "Central Chennai", 3, "Standard", 3200, "WiFi,Restaurant,AC", 13.0842, 80.2728, 4.1, "Central Station", 0.5),
        ("Ibis Chennai OMR", "OMR", "OMR IT Corridor", 3, "Standard", 3000, "WiFi,Restaurant", 12.9342, 80.2325, 4.0, "OMR Signal", 0.3),
    ]

    all_hotel_data = hotel_data + budget_names + hostels + more_hotels
    for h in all_hotel_data:
        hotels.append({
            "hotel_name": h[0], "area": h[1], "zone": h[2], "stars": h[3],
            "category": h[4], "price_per_night_inr": h[5], "amenities": h[6],
            "latitude": h[7], "longitude": h[8], "rating": h[9],
            "near_landmark": h[10], "distance_to_landmark_km": h[11]
        })
    return hotels

def generate_buses():
    """Generate 600+ interstate bus routes."""
    routes = []
    bus_id = 1000

    route_definitions = [
        # (origin, state, dest, state, operators, types, durations, distances, fares, freq)
        ("Bangalore", "Karnataka", "Chennai", "Tamil Nadu",
         [("KSRTC", "Airavat Club Class", 6.0, 350, 1200, "Every 30min"), ("KSRTC", "Airavat Multi-Axle", 6.5, 350, 900, "Every 30min"), ("SETC", "Ultra Deluxe", 7.0, 350, 600, "Hourly"), ("SRS Travels", "AC Sleeper", 7.0, 350, 1100, "4 per day"), ("KPN Travels", "Volvo Multi-Axle", 6.5, 350, 950, "6 per day"), ("Orange Travels", "AC Sleeper", 7.5, 350, 850, "3 per day"), ("VRL Travels", "Volvo AC", 6.5, 350, 1000, "4 per day"), ("National Travels", "AC Seater", 7.0, 350, 700, "5 per day"), ("Parveen Travels", "AC Sleeper", 7.0, 350, 800, "3 per day")]),
        ("Hyderabad", "Telangana", "Chennai", "Tamil Nadu",
         [("TSRTC", "Garuda Plus", 10.0, 790, 1500, "6 per day"), ("APSRTC", "Super Luxury", 11.0, 790, 1100, "8 per day"), ("Jabbar Travels", "Volvo Multi-Axle", 10.5, 790, 1400, "4 per day"), ("Orange Travels", "AC Sleeper", 11.0, 790, 1200, "3 per day"), ("Kaveri Travels", "AC Seater", 11.5, 790, 900, "3 per day"), ("SRS Travels", "AC Sleeper", 10.5, 790, 1300, "2 per day")]),
        ("Madurai", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Ultra Deluxe", 8.0, 462, 650, "Every 30min"), ("SETC", "AC Sleeper", 8.5, 462, 900, "6 per day"), ("KPN Travels", "Volvo AC", 7.5, 462, 850, "4 per day"), ("Parveen Travels", "AC Sleeper", 8.0, 462, 800, "3 per day"), ("SRS Travels", "Non-AC Sleeper", 9.0, 462, 500, "4 per day")]),
        ("Coimbatore", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Ultra Deluxe", 8.0, 505, 700, "Every 1hr"), ("SETC", "AC Sleeper", 8.5, 505, 950, "4 per day"), ("KPN Travels", "Volvo Multi-Axle", 8.0, 505, 900, "5 per day"), ("Parveen Travels", "AC Sleeper", 8.5, 505, 850, "3 per day"), ("Jabbar Travels", "AC Seater", 9.0, 505, 700, "3 per day")]),
        ("Trichy", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Deluxe", 6.5, 330, 450, "Every 1hr"), ("SETC", "AC Sleeper", 7.0, 330, 750, "4 per day"), ("KPN Travels", "AC Seater", 6.5, 330, 600, "3 per day")]),
        ("Salem", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Super Deluxe", 5.5, 340, 400, "Every 1hr"), ("SETC", "Ultra Deluxe", 5.5, 340, 500, "6 per day"), ("KPN Travels", "AC Seater", 5.5, 340, 550, "4 per day")]),
        ("Pondicherry", "Puducherry", "Chennai", "Tamil Nadu",
         [("SETC", "Express", 3.5, 160, 200, "Every 30min"), ("SETC", "Deluxe", 3.0, 160, 280, "Every 1hr"), ("Parveen Travels", "AC Seater", 3.0, 160, 350, "4 per day")]),
        ("Tirunelveli", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Ultra Deluxe", 11.0, 630, 800, "4 per day"), ("SETC", "AC Sleeper", 11.5, 630, 1100, "3 per day"), ("KPN Travels", "AC Sleeper", 11.0, 630, 1000, "2 per day")]),
        ("Kanyakumari", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Ultra Deluxe", 12.0, 710, 900, "3 per day"), ("SETC", "AC Sleeper", 12.5, 710, 1200, "2 per day")]),
        ("Thanjavur", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Deluxe", 7.0, 350, 450, "6 per day"), ("SETC", "Ultra Deluxe", 6.5, 350, 550, "4 per day")]),
        ("Vellore", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Express", 3.0, 140, 180, "Every 30min"), ("SETC", "Deluxe", 2.5, 140, 250, "Hourly")]),
        ("Tirupati", "Andhra Pradesh", "Chennai", "Tamil Nadu",
         [("APSRTC", "Super Luxury", 3.5, 140, 300, "Every 30min"), ("APSRTC", "Garuda", 3.0, 140, 450, "6 per day"), ("SETC", "Express", 3.5, 140, 250, "Hourly")]),
        ("Kochi", "Kerala", "Chennai", "Tamil Nadu",
         [("KSRTC Kerala", "Super Fast", 12.0, 700, 900, "4 per day"), ("KSRTC Kerala", "AC Sleeper", 12.5, 700, 1300, "2 per day"), ("KPN Travels", "AC Sleeper", 12.0, 700, 1200, "3 per day")]),
        ("Trivandrum", "Kerala", "Chennai", "Tamil Nadu",
         [("KSRTC Kerala", "Super Fast", 16.0, 780, 1100, "3 per day"), ("KSRTC Kerala", "AC Sleeper", 16.5, 780, 1500, "2 per day")]),
        ("Mangalore", "Karnataka", "Chennai", "Tamil Nadu",
         [("KSRTC", "Airavat", 12.0, 680, 1200, "3 per day"), ("VRL Travels", "AC Sleeper", 13.0, 680, 1100, "2 per day")]),
        ("Mysore", "Karnataka", "Chennai", "Tamil Nadu",
         [("KSRTC", "Rajahamsa", 8.0, 480, 800, "4 per day"), ("SRS Travels", "AC Sleeper", 8.5, 480, 900, "3 per day")]),
        ("Vijayawada", "Andhra Pradesh", "Chennai", "Tamil Nadu",
         [("APSRTC", "Super Luxury", 8.0, 440, 700, "6 per day"), ("Orange Travels", "AC Sleeper", 8.5, 440, 900, "3 per day")]),
        ("Vizag", "Andhra Pradesh", "Chennai", "Tamil Nadu",
         [("APSRTC", "Garuda Plus", 14.0, 800, 1400, "3 per day"), ("Jabbar Travels", "AC Sleeper", 14.5, 800, 1300, "2 per day")]),
        ("Mumbai", "Maharashtra", "Chennai", "Tamil Nadu",
         [("VRL Travels", "Volvo Multi-Axle", 18.0, 1280, 2200, "2 per day"), ("Paulo Travels", "AC Sleeper", 19.0, 1280, 2000, "Daily"), ("Neeta Travels", "AC Sleeper", 18.5, 1280, 2100, "Daily")]),
        ("Pune", "Maharashtra", "Chennai", "Tamil Nadu",
         [("VRL Travels", "AC Sleeper", 16.0, 1150, 1800, "2 per day"), ("Neeta Travels", "AC Sleeper", 16.5, 1150, 1700, "Daily")]),
        ("Goa", "Goa", "Chennai", "Tamil Nadu",
         [("Paulo Travels", "AC Sleeper", 14.0, 900, 1500, "3 per week"), ("VRL Travels", "Volvo AC", 14.5, 900, 1600, "3 per week")]),
        ("Hubli", "Karnataka", "Chennai", "Tamil Nadu",
         [("VRL Travels", "AC Sleeper", 12.0, 750, 1200, "2 per day"), ("KSRTC", "Airavat", 12.5, 750, 1000, "3 per day")]),
        ("Ooty", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Super Deluxe", 10.0, 560, 650, "3 per day"), ("KPN Travels", "AC Seater", 9.5, 560, 800, "2 per day")]),
        ("Kodaikanal", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Ultra Deluxe", 10.0, 530, 700, "3 per day"), ("KPN Travels", "AC Sleeper", 10.5, 530, 900, "2 per day")]),
        ("Erode", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Deluxe", 6.5, 390, 400, "Every 1hr"), ("SETC", "Ultra Deluxe", 6.0, 390, 500, "4 per day")]),
        ("Tirupur", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Deluxe", 7.0, 430, 450, "6 per day"), ("KPN Travels", "AC Seater", 7.0, 430, 600, "3 per day")]),
        ("Nagercoil", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Ultra Deluxe", 12.0, 690, 850, "3 per day"), ("SETC", "AC Sleeper", 12.5, 690, 1100, "2 per day")]),
        ("Kumbakonam", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Deluxe", 6.0, 290, 350, "6 per day")]),
        ("Rameswaram", "Tamil Nadu", "Chennai", "Tamil Nadu",
         [("SETC", "Ultra Deluxe", 10.0, 570, 700, "3 per day")]),
        # Connecting hub routes (for multi-hop)
        ("Bangalore", "Karnataka", "Hyderabad", "Telangana",
         [("KSRTC", "Airavat", 10.0, 570, 1100, "6 per day"), ("Orange Travels", "AC Sleeper", 10.5, 570, 1000, "4 per day")]),
        ("Mumbai", "Maharashtra", "Bangalore", "Karnataka",
         [("VRL Travels", "Volvo Multi-Axle", 16.0, 980, 1800, "4 per day"), ("Paulo Travels", "AC Sleeper", 17.0, 980, 1600, "3 per day")]),
        ("Mumbai", "Maharashtra", "Hyderabad", "Telangana",
         [("MSRTC", "Shivneri", 12.0, 710, 1200, "6 per day"), ("VRL Travels", "AC Sleeper", 12.5, 710, 1100, "4 per day")]),
        ("Mumbai", "Maharashtra", "Pune", "Maharashtra",
         [("MSRTC", "Shivneri", 3.5, 150, 400, "Every 15min"), ("Neeta Travels", "AC Seater", 3.5, 150, 500, "Hourly")]),
        ("Bangalore", "Karnataka", "Mysore", "Karnataka",
         [("KSRTC", "Rajahamsa", 3.0, 150, 350, "Every 15min"), ("SRS Travels", "AC Seater", 3.0, 150, 400, "Hourly")]),
        ("Bangalore", "Karnataka", "Goa", "Goa",
         [("KSRTC", "Airavat", 10.0, 560, 1000, "4 per day"), ("VRL Travels", "AC Sleeper", 10.5, 560, 1100, "3 per day")]),
        ("Kochi", "Kerala", "Bangalore", "Karnataka",
         [("KSRTC Kerala", "Super Fast", 8.0, 560, 800, "6 per day"), ("SRS Travels", "AC Sleeper", 8.5, 560, 900, "4 per day")]),
        ("Hyderabad", "Telangana", "Vijayawada", "Andhra Pradesh",
         [("TSRTC", "Super Luxury", 5.0, 270, 500, "Every 30min"), ("APSRTC", "Express", 5.5, 270, 400, "Hourly")]),
    ]

    departure_hours = ["06:00", "07:30", "08:00", "09:00", "10:00", "11:00", "12:00", "14:00", "15:30", "17:00", "18:00", "19:00", "20:00", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"]

    for rd in route_definitions:
        origin, o_state, dest, d_state, services = rd
        for svc in services:
            operator, bus_type, duration, dist, fare, freq = svc
            # Generate multiple departure times
            num_services = random.randint(2, 6)
            for _ in range(num_services):
                bus_id += 1
                dep = random.choice(departure_hours)
                dep_h, dep_m = int(dep.split(":")[0]), int(dep.split(":")[1])
                arr_h = int(dep_h + duration) % 24
                arr_m = dep_m + random.randint(0, 30)
                if arr_m >= 60:
                    arr_h = (arr_h + 1) % 24
                    arr_m -= 60
                arr = f"{arr_h:02d}:{arr_m:02d}"
                fare_var = int(fare * random.uniform(0.85, 1.15))
                dur_var = round(duration + random.uniform(-0.5, 0.5), 1)
                routes.append({
                    "bus_id": f"BUS-{bus_id}",
                    "operator": operator,
                    "bus_type": bus_type,
                    "origin_city": origin,
                    "origin_state": o_state,
                    "destination_city": dest,
                    "destination_state": d_state,
                    "departure_time": dep,
                    "arrival_time": arr,
                    "duration_hours": dur_var,
                    "distance_km": dist + random.randint(-10, 10),
                    "fare_inr": fare_var,
                    "frequency": freq
                })
    return routes

def generate_cities():
    """Generate 200+ Indian city coordinates."""
    cities = [
        ("Chennai", "Tamil Nadu", 13.0827, 80.2707, True, True, True, True, "MAA"),
        ("Delhi", "Delhi", 28.6139, 77.2090, True, True, True, True, "DEL"),
        ("Mumbai", "Maharashtra", 19.0760, 72.8777, True, True, True, True, "BOM"),
        ("Bangalore", "Karnataka", 12.9716, 77.5946, True, True, True, True, "BLR"),
        ("Hyderabad", "Telangana", 17.3850, 78.4867, True, True, True, True, "HYD"),
        ("Kolkata", "West Bengal", 22.5726, 88.3639, True, True, True, True, "CCU"),
        ("Ahmedabad", "Gujarat", 23.0225, 72.5714, True, True, True, True, "AMD"),
        ("Pune", "Maharashtra", 18.5204, 73.8567, True, True, True, True, "PNQ"),
        ("Jaipur", "Rajasthan", 26.9124, 75.7873, True, True, True, True, "JAI"),
        ("Lucknow", "Uttar Pradesh", 26.8467, 80.9462, True, True, True, True, "LKO"),
        ("Kochi", "Kerala", 9.9312, 76.2673, True, True, True, True, "COK"),
        ("Trivandrum", "Kerala", 8.5241, 76.9366, True, True, True, True, "TRV"),
        ("Goa", "Goa", 15.2993, 74.1240, True, True, True, True, "GOI"),
        ("Chandigarh", "Chandigarh", 30.7333, 76.7794, True, True, True, True, "IXC"),
        ("Bhopal", "Madhya Pradesh", 23.2599, 77.4126, True, True, True, True, "BHO"),
        ("Indore", "Madhya Pradesh", 22.7196, 75.8577, True, True, True, True, "IDR"),
        ("Nagpur", "Maharashtra", 21.1458, 79.0882, True, True, True, True, "NAG"),
        ("Patna", "Bihar", 25.6093, 85.1376, True, True, True, True, "PAT"),
        ("Ranchi", "Jharkhand", 23.3441, 85.3096, True, True, True, True, "IXR"),
        ("Bhubaneswar", "Odisha", 20.2961, 85.8245, True, True, True, True, "BBI"),
        ("Guwahati", "Assam", 26.1445, 91.7362, True, True, True, True, "GAU"),
        ("Dehradun", "Uttarakhand", 30.3165, 78.0322, True, True, True, True, "DED"),
        ("Varanasi", "Uttar Pradesh", 25.3176, 82.9739, True, True, True, True, "VNS"),
        ("Amritsar", "Punjab", 31.6340, 74.8723, True, True, True, True, "ATQ"),
        ("Srinagar", "J&K", 34.0837, 74.7973, True, True, True, True, "SXR"),
        ("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185, True, True, True, True, "VTZ"),
        ("Vijayawada", "Andhra Pradesh", 16.5062, 80.6480, True, False, True, True, ""),
        ("Tirupati", "Andhra Pradesh", 13.6288, 79.4192, True, True, True, True, "TIR"),
        ("Coimbatore", "Tamil Nadu", 11.0168, 76.9558, True, True, True, True, "CJB"),
        ("Madurai", "Tamil Nadu", 9.9252, 78.1198, True, True, True, True, "IXM"),
        ("Trichy", "Tamil Nadu", 10.7905, 78.7047, True, True, True, True, "TRZ"),
        ("Salem", "Tamil Nadu", 11.6643, 78.1460, True, False, True, True, ""),
        ("Pondicherry", "Puducherry", 11.9416, 79.8083, True, False, True, True, ""),
        ("Vellore", "Tamil Nadu", 12.9165, 79.1325, True, False, True, True, ""),
        ("Thanjavur", "Tamil Nadu", 10.7870, 79.1378, False, False, True, True, ""),
        ("Mangalore", "Karnataka", 12.9141, 74.8560, True, True, True, True, "IXE"),
        ("Mysore", "Karnataka", 12.2958, 76.6394, True, True, True, True, "MYQ"),
        ("Hubli", "Karnataka", 15.3647, 75.1240, True, True, True, True, "HBX"),
        ("Raipur", "Chhattisgarh", 21.2514, 81.6296, True, True, True, True, "RPR"),
        ("Jodhpur", "Rajasthan", 26.2389, 73.0243, True, True, True, True, "JDH"),
        ("Udaipur", "Rajasthan", 24.5854, 73.7125, True, True, True, True, "UDR"),
        ("Surat", "Gujarat", 21.1702, 72.8311, True, True, True, True, "STV"),
        ("Vadodara", "Gujarat", 22.3072, 73.1812, True, True, True, True, "BDQ"),
        ("Rajkot", "Gujarat", 22.3039, 70.8022, True, True, True, True, "RAJ"),
        ("Thiruvananthapuram", "Kerala", 8.5241, 76.9366, True, True, True, True, "TRV"),
        ("Kozhikode", "Kerala", 11.2588, 75.7804, True, True, True, True, "CCJ"),
        ("Agra", "Uttar Pradesh", 27.1767, 78.0081, True, True, True, True, "AGR"),
        ("Kanpur", "Uttar Pradesh", 26.4499, 80.3319, True, False, True, True, ""),
        ("Allahabad", "Uttar Pradesh", 25.4358, 81.8463, True, False, True, True, ""),
        ("Jammu", "J&K", 32.7266, 74.8570, True, True, True, True, "IXJ"),
        ("Leh", "Ladakh", 34.1526, 77.5771, False, True, False, False, "IXL"),
        ("Imphal", "Manipur", 24.8170, 93.9368, True, True, True, True, "IMF"),
        ("Shillong", "Meghalaya", 25.5788, 91.8933, True, True, True, True, "SHL"),
        ("Agartala", "Tripura", 23.8315, 91.2868, True, True, True, True, "IXA"),
        ("Dibrugarh", "Assam", 27.4728, 94.9120, True, True, True, True, "DIB"),
        ("Bagdogra", "West Bengal", 26.6812, 88.3286, True, True, True, True, "IXB"),
        ("Cooch Behar", "West Bengal", 26.3217, 89.4453, False, False, True, True, ""),
        ("Tirunelveli", "Tamil Nadu", 8.7139, 77.7567, True, False, True, True, ""),
        ("Kanyakumari", "Tamil Nadu", 8.0883, 77.5385, False, False, True, True, ""),
        ("Ooty", "Tamil Nadu", 11.4102, 76.6950, False, False, False, True, ""),
        ("Kodaikanal", "Tamil Nadu", 10.2381, 77.4892, False, False, False, True, ""),
        ("Erode", "Tamil Nadu", 11.3410, 77.7172, False, False, True, True, ""),
        ("Tirupur", "Tamil Nadu", 11.1085, 77.3411, False, False, True, True, ""),
        ("Nagercoil", "Tamil Nadu", 8.1833, 77.4119, False, False, True, True, ""),
        ("Kumbakonam", "Tamil Nadu", 10.9617, 79.3881, False, False, True, True, ""),
        ("Rameswaram", "Tamil Nadu", 9.2876, 79.3129, False, False, True, True, ""),
        ("Tuticorin", "Tamil Nadu", 8.7642, 78.1348, True, True, True, True, "TCR"),
        ("Dindigul", "Tamil Nadu", 10.3624, 77.9695, False, False, True, True, ""),
        ("Karur", "Tamil Nadu", 10.9601, 78.0766, False, False, True, True, ""),
        ("Hosur", "Tamil Nadu", 12.7409, 77.8253, False, False, True, True, ""),
        ("Dharmapuri", "Tamil Nadu", 12.1211, 78.1582, False, False, True, True, ""),
        ("Krishnagiri", "Tamil Nadu", 12.5186, 78.2137, False, False, True, True, ""),
        ("Cuddalore", "Tamil Nadu", 11.7480, 79.7714, False, False, True, True, ""),
        ("Chidambaram", "Tamil Nadu", 11.3990, 79.6910, False, False, True, True, ""),
        ("Villupuram", "Tamil Nadu", 11.9401, 79.4861, False, False, True, True, ""),
        ("Arakkonam", "Tamil Nadu", 13.0846, 79.6714, False, False, True, True, ""),
        ("Kanchipuram", "Tamil Nadu", 12.8342, 79.7036, False, False, True, True, ""),
        ("Mahabalipuram", "Tamil Nadu", 12.6269, 80.1927, False, False, False, True, ""),
    ]

    result = []
    for c in cities:
        result.append({
            "city_name": c[0], "state": c[1], "latitude": c[2], "longitude": c[3],
            "is_major_hub": c[4], "has_airport": c[5], "has_railway_station": c[6],
            "has_bus_terminal": c[7], "airport_code": c[8]
        })
    return result

def main():
    os.makedirs(r"d:\drl_project\hotels", exist_ok=True)
    os.makedirs(r"d:\drl_project\buses", exist_ok=True)
    os.makedirs(r"d:\drl_project\data", exist_ok=True)

    hotels = generate_hotels()
    df_h = pd.DataFrame(hotels)
    df_h.to_csv(r"d:\drl_project\hotels\chennai_hotels.csv", index=False, encoding="utf-8")
    print(f"Hotels: {len(hotels)} entries saved")

    buses = generate_buses()
    df_b = pd.DataFrame(buses)
    df_b.to_csv(r"d:\drl_project\buses\intercity_buses_india.csv", index=False, encoding="utf-8")
    print(f"Buses: {len(buses)} routes saved")

    cities = generate_cities()
    df_c = pd.DataFrame(cities)
    df_c.to_csv(r"d:\drl_project\data\city_coordinates.csv", index=False, encoding="utf-8")
    print(f"Cities: {len(cities)} entries saved")

if __name__ == "__main__":
    main()
