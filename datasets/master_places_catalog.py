import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import random
import math

# Curated City Specific Real POIs
REAL_CITY_PLACES = {
    "MAA": [
        ("Marina Beach & Lighthouse Promenade", "Beaches & Coastline", "Sandy Coastline", 13.0499, 80.2824, 2.5, "05:00", "22:00", 0, "Evening", "World's second longest urban beach with historic lighthouse, memorials, and evening street food.", "Sunset walks, lighthouse panoramic view, crispy sundal, horse rides", 4.6, 12500, 1, 1),
        ("Kapaleeshwarar Temple Mylapore", "Temples & Spiritual", "Dravidian Hindu Shrine", 13.0334, 80.2699, 2.0, "06:00", "21:00", 0, "Morning", "7th-century Dravidian temple dedicated to Lord Shiva with an iconic 37-meter rainbow gopuram and sacred tank.", "Dravidian architecture, Panguni Uthiram festival, peacock legends, ghee prasadam", 4.8, 9800, 1, 0),
        ("Fort St. George & Museum", "Heritage & History", "Colonial Fortress", 13.0797, 80.2871, 2.5, "09:00", "17:00", 25, "Morning", "First English fortress in India established in 1644, housing St. Mary's Church and colonial museum relics.", "Clive House, St. Mary's Church, colonial arms, British East India Company documents", 4.5, 4200, 1, 1),
        ("San Thome Minor Basilica", "Heritage & History", "Gothic Revival Cathedral", 13.0337, 80.2778, 1.5, "06:00", "21:00", 0, "Morning", "Neo-Gothic cathedral built over the tomb of St. Thomas the Apostle with stained glass windows.", "Tomb of St. Thomas, stained glass, museum relics, seaside prayer hall", 4.7, 5600, 1, 1),
        ("Phoenix MarketCity Velachery", "Shopping & Markets", "Luxury Shopping Mall", 12.9915, 80.2175, 3.0, "10:00", "22:00", 0, "Afternoon", "Chennai's premier luxury shopping destination with 300+ international fashion brands and IMAX cinemas.", "Luxury retail, Palladium wing, IMAX multiplex, global dining", 4.7, 8900, 1, 1),
        ("Rayar's Mess Mylapore", "Food, Messes & Cafes", "Heritage Tiffin Mess", 13.0345, 80.2680, 1.0, "06:30", "11:30", 0, "Morning", "Legendary 1935 tiffin institution serving piping hot ghee pongal, crispy medu vadas, and degree filter coffee.", "Melt-in-mouth rava pongal, fresh coconut chutney, filter coffee", 4.9, 6700, 1, 0),
        ("DakshinaChitra Heritage Village", "Museums & Arts", "Living History Museum", 12.8258, 80.2415, 3.5, "10:00", "18:00", 175, "Morning", "Living history museum showcasing 18 authentic reconstructed heritage houses of South India.", "Artisan workshops, folk dance performances, traditional craft demonstrations", 4.8, 5200, 1, 1),
        ("Elliot's Beach & Schmidt Memorial", "Beaches & Coastline", "Urban Coastline", 13.0007, 80.2721, 2.0, "05:00", "23:00", 0, "Evening", "Tranquil coastal promenade in Besant Nagar famous for Karl Schmidt memorial and lively beachfront cafes.", "Schmidt Memorial, Coakers walk, seaside artisanal cafes, sunset vista", 4.6, 7800, 1, 1),
        ("Government Museum Egmore", "Museums & Arts", "Historical & Art Museum", 13.0708, 80.2588, 3.0, "09:30", "17:00", 50, "Afternoon", "India's second oldest museum established in 1851, housing the world's finest Chola bronze sculptures.", "Chola Bronzes, Nataraja icon, Amaravati Buddhist sculptures, Roman coin collection", 4.7, 6100, 1, 1),
        ("T. Nagar Ranganathan Street Bazaar", "Shopping & Markets", "Pedestrian Shopping Street", 13.0405, 80.2337, 2.5, "09:00", "22:00", 0, "Evening", "One of India's most bustling commercial pedestrian streets for Kanchipuram silk sarees and gold jewellery.", "Pure Kanchipuram silks, Saravana Stores, wholesale gold and silver", 4.5, 11000, 0, 0),
        ("Guindy National Park & Children's Park", "Parks & Nature", "Protected Urban Forest", 13.0067, 80.2206, 2.5, "09:00", "17:30", 30, "Morning", "Unique protected urban national park in the city center harboring spotted deer, blackbucks, and flora.", "Spotted deer safari, blackbuck conservation, butterfly park", 4.4, 4300, 1, 1),
        ("Murugan Idli Shop T. Nagar", "Food, Messes & Cafes", "Authentic South Indian Dining", 13.0412, 80.2345, 1.5, "07:00", "23:00", 0, "Morning", "World-renowned South Indian restaurant famous for pillow-soft idlis served with four signature chutneys.", "Steamed mallipoo idlis, onion podi uthappam, jigarthanda", 4.7, 14000, 1, 1),
        ("Valluvar Kottam Memorial", "Heritage & History", "Granite Architectural Monument", 13.0551, 80.2415, 1.5, "08:30", "17:30", 20, "Morning", "Granite temple chariot monument honoring Tamil philosopher Saint Thiruvalluvar with 1330 inscribed verses.", "Monolithic stone chariot, 1330 Thirukkural verses engraved in granite", 4.4, 3800, 1, 1),
        ("Semmozhi Poonga Botanical Garden", "Parks & Nature", "Landscaped Eco Park", 13.0515, 80.2514, 2.0, "10:00", "19:00", 25, "Evening", "Lush 20-acre botanical oasis with rare medicinal plants, vertical gardens, and illuminated duck pond.", "Bonsai pavilion, vertical gardens, evening musical fountains", 4.5, 4900, 1, 1),
        ("Burma Bazaar Import Market", "Shopping & Markets", "Historic Trade Market", 13.0906, 80.2922, 2.0, "10:00", "21:00", 0, "Evening", "Legendary marketplace set up by Burmese refugees in 1969, renowned for imported electronics, perfumes, and Atho noodles.", "Atho street noodles, imported electronics, Burmese mohinga", 4.3, 3900, 0, 0)
    ],
    "DEL": [
        ("Red Fort (Lal Qila)", "Heritage & History", "Mughal Imperial Fortress", 28.6562, 77.2410, 3.0, "09:30", "16:30", 50, "Morning", "Historic Mughal red sandstone fortress built by Emperor Shah Jahan in 1639.", "Diwan-i-Aam, Diwan-i-Khas, Sound and Light Show, Lahori Gate", 4.6, 25000, 1, 1),
        ("Qutub Minar & Iron Pillar Complex", "Heritage & History", "UNESCO Minaret & Ruins", 28.5245, 77.1855, 2.5, "07:00", "18:00", 50, "Morning", "73-meter tall fluted brick minaret built in 1192 surrounded by 4th-century rust-resistant Iron Pillar.", "Qutub Minar, rust-resistant Iron Pillar, Alai Darwaza", 4.7, 21000, 1, 1),
        ("Humayun's Tomb & Charbagh Gardens", "Heritage & History", "Mughal Garden Tomb", 28.5933, 77.2507, 2.5, "06:00", "18:00", 50, "Afternoon", "First garden tomb on the Indian subcontinent, precursor and architectural inspiration for the Taj Mahal.", "Charbagh Persian gardens, marble dome, Isa Khan tomb", 4.8, 18000, 1, 1),
        ("India Gate & Kartavya Path", "Heritage & History", "National War Memorial", 28.6129, 77.2295, 2.0, "00:00", "23:59", 0, "Evening", "42-meter triumphal arch war memorial illuminated spectacularly at night along the central vista.", "Amar Jawan Jyoti, National War Memorial, evening strolls", 4.7, 34000, 1, 1),
        ("Swaminarayan Akshardham Temple", "Temples & Spiritual", "Grand Hindu Complex", 28.6127, 77.2773, 4.0, "09:30", "18:30", 0, "Afternoon", "Magnificent 100-acre spiritual complex featuring pink sandstone carvings and musical fountain show.", "Sahaj Anand water show, boat ride of Indian heritage, stone carving", 4.9, 29000, 1, 1),
        ("Chandni Chowk & Paranthe Wali Gali", "Food, Messes & Cafes", "Historic Street Food", 28.6506, 77.2303, 2.5, "09:00", "22:00", 0, "Evening", "17th-century Mughal bazaar famous for rabri jalebi, stuffed fried paranthas, and spice markets.", "Rabri falooda, deep-fried stuffed paranthas, Khari Baoli spice bazaar", 4.7, 19000, 0, 0),
        ("Dilli Haat INA Crafts Emporium", "Shopping & Markets", "Open-Air Craft Bazaar", 28.5732, 77.2075, 2.5, "10:30", "22:00", 30, "Evening", "Vibrant open-air village market with authentic regional handicraft stalls and state food pavilions.", "State food stalls (Momo, Thali), handmade shawls, Madhubani paintings", 4.6, 12000, 1, 1),
        ("Lodhi Gardens & Architectural Tombs", "Parks & Nature", "Historical Botanical Park", 28.5931, 77.2197, 2.0, "06:00", "20:00", 0, "Morning", "90-acre heritage city park dotted with 15th-century Sayyid and Lodhi dynasty domed tombs.", "Shisha Gumbad, Bara Gumbad, morning yoga walking trails", 4.8, 9500, 1, 1),
        ("Karim's Historic Mughlai Restaurant", "Food, Messes & Cafes", "Legendary Mughlai Dining", 28.6514, 77.2334, 1.5, "11:00", "23:30", 0, "Evening", "Founded in 1913 near Jama Masjid, famed for royal mutton burra kebabs and slow-cooked nihari.", "Mutton Burra kebab, royal Nihari, butter naan, shahi kheer", 4.8, 16000, 0, 0),
        ("Hauz Khas Village & Lake Fortress", "Entertainment & Theme Parks", "Heritage Lake & Nightlife", 28.5494, 77.1937, 3.0, "10:30", "23:00", 25, "Evening", "13th-century medieval reservoir and madrasa ruins surrounded by chic rooftop bistros and boutiques.", "Medieval madrasa ruins, deer park, lakeside sunset cafes", 4.6, 14000, 0, 0)
    ],
    "BOM": [
        ("Gateway of India & Apollo Bunder", "Heritage & History", "Colonial Triumphal Arch", 18.9220, 72.8347, 2.0, "00:00", "23:59", 0, "Morning", "Grand 1924 basalt arch overlooking the Arabian Sea harbor opposite the historic Taj Mahal Palace.", "Arabian Sea ferry rides, Taj Mahal Hotel view, sunrise photography", 4.7, 35000, 1, 1),
        ("Marine Drive Queen's Necklace", "Beaches & Coastline", "Seaside Boulevard", 18.9432, 72.8230, 2.5, "00:00", "23:59", 0, "Evening", "3.6-kilometer sweeping seaside promenade curving around Back Bay, glittering like a pearl necklace at night.", "Sunset promenade walk, Arabian sea breeze, tetrapod seating", 4.8, 42000, 1, 1),
        ("Elephanta Caves UNESCO Island", "Heritage & History", "Ancient Rock-Cut Caves", 18.9633, 72.9315, 4.0, "09:00", "17:30", 40, "Morning", "6th-century rock-cut cave temples on Gharapuri Island featuring the monolithic 20-foot Trimurti sculpture.", "Trimurti Shiva sculpture, ferry ride from Gateway, monolithic rock art", 4.7, 11000, 0, 0),
        ("Chhatrapati Shivaji Maharaj Terminus (CSMT)", "Heritage & History", "Victorian Gothic Rail Terminus", 18.9398, 72.8355, 1.5, "00:00", "23:59", 0, "Evening", "UNESCO World Heritage Victorian Gothic railway headquarters featuring gargoyles, domes, and illumination.", "Illuminated Gothic facade, stained glass, heritage museum", 4.8, 19000, 1, 1),
        ("Siddhivinayak Ganpati Temple Prabhadevi", "Temples & Spiritual", "Sacred Hindu Shrine", 19.0169, 72.8304, 2.0, "05:30", "21:45", 0, "Morning", "Historic 1801 gold-plated temple dedicated to Lord Ganesha, revered by millions of devotees.", "Gold-plated sanctum, Tuesday special aarti, modak prasad", 4.8, 26000, 1, 1),
        ("Juhu Beach Street Food Promenade", "Beaches & Coastline", "Coastal Street Food Beach", 19.0988, 72.8264, 2.5, "06:00", "23:00", 0, "Evening", "Vibrant sandy beach renowned for iconic Mumbai street delicacies like pav bhaji, bhel puri, and kulfi.", "Butter Pav Bhaji, Sev Puri, Kala Khatta gola, celebrity bungalows", 4.5, 28000, 1, 1),
        ("Colaba Causeway Flea & Antique Market", "Shopping & Markets", "Historic Shopping Street", 18.9218, 72.8322, 2.5, "10:00", "21:30", 0, "Evening", "Lively shopping street packed with vintage silver jewellery, antique brassware, and fashion bargains.", "Silver jewellery, vintage posters, brass artifacts, Leopold Cafe", 4.6, 15000, 0, 0),
        ("Britannia & Co. Parsi Heritage Dining", "Food, Messes & Cafes", "Colonial Parsi Cafe", 18.9351, 72.8385, 1.5, "11:30", "16:00", 0, "Afternoon", "Beloved 1923 colonial cafe in Ballard Estate famous for authentic Iranian Berry Pulao and Caramel Custard.", "Berry Pulao, Sali Boti, Caramel Custard, vintage wooden clock", 4.8, 7900, 1, 0),
        ("Sanjay Gandhi National Park & Kanheri Caves", "Parks & Nature", "Urban Forest & Ancient Caves", 19.2215, 72.9130, 4.0, "07:30", "17:30", 85, "Morning", "104 sq km protected urban national park with 109 rock-cut Buddhist Kanheri caves dating to 1st century BC.", "Kanheri Buddhist caves, lion and tiger safari, toy train", 4.6, 13000, 1, 1)
    ],
    "BLR": [
        ("Bangalore Palace & Tudor Grounds", "Heritage & History", "Tudor Royal Palace", 12.9988, 77.5921, 2.5, "10:00", "17:30", 250, "Morning", "1887 royal palace built in Tudor architectural style with fortified towers, stained glass, and hunting relics.", "Tudor architecture, royal durbar hall, wooden carvings", 4.6, 14000, 1, 1),
        ("Lalbagh Botanical Garden & Glass House", "Parks & Nature", "Historical Botanical Sanctuary", 12.9507, 77.5848, 2.5, "06:00", "19:00", 30, "Morning", "240-acre botanical garden commissioned by Hyder Ali in 1760 with historic London Crystal Palace inspired Glass House.", "Glass House flower shows, 3000-million-year-old Lalbagh rock, bonsai park", 4.7, 24000, 1, 1),
        ("Vidyarthi Bhavan Dosa Institution", "Food, Messes & Cafes", "Historic Heritage Tiffin", 12.9427, 77.5739, 1.0, "06:30", "11:30", 0, "Morning", "Iconic Gandhi Bazaar restaurant founded in 1943 famous for thick, golden, crispy butter Masala Dosas.", "Crispy butter Masala Dosa with saagu, filter coffee, vintage heritage", 4.8, 17000, 1, 0),
        ("Cubbon Park & Bamboo Groves", "Parks & Nature", "Urban Forest Oasis", 12.9763, 77.5929, 2.0, "06:00", "18:00", 0, "Morning", "300-acre lush lung space in the city center with colonial statues, bamboo groves, and heritage library.", "Bandstand, State Central Library, morning pet walks, shady bamboo trails", 4.7, 19000, 1, 1),
        ("Bannerghatta National Park Biological Reserve", "Parks & Nature", "Wildlife Safari & Zoo", 12.8009, 77.5777, 4.0, "09:30", "17:00", 350, "Morning", "Sprawling wildlife reserve offering tiger/lion safaris, a butterfly conservatory, and rescue center.", "Tiger and lion bus safari, Asia's first butterfly conservatory", 4.5, 16000, 1, 1),
        ("Commercial Street & Brigade Road Bazaars", "Shopping & Markets", "Bustling Retail Hub", 12.9822, 77.6083, 3.0, "10:30", "21:30", 0, "Evening", "Premier street shopping destination for fashion, embroidered silks, shoes, and street food.", "Street fashion, Dupattas, silver jewellery, food alleys", 4.6, 21000, 0, 0),
        ("Mavalli Tiffin Room (MTR) Lalbagh", "Food, Messes & Cafes", "Traditional Vegetarian Dining", 12.9520, 77.5860, 1.5, "06:30", "21:00", 0, "Morning", "Legendary institution founded in 1924, creator of Rava Idli and authentic pure ghee silver-cup coffee.", "Rava Idli with ghee, Chandrahara sweet, pure filter coffee", 4.8, 15000, 1, 1),
        ("Visvesvaraya Industrial & Technological Museum", "Museums & Arts", "Interactive Science Center", 12.9752, 77.5963, 2.5, "09:30", "18:00", 85, "Afternoon", "Interactive science exploratorium with dynamic aerospace, dinosaur, and engine mechanics galleries.", "Moving Spinosaurus replica, Wright brothers simulator, engine mechanics", 4.7, 11000, 1, 1)
    ],
    "JAI": [
        ("Amer Fort (Amber Fort) & Maota Lake", "Heritage & History", "Hilltop Rajput Fortress", 26.9855, 75.8513, 3.5, "08:00", "17:30", 100, "Morning", "Majestic 16th-century red sandstone and marble fortress overlooking Maota Lake with Sheesh Mahal.", "Sheesh Mahal (Mirror Palace), Diwan-i-Khas, Ganesh Pol, Elephant rides", 4.8, 31000, 1, 1),
        ("Hawa Mahal Palace of Winds", "Heritage & History", "Iconic Pink Sandstone Facade", 26.9239, 75.8267, 1.5, "09:00", "17:00", 50, "Morning", "Five-story pink sandstone palace built in 1799 with 953 intricately carved jharokhas (casements).", "953 jharokhas casements, panoramic Old City view, royal latticework", 4.7, 28000, 1, 0),
        ("City Palace & Chandra Mahal Jaipur", "Heritage & History", "Royal Rajput-Mughal Residence", 26.9258, 75.8236, 2.5, "09:30", "17:00", 300, "Afternoon", "Grand royal palace complex featuring Mubarak Mahal, Peacock Courtyard, and royal textile museum.", "Peacock Gate in Pritam Niwas Chowk, silver Gangajali urns, royal museum", 4.7, 19000, 1, 1),
        ("Jantar Mantar Astronomical Observatory", "Heritage & History", "UNESCO Stone Observatory", 26.9248, 75.8246, 2.0, "09:00", "17:00", 50, "Morning", "World's largest stone astronomical observatory built by Sawai Jai Singh II in 1734 featuring Samrat Yantra.", "Vrihat Samrat Yantra sundial, stone astrological instruments", 4.7, 16000, 1, 1),
        ("Nahargarh Fort Sunset Viewpoint", "Heritage & History", "Panoramic Ridge Fort", 26.9373, 75.8155, 2.5, "10:00", "22:00", 50, "Evening", "Defensive fort perched on the Aravalli hills offering spectacular panoramic sunset vistas of Jaipur city.", "Panoramic city sunset view, Padao open restaurant, Madhavendra Bhawan", 4.7, 22000, 1, 1),
        ("Johari Bazaar & Bapu Bazaar", "Shopping & Markets", "Traditional Craft Bazaars", 26.9200, 75.8280, 2.5, "10:30", "21:00", 0, "Evening", "Famous pink bazaars for Kundan Meenakari gemstone jewellery, Jaipuri quilts, and Mojari leather juttis.", "Kundan jewelry, Jaipuri razai quilts, camel leather mojari juttis", 4.6, 17000, 0, 0),
        ("LMB (Laxmi Misthan Bhandar) Johari Bazaar", "Food, Messes & Cafes", "Royal Rajasthani Sweet Shop", 26.9205, 75.8288, 1.5, "08:00", "23:00", 0, "Evening", "Historic 1727 institution renowned for authentic Rajasthani Dal Baati Churma and honeycomb Paneer Ghewar.", "Paneer Ghewar, Pyaaz Kachori, royal Rajasthani Thali, Mawa Kachori", 4.8, 14000, 1, 1)
    ],
    "VNS": [
        ("Kashi Vishwanath Temple & Corridor", "Temples & Spiritual", "Prime Shiva Jyotirlinga", 25.3109, 83.0107, 2.5, "04:00", "23:00", 0, "Morning", "One of the 12 sacred Jyotirlingas of Lord Shiva standing on the western bank of the Holy Ganga.", "Gold spire, sacred Shiva Lingam, Ganga view corridor", 4.9, 32000, 1, 1),
        ("Dashashwamedh Ghat Evening Ganga Aarti", "Heritage & History", "Holy Riverfront Ghat", 25.3068, 83.0103, 2.0, "05:00", "21:00", 0, "Evening", "Varanasi's most spectacular riverfront ghat where priests perform the grand multi-tiered brass lamp Ganga Aarti.", "Grand brass lamp Aarti, floating diya oil lamps, holy chanting", 4.9, 38000, 1, 1),
        ("Assi Ghat Subah-e-Banaras", "Temples & Spiritual", "Sacred Confluence Ghat", 25.2898, 83.0068, 2.0, "04:30", "22:00", 0, "Morning", "Southernmost ghat where river Assi meets Ganga, famous for sunrise yoga, classical music, and boat rides.", "Subah-e-Banaras sunrise music, rowing boat ride, lemon tea", 4.8, 19000, 1, 1),
        ("Sarnath Deer Park & Dhamek Stupa", "Heritage & History", "Buddhist Pilgrimage Site", 25.3811, 83.0214, 3.0, "09:00", "17:00", 25, "Morning", "Where Gautama Buddha delivered his first sermon in 528 BC, marked by the 43-meter cylindrical Dhamek Stupa.", "Dhamek Stupa, Ashoka Lion Capital museum, Bodhi tree", 4.8, 14000, 1, 1),
        ("Vishwanath Gali Banarasi Silk & Chaat Alleys", "Shopping & Markets", "Ancient Narrow Alleys", 25.3115, 83.0098, 2.0, "09:00", "21:30", 0, "Evening", "Narrow ancient stone alleys renowned for pure handwoven Banarasi silk sarees and Tamatar Chaat.", "Banarasi bridal silks, Tamatar Chaat at Kashi Chaat Bhandar, Malaiyo sweet", 4.7, 12000, 0, 0)
    ],
    "AGR": [
        ("Taj Mahal & Yamuna Riverfront", "Heritage & History", "UNESCO World Wonder", 27.1751, 78.0421, 3.5, "06:00", "18:30", 50, "Morning", "17th-century white marble mausoleum built by Mughal Emperor Shah Jahan for his empress Mumtaz Mahal.", "Ivory-white marble dome, pietra dura inlay, charbagh gardens, Yamuna reflection", 4.9, 65000, 1, 1),
        ("Agra Fort Jahangiri Mahal & Diwan-i-Am", "Heritage & History", "Mughal Imperial Residence", 27.1795, 78.0211, 2.5, "06:00", "18:00", 50, "Morning", "Vast red sandstone fortress that served as the main residence of emperors Akbar, Jahangir, and Shah Jahan.", "Jahangiri Mahal, Musamman Burj, Sheesh Mahal, Amar Singh Gate", 4.7, 28000, 1, 1),
        ("Fatehpur Sikri & Buland Darwaza", "Heritage & History", "UNESCO Mughal Ghost City", 27.0945, 77.6679, 3.5, "06:00", "18:00", 50, "Afternoon", "16th-century Mughal capital city founded by Emperor Akbar featuring the 54-meter grand Buland Darwaza.", "54m Buland Darwaza, Tomb of Salim Chishti, Panch Mahal, Jodha Bai Palace", 4.8, 17000, 1, 1),
        ("Mehtab Bagh Moonlight Garden", "Parks & Nature", "Mughal Sunset Riverfront Park", 27.1800, 78.0425, 2.0, "06:00", "18:00", 25, "Evening", "Charbagh riverside garden complex offering the most pristine sunset view of the Taj Mahal without crowds.", "Taj Mahal reflection in Yamuna, peaceful photography, sunset lawn", 4.7, 11000, 1, 1)
    ]
}

GENERIC_ATTRACTIONS_MAP = {
    "Temples & Spiritual": [
        ("{city} Ancient Shiva Sanctum", "Stone Temple Shrine", "Centuries-old stone temple with carved sanctum and peaceful pradakshina hall.", "Morning aarti, stone architecture, sacred bells"),
        ("{city} Historic Devi Mandir", "Holy Pilgrimage Shrine", "Revered regional Devi temple known for festivals and vibrant temple pond.", "Festive processions, temple pond, spiritual atmosphere"),
        ("{city} Sacred Gurudwara Sahib", "Sikh Shrine & Langar", "Peaceful community Gurudwara with soothing kirtan and 24/7 community langar hall.", "Community langar, sacred sarovar, peaceful hymns"),
        ("{city} Central Heritage Mosque", "Islamic Monument", "Historic city mosque featuring arched reflection courtyards and marble minarets.", "Friday prayers, marble calligraphy, peaceful cloister")
    ],
    "Heritage & History": [
        ("{city} Royal Hill Fort", "Historic Bastion", "Historic stone ramparts and watchtowers offering panoramic views of the district.", "Rampart walking trails, panoramic valley views, historic cannons"),
        ("{city} Regional Heritage Museum", "Sculptures & Relics", "Curated museum showcasing archaeological bronzes, tribal art, and manuscripts.", "Ancient stone sculptures, royal coins, regional history"),
        ("{city} Clock Tower & Heritage Square", "Colonial Landmark", "Historic town square with Victorian clock tower and bustling pedestrian plaza.", "Heritage architecture, town gathering square, photography"),
        ("{city} Palace Heritage Haveli", "Royal Residence", "Restored princely haveli showcasing teakwood balconies and stained glass halls.", "Carved jharokhas, courtyards, princely memorabilia")
    ],
    "Beaches & Coastline": [
        ("{city} Golden Beach Promenade", "Coastal Shore", "Wide sandy beach with sea breeze, palm groves, and walking track.", "Sunset ocean view, sea breeze, fresh coconut water"),
        ("{city} Coastal Lighthouse Point", "Sea Viewpoint", "Scenic coastal cliff with lighthouse offering sweeping ocean horizons.", "Lighthouse panoramic view, rock formations, coastal photography"),
        ("{city} Quiet Fishermen Cove Beach", "Serene Shoreline", "Tranquil shoreline with colorful catamarans and gentle ocean waves.", "Pristine sand, morning fishing boats, peace and calm")
    ],
    "Food, Messes & Cafes": [
        ("{city} Heritage Traditional Mess", "Iconic Breakfast Institution", "Beloved local tiffin mess serving freshly made regional specialties and hot coffee.", "Hot filter coffee, crispy vadas, authentic local thali"),
        ("{city} Royal Dum Biryani House", "Regional Specialty Dining", "Renowned culinary spot specializing in slow-cooked fragrant firewood dum biryani.", "Signature slow-cooked biryani, kebabs, regional curries"),
        ("{city} Garden Verandah Tea Cafe", "Artisanal Bakery & Cafe", "Charming garden cafe nestled among shady trees serving artisanal tea and snacks.", "Garden seating, regional snacks, artisanal coffee"),
        ("{city} Evening Street Food Bazaar", "Local Night Market", "Vibrant street food lane packed with sizzling delicacies, chaats, and sweets.", "Fresh jalebis, street chaat, local sweets")
    ],
    "Shopping & Markets": [
        ("{city} Central Wholesale Bazaar", "Traditional Pedestrian Market", "Historic pedestrian market known for handloom textiles, spices, and brassware.", "Authentic handlooms, spices, brass utensils, street bargains"),
        ("{city} Artisan Handicrafts Emporium", "State Crafts Gallery", "Government-certified emporium showcasing regional woodwork, silks, and pottery.", "Authentic GI-tagged handicrafts, wooden carvings, silk shawls"),
        ("{city} Premier Lifestyle Mall", "Modern Shopping Center", "Modern retail complex featuring branded outlets, multiplex, and food court.", "Brand shopping, cinema screens, family dining")
    ],
    "Parks & Nature": [
        ("{city} Botanical Lake Garden", "Eco Nature Park", "Landscaped botanical gardens surrounding a central boating lake with walking trails.", "Pedal boating, landscaped flower beds, walking track"),
        ("{city} Hilltop Viewpoint Reserve", "Scenic High Overlook", "Scenic hilltop vantage point providing panoramic views of the surrounding valleys.", "Sunrise vista, cool mountain breeze, photography"),
        ("{city} Urban Eco Wildlife Sanctuary", "Protected Green Forest", "Protected nature forest harboring indigenous birds, deer, and walking trails.", "Bird watching, shaded nature trails, deer conservation")
    ],
    "Entertainment & Theme Parks": [
        ("{city} Science Exploratorium & Planetarium", "Interactive Space Dome", "Interactive science center with planetarium sky show and hands-on physics exhibits.", "Dome sky show, hands-on science exhibits, children's park"),
        ("{city} Water World & Amusement Park", "Family Adventure Park", "Thrilling water rides, wave pool, and family adventure slides.", "Wave pool, spiral water slides, rain dance floor")
    ]
}

def generate_distinct_places_for_cities(cities_data):
    """
    Generates realistic, completely distinct, non-repeated tourist attractions
    and food places for cities across India.
    """
    all_places = []
    seen_place_names = set()

    for city in cities_data:
        cid = city["id"]
        cname = city["name"]
        clat = float(city["latitude"])
        clon = float(city["longitude"])
        ctags = str(city.get("tags", ""))
        
        # 1. If city has hand-curated real places, load them directly
        if cid in REAL_CITY_PLACES:
            for item in REAL_CITY_PLACES[cid]:
                (pname, cat, sub_cat, plat, plon, dur, op_t, cl_t, fee, tod, desc, famous, rating, num_rev, elderly, wheel) = item
                if pname in seen_place_names:
                    continue
                seen_place_names.add(pname)
                
                pid = f"PLC_{cid}_{cat[:3].upper()}_{len(all_places)+1}"
                all_places.append({
                    "id": pid,
                    "city_id": cid,
                    "name": pname,
                    "category": cat,
                    "sub_category": sub_cat,
                    "area": f"{cname} Central",
                    "latitude": plat,
                    "longitude": plon,
                    "recommended_duration_hours": dur,
                    "open_time": op_t,
                    "close_time": cl_t,
                    "entry_fee_inr": fee,
                    "best_time_of_day": tod,
                    "description": desc,
                    "famous_for": famous,
                    "rating": rating,
                    "num_reviews": num_rev,
                    "elderly_friendly": elderly,
                    "wheelchair_accessible": wheel
                })
        else:
            # 2. Generate curated distinct attractions tailored to city characteristics
            # Top cities get 8-12 attractions, others get 3-5 distinct attractions
            rank = city.get("popularity_rank", 50)
            is_hub = city.get("is_hub", 0)
            target_count = 10 if is_hub or rank <= 25 else (5 if rank <= 60 else 3)
            
            cats_to_pick = ["Temples & Spiritual", "Heritage & History", "Food, Messes & Cafes", "Shopping & Markets", "Parks & Nature"]
            if "Coast" in ctags or "Beach" in ctags or "Port" in ctags:
                cats_to_pick.append("Beaches & Coastline")

            count = 0
            for cat in cats_to_pick:
                if count >= target_count:
                    break
                tmpls = GENERIC_ATTRACTIONS_MAP.get(cat, [])
                for tmpl_title, sub_cat, desc, famous in tmpls:
                    if count >= target_count:
                        break
                    
                    pname = tmpl_title.replace("{city}", cname)
                    if pname in seen_place_names:
                        pname = f"{cname} {sub_cat}"
                    if pname in seen_place_names:
                        pname = f"{cname} Heritage {cat.split()[0]}"
                    if pname in seen_place_names:
                        continue
                    seen_place_names.add(pname)

                    plat = clat + random.uniform(-0.035, 0.035)
                    plon = clon + random.uniform(-0.035, 0.035)
                    dur = random.choice([1.5, 2.0, 2.5])
                    fee = random.choice([0, 0, 25, 50, 100]) if cat in ["Heritage & History", "Parks & Nature"] else 0
                    rating = round(random.uniform(4.3, 4.8), 1)
                    num_rev = random.randint(150, 4500)
                    
                    pid = f"PLC_{cid}_{cat[:3].upper()}_{count+1}"
                    all_places.append({
                        "id": pid,
                        "city_id": cid,
                        "name": pname,
                        "category": cat,
                        "sub_category": sub_cat,
                        "area": f"{cname} Central",
                        "latitude": round(plat, 4),
                        "longitude": round(plon, 4),
                        "recommended_duration_hours": dur,
                        "open_time": "08:30",
                        "close_time": "20:30",
                        "entry_fee_inr": fee,
                        "best_time_of_day": random.choice(["Morning", "Afternoon", "Evening"]),
                        "description": f"{desc.replace('{city}', cname)} Located in {cname}.",
                        "famous_for": famous,
                        "rating": rating,
                        "num_reviews": num_rev,
                        "elderly_friendly": 1 if cat in ["Temples & Spiritual", "Food, Messes & Cafes", "Parks & Nature"] else 0,
                        "wheelchair_accessible": 1 if cat in ["Shopping & Markets", "Museums & Arts"] else 0
                    })
                    count += 1

    return all_places

if __name__ == "__main__":
    from database.generate_1k_cities import generate_10k_cities
    cities = generate_10k_cities()
    places = generate_distinct_places_for_cities(cities)
    print(f"✅ Generated {len(places)} completely distinct, non-repeated places across {len(cities)} cities.")
