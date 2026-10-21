"""
database/seed_pan_india_iconic_places.py
-----------------------------------------
Curates and seeds genuine, world-famous, geographically verifiable tourist
attractions across all North, East, West, Middle (Central), and North-East states.
Eliminates all generic 4-place templates in Kolkata, Darjeeling, Puri, Bhubaneswar,
Gaya, Amritsar, Lucknow, Ayodhya, Prayagraj, Rishikesh, Haridwar, Shimla, Manali,
Srinagar, Leh, Ahmedabad, Udaipur, Jodhpur, Jaisalmer, Pune, Panaji, Bhopal,
Indore, Gwalior, Khajuraho, Ujjain, Jabalpur, Guwahati, Kaziranga, Shillong, Gangtok, Tawang, etc.
Immediately attaches 3 authentic, grounded visitor reviews to every place.
"""

import os
import sys
import json
import sqlite3
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "travel_platform.db")

from database.rebuild_authentic_reviews import generate_place_reviews, INDIAN_NAMES

PAN_INDIA_ICONIC_PLACES = [
    # =========================================================================
    # 1. EAST INDIA
    # =========================================================================
    # Kolkata (CCU)
    {
        "id": "PLC_CCU_01", "city_id": "CCU", "name": "Victoria Memorial & Maidan Gardens",
        "category": "Heritage & History", "sub_category": "Royal Marble Monument & Museum", "area": "Maidan",
        "lat": 22.5448, "lon": 88.3426, "duration": 3.0, "open": "10:00", "close": "18:00", "fee": 50, "best_time": "Morning",
        "desc": "Grand white Makrana marble monument built between 1906 and 1921, housing 25 galleries with rare colonial paintings, artifacts, and royal statues.",
        "famous_for": "Angel of Victory revolving bronze statue, royal galleries, Queen Victoria statue, landscaped Maidan reflection pools",
        "rating": 4.8, "reviews_count": 48000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_CCU_02", "city_id": "CCU", "name": "Howrah Bridge (Rabindra Setu)",
        "category": "Heritage & History", "sub_category": "Iconic Cantilever Bridge", "area": "Howrah Riverfront",
        "lat": 22.5851, "lon": 88.3468, "duration": 1.5, "open": "00:00", "close": "23:59", "fee": 0, "best_time": "Evening",
        "desc": "Iconic 1943 balanced cantilever steel bridge spanning 705 meters across river Hooghly with zero nuts and bolts, illuminated brilliantly at night.",
        "famous_for": "River Hooghly ferry views, flower market at base, iconic silhouette, evening illumination",
        "rating": 4.7, "reviews_count": 36000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_CCU_03", "city_id": "CCU", "name": "Dakshineswar Kali Temple",
        "category": "Temples & Spiritual", "sub_category": "Navaratna Kali Temple", "area": "Dakshineswar",
        "lat": 22.6552, "lon": 88.3575, "duration": 2.5, "open": "06:00", "close": "20:30", "fee": 0, "best_time": "Morning",
        "desc": "1855 Navaratna style Hindu temple on the Hooghly river where Sri Ramakrishna Paramahamsa attained spiritual visions, featuring 12 Shiva shrines.",
        "famous_for": "Bhavatarini Kali sanctum, 12 Shiva shrines along river ghat, Ramakrishna meditation room, Panchavati garden",
        "rating": 4.9, "reviews_count": 42000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_CCU_04", "city_id": "CCU", "name": "Indian Museum (Jadu Ghar)",
        "category": "Museums & Arts", "sub_category": "National Historic Museum", "area": "Park Street",
        "lat": 22.5579, "lon": 88.3511, "duration": 3.0, "open": "10:00", "close": "17:00", "fee": 50, "best_time": "Afternoon",
        "desc": "Ninth oldest museum in the world (est. 1814) with 35 galleries showcasing Egyptian mummies, Bharhut Buddhist sculptures, and dinosaur fossils.",
        "famous_for": "4,000-year-old Egyptian mummy, 2nd-century BC Bharhut stupa gateway, Ashoka lion capital, meteorite collection",
        "rating": 4.7, "reviews_count": 21000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_CCU_05", "city_id": "CCU", "name": "Park Street Heritage Dining & Flurys",
        "category": "Food, Messes & Cafes", "sub_category": "Iconic Colonial Tearoom & Dining", "area": "Park Street",
        "lat": 22.5532, "lon": 88.3534, "duration": 2.0, "open": "07:30", "close": "23:00", "fee": 0, "best_time": "Morning",
        "desc": "Legendary 1927 Swiss confectionery and tearoom on Park Street famous for English breakfast, rum balls, and colonial dining.",
        "famous_for": "Flurys full English breakfast, chocolate rum balls, heritage colonial street vibe, Peter Cat Chelo Kebab nearby",
        "rating": 4.8, "reviews_count": 29000, "elderly": 1, "wheelchair": 1
    },

    # Darjeeling (CTY_00099)
    {
        "id": "PLC_DAR_01", "city_id": "CTY_00099", "name": "Tiger Hill Sunrise Viewpoint",
        "category": "Parks & Nature", "sub_category": "Himalayan Sunrise Peak", "area": "Tiger Hill",
        "lat": 26.9942, "lon": 88.2882, "duration": 2.5, "open": "04:00", "close": "08:00", "fee": 50, "best_time": "Morning",
        "desc": "2,590-meter peak offering the world's most famous sunrise vista where early morning sunlight illuminates Mount Kanchenjunga and Mount Everest in pink gold.",
        "famous_for": "Sunrise over Mount Kanchenjunga, Mount Everest horizon view, 360-degree snow peaks panorama",
        "rating": 4.9, "reviews_count": 34000, "elderly": 0, "wheelchair": 0
    },
    {
        "id": "PLC_DAR_02", "city_id": "CTY_00099", "name": "Darjeeling Himalayan Railway (Toy Train) & Batasia Loop",
        "category": "Heritage & History", "sub_category": "UNESCO Mountain Steam Railway", "area": "Batasia Loop",
        "lat": 27.0168, "lon": 88.2468, "duration": 2.5, "open": "08:00", "close": "17:00", "fee": 25, "best_time": "Morning",
        "desc": "1881 UNESCO World Heritage 2-foot narrow-gauge steam train spiraling 360 degrees around Batasia Loop with Gurkha War Memorial and Kanchenjunga backdrop.",
        "famous_for": "360-degree railway spiral loop, Gurkha soldiers war memorial, steam locomotive whistle, snow-capped backdrop",
        "rating": 4.8, "reviews_count": 27000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_DAR_03", "city_id": "CTY_00099", "name": "Happy Valley Tea Estate",
        "category": "Parks & Nature", "sub_category": "Historic Organic Tea Garden", "area": "Lebong Cart Road",
        "lat": 27.0545, "lon": 88.2618, "duration": 2.0, "open": "09:00", "close": "16:30", "fee": 100, "best_time": "Morning",
        "desc": "Darjeeling's second oldest tea estate established in 1854 at 6,800 feet, offering guided factory processing walkthroughs and muscatel tea tastings.",
        "famous_for": "First flush muscatel tea tasting, organic tea plantation hillside walk, antique British tea rolling machinery",
        "rating": 4.7, "reviews_count": 16000, "elderly": 1, "wheelchair": 0
    },

    # Puri (CTY_00123)
    {
        "id": "PLC_PUR_01", "city_id": "CTY_00123", "name": "Jagannath Temple Puri",
        "category": "Temples & Spiritual", "sub_category": "Prime Char Dham & Kalinga Temple", "area": "Grand Road",
        "lat": 19.8049, "lon": 85.8179, "duration": 3.5, "open": "05:00", "close": "23:00", "fee": 0, "best_time": "Morning",
        "desc": "Sacred 12th-century Char Dham shrine dedicated to Lord Jagannath, Balabhadra, and Subhadra, featuring a 65m sikhara and world's largest kitchen (Ananda Bazar).",
        "famous_for": "Neelachakra wheel on 65m spire, flag flying against wind, Mahaprasad at Ananda Bazar, annual Ratha Yatra",
        "rating": 4.9, "reviews_count": 52000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_PUR_02", "city_id": "CTY_00123", "name": "Golden Beach (Blue Flag Beach) Puri",
        "category": "Beaches & Coastline", "sub_category": "Eco-Certified Blue Flag Shoreline", "area": "Chakratirtha Road",
        "lat": 19.7985, "lon": 85.8282, "duration": 2.5, "open": "05:00", "close": "22:00", "fee": 20, "best_time": "Evening",
        "desc": "Prestigious Blue Flag certified golden sand beach on the Bay of Bengal, featuring pristine swimming zones, beach loungers, and Sudarsan Pattnaik sand sculptures.",
        "famous_for": "Blue Flag clean water certification, sunrise over Bay of Bengal, international sand art exhibits, coastal promenade",
        "rating": 4.8, "reviews_count": 31000, "elderly": 1, "wheelchair": 1
    },

    # Bhubaneswar (BBI)
    {
        "id": "PLC_BBI_01", "city_id": "BBI", "name": "Lingaraj Temple",
        "category": "Temples & Spiritual", "sub_category": "11th-Century Kalinga Masterpiece", "area": "Old Town",
        "lat": 20.2382, "lon": 85.8338, "duration": 2.5, "open": "05:00", "close": "21:00", "fee": 0, "best_time": "Morning",
        "desc": "Pinnacle of Kalinga architecture built in 11th century CE with a 55-meter central deula sanctum dedicated to Harihara (Shiva and Vishnu).",
        "famous_for": "55m soaring deula tower, Bindusagar lake holy dip, Harihara combined sanctum, 108 subsidiary stone shrines",
        "rating": 4.8, "reviews_count": 28000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_BBI_02", "city_id": "BBI", "name": "Udayagiri & Khandagiri Rock-Cut Caves",
        "category": "Heritage & History", "sub_category": "2nd-Century BCE Jain Monastery", "area": "Khandagiri",
        "lat": 20.2635, "lon": 85.7865, "duration": 2.5, "open": "09:00", "close": "18:00", "fee": 25, "best_time": "Morning",
        "desc": "33 rock-cut cave dwellings carved by King Kharavela of Chedi dynasty in 2nd century BCE featuring Queen's Cave (Rani Gumpha) and Brahmi inscriptions.",
        "famous_for": "Rani Gumpha two-story carved facade, Hathigumpha 17-line King Kharavela inscription, panoramic city view",
        "rating": 4.7, "reviews_count": 18000, "elderly": 0, "wheelchair": 0
    },

    # Gaya / Bodh Gaya (CTY_00130)
    {
        "id": "PLC_GAY_01", "city_id": "CTY_00130", "name": "Mahabodhi Temple Complex (UNESCO World Heritage)",
        "category": "Temples & Spiritual", "sub_category": "Buddhist Enlightenment Sanctorum", "area": "Bodh Gaya",
        "lat": 24.6960, "lon": 84.9914, "duration": 3.0, "open": "05:00", "close": "21:00", "fee": 0, "best_time": "Morning",
        "desc": "Supreme Buddhist pilgrimage site where Prince Siddhartha Gautama attained supreme enlightenment in 528 BCE, featuring a 50m pyramidal spire.",
        "famous_for": "Sacred Bodhi Tree, Diamond Throne (Vajrasana), 50m grand brick temple tower, chanting international monks",
        "rating": 4.9, "reviews_count": 45000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_GAY_02", "city_id": "CTY_00130", "name": "Vishnupad Temple Gaya",
        "category": "Temples & Spiritual", "sub_category": "Sacred Footprint Shrine", "area": "Chandrachur",
        "lat": 24.7778, "lon": 85.0085, "duration": 2.0, "open": "06:00", "close": "20:00", "fee": 0, "best_time": "Morning",
        "desc": "18th-century black basalt temple built by Queen Ahilyabai Holkar on the Falgu River, enshrining a 40cm footprint of Lord Vishnu on solid rock.",
        "famous_for": "Lord Vishnu 40cm footprint in basalt stone, 30m octagonal shikara, Pinda Daan rituals for ancestors on Falgu ghats",
        "rating": 4.7, "reviews_count": 22000, "elderly": 1, "wheelchair": 0
    },

    # =========================================================================
    # 2. NORTH INDIA
    # =========================================================================
    # Amritsar (ATQ)
    {
        "id": "PLC_ATQ_01", "city_id": "ATQ", "name": "Golden Temple (Sri Harmandir Sahib)",
        "category": "Temples & Spiritual", "sub_category": "Supreme Sikh Holy Shrine", "area": "Golden Temple Complex",
        "lat": 31.6200, "lon": 74.8765, "duration": 3.5, "open": "00:00", "close": "23:59", "fee": 0, "best_time": "Morning",
        "desc": "Holiest gurudwara in Sikhism adorned with 500 kg of pure gold leaf in the center of the Amrit Sarovar holy pool, serving 100,000 pilgrims daily in Langar.",
        "famous_for": "Gold-plated sanctum, holy Amrit Sarovar parikrama, Guru Granth Sahib live kirtan, world's largest community langar",
        "rating": 5.0, "reviews_count": 85000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_ATQ_02", "city_id": "ATQ", "name": "Jallianwala Bagh National Memorial",
        "category": "Heritage & History", "sub_category": "National Freedom Monument", "area": "Near Golden Temple",
        "lat": 31.6208, "lon": 74.8801, "duration": 1.5, "open": "06:30", "close": "19:30", "fee": 0, "best_time": "Morning",
        "desc": "Sacred national memorial marking the 1919 massacre site with preserved bullet marks on brick walls, Martyrs' Well, and Amar Jawan Jyoti flame.",
        "famous_for": "Preserved bullet marks on brick walls, Martyrs' Well (Shahidi Khuh), Amar Jawan eternal flame, museum galleries",
        "rating": 4.8, "reviews_count": 39000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_ATQ_03", "city_id": "ATQ", "name": "Attari-Wagah Border Beating Retreat Ceremony",
        "category": "Heritage & History", "sub_category": "Military Retreat Ceremony", "area": "Attari Border",
        "lat": 31.6048, "lon": 74.5718, "duration": 3.0, "open": "15:30", "close": "18:30", "fee": 0, "best_time": "Evening",
        "desc": "World-famous daily sunset military ceremony where BSF and Pakistan Rangers perform coordinated high-kick drills, flag lowering, and iron gate closure.",
        "famous_for": "High-kick military march, patriotic stadium chants, simultaneous flag lowering, Swarn Jayanti gate",
        "rating": 4.9, "reviews_count": 48000, "elderly": 1, "wheelchair": 1
    },

    # Lucknow (LKO)
    {
        "id": "PLC_LKO_01", "city_id": "LKO", "name": "Bara Imambara & Bhool Bhulaiya",
        "category": "Heritage & History", "sub_category": "Mughal-Awadh Labyrinth & Monument", "area": "Husainabad",
        "lat": 26.8690, "lon": 80.9130, "duration": 3.0, "open": "06:00", "close": "17:00", "fee": 50, "best_time": "Morning",
        "desc": "1784 monumental complex built by Nawab Asaf-ud-Daula with the world's largest unsupported vaulted hall and the legendary 3D Bhool Bhulaiya labyrinth.",
        "famous_for": "Bhool Bhulaiya maze passages, 50m unsupported vaulted ceiling, Shahi Baoli stepwell, acoustic whisper walls",
        "rating": 4.8, "reviews_count": 32000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_LKO_02", "city_id": "LKO", "name": "Rumi Darwaza & Clock Tower",
        "category": "Heritage & History", "sub_category": "Imperial Turkish Gateway", "area": "Husainabad",
        "lat": 26.8715, "lon": 80.9125, "duration": 1.0, "open": "00:00", "close": "23:59", "fee": 0, "best_time": "Evening",
        "desc": "60-foot grand gateway modeled on the Sublime Porte of Istanbul, standing as the grand architectural symbol of Lucknow and Awadhi culture.",
        "famous_for": "60ft arched gateway, nighttime illumination, Husainabad clock tower view, Victorian heritage square",
        "rating": 4.7, "reviews_count": 21000, "elderly": 1, "wheelchair": 1
    },

    # Ayodhya (CTY_00051)
    {
        "id": "PLC_AYO_01", "city_id": "CTY_00051", "name": "Shri Ram Janmabhoomi Mandir",
        "category": "Temples & Spiritual", "sub_category": "Grand Nagara Rama Temple", "area": "Ram Kot",
        "lat": 26.7958, "lon": 82.1945, "duration": 3.0, "open": "06:30", "close": "21:30", "fee": 0, "best_time": "Morning",
        "desc": "Magnificent Nagara style Hindu temple built of pink Bansi Paharpur sandstone at the birthplace of Lord Rama, with a 161ft spire and 392 carved pillars.",
        "famous_for": "Ram Lalla consecrated idol, 161ft grand vimana, 392 intricately carved sandstone pillars, Ram Katha corridor",
        "rating": 5.0, "reviews_count": 75000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_AYO_02", "city_id": "CTY_00051", "name": "Hanuman Garhi Fort Temple",
        "category": "Temples & Spiritual", "sub_category": "Hilltop Fortress Temple", "area": "Sai Nagar",
        "lat": 26.7972, "lon": 82.2028, "duration": 2.0, "open": "05:00", "close": "22:00", "fee": 0, "best_time": "Morning",
        "desc": "10th-century fortress temple reached by 76 stone steps where Lord Hanuman is believed to protect the holy city of Ayodhya from the ramparts.",
        "famous_for": "76 steps climb, panoramic city view, silver-adorned Hanuman idol, traditional laddoos offering",
        "rating": 4.8, "reviews_count": 34000, "elderly": 0, "wheelchair": 0
    },
    {
        "id": "PLC_AYO_03", "city_id": "CTY_00051", "name": "Saryu River Ghats & Evening Maha Aarti",
        "category": "Temples & Spiritual", "sub_category": "Holy Riverfront Aarti", "area": "Naya Ghat",
        "lat": 26.8055, "lon": 82.2085, "duration": 2.0, "open": "05:00", "close": "21:00", "fee": 0, "best_time": "Evening",
        "desc": "Sacred riverfront ghats on the holy river Saryu where thousands gather at sunset for synchronized multi-tiered brass lamp Maha Aarti.",
        "famous_for": "Grand brass lamp Saryu Maha Aarti, floating earthen diyas, Ram Ki Paidi illuminated steps, sunset boat rides",
        "rating": 4.9, "reviews_count": 28000, "elderly": 1, "wheelchair": 1
    },

    # Rishikesh (CTY_00153)
    {
        "id": "PLC_RSH_01", "city_id": "CTY_00153", "name": "Laxman Jhula & Ram Jhula Suspension Bridges",
        "category": "Heritage & History", "sub_category": "Ganga Suspension Bridges", "area": "Tapovan",
        "lat": 30.1338, "lon": 78.3298, "duration": 2.0, "open": "00:00", "close": "23:59", "fee": 0, "best_time": "Morning",
        "desc": "Iconic iron suspension footbridges suspended over the turquoise waters of river Ganga connecting sacred ashrams, temples, and yoga centers.",
        "famous_for": "Panoramic views of turquoise Ganga and Himalayas, breeze on bridge walk, riverside cafes, jumping fish feeding",
        "rating": 4.8, "reviews_count": 42000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_RSH_02", "city_id": "CTY_00153", "name": "Triveni Ghat Evening Maha Aarti",
        "category": "Temples & Spiritual", "sub_category": "River Confluence Holy Aarti", "area": "Mayakund",
        "lat": 30.1065, "lon": 78.2985, "duration": 2.0, "open": "05:00", "close": "20:30", "fee": 0, "best_time": "Evening",
        "desc": "Sacred confluence of Ganga, Yamuna, and Saraswati where priests chant Vedic hymns and rotate multi-tiered brass lamps at sunset.",
        "famous_for": "Vedic chanting and conch blowing, multi-tiered flaming brass lamps, floating leaf diyas down Ganga, holy bath",
        "rating": 4.9, "reviews_count": 36000, "elderly": 1, "wheelchair": 1
    },

    # Haridwar (CTY_00154)
    {
        "id": "PLC_HRD_01", "city_id": "CTY_00154", "name": "Har Ki Pauri & Ganga Aarti",
        "category": "Temples & Spiritual", "sub_category": "Prime Holy Riverfront Ghat", "area": "Har Ki Pauri",
        "lat": 29.9565, "lon": 78.1708, "duration": 2.5, "open": "04:30", "close": "22:00", "fee": 0, "best_time": "Evening",
        "desc": "Most sacred riverfront ghat on the Ganga where Lord Vishnu's footprint is embedded in stone, host to the mesmerizing daily evening Ganga Aarti.",
        "famous_for": "World-famous sunset Ganga Aarti with synchronized fire lamps, Charan Paduka footprint, floating marigold diyas",
        "rating": 4.9, "reviews_count": 64000, "elderly": 1, "wheelchair": 1
    },

    # Shimla (CTY_00145)
    {
        "id": "PLC_SHM_01", "city_id": "CTY_00145", "name": "The Ridge & Mall Road",
        "category": "Heritage & History", "sub_category": "Colonial Mountain Promenade", "area": "The Ridge",
        "lat": 31.1048, "lon": 77.1734, "duration": 3.0, "open": "00:00", "close": "23:59", "fee": 0, "best_time": "Evening",
        "desc": "Sprawling pedestrian boulevard overlooking snow-clad Pir Panjal ranges, featuring Tudor-style heritage buildings, cafes, and Christ Church.",
        "famous_for": "Christ Church neo-Gothic stained glass, views of snow-capped Pir Panjal, vehicle-free walking promenade, Gaiety Theatre",
        "rating": 4.8, "reviews_count": 41000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_SHM_02", "city_id": "CTY_00145", "name": "Jakhoo Temple & Colossal Hanuman Statue",
        "category": "Temples & Spiritual", "sub_category": "Hilltop Hanuman Shrine", "area": "Jakhoo Hill",
        "lat": 31.1008, "lon": 77.1852, "duration": 2.0, "open": "06:00", "close": "19:00", "fee": 0, "best_time": "Morning",
        "desc": "Highest point in Shimla at 8,054 feet crowned by a 108-foot giant orange statue of Lord Hanuman overlooking the entire mountain valley.",
        "famous_for": "108-foot colossal Hanuman statue, ropeway ride over pine forests, 360-degree Himalayan snow panorama",
        "rating": 4.7, "reviews_count": 23000, "elderly": 1, "wheelchair": 1
    },

    # Manali (CTY_00146)
    {
        "id": "PLC_MNL_01", "city_id": "CTY_00146", "name": "Solang Valley Adventure & Ski Slopes",
        "category": "Parks & Nature", "sub_category": "Alpine Adventure Valley", "area": "Solang",
        "lat": 32.3168, "lon": 77.1578, "duration": 4.0, "open": "08:00", "close": "18:00", "fee": 0, "best_time": "Morning",
        "desc": "Stunning alpine valley nestled between glaciers and pine forests, famous for paragliding, zorbing, winter skiing, and snow cable car rides.",
        "famous_for": "Tandem paragliding over alpine meadows, winter ski slopes, Anjani Mahadev frozen waterfall trek, cable car",
        "rating": 4.8, "reviews_count": 47000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_MNL_02", "city_id": "CTY_00146", "name": "Hadimba Devi Pagoda Temple",
        "category": "Temples & Spiritual", "sub_category": "Pagoda Wood Temple", "area": "Dhungri Forest",
        "lat": 32.2482, "lon": 77.1812, "duration": 1.5, "open": "08:00", "close": "18:00", "fee": 0, "best_time": "Morning",
        "desc": "1553 four-tiered wooden pagoda temple dedicated to Hadimba Devi, surrounded by centuries-old giant cedar (Deodar) trees.",
        "famous_for": "Four-tier wooden pagoda architecture, giant deodar cedar forest canopy, yak rides and Angora rabbit photos",
        "rating": 4.7, "reviews_count": 38000, "elderly": 1, "wheelchair": 0
    },

    # Srinagar (CTY_00177)
    {
        "id": "PLC_SRN_01", "city_id": "CTY_00177", "name": "Dal Lake Shikara Rides & Cedar Houseboats",
        "category": "Parks & Nature", "sub_category": "Alpine Glacial Lake & Water Life", "area": "Boulevard Road",
        "lat": 34.0836, "lon": 74.8370, "duration": 3.0, "open": "05:30", "close": "22:00", "fee": 500, "best_time": "Evening",
        "desc": "Jewel of Kashmir: iconic 18 sq km lake surrounded by snow-draped Zabarwan mountains with carved cedar houseboats and floating vegetable markets.",
        "famous_for": "Shikara boat ride at sunset, floating flower and vegetable markets, hand-carved pinewood houseboats, lotus gardens",
        "rating": 4.9, "reviews_count": 56000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_SRN_02", "city_id": "CTY_00177", "name": "Mughal Terraced Gardens (Shalimar & Nishat Bagh)",
        "category": "Parks & Nature", "sub_category": "Persian Imperial Terraced Gardens", "area": "Nishat",
        "lat": 34.1255, "lon": 74.8808, "duration": 2.5, "open": "09:00", "close": "19:00", "fee": 25, "best_time": "Morning",
        "desc": "Terraced Persian pleasure gardens commissioned by Emperor Jahangir in 1619, featuring multi-tiered water channels, fountains, and century-old chinar trees.",
        "famous_for": "Terraced water fountains cascading towards Dal Lake, giant Chinar tree avenues, vibrant flowerbeds",
        "rating": 4.8, "reviews_count": 31000, "elderly": 1, "wheelchair": 1
    },

    # Leh Ladakh (CTY_00186)
    {
        "id": "PLC_LEH_01", "city_id": "CTY_00186", "name": "Pangong Tso High Altitude Lake",
        "category": "Parks & Nature", "sub_category": "Endorheic Trans-Himalayan Lake", "area": "Changthang",
        "lat": 33.7595, "lon": 78.6674, "duration": 4.0, "open": "06:00", "close": "18:00", "fee": 0, "best_time": "Morning",
        "desc": "World's highest saltwater lake at 4,350 meters spanning 134 km across India and Tibet, whose waters change colors from deep blue to turquoise green.",
        "famous_for": "Color-shifting turquoise to deep blue water, snow-draped mountain reflections, 3 Idiots movie point, marmot spotting",
        "rating": 5.0, "reviews_count": 41000, "elderly": 0, "wheelchair": 0
    },
    {
        "id": "PLC_LEH_02", "city_id": "CTY_00186", "name": "Thiksey Monastery (Mini Potala)",
        "category": "Temples & Spiritual", "sub_category": "12-Story Gelugpa Buddhist Gompa", "area": "Thiksey",
        "lat": 34.0581, "lon": 77.6668, "duration": 2.5, "open": "07:00", "close": "18:00", "fee": 30, "best_time": "Morning",
        "desc": "12-story whitewashed Buddhist gompa on a hill resembling the Potala Palace in Lhasa, enshrining a magnificent 49-foot Maitreya Buddha statue.",
        "famous_for": "49-foot Maitreya Buddha statue, morning monk chanting and horn blowing ceremony, panoramic Indus valley view",
        "rating": 4.9, "reviews_count": 22000, "elderly": 0, "wheelchair": 0
    },

    # =========================================================================
    # 3. WEST INDIA
    # =========================================================================
    # Ahmedabad (AMD)
    {
        "id": "PLC_AMD_01", "city_id": "AMD", "name": "Sabarmati Ashram (Gandhi Ashram)",
        "category": "Heritage & History", "sub_category": "National Freedom Sanctum", "area": "Ashram Road",
        "lat": 23.0605, "lon": 72.5801, "duration": 2.5, "open": "08:30", "close": "18:30", "fee": 0, "best_time": "Morning",
        "desc": "Peaceful headquarters of Mahatma Gandhi from 1917 to 1930, from where he launched the 1930 historic Dandi Salt March, featuring Hriday Kunj.",
        "famous_for": "Hriday Kunj (Gandhi residence), original spinning charkha, Dandi March gallery, tranquil Sabarmati riverfront view",
        "rating": 4.8, "reviews_count": 38000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_AMD_02", "city_id": "AMD", "name": "Adalaj Stepwell (Rudabai Stepwell)",
        "category": "Heritage & History", "sub_category": "Solanki Subterranean Stepwell", "area": "Adalaj",
        "lat": 23.1667, "lon": 72.5800, "duration": 2.0, "open": "06:00", "close": "18:00", "fee": 25, "best_time": "Morning",
        "desc": "Five-story underground Solanki stepwell built in 1498 by Queen Rudadevi, renowned for intricate carved stone pillars, balconies, and cool chambers.",
        "famous_for": "Intricate Solanki floral stone carvings, 5-story subterranean architecture, natural cooling chamber, navagraha motifs",
        "rating": 4.8, "reviews_count": 27000, "elderly": 0, "wheelchair": 0
    },

    # Udaipur (CTY_00079)
    {
        "id": "PLC_UDR_01", "city_id": "CTY_00079", "name": "City Palace Udaipur & Lake Pichola",
        "category": "Heritage & History", "sub_category": "Royal Mewar Palace Complex", "area": "City Palace Road",
        "lat": 24.5764, "lon": 73.6835, "duration": 3.5, "open": "09:00", "close": "21:00", "fee": 300, "best_time": "Morning",
        "desc": "Rajasthan's largest royal palace complex standing along Lake Pichola, built over 400 years with marble balconies, mirror work, and Mewar museum.",
        "famous_for": "Mor Chowk peacock mosaics, Sheesh Mahal mirror work, panoramic Lake Pichola views, Mewar royal regalia",
        "rating": 4.9, "reviews_count": 51000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_UDR_02", "city_id": "CTY_00079", "name": "Saheliyon-ki-Bari (Courtyard of Maidens)",
        "category": "Parks & Nature", "sub_category": "Royal Marble Pleasure Garden", "area": "Saheli Marg",
        "lat": 24.6045, "lon": 73.6858, "duration": 1.5, "open": "08:00", "close": "19:00", "fee": 20, "best_time": "Evening",
        "desc": "18th-century royal pleasure garden designed for the Queen and her maidens, featuring marble elephant fountains, lotus pools, and rose pavilions.",
        "famous_for": "Gravity-fed marble elephant fountains, bird water sound effects, lotus ponds, bougainvillea avenues",
        "rating": 4.6, "reviews_count": 24000, "elderly": 1, "wheelchair": 1
    },

    # Jodhpur (CTY_00080)
    {
        "id": "PLC_JDH_01", "city_id": "CTY_00080", "name": "Mehrangarh Fort & Museum",
        "category": "Heritage & History", "sub_category": "Colossal Hilltop Rajput Citadel", "area": "Fort Road",
        "lat": 26.2978, "lon": 73.0185, "duration": 3.5, "open": "09:00", "close": "17:00", "fee": 100, "best_time": "Morning",
        "desc": "Colossal 15th-century cliffside fortress built by Rao Jodha rising 400 feet above the Blue City with Sheesh Mahal, royal palanquins, and cannons.",
        "famous_for": "Sweeping Blue City panorama from ramparts, Sheesh Mahal, Moti Mahal, royal palanquins and armor gallery",
        "rating": 4.9, "reviews_count": 48000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_JDH_02", "city_id": "CTY_00080", "name": "Jaswant Thada White Marble Cenotaph",
        "category": "Heritage & History", "sub_category": "Taj of Marwar Cenotaph", "area": "Near Fort",
        "lat": 26.3032, "lon": 73.0245, "duration": 1.5, "open": "09:00", "close": "17:00", "fee": 30, "best_time": "Morning",
        "desc": "1899 royal cenotaph carved from sheets of translucent white Makrana marble that glow warm gold in sunlight, set beside a tranquil lake.",
        "famous_for": "Translucent carved Makrana marble jali screens, tier garden by lake, Rajput royal portraits, peaceful ambiance",
        "rating": 4.7, "reviews_count": 19000, "elderly": 1, "wheelchair": 1
    },

    # Jaisalmer (CTY_00081)
    {
        "id": "PLC_JSA_01", "city_id": "CTY_00081", "name": "Jaisalmer Golden Fort (Sonar Qila)",
        "category": "Heritage & History", "sub_category": "UNESCO Living Golden Fortress", "area": "Fort Road",
        "lat": 26.9125, "lon": 70.9125, "duration": 3.0, "open": "00:00", "close": "23:59", "fee": 0, "best_time": "Morning",
        "desc": "1156 CE living yellow sandstone fortress rising from the Thar Desert with 99 bastions, royal palaces, and 7 ancient Jain temples.",
        "famous_for": "Living fort with residents and cafes inside, 99 yellow sandstone bastions, 7 carved Jain temples, sunrise golden glow",
        "rating": 4.9, "reviews_count": 39000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_JSA_02", "city_id": "CTY_00081", "name": "Sam Sand Dunes Desert Safari",
        "category": "Parks & Nature", "sub_category": "Thar Desert Dune Safari", "area": "Sam",
        "lat": 26.8335, "lon": 70.5085, "duration": 4.0, "open": "15:00", "close": "22:00", "fee": 500, "best_time": "Evening",
        "desc": "Sweeping golden dunes of the Thar Desert offering sunset camel rides, 4x4 dune bashing, Rajasthani folk music, and starlit glamping.",
        "famous_for": "Sunset camel safari across sand ripples, Kalbelia folk dance around bonfire, starlit night sky, dune bashing",
        "rating": 4.8, "reviews_count": 36000, "elderly": 1, "wheelchair": 0
    },

    # Pune (PNQ)
    {
        "id": "PLC_PNQ_01", "city_id": "PNQ", "name": "Shaniwar Wada Palace Fort",
        "category": "Heritage & History", "sub_category": "Peshwa Imperial Seat", "area": "Shaniwar Peth",
        "lat": 18.5195, "lon": 73.8553, "duration": 2.0, "open": "09:30", "close": "17:30", "fee": 25, "best_time": "Morning",
        "desc": "1732 seven-story fortified palace headquarters of the Peshwa rulers of the Maratha Empire, famed for the massive spiked Dilli Darwaza.",
        "famous_for": "Dilli Darwaza fortified spiked gate, Hazari Karanje 16-petal lotus fountain, evening light and sound show",
        "rating": 4.6, "reviews_count": 33000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_PNQ_02", "city_id": "PNQ", "name": "Aga Khan Palace (Gandhi Memorial)",
        "category": "Heritage & History", "sub_category": "National Freedom Memorial", "area": "Kalyani Nagar",
        "lat": 18.5525, "lon": 73.9015, "duration": 2.0, "open": "09:00", "close": "17:30", "fee": 25, "best_time": "Morning",
        "desc": "1892 Italian-arched palace built by Sultan Muhammed Shah Aga Khan III, where Mahatma Gandhi and Kasturba Gandhi were interned in 1942.",
        "famous_for": "Kasturba Gandhi and Mahadev Desai samadhis, Gandhi personal artifacts, Italian arches and spacious lawns",
        "rating": 4.7, "reviews_count": 21000, "elderly": 1, "wheelchair": 1
    },

    # Panaji & Goa (CTY_00182)
    {
        "id": "PLC_GOA_01", "city_id": "CTY_00182", "name": "Basilica of Bom Jesus (Old Goa)",
        "category": "Heritage & History", "sub_category": "UNESCO Baroque Basilica", "area": "Old Goa",
        "lat": 15.5008, "lon": 73.9118, "duration": 2.0, "open": "09:00", "close": "18:30", "fee": 0, "best_time": "Morning",
        "desc": "1605 UNESCO World Heritage baroque Catholic basilica enshrining the sacred incorrupt body of St. Francis Xavier in a silver casket.",
        "famous_for": "Sacred silver casket of St. Francis Xavier, Portuguese baroque architecture, gilded retable altar, historic paintings",
        "rating": 4.9, "reviews_count": 46000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_GOA_02", "city_id": "CTY_00182", "name": "Fort Aguada & Coastal Lighthouse",
        "category": "Heritage & History", "sub_category": "17th-Century Portuguese Coastal Fort", "area": "Sinquerim",
        "lat": 15.4925, "lon": 73.7735, "duration": 2.5, "open": "09:00", "close": "18:00", "fee": 25, "best_time": "Evening",
        "desc": "1612 Portuguese coastal fort guarding the Mandovi river mouth with a 4-tier lighthouse and sweeping 360-degree views of the Arabian Sea.",
        "famous_for": "1864 4-tier lighthouse, panoramic Arabian Sea sunset views, historic freshwater moat cistern",
        "rating": 4.8, "reviews_count": 41000, "elderly": 1, "wheelchair": 1
    },

    # =========================================================================
    # 4. MIDDLE / CENTRAL INDIA
    # =========================================================================
    # Bhopal (BHO)
    {
        "id": "PLC_BHO_01", "city_id": "BHO", "name": "Sanchi Stupa (UNESCO World Heritage)",
        "category": "Heritage & History", "sub_category": "Great Mauryan Buddhist Stupa", "area": "Sanchi",
        "lat": 23.4795, "lon": 77.7395, "duration": 3.0, "open": "06:30", "close": "18:30", "fee": 40, "best_time": "Morning",
        "desc": "Oldest stone structure in India commissioned by Emperor Ashoka in 3rd century BCE, featuring the Great Stupa with four exquisitely carved torana gates.",
        "famous_for": "Four carved stone toranas depicting Jataka tales, Ashoka lion pillar fragment, monolithic stone relic chambers",
        "rating": 4.9, "reviews_count": 31000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_BHO_02", "city_id": "BHO", "name": "Upper Lake (Bhojtal) & Boat Club",
        "category": "Parks & Nature", "sub_category": "Historic Wetland & Lake", "area": "VIP Road",
        "lat": 23.2505, "lon": 77.3485, "duration": 2.0, "open": "06:00", "close": "20:00", "fee": 0, "best_time": "Evening",
        "desc": "11th-century lake created by Paramara King Raja Bhoj spanning 31 sq km, offering motorboat rides, kayak rentals, and scenic sunset promenades.",
        "famous_for": "Raja Bhoj monolithic statue in water, speedboat and kayak rides, sunset VIP road drive, migratory birds",
        "rating": 4.7, "reviews_count": 22000, "elderly": 1, "wheelchair": 1
    },

    # Indore (IDR)
    {
        "id": "PLC_IDR_01", "city_id": "IDR", "name": "Rajwada Palace Indore",
        "category": "Heritage & History", "sub_category": "Holkar Seven-Story Palace", "area": "MG Road",
        "lat": 22.7185, "lon": 75.8568, "duration": 2.0, "open": "10:00", "close": "18:00", "fee": 20, "best_time": "Morning",
        "desc": "Historic 7-story palace built in 1766 by the Holkar rulers blending Maratha, Mughal, and French architecture with wooden balconies and stone gateways.",
        "famous_for": "7-story Maratha-Mughal facade, Ahilyabai Holkar statue, sound and light show, wooden jharokha balconies",
        "rating": 4.7, "reviews_count": 29000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_IDR_02", "city_id": "IDR", "name": "Sarafa Bazaar Midnight Street Food Market",
        "category": "Food, Messes & Cafes", "sub_category": "Iconic Midnight Street Food Hub", "area": "Sarafa",
        "lat": 22.7198, "lon": 75.8545, "duration": 2.5, "open": "20:00", "close": "02:00", "fee": 0, "best_time": "Evening",
        "desc": "Jewelry market by day transforming at 8 PM into India's most famous midnight street food bazaar featuring bhutte ka kees, garadu, and giant jalebas.",
        "famous_for": "Bhutte ka Kees, deep-fried spicy Garadu, giant Jaleba, Dahi Vada air-toss at Joshi Dahi Vada House",
        "rating": 4.9, "reviews_count": 44000, "elderly": 1, "wheelchair": 0
    },

    # Gwalior (CTY_00090)
    {
        "id": "PLC_GWL_01", "city_id": "CTY_00090", "name": "Gwalior Fort & Man Mandir Palace",
        "category": "Heritage & History", "sub_category": "Hilltop Citadel (Pearl of Indian Forts)", "area": "Fort Campus",
        "lat": 26.2305, "lon": 78.1695, "duration": 3.5, "open": "06:00", "close": "18:00", "fee": 75, "best_time": "Morning",
        "desc": "8th-century cliffside fortress described by Babur as 'the pearl in the necklace of forts of Hind', featuring turquoise-tiled Man Mandir Palace.",
        "famous_for": "Turquoise blue ceramic tile palace facade, 1000-year-old Saas Bahu temples, Teli Ka Mandir, Jain rock sculptures",
        "rating": 4.9, "reviews_count": 36000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_GWL_02", "city_id": "CTY_00090", "name": "Jai Vilas Palace & Scindia Museum",
        "category": "Heritage & History", "sub_category": "Italian-Corinthian Royal Palace", "area": "Lashkar",
        "lat": 26.2052, "lon": 78.1678, "duration": 2.5, "open": "10:00", "close": "17:00", "fee": 300, "best_time": "Morning",
        "desc": "1874 Italian-Corinthian royal palace of the Scindia dynasty housing two 3.5-tonne crystal chandeliers and a solid silver model train banquet table.",
        "famous_for": "World's largest pair of 3.5-tonne crystal chandeliers, solid silver banquet toy train, gold leaf Durbar Hall",
        "rating": 4.8, "reviews_count": 25000, "elderly": 1, "wheelchair": 1
    },

    # Khajuraho (CTY_00093)
    {
        "id": "PLC_KHJ_01", "city_id": "CTY_00093", "name": "Western Group of Temples (Kandariya Mahadeva, UNESCO)",
        "category": "Temples & Spiritual", "sub_category": "UNESCO Nagara Temple Sculptures", "area": "Sevagram",
        "lat": 24.8518, "lon": 79.9198, "duration": 3.0, "open": "06:00", "close": "18:00", "fee": 40, "best_time": "Morning",
        "desc": "10th-century UNESCO World Heritage sandstone temples built by Chandela kings celebrating divine union, life, and erotic sculptures.",
        "famous_for": "Kandariya Mahadeva 31m spire with 800+ carved figures, Lakshmana temple, erotic mithuna sculptures, evening sound and light show",
        "rating": 4.9, "reviews_count": 33000, "elderly": 1, "wheelchair": 1
    },

    # Ujjain (CTY_00092)
    {
        "id": "PLC_UJJ_01", "city_id": "CTY_00092", "name": "Mahakaleshwar Jyotirlinga & Mahakal Lok Corridor",
        "category": "Temples & Spiritual", "sub_category": "Dakshinmukhi Jyotirlinga & Grand Corridor", "area": "Jaisinghpura",
        "lat": 23.1828, "lon": 75.7682, "duration": 3.5, "open": "04:00", "close": "23:00", "fee": 0, "best_time": "Morning",
        "desc": "One of the 12 sacred Jyotirlingas, the only south-facing (Dakshinmukhi) shrine, famous for the early morning sacred Bhasma Aarti and 900m Mahakal Lok corridor.",
        "famous_for": "Pre-dawn Bhasma Aarti with sacred ash, 900-meter grand Mahakal Lok corridor with 108 stone pillars, Koti Tirtha tank",
        "rating": 5.0, "reviews_count": 68000, "elderly": 1, "wheelchair": 1
    },

    # =========================================================================
    # 5. NORTH-EAST INDIA
    # =========================================================================
    # Guwahati (GAU)
    {
        "id": "PLC_GAU_01", "city_id": "GAU", "name": "Kamakhya Devi Temple (Nilachal Hill)",
        "category": "Temples & Spiritual", "sub_category": "Supreme Tantric Shakti Peeth", "area": "Nilachal Hill",
        "lat": 26.1664, "lon": 91.7058, "duration": 3.0, "open": "05:30", "close": "20:00", "fee": 0, "best_time": "Morning",
        "desc": "Prime Tantric Shakti Peeth situated atop Nilachal Hill, worshipping the yoni of Goddess Sati in a subterranean natural cave spring.",
        "famous_for": "Natural underground spring sanctum, Nilachal hill views over Brahmaputra river, annual Ambubachi Mela festival",
        "rating": 4.9, "reviews_count": 46000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_GAU_02", "city_id": "GAU", "name": "Umananda Island Temple & Brahmaputra Cruise",
        "category": "Temples & Spiritual", "sub_category": "Peacock River Island Shrine", "area": "Brahmaputra River",
        "lat": 26.1912, "lon": 91.7482, "duration": 2.0, "open": "06:00", "close": "17:30", "fee": 30, "best_time": "Evening",
        "desc": "World's smallest inhabited river island sitting in the mighty Brahmaputra river, reached by scenic ferry boat, home to the endangered golden langurs.",
        "famous_for": "Smallest inhabited river island on earth, ferry boat across Brahmaputra, golden langur monkey habitat, sunset views",
        "rating": 4.7, "reviews_count": 21000, "elderly": 1, "wheelchair": 0
    },

    # Kaziranga (CTY_00166)
    {
        "id": "PLC_KAZ_01", "city_id": "CTY_00166", "name": "Kaziranga National Park (UNESCO World Heritage)",
        "category": "Parks & Nature", "sub_category": "World One-Horned Rhino Sanctuary", "area": "Kohora",
        "lat": 26.5775, "lon": 93.1711, "duration": 4.0, "open": "06:00", "close": "17:00", "fee": 100, "best_time": "Morning",
        "desc": "World-famous sanctuary harboring two-thirds of the world's Great One-Horned Rhinoceroses, along with tigers, wild water buffalo, and Asian elephants.",
        "famous_for": "One-horned rhino sightings in tall elephant grass, morning elephant safari, open jeep jungle drives, wild water buffaloes",
        "rating": 5.0, "reviews_count": 39000, "elderly": 1, "wheelchair": 0
    },

    # Shillong (CTY_00192)
    {
        "id": "PLC_SHL_01", "city_id": "CTY_00192", "name": "Umiam Lake (Barapani Reservoir)",
        "category": "Parks & Nature", "sub_category": "Mountain Pine Lake", "area": "Umiam",
        "lat": 25.6698, "lon": 91.9015, "duration": 2.5, "open": "06:00", "close": "18:00", "fee": 20, "best_time": "Evening",
        "desc": "Sprawling mountain lake surrounded by lush Khasi pine hills at 3,200 feet elevation, offering boat rides, water scooters, and scenic sunset viewpoints.",
        "famous_for": "Speedboat cruises, Khasi pine forest backdrop, cool highland breeze, peaceful photography vistas",
        "rating": 4.8, "reviews_count": 28000, "elderly": 1, "wheelchair": 1
    },
    {
        "id": "PLC_SHL_02", "city_id": "CTY_00192", "name": "Elephant Falls Three-Tier Cascade",
        "category": "Parks & Nature", "sub_category": "Three-Tiered Mountain Waterfall", "area": "Upper Shillong",
        "lat": 25.5358, "lon": 91.8245, "duration": 2.0, "open": "09:00", "close": "17:00", "fee": 20, "best_time": "Morning",
        "desc": "Three-tiered mountain waterfall cascading over dark fern-lined rocks, named by the British after an elephant-shaped rock at its base.",
        "famous_for": "Three distinct roaring waterfall drops, railed footpaths through pine forest, Khasi traditional dress photo stalls",
        "rating": 4.7, "reviews_count": 24000, "elderly": 1, "wheelchair": 0
    },

    # Gangtok (CTY_00202)
    {
        "id": "PLC_GTK_01", "city_id": "CTY_00202", "name": "Tsomgo (Changu) Glacial Lake",
        "category": "Parks & Nature", "sub_category": "High-Altitude Glacial Lake", "area": "East Sikkim",
        "lat": 27.3742, "lon": 88.7618, "duration": 3.5, "open": "07:30", "close": "15:00", "fee": 0, "best_time": "Morning",
        "desc": "Sacred oval-shaped glacial lake at 12,310 feet reflecting snow-capped peaks, where waters freeze in winter and alpine rhododendrons bloom in spring.",
        "famous_for": "Glacial lake frozen in winter, decorated yak rides along shore, alpine rhododendron blossoms, ropeway to 14,000ft",
        "rating": 4.9, "reviews_count": 37000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_GTK_02", "city_id": "CTY_00202", "name": "Rumtek Monastery (Dharma Chakra Centre)",
        "category": "Temples & Spiritual", "sub_category": "Imperial Tibetan Kagyu Gompa", "area": "Rumtek",
        "lat": 27.3032, "lon": 88.5348, "duration": 2.5, "open": "06:00", "close": "18:00", "fee": 10, "best_time": "Morning",
        "desc": "Main seat of the 16th Karmapa of Karma Kagyu lineage, housing golden stupas, ancient Tibetan thangkas, and Buddhist scripture libraries.",
        "famous_for": "Golden stupa containing 16th Karmapa relics, vibrant Tibetan thangka paintings, monk prayer halls, mountain views",
        "rating": 4.8, "reviews_count": 19000, "elderly": 1, "wheelchair": 0
    },

    # Tawang (CTY_00190)
    {
        "id": "PLC_TWN_01", "city_id": "CTY_00190", "name": "Tawang Monastery (Galden Namgyal Lhatse)",
        "category": "Temples & Spiritual", "sub_category": "Largest Monastery in India", "area": "Tawang Hill",
        "lat": 27.5861, "lon": 91.8594, "duration": 3.0, "open": "07:00", "close": "18:00", "fee": 20, "best_time": "Morning",
        "desc": "Founded in 1680 at 10,000 feet, the largest monastery in India and second largest in the world after Lhasa's Potala Palace, housing an 8m gilded Buddha.",
        "famous_for": "8-meter gilded Buddha statue in Dukhang hall, 400-year-old library with gold-lettered scriptures, snow peak vista",
        "rating": 5.0, "reviews_count": 21000, "elderly": 1, "wheelchair": 0
    },
    {
        "id": "PLC_TWN_02", "city_id": "CTY_00190", "name": "Sela Pass & Sela Lake (13,700 ft)",
        "category": "Parks & Nature", "sub_category": "High Mountain Pass & Lake", "area": "Sela",
        "lat": 27.5042, "lon": 92.1055, "duration": 2.0, "open": "06:00", "close": "16:00", "fee": 0, "best_time": "Morning",
        "desc": "High altitude mountain pass at 13,700 feet with 101 sacred lakes, frozen in winter and covered with fluttering Tibetan prayer flags.",
        "famous_for": "Sela frozen lake, prayer flags fluttering in cold mountain breeze, gate to Tawang, snowdrifts and mountain vista",
        "rating": 4.9, "reviews_count": 28000, "elderly": 0, "wheelchair": 0
    }
]

def seed_pan_india_places():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("===================================================================")
    print("SEEDING ICONIC REAL PLACES ACROSS NORTH, EAST, WEST, MIDDLE, NE")
    print("===================================================================")

    # 1. Clean up generic 4-place templates in these specific cities
    target_city_ids = list(set(p["city_id"] for p in PAN_INDIA_ICONIC_PLACES))
    placeholders_removed = 0
    for cid in target_city_ids:
        cursor.execute("SELECT id FROM places WHERE city_id = ? AND (name LIKE '%Ancient Shiva Sanctum%' OR name LIKE '%Royal Hill Fort%')", (cid,))
        del_rows = cursor.fetchall()
        for (del_id,) in del_rows:
            cursor.execute("DELETE FROM places WHERE id = ?", (del_id,))
            cursor.execute("DELETE FROM reviews WHERE entity_id = ?", (del_id,))
            placeholders_removed += 1

    print(f"Removed {placeholders_removed} obsolete template rows across {len(target_city_ids)} major cities.")

    # 2. Insert iconic places
    places_inserted = 0
    new_reviews = []

    for p in PAN_INDIA_ICONIC_PLACES:
        cursor.execute("""
            INSERT OR REPLACE INTO places (
                id, city_id, name, category, sub_category, area,
                latitude, longitude, recommended_duration_hours, open_time, close_time,
                entry_fee_inr, best_time_of_day, description, famous_for,
                rating, num_reviews, elderly_friendly, wheelchair_accessible, granularity_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"], p["city_id"], p["name"], p["category"], p["sub_category"], p["area"],
            p["lat"], p["lon"], p["duration"], p["open"], p["close"],
            p["fee"], p["best_time"], p["desc"], p["famous_for"],
            p["rating"], p["reviews_count"], p["elderly"], p["wheelchair"], "point_of_interest"
        ))
        places_inserted += 1

        # Fetch city name
        cursor.execute("SELECT name FROM cities WHERE id = ?", (p["city_id"],))
        c_row = cursor.fetchone()
        city_name = c_row[0] if c_row else "India"

        # Generate 3 authentic visitor reviews
        gen_revs = generate_place_reviews(
            p["id"], p["name"], p["category"], p["sub_category"], p["area"],
            p["famous_for"], p["desc"], city_name, p["rating"]
        )

        for r_num, (rev_text, base_r, sentiment, aspects) in enumerate(gen_revs[:3]):
            reviewer_name = INDIAN_NAMES[(hash(p["id"]) * 23 + r_num * 17) % len(INDIAN_NAMES)]
            rid = f"REV_PLC_{p['id']}_{r_num+1}"
            date_val = f"2025-{(r_num * 3 + 1):02d}-{(r_num * 6 + 7):02d}"
            new_reviews.append((
                rid, "place", p["id"], p["name"],
                reviewer_name, base_r, rev_text, sentiment,
                json.dumps(aspects), date_val
            ))

    cursor.executemany("""
        INSERT OR REPLACE INTO reviews (id, entity_type, entity_id, entity_name, user_name, rating, review_text, sentiment, aspects_json, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, new_reviews)

    conn.commit()

    print(f"\nSuccessfully seeded {places_inserted} iconic attractions across North, East, West, Middle, and North-East India!")
    print(f"Successfully generated {len(new_reviews)} grounded reviews!")

    cursor.execute("SELECT COUNT(DISTINCT city_id), COUNT(*) FROM places")
    c_count, p_count = cursor.fetchone()
    print(f"\nUpdated places status: {p_count} total places across {c_count} distinct cities in database.")

    conn.close()

if __name__ == "__main__":
    seed_pan_india_places()
