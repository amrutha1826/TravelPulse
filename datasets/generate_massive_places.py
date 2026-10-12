"""
Exhaustive 500+ Chennai Places and Local Gems Dataset Generator.
Expands the dataset to cover every corner of Chennai across all zones.
"""
import json
import os
import pandas as pd

# Load existing
places_file = r"d:\drl_project\tourist_places\chennai_places.json"
if os.path.exists(places_file):
    with open(places_file, "r", encoding="utf-8") as f:
        all_places = json.load(f)
else:
    all_places = []

existing_ids = {p["id"] for p in all_places}

# Micro spots and detailed local entries across Chennai
MORE_SPOTS = []

# Generate structured micro entries across various categories and zones
temples_data = [
    ("Madhavaram Sivasubramaniya Swamy Temple", "North Chennai", "Madhavaram", 13.1492, 80.2312, "Peaceful suburban Murugan temple with annual Brahmotsavam."),
    ("Tiruvottiyur Pattinathar Samadhi Temple", "North Chennai", "Tiruvottiyur", 13.1652, 80.3045, "Sacred Samadhi temple of the venerated Tamil saint-poet Pattinathar on the seashore."),
    ("Kolathur Sivan Temple (Somanatheswarar)", "North Chennai", "Kolathur", 13.1235, 80.2185, "Ancient Chola era Shiva temple with peaceful tank and sacred sthala vriksham."),
    ("Perambur Pillayar Kovil (Vadapazhaniyur Vinayagar)", "North Chennai", "Perambur", 13.1095, 80.2395, "Centuries-old community Ganesha temple known for Modak prasadam."),
    ("Washermanpet Sri Prasanna Venkatesa Perumal", "North Chennai", "Washermanpet", 13.1075, 80.2855, "Famous Vaishnavite temple celebrating grand Vaikunta Ekadasi processions."),
    ("Kasimedu Chenna Kesava Perumal Temple", "North Chennai", "Kasimedu", 13.1215, 80.2952, "Coastal Perumal temple worshipped by fishermen before venturing out to sea."),
    ("Vepery Sri Prasanna Vinayagar Temple", "Central Chennai", "Vepery", 13.0825, 80.2635, "Heritage Ganesha shrine revered by local residents for obstacle removal."),
    ("Chintadripet Adikesava Perumal Temple", "Central Chennai", "Chintadripet", 13.0765, 80.2735, "18th-century temple built during the weaver settlement era of British Madras."),
    ("Royapettah Balasubramanya Swamy Temple", "Central Chennai", "Royapettah", 13.0545, 80.2612, "Historic Murugan temple popular for Tuesday special poojas."),
    ("Thousand Lights Dargah & Mosque Complex", "Central Chennai", "Anna Salai", 13.0562, 80.2542, "Sacred Shia landmark with majestic minarets and peaceful prayer halls."),
    ("Triplicane Big Mosque (Wallajah Mosque)", "Central Chennai", "Triplicane", 13.0585, 80.2732, "Built in 1795 by the Nawab of Arcot entirely of teak and granite without iron nails."),
    ("Mylapore Madhava Perumal Temple", "Mylapore & Mandaveli", "Mylapore", 13.0365, 80.2725, "Birthplace of Peyalvar with expansive pillared corridors and sacred pushkarini."),
    ("Mylapore Virupaksheeswarar Temple", "Mylapore & Mandaveli", "Mylapore", 13.0315, 80.2685, "One of the Sapta Sthana Shiva temples of Mylapore with ancient Chola inscriptions."),
    ("Mylapore Valeeswarar Temple", "Mylapore & Mandaveli", "Mylapore", 13.0305, 80.2675, "Ancient temple where monkey king Vali worshipped Lord Shiva for divine strength."),
    ("Mandaveli Sri Ramakrishna Math & Universal Temple", "Mylapore & Mandaveli", "Mylapore / Mandaveli", 13.0378, 80.2655, "Sublime white marble universal temple designed in unified architectural motifs with silent meditation."),
    ("Alwarpet Sri Anjaneyar Temple (Luz)", "T. Nagar & Alwarpet", "Luz Church Road", 13.0392, 80.2565, "Vibrant roadside shrine offering butter alankaram and vadamala to Lord Hanuman."),
    ("T. Nagar Ayodhya Mandapam", "T. Nagar & Alwarpet", "West Mambalam", 13.0415, 80.2265, "Cultural and spiritual epicentre for Ramayana discourses, Carnatic concerts, and Vedic chanting."),
    ("West Mambalam Kasi Viswanathar Temple", "T. Nagar & Alwarpet", "West Mambalam", 13.0385, 80.2235, "Chola era Shiva temple known as the Dakshina Kasi of Chennai."),
    ("Saidapet Karaneeswarar Temple", "South Chennai", "Saidapet", 13.0235, 80.2245, "Historic temple with vast temple tank that holds the grand annual Theppam (float) festival."),
    ("Guindy Ekambareswarar Temple", "South Chennai", "Guindy", 13.0095, 80.2185, "Peaceful neighborhood temple revered by local tech and industrial community."),
    ("Adyar Ananthapadmanabha Swamy Temple", "South Chennai", "Gandhi Nagar Adyar", 13.0075, 80.2525, "Replica of Trivandrum Padmanabhaswamy temple with reclining deity and granite carving."),
    ("Velachery Dhandeeswarar Temple", "South Chennai", "Velachery", 12.9805, 80.2215, "1,000-year-old temple where Lord Yama worshipped Shiva to regain his staff of righteousness (Dhandam)."),
    ("Chromepet Kumaran Kundram Murugan Temple", "Outer Suburbs & Tambaram", "Chromepet", 12.9495, 80.1415, "Scenic hillock temple with 80 granite steps offering breezy panoramic sunset views."),
    ("Tambaram Kasi Viswanathar Temple", "Outer Suburbs & Tambaram", "East Tambaram", 12.9235, 80.1295, "Sacred pond and ancient sanctum serving the southern metropolitan hub."),
    ("Medavakkam Vadakkupattu Perumal Temple", "OMR IT Corridor", "Medavakkam", 12.9185, 80.1915, "Serene village-setting temple surrounded by coconut groves."),
    ("Sholinganallur Pratyangira Devi Temple", "OMR IT Corridor", "Sholinganallur", 12.8995, 80.2315, "Famed temple for Sri Maha Pratyangira Devi known for powerful midnight Amavasya poojas."),
    ("Kelambakkam Sri Veera Anjaneyar Temple", "OMR IT Corridor", "Kelambakkam", 12.7885, 80.2195, "Gateway temple to the OMR-ECR link road with peaceful garden courtyard."),
    ("Thiruvidanthai Nityakalyana Perumal Temple", "ECR & Coastal Corridor", "Thiruvidanthai", 12.7635, 80.2415, "Famous Divya Desam temple where Lord Varaha married 360 daughters of sage Kalava."),
    ("Mahabalipuram Mahishasuramardini Cave", "Mahabalipuram", "Mamallapuram", 12.6175, 80.1915, "7th-century rock cave carving depicting Goddess Durga slaying the buffalo demon Mahishasura."),
    ("Mahabalipuram Varaha Cave Temple", "Mahabalipuram", "Mamallapuram", 12.6182, 80.1922, "Pallava rock-cut temple with magnificent bas-reliefs of Lord Varaha lifting Bhudevi."),
    ("Mahabalipuram Olakkannesvara Temple (Old Lighthouse)", "Mahabalipuram", "Mamallapuram", 12.6168, 80.1918, "Masonry temple on top of a giant rock that served as India's oldest lighthouse in 700 AD."),
    ("Anna Nagar Ayyappan Temple", "West Chennai", "Anna Nagar West", 13.0895, 80.2035, "Majestic Kerala-style teakwood temple with authentic Panchavadyam drumming during festivals."),
    ("Koyambedu Kurungaleeswarar Temple", "West Chennai", "Koyambedu", 13.0725, 80.1985, "Where Lava and Kusha (sons of Lord Rama) are believed to have studied and worshipped Shiva."),
    ("Poonamallee Vaidyanatha Swamy Temple", "West Chennai", "Poonamallee", 13.0485, 80.1125, "Ancient temple praising Shiva as the divine doctor who cured Angaraka (Mars)."),
    ("Porur Ramanatheswarar Temple", "West Chennai", "Porur", 13.0365, 80.1595, "Sacred place where Lord Rama stayed and performed penance en route to Lanka.")
]

food_data = [
    ("Sree Akshayam (Anna Nagar)", "Food, Messes & Cafes", "Pure Veg Restaurant", "West Chennai", "Anna Nagar", 13.0875, 80.2145, "Premium vegetarian dining with signature Podi Idlis, Ghee Roast, and North Indian curries."),
    ("Ente Keralam (Poes Garden)", "Food, Messes & Cafes", "Fine-Dining Kerala Cuisine", "Central Chennai", "Poes Garden", 13.0495, 80.2525, "Celebrated fine-dining Kerala restaurant with Appam, Stew, Karimeen Pollichathu, and Elaneer Payasam."),
    ("The Marina (Seafood Specialist)", "Food, Messes & Cafes", "Seafood Restaurant", "Central Chennai", "College Road, Nungambakkam", 13.0645, 80.2475, "Pick your own fresh live catch from ice displays cooked to coastal Chettinad, Kerala, or Tandoori styles."),
    ("Chamiers Cafe (RA Puram)", "Food, Messes & Cafes", "Artisanal Verandah Cafe", "Mylapore & Mandaveli", "Chamiers Road", 13.0315, 80.2465, "Chic vintage European cafe with antique floral wallpaper, artisanal pastas, and freshly brewed coffees."),
    ("Sandy's Chocolate Laboratory", "Food, Messes & Cafes", "Dessert & Gourmet Bistro", "Central Chennai", "Wallace Garden, Nungambakkam", 13.0615, 80.2485, "Madras institution for decadent dark chocolate desserts, Nutella shakes, and gourmet burgers."),
    ("Geetha Cafe (T. Nagar)", "Food, Messes & Cafes", "Traditional Tiffin Center", "T. Nagar & Alwarpet", "Pondy Bazaar", 13.0412, 80.2365, "Old-school pocket-friendly tiffin room serving crisp Masala Dosa, hot Medu Vada, and Filter Coffee since 1950s."),
    ("Mami Tiffin Stall (Mylapore)", "Food, Messes & Cafes", "Iconic Brahmin Street Food", "Mylapore & Mandaveli", "Pitchu Pillai Street", 13.0338, 80.2692, "Tiny alley stall packed with foodies for hot Kozhukattai, Vazhaipoo Bajji, and Kunukku."),
    ("Al Reef Restaurant (Kotturpuram)", "Food, Messes & Cafes", "Arabian & Shawarma Landmark", "South Chennai", "Kotturpuram", 13.0165, 80.2415, "Night owl hotspot renowned for jumbo chicken shawarmas, Alfahm chicken, and Kerala parottas."),
    ("Sea Empire (Besant Nagar)", "Food, Messes & Cafes", "Coastal Arabian & Grill", "South Chennai", "Besant Nagar", 12.9995, 80.2695, "Midnight beach dining joint popular for Dragon Chicken, Barbecue platters, and egg kothu parotta."),
    ("Zaitoon (Velachery / Adyar)", "Food, Messes & Cafes", "Mughlai & Arabian Dine", "South Chennai", "Adyar", 13.0075, 80.2565, "Family favorite for succulent Mutton Raan, Barbecue Fish, Hummus with Kuboos, and Biryani."),
    ("Kabab Court (Sowcarpet)", "Food, Messes & Cafes", "Mughlai Street Rolls", "Central Chennai", "Sowcarpet", 13.0935, 80.2792, "Crispy roomali roti rolls stuffed with spiced paneer, tikka, and green mint chutney."),
    ("Sri Raghavendra Tiffin Room (Triplicane)", "Food, Messes & Cafes", "Traditional Karnataka Tiffin", "Central Chennai", "Triplicane", 13.0542, 80.2755, "Bisi Bele Bath, Kesari Bath, and Davangere Benne Dosa served with fragrant pure ghee."),
    ("Pattukottai Mess (T. Nagar)", "Food, Messes & Cafes", "Village Non-Veg Mess", "T. Nagar & Alwarpet", "T. Nagar", 13.0392, 80.2375, "Authentic rural Tamil Nadu non-veg meals with Nattu Kozhi (country chicken), brain fry, and mutton biryani."),
    ("Manga (ECR Beach Cafe)", "Food, Messes & Cafes", "Bohemian Beach Cafe", "ECR & Coastal Corridor", "Palavakkam", 12.9565, 80.2615, "Laid-back open lawn cafe offering woodfire pizza, mango smoothies, and acoustic music jams."),
    ("Bay View (Taj Fisherman's Cove)", "Food, Messes & Cafes", "Luxury Beachfront Seafood", "ECR & Coastal Corridor", "Covelong", 12.7938, 80.2522, "Romantic seaside open-air restaurant serving freshly grilled lobster, tiger prawns, and ocean breezes."),
    ("Moonrakers Restaurant (Mahabalipuram)", "Food, Messes & Cafes", "Travellers Seafood Cafe", "Mahabalipuram", "Othavadai Street", 12.6275, 80.1945, "Iconic backpacker cafe serving garlic butter calamari, tandoori kingfish, and chilled fresh juices."),
    ("Aadvaitha Tiffin House (Vadapalani)", "Food, Messes & Cafes", "Pure Veg Heritage Eatery", "West Chennai", "Vadapalani", 13.0515, 80.2125, "Traditional South Indian breakfast joint popular with film studio crews for hot Poha and Pongal."),
    ("Thambi Vilas (T. Nagar / Anna Nagar)", "Food, Messes & Cafes", "Vintage Tamil Bistro", "T. Nagar & Alwarpet", "T. Nagar", 13.0425, 80.2385, "Retro 1970s themed diner serving Goli Soda, Bun Parotta, Chicken Chinthamani, and Jigarthanda."),
    ("Blind Chymist (Nungambakkam)", "Food, Messes & Cafes", "Experimental Molecular Cafe", "Central Chennai", "Nungambakkam", 13.0635, 80.2425, "Quirky laboratory-themed cafe serving smoking nitrogen drinks, beaker shakes, and loaded nachos."),
    ("Ciclo Cafe (Kotturpuram)", "Food, Messes & Cafes", "Bicycle Themed Cafe", "South Chennai", "Gandhi Mandapam Road", 13.0145, 80.2435, "India's first cycling cafe with cycle art installations, premium espresso, gourmet quiches, and burgers.")
]

heritage_nature_shopping = [
    ("Madras Boat Club (Est. 1867)", "Heritage & History", "Historic Rowing Club", "South Chennai", "RA Puram", 13.0215, 80.2455, "One of the oldest rowing clubs in India on the scenic banks of Adyar river."),
    ("Victoria Public Hall (Town Hall)", "Heritage & History", "Victorian Landmark", "Central Chennai", "Park Town", 13.0832, 80.2758, "1888 Victorian town hall where stalwarts like Mahatma Gandhi and Swami Vivekananda addressed citizens."),
    ("C.P. Art Centre (Alwarpet)", "Museums & Arts", "Cultural Exhibition Centre", "T. Nagar & Alwarpet", "Eldams Road", 13.0395, 80.2525, "Vibrant gallery hosting traditional Tanjore paintings, tribal arts, handlooms, and live workshops."),
    ("Apparao Galleries (Nungambakkam)", "Museums & Arts", "Contemporary Art Gallery", "Central Chennai", "Wallace Garden", 13.0605, 80.2475, "Pioneering Indian contemporary art gallery showcasing renowned sculptors and painters."),
    ("Lalit Kala Akademi Regional Centre", "Museums & Arts", "National Academy of Fine Arts", "Central Chennai", "Greams Road", 13.0575, 80.2515, "Government art complex with sculpture studios, graphic printmaking workshops, and national exhibitions."),
    ("Santhome Waves Boardwalk", "Beaches & Coastline", "Seaside Boardwalk", "Mylapore & Mandaveli", "Santhome Beach", 13.0325, 80.2795, "Scenic beachfront walking promenade adjacent to San Thome Basilica overlooking local catamaran launches."),
    ("Kottivakkam Beach Sunset Point", "Beaches & Coastline", "Quiet Neighborhood Beach", "ECR & Coastal Corridor", "Kottivakkam", 12.9695, 80.2615, "Peaceful wide sandy beach loved by evening runners, sunset photographers, and tea lovers."),
    ("Injambakkam Sea Breeze Point", "Beaches & Coastline", "Private Vibe Beach", "ECR & Coastal Corridor", "Injambakkam", 12.9115, 80.2525, "Unspoiled golden coast framed by coastal casuarina pines and luxury beachfront bungalows."),
    ("Uthandi Beach Promenade", "Beaches & Coastline", "Secluded Coastal Stretch", "ECR & Coastal Corridor", "Uthandi", 12.8525, 80.2465, "Pristine beach away from city noise, popular for peaceful romantic walks and shell collecting."),
    ("Covelong Point Surf School", "Entertainment & Theme Parks", "Surfing & Ocean Sports Hub", "ECR & Coastal Corridor", "Covelong", 12.7925, 80.2515, "Internationally certified surf academy offering daily surf lessons, kayak tours, and board rentals."),
    ("VGP Snow Kingdom", "Entertainment & Theme Parks", "Indoor Snow & Ice Theme Park", "ECR & Coastal Corridor", "Injambakkam", 12.9062, 80.2482, "Sub-zero -8 degree indoor winter wonderland with ice slides, snow castles, and artificial snowfall."),
    ("Chennai Citi Centre Mall", "Shopping & Markets", "Retail Mall & Cinema", "Mylapore & Mandaveli", "RK Salai", 13.0455, 80.2695, "Centrally located sea-facing shopping mall with multiplex, gaming zone, and food court."),
    ("Pothys Swarna Mahal & Boutique", "Shopping & Markets", "Grand Silk & Gold Megastore", "T. Nagar & Alwarpet", "GN Chetty Road", 13.0418, 80.2372, "Multi-storey palace-style emporium offering bridal Kanjeevarams, antique gold jewelry, and diamonds."),
    ("Nalli Chinnasami Chetty (Panagal Park)", "Shopping & Markets", "Historic Flagship Silk Showroom", "T. Nagar & Alwarpet", "Panagal Park", 13.0408, 80.2325, "The legendary 1928 flagship silk house of Nalli where generations of South Indian brides select wedding sarees."),
    ("Sri Kumaran Thanga Maligai", "Shopping & Markets", "Traditional Gold & Diamond Jewellery", "T. Nagar & Alwarpet", "Usman Road", 13.0398, 80.2335, "Sprawling gold jewelry showroom famed for authentic temple jewelry designs and bridal sets."),
    ("Luz Corner Flower & Puja Stalls", "Shopping & Markets", "Traditional Puja Bazaar", "Mylapore & Mandaveli", "Luz Corner", 13.0388, 80.2652, "Fragrant street intersection bustling with fresh lotus flowers, marigold garlands, and puja brassware."),
    ("Ranganathan Street Night Flea Market", "Shopping & Markets", "Bustling Bargain Flea Market", "T. Nagar & Alwarpet", "Ranganathan Street", 13.0402, 80.2332, "High-energy pedestrian shopping lane packed with apparel deals, accessories, shoes, and street snacks."),
    ("Parry's Corner Paper & Stationery Lane", "Shopping & Markets", "Wholesale Specialty Market", "Central Chennai", "Bunder Street", 13.0888, 80.2852, "Historic wholesale district where wedding invitation card printers and artisanal paper makers operate."),
    ("Madras Music Academy Mini Hall", "Hidden Gems & Local Culture", "Acoustic Recital Hall", "T. Nagar & Alwarpet", "TTK Road", 13.0455, 80.2568, "Intimate performance space where upcoming Carnatic prodigies showcase kutcheris."),
    ("Brahma Gana Sabha", "Hidden Gems & Local Culture", "Cultural Fine Arts Sabha", "Mylapore & Mandaveli", "Mylapore", 13.0345, 80.2685, "Prestigious cultural organisation presenting classical dance dramas, vocal recitals, and Tamil theatre."),
    ("Tamil Isai Sangam (Raja Annamalai Hall)", "Hidden Gems & Local Culture", "Tamil Music Heritage Hall", "Central Chennai", "Esplanade", 13.0865, 80.2845, "Historic movement centre founded in 1943 to champion and preserve classical Carnatic compositions in Tamil.")
]

# Generate unique entries
new_entries = []
idx = 100

for item in temples_data:
    idx += 1
    new_entries.append({
        "id": f"CHN_TMP_GEN_{idx}",
        "name": item[0],
        "category": "Temples & Spiritual",
        "sub_category": "Temple & Spiritual Shrine",
        "zone": item[1],
        "area": item[2],
        "latitude": item[3],
        "longitude": item[4],
        "recommended_duration_hours": 1.0,
        "open_time": "06:00",
        "close_time": "20:30",
        "entry_fee_inr": 0,
        "best_time_of_day": "Morning",
        "description": item[5],
        "famous_for": item[0],
        "rating": 4.6,
        "tags": ["temple", "spiritual", item[1].lower(), "culture"]
    })

for item in food_data:
    idx += 1
    new_entries.append({
        "id": f"CHN_FOD_GEN_{idx}",
        "name": item[0],
        "category": item[1],
        "sub_category": item[2],
        "zone": item[3],
        "area": item[4],
        "latitude": item[5],
        "longitude": item[6],
        "recommended_duration_hours": 1.5,
        "open_time": "11:00",
        "close_time": "23:00",
        "entry_fee_inr": 0,
        "best_time_of_day": "Afternoon",
        "description": item[7],
        "famous_for": item[0],
        "rating": 4.6,
        "tags": ["food", "restaurant", "chennai food", item[3].lower()]
    })

for item in heritage_nature_shopping:
    idx += 1
    new_entries.append({
        "id": f"CHN_HNS_GEN_{idx}",
        "name": item[0],
        "category": item[1],
        "sub_category": item[2],
        "zone": item[3],
        "area": item[4],
        "latitude": item[5],
        "longitude": item[6],
        "recommended_duration_hours": 1.5,
        "open_time": "09:00",
        "close_time": "19:00",
        "entry_fee_inr": 20,
        "best_time_of_day": "Evening",
        "description": item[7],
        "famous_for": item[0],
        "rating": 4.5,
        "tags": ["attraction", item[1].lower(), item[3].lower()]
    })

# Add all new unique entries to all_places
for entry in new_entries:
    if entry["id"] not in existing_ids:
        all_places.append(entry)
        existing_ids.add(entry["id"])

# Save updated full dataset
out_dir = r"d:\drl_project\tourist_places"
with open(os.path.join(out_dir, "chennai_places.json"), "w", encoding="utf-8") as f:
    json.dump(all_places, f, indent=2, ensure_ascii=False)

df = pd.DataFrame(all_places)
df.to_csv(os.path.join(out_dir, "chennai_places.csv"), index=False, encoding="utf-8")
print(f"Total Places in Database: {len(all_places)}")
