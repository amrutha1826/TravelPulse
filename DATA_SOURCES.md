# 📚 Comprehensive Data Sources, Citations & Origin Links

This document provides all direct source links, Kaggle repositories, Open Data portals, and government datasets used across the **Chennai DRL Multi-Modal Trip Planner**.

---

## 1. 🚆 Indian Railways Train Schedules & Routes Dataset

### Primary Sources:
- **Kaggle Indian Railways Complete Dataset**:
  - URL: [https://www.kaggle.com/datasets/sulianova/information-about-indian-railway-trains](https://www.kaggle.com/datasets/sulianova/information-about-indian-railway-trains)
  - Dataset file: `Train_details_22122017.csv` (186,126 station schedule records across all Indian trains, stations, departure/arrival timings, and distances).
- **Kaggle All Indian Trains Dataset**:
  - URL: [https://www.kaggle.com/datasets/sanketghule/all-indian-trains-dataset](https://www.kaggle.com/datasets/sanketghule/all-indian-trains-dataset)
  - Dataset file: `All_Indian_Trains.csv`
- **Data.gov.in (National Open Data Portal - Indian Railways Schedule)**:
  - URL: [https://data.gov.in/resource/indian-railways-time-table-train-schedules](https://data.gov.in/resource/indian-railways-time-table-train-schedules)
  - License: Government Open Data License - India (GODL)

---

## 2. ✈️ Indian Domestic Flights Dataset

### Primary Sources:
- **Kaggle Cleaned Indian Flight Prices & Routes Dataset**:
  - URL: [https://www.kaggle.com/datasets/shubhambathwal/flight-price-prediction](https://www.kaggle.com/datasets/shubhambathwal/flight-price-prediction)
  - URL: [https://www.kaggle.com/datasets/sudalairajkumar/indian-flight-routes-and-fares](https://www.kaggle.com/datasets/sudalairajkumar/indian-flight-routes-and-fares)
  - Dataset file: `indian_all_places_flights_dataset.csv` (1,314 domestic flight routes between all Indian airport hubs, airlines like IndiGo, Air India, SpiceJet, departure/arrival times, durations, and cabin fares).
- **Directorate General of Civil Aviation (DGCA) Domestic City-Pair Data**:
  - URL: [https://www.dgca.gov.in/digigov-portal/?page=4265/4260/servicename](https://www.dgca.gov.in/digigov-portal/?page=4265/4260/servicename)

---

## 3. 🚇 Chennai Metro Rail (CMRL) Network Dataset

### Primary Sources:
- **Chennai Metro Rail Limited (CMRL) Official Station & Route Data**:
  - Official Portal: [https://chennaimetrorail.org/](https://chennaimetrorail.org/)
  - Line 1 (Blue Line: Wimco Nagar Depot $\leftrightarrow$ Chennai International Airport) & Line 2 (Green Line: Chennai Central $\leftrightarrow$ St. Thomas Mount).
- **OpenCity.in Urban Data Portal (Chennai Metro Rail)**:
  - URL: [https://opencity.in/data/chennai-metro-rail-limited-station-details](https://opencity.in/data/chennai-metro-rail-limited-station-details)
  - Dataset file: `chennai_metro_rail_limited_chennai.csv` & `chennai-metro-eda.ipynb`
- **KML Geocoded Spatial Lines (Phase 1 CMRL)**:
  - Dataset files: `77c9aa1c-d8d3-44e4-b55c-90a1046ba87e.kml` and `b3221b7e-cb19-4f5d-a404-1fc96060cb66.kml` (extracted spatial alignments).

---

## 4. 🏛️ Chennai POI, Heritage, Temples, Beaches & Food Places Dataset

### Primary Sources:
- **OpenStreetMap (OSM) Chennai Geographical & Tourism Extraction**:
  - Overpass Turbo API / OSM Chennai Bounding Box: `[bbox:12.75, 80.05, 13.30, 80.35]`
  - Query: `node["tourism"]`, `node["historic"]`, `node["amenity"="place_of_worship"]`, `node["amenity"="restaurant"]`
  - URL: [https://www.openstreetmap.org/](https://www.openstreetmap.org/) / [https://overpass-turbo.eu/](https://overpass-turbo.eu/)
  - License: Open Database License (ODbL)
- **Tamil Nadu Tourism Development Corporation (TTDC) Official Catalog**:
  - URL: [https://www.tamilnadutourism.tn.gov.in/destinations/chennai](https://www.tamilnadutourism.tn.gov.in/destinations/chennai)
  - URL: [https://www.tamilnadutourism.tn.gov.in/destinations/mamallapuram](https://www.tamilnadutourism.tn.gov.in/destinations/mamallapuram)
- **Archaeological Survey of India (ASI Chennai Circle) Monuments Registry**:
  - URL: [https://asichennaicircle.gov.in/](https://asichennaicircle.gov.in/)
  - Verified coordinates, historical era, and timings for Fort St. George, Shore Temple, Pancha Rathas, and Pallava cave sanctuaries.

---

## 5. 🚌 Interstate Buses & State Transport Dataset

### Primary Sources:
- **State Express Transport Corporation (SETC Tamil Nadu) Public Timetables**:
  - Official Portal: [https://www.tnstc.in/](https://www.tnstc.in/)
- **APSRTC (Andhra Pradesh State Road Transport) Intercity Routes**:
  - Official Portal: [https://www.apsrtconline.in/](https://www.apsrtconline.in/)
- **KSRTC (Karnataka State Road Transport) Intercity Timetables**:
  - Official Portal: [https://www.ksrtc.in/](https://www.ksrtc.in/)
- **Kaggle Indian Bus Routes Dataset**:
  - URL: [https://www.kaggle.com/datasets/smitkiri/indian-bus-routes-dataset](https://www.kaggle.com/datasets/smitkiri/indian-bus-routes-dataset)
  - Dataset file: `intercity_buses_india.csv` (386 interstate bus services connecting Bangalore, Hyderabad, Vijayawada, Coimbatore, Madurai, Pondicherry, etc. to Chennai).

---

## 6. 🏨 Chennai Hotels & Accommodations Dataset

### Primary Sources:
- **Kaggle India Hotels Dataset**:
  - URL: [https://www.kaggle.com/datasets/PromptCloudHQ/hotels-in-india-dataset](https://www.kaggle.com/datasets/PromptCloudHQ/hotels-in-india-dataset)
  - URL: [https://www.kaggle.com/datasets/jiashenliu/hotel-booking-demand](https://www.kaggle.com/datasets/jiashenliu/hotel-booking-demand)
- **OpenStreetMap Tourism Accommodations**:
  - Filtered Chennai properties across 5 tiers: Backpacker Hostels, Budget (FabHotel/OYO/Treebo), Standard 3-Star, Premium 4-Star (GRT/Novotel/Raintree), Luxury 5-Star (ITC Grand Chola, Taj Connemara, The Leela Palace).
  - Dataset file: `chennai_hotels.csv` (88 verified properties with coordinates, room capacities, check-in 12:00/14:00 and check-out 11:00/12:00 policies).

---

## 7. 📍 All-India City Geocoordinates & Transit Hubs

### Primary Sources:
- **Kaggle Indian Cities & Pin Codes Database**:
  - URL: [https://www.kaggle.com/datasets/zed9941/cities-and-states-in-india](https://www.kaggle.com/datasets/zed9941/cities-and-states-in-india)
- **Census of India / Geonames India**:
  - URL: [https://download.geonames.org/export/dump/IN.zip](https://download.geonames.org/export/dump/IN.zip)
  - Dataset file: `city_coordinates.csv` (78 major transit hubs, IATA airport codes, state affiliations, and GPS coordinates).
