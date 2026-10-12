"""
TravelPulse - Next-Gen Autonomous Trip & Transit Platform.
Complete, working, full-stack travel platform powered by indexed SQLite database,
strict multi-modal transit filtering, TravelPulse ranking & price breakdowns,
interactive day-wise itinerary customizer, DRL sequential policy, RAG vector retrieval & grounded review summarizer.
"""
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import json
import os
import sys
from datetime import datetime, date, timedelta

# Ensure root path is accessible
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from engine.rag_service import RAGService
from engine.transport_service import TransportSearchService
from engine.itinerary_service import ItineraryPlanningService
from engine.hotel_service import HotelSearchService
from engine.booking_service import BookingCheckoutService
from engine.nlu_chatbot import CustomNLUReplanner
from engine.chatbot import TripState
from engine.map_service import build_interactive_map


# Page Configuration
st.set_page_config(
    page_title="TravelPulse - Next-Gen Autonomous Trip & Transit Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom TravelPulse Brand CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .travelpulse-brand-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 40%, #0284C7 100%);
        color: white;
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.25);
    }
    
    .travelpulse-title { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 4px; }
    .travelpulse-subtitle { font-size: 1.05rem; opacity: 0.92; font-weight: 400; }
    
    .search-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .result-card {
        background: #ffffff;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 16px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .result-card:hover {
        border-color: #0284C7;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.12);
    }
    
    .badge-mode {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    .badge-flight { background: #E0F2FE; color: #0369A1; }
    .badge-train { background: #DCFCE7; color: #15803D; }
    .badge-bus { background: #FEF3C7; color: #B45309; }
    .badge-cab { background: #F3E8FF; color: #7E22CE; }
    
    .price-tag {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0F172A;
    }
    
    .itinerary-card {
        background: #F8FAFC;
        border-left: 4px solid #0284C7;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .hotel-card {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
        background: #FFFFFF;
    }
    
    .rag-review-box {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    
    .drl-badge {
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .places-preview-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 6px;
        margin-bottom: 12px;
        font-size: 0.88rem;
        color: #334155;
    }

    .place-tag {
        display: inline-block;
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 2px 8px;
        margin: 3px 4px 3px 0;
        font-size: 0.8rem;
        color: #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# Cache service instances
@st.cache_resource
def get_services():
    db = DatabaseManager()
    rag = RAGService(db)
    transport_svc = TransportSearchService(db, rag)
    itin_svc = ItineraryPlanningService(db, rag)
    hotel_svc = HotelSearchService(db)
    booking_svc = BookingCheckoutService(db)
    nlu_bot = CustomNLUReplanner()
    states = db.get_states()
    return db, rag, transport_svc, itin_svc, hotel_svc, booking_svc, nlu_bot, states

db, rag_service, transport_service, itinerary_service, hotel_service, booking_service, nlu_chatbot, STATES = get_services()

# Initialize Session State
if "trip_state" not in st.session_state:
    st.session_state.trip_state = TripState(origin_city="Ahmedabad", num_days=3, pace="Moderate", budget_per_day=3500)
if "active_dest_state" not in st.session_state:
    st.session_state.active_dest_state = "Tamil Nadu"
if "active_dest_city" not in st.session_state:
    st.session_state.active_dest_city = "Chennai"
if "active_dest_city_id" not in st.session_state:
    st.session_state.active_dest_city_id = "MAA"
if "selected_transport" not in st.session_state:
    st.session_state.selected_transport = None
if "selected_hotel" not in st.session_state:
    init_hotels = hotel_service.search_hotels(st.session_state.active_dest_city_id, limit=1)
    st.session_state.selected_hotel = init_hotels[0] if init_hotels else None
if "active_itinerary" not in st.session_state:
    st.session_state.active_itinerary = itinerary_service.generate_itinerary(
        destination_city_id=st.session_state.active_dest_city_id,
        num_days=3,
        pace="Moderate",
        selected_hotel=st.session_state.selected_hotel
    )
if "cart_items" not in st.session_state:
    st.session_state.cart_items = {}
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "⚡ **Welcome to TravelPulse Autonomous Trip Assistant!**\n\nI can dynamically modify your multi-modal transit, hotel stays, or day-wise activities. Try saying:\n- *'Plan it for 4 days'*\n- *'Exclude flights and show trains only'*\n- *'Focus only on Shopping and Beaches'*\n- *'Change hotel to Budget near Central'*\n- *'Make Day 1 more relaxed'*"}
    ]



# Top Brand Header
st.markdown("""
<div class="travelpulse-brand-header">
    <div class="travelpulse-title">⚡ TravelPulse — Next-Gen Autonomous Travel Platform</div>
    <div class="travelpulse-subtitle">Deep Reinforcement Learning (DRL) Core Policy • Local RAG Vector Search & Grounded Reviews • Pan-India Multi-Modal Transit</div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tabs = st.tabs([
    "✈️ Transport Search",
    "🏨 Hotels & Stays",
    "🗓️ Day-Wise Itinerary Planner",
    "🗺️ Interactive Route Map",
    "🛒 Booking Checkout",
    "🤖 Conversational Replanner",
    "📊 DRL Training Analytics"
])

# ==============================================================================
# TAB 1: TRANSPORT SEARCH (TRAVELPULSE FLIGHTS / TRAINS / BUSES / CABS)
# ==============================================================================
with tabs[0]:
    st.markdown("### 🔍 Find Flights, Trains, Buses & Cabs Across India")
    
    with st.container():
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        
        # Two-Step Selection Flow: State -> City
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("#### 📍 Origin Location")
            c_o1, c_o2 = st.columns(2)
            with c_o1:
                t_orig_state = st.selectbox("🗺️ Origin State:", STATES, index=STATES.index("Gujarat") if "Gujarat" in STATES else 0, key="trans_orig_state")
            orig_cities_list = db.get_cities_by_state(t_orig_state)
            orig_city_names = [c["name"] for c in orig_cities_list] if orig_cities_list else ["Ahmedabad"]
            with c_o2:
                orig_name = st.selectbox("🏙️ Origin City:", orig_city_names, key="trans_orig_city")
            
            orig_city_obj = next((c for c in orig_cities_list if c["name"] == orig_name), orig_cities_list[0] if orig_cities_list else None)
            orig_city_id = orig_city_obj["id"] if orig_city_obj else "AMD"
            
            # Place-level granularity preview for origin city
            orig_places = db.get_city_places_preview(orig_city_id, limit=4)
            if orig_places:
                st.caption(f"🏛️ **Attractions in {orig_name}:** " + ", ".join([p["name"] for p in orig_places]))

        with col_t2:
            st.markdown("#### 🏁 Destination Location")
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                t_dest_state = st.selectbox("🗺️ Destination State:", STATES, index=STATES.index("Tamil Nadu") if "Tamil Nadu" in STATES else 0, key="trans_dest_state")
            dest_cities_list = db.get_cities_by_state(t_dest_state)
            dest_city_names = [c["name"] for c in dest_cities_list] if dest_cities_list else ["Chennai"]
            with c_d2:
                dest_name = st.selectbox("🏙️ Destination City:", dest_city_names, key="trans_dest_city")
            
            dest_city_obj = next((c for c in dest_cities_list if c["name"] == dest_name), dest_cities_list[0] if dest_cities_list else None)
            dest_city_id = dest_city_obj["id"] if dest_city_obj else "MAA"

            # Place-level granularity preview for destination city
            dest_places = db.get_city_places_preview(dest_city_id, limit=4)
            if dest_places:
                st.caption(f"🏛️ **Attractions in {dest_name}:** " + ", ".join([p["name"] for p in dest_places]))

        col_t3, col_t4 = st.columns(2)
        with col_t3:
            dep_date = st.date_input("📅 Departure Date:", value=date.today() + timedelta(days=7), min_value=date.today(), key="trans_dep_date")
        with col_t4:
            travelers_count = st.number_input("👥 Travelers:", min_value=1, max_value=10, value=2, key="trans_pax_count")

        # Stage 2: Free-Text Search Box (Local RAG Vector Search)
        rag_trans_query = st.text_input("🔎 Free-Text Transit Preference (Powered by Local Vector RAG):", placeholder="e.g. 'cheap overnight sleeper bus with AC' or 'early morning superfast express train'")

        st.markdown("#### ⚡ Transport Mode Filter & Preferences (Stage 1 SQL Hard Filter)")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            use_flights = st.checkbox("✈️ Flights", value=True, key="chk_mode_flight")
        with col_m2:
            use_trains = st.checkbox("🚆 Trains (IRCTC)", value=True, key="chk_mode_train")
        with col_m3:
            use_buses = st.checkbox("🚌 Intercity Buses", value=True, key="chk_mode_bus")
        with col_m4:
            use_cabs = st.checkbox("🚖 Outstation Cabs", value=True, key="chk_mode_cab")
            
        selected_modes = []
        if use_flights: selected_modes.append("flight")
        if use_trains: selected_modes.append("train")
        if use_buses: selected_modes.append("bus")
        if use_cabs: selected_modes.append("cab")

        col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 1.5])
        with col_f1:
            sort_option = st.selectbox("📊 Sort By:", ["Cheapest First", "Fastest First", "Earliest Departure", "Best Value"], index=0, key="trans_sort_sel")
            sort_key_map = {"Cheapest First": "cheapest", "Fastest First": "fastest", "Earliest Departure": "earliest", "Best Value": "best_value"}
        with col_f2:
            dep_slot = st.selectbox("🕒 Departure Window:", ["Any Time", "Early Morning (00:00-06:00)", "Morning (06:00-12:00)", "Afternoon (12:00-18:00)", "Evening/Night (18:00-24:00)"], key="trans_dep_slot")
            window_map = {
                "Any Time": None,
                "Early Morning (00:00-06:00)": ("00:00", "06:00"),
                "Morning (06:00-12:00)": ("06:00", "12:00"),
                "Afternoon (12:00-18:00)": ("12:00", "18:00"),
                "Evening/Night (18:00-24:00)": ("18:00", "23:59")
            }
        with col_f3:
            max_price_budget = st.slider("💰 Max Fare per Person (₹):", min_value=500, max_value=25000, value=15000, step=500, key="trans_max_price")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # Search Execution (4-Stage Pipeline)
    results = transport_service.search_routes(
        origin_city_id=orig_city_id,
        dest_city_id=dest_city_id,
        selected_modes=selected_modes,
        max_price=max_price_budget,
        departure_window=window_map.get(dep_slot),
        sort_by=sort_key_map.get(sort_option, "cheapest"),
        free_text_query=rag_trans_query,
        include_connecting=True
    )

    st.markdown(f"#### 🎯 Results: {orig_name} ➔ {dest_name} ({results['total_count']} options found) <span class='drl-badge'>DRL Graph Policy</span> <span class='drl-badge'>RAG Review Grounded</span>", unsafe_allow_html=True)

    if results["total_count"] == 0:
        st.warning(f"⚠️ {results['empty_reason']}")
    else:
        for idx, route in enumerate(results["all_routes"][:20]):
            mode = route.get("transport_mode", "flight").lower()
            badge_class = f"badge-{mode}" if mode in ["flight", "train", "bus", "cab"] else "badge-flight"
            
            with st.container():
                st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
                r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([2.2, 2.5, 1.8, 1.8, 1.7])
                
                with r_col1:
                    st.markdown(f"<span class='badge-mode {badge_class}'>{route.get('logo_emoji', '🚀')} {route.get('transport_mode', 'Mode').upper()}</span>", unsafe_allow_html=True)
                    st.markdown(f"**{route.get('operator_name', 'Operator')}**")
                    st.caption(f"Service: `{route.get('service_number', 'N/A')}` | Class: {route.get('seat_class', 'Standard')}")
                    
                with r_col2:
                    st.markdown(f"### {route.get('departure_time', '00:00')} ➔ {route.get('arrival_time', '00:00')}")
                    st.caption(f"⏱️ **{route.get('duration_hours', 0)} hrs** | 📍 {route.get('route_type', 'Direct')} | 🌿 {route.get('carbon_kg', 30)} kg CO₂")
                    if route.get("via_city_name"):
                        st.info(f"Connecting via **{route.get('via_city_name')}** (Layover: 2.0h)")

                with r_col3:
                    st.markdown(f"**⭐ {route.get('operator_rating', 4.5)} / 5.0**")
                    amenities = route.get("amenities", [])
                    if amenities:
                        st.caption(" • ".join(amenities[:3]))

                with r_col4:
                    st.markdown(f"<div class='price-tag'>₹{route.get('total_fare_inr', 0):,}</div>", unsafe_allow_html=True)
                    st.caption(f"Base: ₹{route.get('base_fare_inr', 0):,} + Tax: ₹{route.get('tax_inr', 0):,}")
                    st.caption("✓ Refundable | Free cancellation")

                with r_col5:
                    if st.button("🛒 Select & Book", key=f"btn_book_route_{idx}", use_container_width=True):
                        st.session_state.selected_transport = route
                        st.session_state.cart_items["transport"] = route
                        st.success(f"✓ Added {route.get('transport_mode').title()} to cart!")
                        st.rerun()

                # Stage 4 Grounded Review Summary Expander
                op_summary = route.get("operator_review_summary", {})
                op_name = route.get("operator_name", "Carrier")
                if op_summary and op_summary.get("has_reviews"):
                    rev_count = op_summary.get("total_reviews_analyzed", len(op_summary.get("retrieved_reviews", [])))
                    avg_r = op_summary.get("average_rating", route.get("operator_rating", "4.5"))
                    with st.expander(f"📝 Stage 4 Grounded Reviews: {op_name} ({avg_r}★ · {rev_count} verified reviews)", expanded=False):
                        st.markdown(f"**Traveler Consensus:** {op_summary.get('summary')}")
                        col_p, col_c = st.columns(2)
                        with col_p:
                            st.markdown("**✅ Grounded Pros:**")
                            for pro in op_summary.get("pros", []):
                                st.markdown(f"- {pro}")
                        with col_c:
                            st.markdown("**⚠️ Grounded Cons / Watch-outs:**")
                            for con in op_summary.get("cons", []):
                                st.markdown(f"- {con}")
                        if op_summary.get("retrieved_reviews"):
                            st.markdown("**💬 Retrieved Verified Reviews:**")
                            for rr in op_summary.get("retrieved_reviews", []):
                                st.caption(f"⭐ **{rr.get('rating')}★** — *\"{rr.get('text')}\"* ({rr.get('user')}, {rr.get('date', '2026-02')})")
                else:
                    with st.expander(f"📝 Stage 4 Reviews: {op_name}", expanded=False):
                        st.info(f"ℹ️ No reviews available for {op_name} in the verified database.")

                # If connecting route, also display Leg 2 carrier review summary
                if route.get("route_type") == "Connecting":
                    l2_sum = route.get("leg2_review_summary", {})
                    l2_name = route.get("leg2_operator", "Connecting Carrier")
                    if l2_sum and l2_sum.get("has_reviews"):
                        l2_rev_count = l2_sum.get("total_reviews_analyzed", len(l2_sum.get("retrieved_reviews", [])))
                        l2_avg_r = l2_sum.get("average_rating", "4.5")
                        with st.expander(f"📝 Stage 4 Grounded Reviews (Connecting Leg 2): {l2_name} ({l2_avg_r}★ · {l2_rev_count} verified reviews)", expanded=False):
                            st.markdown(f"**Traveler Consensus:** {l2_sum.get('summary')}")
                            col_p2, col_c2 = st.columns(2)
                            with col_p2:
                                st.markdown("**✅ Grounded Pros:**")
                                for pro in l2_sum.get("pros", []):
                                    st.markdown(f"- {pro}")
                            with col_c2:
                                st.markdown("**⚠️ Grounded Cons / Watch-outs:**")
                                for con in l2_sum.get("cons", []):
                                    st.markdown(f"- {con}")
                            if l2_sum.get("retrieved_reviews"):
                                st.markdown("**💬 Retrieved Verified Reviews:**")
                                for rr in l2_sum.get("retrieved_reviews", []):
                                    st.caption(f"⭐ **{rr.get('rating')}★** — *\"{rr.get('text')}\"* ({rr.get('user')}, {rr.get('date', '2026-02')})")
                    else:
                        with st.expander(f"📝 Stage 4 Reviews (Connecting Leg 2): {l2_name}", expanded=False):
                            st.info(f"ℹ️ No reviews available for {l2_name} in the verified database.")

                st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# TAB 2: HOTELS & ACCOMMODATIONS (TRAVELPULSE STAYS)
# ==============================================================================
with tabs[1]:
    st.markdown("### 🏨 Hotels & Accommodations in India")
    
    # Two-Step Selection: State -> City
    col_h_st, col_h_ct, col_h_srch2, col_h_srch3, col_h_srch4 = st.columns([1.3, 1.3, 1.0, 1.1, 1.1])
    with col_h_st:
        hotel_state = st.selectbox("🗺️ State:", STATES, index=STATES.index(st.session_state.active_dest_state) if st.session_state.active_dest_state in STATES else 0, key="htl_state_sel")
    hotel_cities_list = db.get_cities_by_state(hotel_state)
    hotel_city_names = [c["name"] for c in hotel_cities_list] if hotel_cities_list else ["Chennai"]
    with col_h_ct:
        hotel_city_name = st.selectbox("🏙️ City:", hotel_city_names, index=hotel_city_names.index(st.session_state.active_dest_city) if st.session_state.active_dest_city in hotel_city_names else 0, key="htl_city_sel")
    with col_h_srch2:
        hotel_tier = st.selectbox("⭐ Property Tier:", ["Any Tier", "Luxury", "Standard", "Budget", "Hostel"], key="htl_tier_sel")
    with col_h_srch3:
        hotel_sort = st.selectbox("📊 Sort By:", ["Top Rated", "Price: Low to High", "Price: High to Low", "Most Popular"], key="htl_sort_sel")
        hotel_sort_map = {"Top Rated": "rating", "Price: Low to High": "price_asc", "Price: High to Low": "price_desc", "Most Popular": "popularity"}
    with col_h_srch4:
        hotel_budget = st.slider("💰 Max Nightly Rate (₹):", min_value=500, max_value=25000, value=8000, step=500, key="htl_budget_slider")

    target_hotel_city_id = next((c["id"] for c in hotel_cities_list if c["name"] == hotel_city_name), "MAA")
    hotels_found = hotel_service.search_hotels(
        city_id=target_hotel_city_id,
        category=hotel_tier,
        max_price=hotel_budget,
        sort_by=hotel_sort_map.get(hotel_sort, "rating")
    )

    st.markdown(f"#### 🏨 Available Properties in {hotel_city_name}, {hotel_state} ({len(hotels_found)} found)")

    for h_idx, h in enumerate(hotels_found[:15]):
        with st.container():
            st.markdown('<div class="hotel-card">', unsafe_allow_html=True)
            hc1, hc2, hc3, hc4 = st.columns([1.5, 3.0, 1.8, 1.7])
            with hc1:
                st.image(h.get("image_url", "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=400&q=80"), use_container_width=True)
            with hc2:
                st.markdown(f"### {h.get('name')}")
                st.markdown(f"📍 **{h.get('area')}** ({h.get('zone', 'Central')}) | ⭐ **{h.get('rating')} / 5.0** ({h.get('num_reviews')} verified reviews)")
                st.caption(f"🕒 Check-In: **{h.get('check_in_time', '14:00')}** | Check-Out: **{h.get('check_out_time', '11:00')}**")
                amenities = h.get("amenities", [])
                st.caption(" • ".join(amenities[:4]))
            with hc3:
                st.markdown(f"<div class='price-tag'>₹{h.get('price_per_night_inr', 0):,}</div>", unsafe_allow_html=True)
                st.caption(f"+ ₹{h.get('tax_per_night_inr', 0):,} taxes & service fees")
                st.caption("✓ Free WiFi & Breakfast")
            with hc4:
                if st.button("🛎️ Select Hotel", key=f"btn_htl_{h_idx}", use_container_width=True):
                    st.session_state.selected_hotel = h
                    st.session_state.cart_items["hotel"] = h
                    st.success(f"✓ Selected {h.get('name')}!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# TAB 3: DAY-WISE ITINERARY PLANNER (DRL POLICY + RAG VECTOR SEARCH & REVIEWS)
# ==============================================================================
with tabs[2]:
    st.markdown("### 🗓️ Day-Wise Sightseeing & Local Itinerary Planner")
    
    with st.container():
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        
        # Two-Step Selection Flow: State -> City
        col_p_st, col_p_ct, col_p2, col_p3, col_p4 = st.columns([1.3, 1.3, 0.9, 1.0, 1.2])
        with col_p_st:
            itin_state = st.selectbox("🗺️ Destination State:", STATES, index=STATES.index(st.session_state.active_dest_state) if st.session_state.active_dest_state in STATES else 0, key="itin_state_sel")
        
        itin_cities_list = db.get_cities_by_state(itin_state)
        itin_city_names = [c["name"] for c in itin_cities_list] if itin_cities_list else ["Chennai"]
        
        with col_p_ct:
            itin_city = st.selectbox("🏙️ Destination City:", itin_city_names, index=itin_city_names.index(st.session_state.active_dest_city) if st.session_state.active_dest_city in itin_city_names else 0, key="itin_city_sel")
            
        dest_city_obj = next((c for c in itin_cities_list if c["name"] == itin_city), itin_cities_list[0] if itin_cities_list else None)
        target_cid = dest_city_obj["id"] if dest_city_obj else "MAA"

        with col_p2:
            itin_days = st.slider("🗓️ Days:", min_value=1, max_value=7, value=st.session_state.trip_state.num_days, key="itin_days_slider")
        with col_p3:
            itin_pace = st.select_slider("⚡ Pacing:", options=["Relaxed", "Moderate", "Packed"], value=st.session_state.trip_state.pace, key="itin_pace_slider")
        with col_p4:
            itin_budget = st.number_input("💰 Daily Budget (₹):", min_value=1000, max_value=50000, value=st.session_state.trip_state.budget_per_day, step=500, key="itin_budget_input")

        # Place-Level Granularity Display
        city_all_places = db.get_places_for_city(target_cid, limit=100)
        st.markdown(f'<div class="places-preview-box"><strong>🏛️ Specific Places & Attractions in {itin_city} ({len(city_all_places)} curated locations):</strong><br/>', unsafe_allow_html=True)
        place_badge_html = "".join([f'<span class="place-tag">📍 {p["name"]} ({p["category"]})</span>' for p in city_all_places[:14]])
        if len(city_all_places) > 14:
            place_badge_html += f'<span class="place-tag">+ {len(city_all_places)-14} more places</span>'
        st.markdown(place_badge_html + '</div>', unsafe_allow_html=True)

        # Stage 2: Free-Text Natural Language Query for Itinerary
        rag_itin_query = st.text_input("🔎 Natural Language Travel Query (Local Vector Search):", placeholder="e.g. 'historical landmarks, sea-breeze walks and authentic South Indian filter coffee'", key="itin_rag_query")

        st.markdown("#### 🎯 Interest Categories & Purpose (Stage 1 SQL Hard Filter)")
        categories_selected = st.multiselect(
            "Select Sightseeing Interests (Strictly Respected):",
            options=["Shopping & Markets", "Beaches & Coastline", "Food, Messes & Cafes", "Heritage & History", "Temples & Spiritual", "Parks & Nature", "Entertainment & Theme Parks", "Museums & Arts"],
            default=["Shopping & Markets", "Beaches & Coastline", "Food, Messes & Cafes", "Heritage & History"],
            key="itin_cat_multisel"
        )

        st.markdown("#### ⏰ Daily Available Time Window")
        time_presets = [
            "Standard Full Day (09:00 - 21:00)",
            "Late Start / Relaxed (10:30 - 20:30)",
            "Early Bird (07:30 - 22:00)",
            "Afternoon & Evening (14:00 - 23:00)",
            "Custom Daily Hours"
        ]
        col_t1, col_t2, col_t3 = st.columns([1.5, 1.0, 1.0])
        with col_t1:
            sel_preset = st.selectbox("🕒 Time Preset:", time_presets, index=0, key="itin_time_preset")
        
        if "09:00 - 21:00" in sel_preset:
            def_start, def_end = "09:00", "21:00"
        elif "10:30 - 20:30" in sel_preset:
            def_start, def_end = "10:30", "20:30"
        elif "07:30 - 22:00" in sel_preset:
            def_start, def_end = "07:30", "22:00"
        elif "14:00 - 23:00" in sel_preset:
            def_start, def_end = "14:00", "23:00"
        else:
            def_start, def_end = "09:00", "21:00"

        time_options = [
            "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
            "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
            "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"
        ]

        with col_t2:
            itin_start_time = st.selectbox("🌅 Daily Start Time:", time_options, index=time_options.index(def_start) if def_start in time_options else 6, key="itin_start_time_sel")
        with col_t3:
            itin_end_time = st.selectbox("🌙 Daily End Time:", time_options, index=time_options.index(def_end) if def_end in time_options else 30, key="itin_end_time_sel")

        custom_day_windows = {}
        with st.expander("⚙️ Customize Specific Hours Per Day (e.g. Flight Arrival / Train Departure)", expanded=False):
            st.caption("Override start/end available hours for specific days if your arrival or departure times differ.")
            for d in range(1, itin_days + 1):
                c_d1, c_d2, c_d3 = st.columns([1, 1.5, 1.5])
                with c_d1:
                    st.markdown(f"**Day {d}:**")
                with c_d2:
                    d_start = st.selectbox(f"Day {d} Start", time_options, index=time_options.index(itin_start_time), key=f"d_start_{d}")
                with c_d3:
                    d_end = st.selectbox(f"Day {d} End", time_options, index=time_options.index(itin_end_time), key=f"d_end_{d}")
                custom_day_windows[d] = (d_start, d_end)

        # Persistent Always-Visible Generate Button (Fixes Bug 2)
        if st.button("🚀 Generate Autonomous DRL Multi-Day Itinerary", type="primary", use_container_width=True):
            st.session_state.active_dest_state = itin_state
            st.session_state.active_dest_city = itin_city
            st.session_state.active_dest_city_id = target_cid

            # Re-select top hotel for new city if not already matched
            city_hotels = hotel_service.search_hotels(target_cid, limit=1)
            st.session_state.selected_hotel = city_hotels[0] if city_hotels else None

            st.session_state.active_itinerary = itinerary_service.generate_itinerary(
                destination_city_id=target_cid,
                num_days=itin_days,
                pace=itin_pace,
                categories=categories_selected,
                budget_per_day=itin_budget,
                selected_hotel=st.session_state.selected_hotel,
                daily_start_time=itin_start_time,
                daily_end_time=itin_end_time,
                day_time_windows=custom_day_windows,
                free_text_query=rag_itin_query
            )
            st.session_state.trip_state.num_days = itin_days
            st.session_state.trip_state.pace = itin_pace
            st.session_state.trip_state.daily_start_time = itin_start_time
            st.session_state.trip_state.daily_end_time = itin_end_time
            st.session_state.trip_state.day_time_windows = custom_day_windows
            st.success(f"✓ Generated DRL-optimized {itin_days}-day itinerary for {itin_city}, {itin_state} ({itin_start_time} ➔ {itin_end_time})!")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Render Day-Wise Itinerary with Interactive Customization
    place_options_map = {p["id"]: f"{p['name']} ({p['category']})" for p in city_all_places}
    total_trip_cost = 0.0

    st.markdown(f"#### 📅 Active Itinerary for **{st.session_state.active_dest_city}, {st.session_state.active_dest_state}**")

    for day_num, day_data in st.session_state.active_itinerary.items():
        total_trip_cost += day_data.get("estimated_day_cost_inr", 0)
        
        st_badge = day_data.get("available_start_time", "09:00")
        et_badge = day_data.get("available_end_time", "21:00")
        hrs_badge = day_data.get("available_hours", 12.0)

        with st.expander(f"📅 **Day {day_num}: {day_data.get('theme_title')}** — 🕒 Available: {st_badge} ➔ {et_badge} ({hrs_badge} hrs) | 💰 Est. Cost: ₹{day_data.get('estimated_day_cost_inr'):,} | 🚗 Travel: {day_data.get('total_day_distance_km')} km", expanded=True):
            
            # Action to regenerate only this specific day via DRL Policy re-invocation
            col_d_act1, col_d_act2 = st.columns([3, 1])
            with col_d_act2:
                if st.button(f"🔄 Regenerate Day {day_num} Only", key=f"btn_regen_day_{day_num}", use_container_width=True):
                    st.session_state.active_itinerary = itinerary_service.regenerate_single_day(
                        st.session_state.active_itinerary,
                        destination_city_id=st.session_state.active_dest_city_id,
                        day_num=day_num,
                        pace=itin_pace,
                        categories=categories_selected,
                        selected_hotel=st.session_state.selected_hotel,
                        daily_start_time=st_badge,
                        daily_end_time=et_badge
                    )
                    st.success(f"✓ Regenerated Day {day_num} independently within {st_badge} - {et_badge} via DRL Policy!")
                    st.rerun()

            for a_idx, act in enumerate(day_data.get("activities", [])):
                poi = act.get("poi", {})
                
                st.markdown(f"""
                <div style="background: #FFFFFF; border-left: 4px solid #0284C7; border-radius: 8px; padding: 14px; margin-bottom: 6px; border: 1px solid #E2E8F0;">
                    <strong>🕒 {act.get('time_slot')}</strong> — <span style="font-weight:700; color:#0284C7;">{act.get('activity_role')}</span>: <strong>{poi.get('name')}</strong><br>
                    <span style="color:#4B5563; font-size:0.9rem;">📍 {poi.get('area', 'Central')} | ⭐ {poi.get('rating', 4.5)}/5.0 | 🚗 Transit: {act.get('travel_from_prev', {}).get('distance_km', 0)} km ({act.get('travel_from_prev', {}).get('suggested_mode', 'Auto')}) | 💰 Est. Cost: ₹{act.get('estimated_activity_cost_inr', 0):,}</span><br>
                    <span style="font-size:0.85rem; color:#64748B;">{poi.get('description', '')}</span>
                </div>
                """, unsafe_allow_html=True)

                # Stage 4: Grounded Review Summary for this specific POI
                act_rev = act.get("review_summary", {})
                if act_rev and act_rev.get("has_reviews"):
                    act_rev_count = act_rev.get("total_reviews_analyzed", len(act_rev.get("retrieved_reviews", [])))
                    act_avg_r = act_rev.get("average_rating", poi.get("rating", 4.5))
                    with st.expander(f"📝 Verified Reviews & Grounded Pros/Cons for {poi.get('name')} ({act_avg_r}★ · {act_rev_count} reviews)", expanded=False):
                        st.markdown(f"**Traveler Consensus:** {act_rev.get('summary')}")
                        col_ap, col_ac = st.columns(2)
                        with col_ap:
                            st.markdown("**✅ Grounded Pros:**")
                            for pro in act_rev.get("pros", []):
                                st.markdown(f"- {pro}")
                        with col_ac:
                            st.markdown("**⚠️ Grounded Cons / Watch-outs:**")
                            for con in act_rev.get("cons", []):
                                st.markdown(f"- {con}")
                        if act_rev.get("retrieved_reviews"):
                            st.markdown("**💬 Retrieved Verified Reviews:**")
                            for rr in act_rev.get("retrieved_reviews", []):
                                st.caption(f"⭐ **{rr.get('rating')}★** — *\"{rr.get('text')}\"* ({rr.get('user')}, {rr.get('date', '2026-02')})")
                else:
                    with st.expander(f"📝 Verified Reviews for {poi.get('name')}", expanded=False):
                        st.info(f"ℹ️ No reviews available for {poi.get('name')} in verified database.")

                # Customizer controls for activity swapping
                with st.container():
                    c_act1, c_act2 = st.columns([3, 1])
                    with c_act1:
                        new_swap_id = st.selectbox(
                            f"Swap Activity {a_idx+1} with alternative place:",
                            options=list(place_options_map.keys()),
                            format_func=lambda x: place_options_map.get(x, x),
                            key=f"sel_swap_{day_num}_{a_idx}"
                        )
                    with c_act2:
                        if st.button("🔁 Swap Place", key=f"btn_swap_{day_num}_{a_idx}", use_container_width=True):
                            st.session_state.active_itinerary = itinerary_service.swap_activity(
                                st.session_state.active_itinerary,
                                day_num=day_num,
                                activity_idx=a_idx,
                                new_place_id=new_swap_id
                            )
                            st.success("✓ Swapped activity!")
                            st.rerun()

    # Dynamic Embedded Map in Itinerary Tab (Fixes Bug 4: Map Re-renders per Selected Plan)
    st.markdown("#### 🗺️ Plan Route & Waypoint Map")
    deck_obj, df_pts = build_interactive_map(
        st.session_state.active_itinerary,
        st.session_state.selected_hotel,
        dest_city_info=dest_city_obj
    )
    if deck_obj:
        st.pydeck_chart(deck_obj, key=f"deck_itin_map_{st.session_state.active_dest_city_id}_{len(df_pts)}")
    else:
        st.info("Select or generate a plan to visualize route waypoints.")

    # Stage 4 Plan Review Digest Expander
    sample_day = next(iter(st.session_state.active_itinerary.values()), {})
    plan_digest = sample_day.get("plan_review_summary", {})
    with st.expander("📚 Stage 4: Grounded Review Digest for Entire Itinerary", expanded=False):
        if plan_digest and plan_digest.get("has_reviews") and plan_digest.get("grounded_digest"):
            st.markdown(f"**Synthesized from {plan_digest.get('total_citations', 0)} verified visitor reviews across {plan_digest.get('total_places_reviewed', 0)} attractions:**")
            for item in plan_digest.get("grounded_digest", []):
                st.markdown(f"**🏛️ {item['poi_name']}** ({item.get('average_rating', '4.5')}★ · {item.get('review_count', 0)} citations)")
                for q in item["quotes"]:
                    st.caption(f"💬 {q}")
            if plan_digest.get("unreviewed_places"):
                st.markdown("---")
                st.caption("ℹ️ **Places with no reviews in database:** " + ", ".join([p["poi_name"] for p in plan_digest["unreviewed_places"]]))
        else:
            st.info("ℹ️ No reviews available for the attractions in this itinerary.")

# ==============================================================================
# TAB 4: INTERACTIVE ROUTE MAP (PYDECK DYNAMIC RENDERER)
# ==============================================================================
with tabs[3]:
    st.markdown(f"### 🗺️ Interactive Destination Map for **{st.session_state.active_dest_city}, {st.session_state.active_dest_state}**")
    st.caption("Visualizing day-wise activity pins, route sequence trajectories, and stay location. Updates automatically with every plan generation or activity swap.")

    # Legend
    st.markdown("""
    <div style="display: flex; gap: 16px; margin-bottom: 14px; flex-wrap: wrap;">
        <span>🔴 <strong style="color:#DC2626;">Hotel / Stay</strong></span>
        <span>🔵 <strong style="color:#0284C7;">Day 1 Places</strong></span>
        <span>🟢 <strong style="color:#10B981;">Day 2 Places</strong></span>
        <span>🟠 <strong style="color:#F59E0B;">Day 3 Places</strong></span>
        <span>🟣 <strong style="color:#9333EA;">Day 4+ Places</strong></span>
    </div>
    """, unsafe_allow_html=True)

    deck_map_tab, df_map_tab = build_interactive_map(
        st.session_state.active_itinerary,
        st.session_state.selected_hotel,
        dest_city_info=db.get_city_by_id(st.session_state.active_dest_city_id)
    )

    if deck_map_tab and df_map_tab is not None:
        st.pydeck_chart(deck_map_tab, key=f"deck_tab_map_{st.session_state.active_dest_city_id}_{len(df_map_tab)}")
        
        # Waypoints Data Table
        with st.expander("📍 View All Route Waypoints & Coordinates", expanded=False):
            st.dataframe(
                df_map_tab[["name", "details", "lat", "lon", "day"]],
                column_config={
                    "name": "Location & Schedule",
                    "details": "Activity Metadata",
                    "lat": "Latitude",
                    "lon": "Longitude",
                    "day": "Day #"
                },
                use_container_width=True
            )
    else:
        st.info("No location waypoints available to display.")

# ==============================================================================
# TAB 5: BOOKING CHECKOUT (TRAVELPULSE VOUCHER)
# ==============================================================================
with tabs[4]:
    st.markdown("### 🛒 Booking Checkout & Voucher Generation")
    
    col_c1, col_c2 = st.columns([1.8, 1.2])
    
    with col_c1:
        st.markdown("#### 📋 Selected Trip Summary")
        if st.session_state.selected_transport:
            t = st.session_state.selected_transport
            st.info(f"✈️ **Transport:** {t.get('transport_mode').title()} — {t.get('operator_name')} ({t.get('departure_time')} ➔ {t.get('arrival_time')}) — ₹{t.get('total_fare_inr'):,}")
            t_rev = t.get("operator_review_summary", {})
            if t_rev and t_rev.get("has_reviews"):
                st.caption(f"⭐ **Carrier Verified Reputation:** {t_rev.get('average_rating', '4.5')}★ based on {t_rev.get('total_reviews_analyzed', 0)} verified traveler reviews — *{t_rev.get('summary')}*")
            else:
                st.caption(f"ℹ️ Carrier reviews: No reviews available for {t.get('operator_name')} in verified database.")
        else:
            st.caption("No transport selected yet.")

        if st.session_state.selected_hotel:
            h = st.session_state.selected_hotel
            st.info(f"🏨 **Hotel:** {h.get('name')} ({h.get('category')}) — ₹{h.get('price_per_night_inr'):,}/night")
        else:
            st.caption("No hotel selected yet.")

        st.markdown(f"🗓️ **Itinerary:** {len(st.session_state.active_itinerary)} Days planned for **{st.session_state.active_dest_city}** (Est. Activity & Transit: ₹{sum(d.get('estimated_day_cost_inr', 0) for d in st.session_state.active_itinerary.values()):,})")

        st.markdown("#### 👤 Primary Traveler Details")
        u_name = st.text_input("Full Name:", value="Aarav Sharma", key="book_user_name")
        u_email = st.text_input("Email Address:", value="aarav.sharma@example.com", key="book_user_email")
        u_phone = st.text_input("Phone Number:", value="+91 9876543210", key="book_user_phone")

    with col_c2:
        st.markdown("#### 💳 Price Breakdown")
        trans_cost = st.session_state.selected_transport.get("total_fare_inr", 0) if st.session_state.selected_transport else 0
        hotel_cost = (st.session_state.selected_hotel.get("price_per_night_inr", 0) * len(st.session_state.active_itinerary)) if st.session_state.selected_hotel else 0
        itin_cost = sum(d.get("estimated_day_cost_inr", 0) for d in st.session_state.active_itinerary.values())
        total_trip_val = trans_cost + hotel_cost + itin_cost

        st.markdown(f"""
        - Transport Total: **₹{trans_cost:,}**
        - Hotel Total ({len(st.session_state.active_itinerary)} nights): **₹{hotel_cost:,}**
        - Sightseeing & Local Transit: **₹{itin_cost:,}**
        ---
        ### Total Amount: **₹{total_trip_val:,}**
        """)

        if st.button("💳 Confirm Booking & Generate Voucher", type="primary", use_container_width=True, key="btn_confirm_checkout"):
            pnr = db.create_booking(
                user_name=u_name,
                user_email=u_email,
                user_phone=u_phone,
                booking_type="full_trip",
                item_details={
                    "transport": st.session_state.selected_transport,
                    "hotel": st.session_state.selected_hotel,
                    "itinerary_days": len(st.session_state.active_itinerary),
                    "destination": st.session_state.active_dest_city
                },
                total_amount=total_trip_val
            )
            st.success(f"🎉 Booking Confirmed! Your TravelPulse PNR is **{pnr}**")
            st.balloons()

# ==============================================================================
# TAB 6: CONVERSATIONAL REPLANNER (NLU CHATBOT)
# ==============================================================================
with tabs[5]:
    st.markdown("### 🤖 Conversational AI Replanner (100% Offline NLU)")
    st.caption("Interact naturally with the assistant to modify trip duration, interest categories, time windows, or transport.")
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("Ask to modify your trip (e.g. 'plan from 10 am to 6 pm', 'change days to 4', 'only shopping')..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Process with custom offline NLU
        reply = nlu_chatbot.process_query(
            user_prompt,
            st.session_state.trip_state,
            st.session_state.selected_hotel,
            itinerary_service,
            hotel_service
        )
        
        # Update active itinerary if replanned
        if reply.get("new_itinerary"):
            st.session_state.active_itinerary = reply["new_itinerary"]

        bot_reply = reply.get("reply", "I have updated your preferences.")
        st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

# ==============================================================================
# TAB 7: DRL TRAINING ANALYTICS
# ==============================================================================
with tabs[6]:
    st.markdown("### 📊 Deep Reinforcement Learning (DRL) Training Analytics")
    st.caption("Convergence curves and performance metrics for the Double-DQN Multi-Modal Route Agent and PPO Itinerary Policy.")

    col_dr1, col_dr2 = st.columns(2)
    with col_dr1:
        st.markdown("#### 🚄 Multi-Modal Route DQN Policy")
        route_curve_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training", "plots", "route_training_curve.png")
        if os.path.exists(route_curve_path):
            st.image(route_curve_path, caption="DQN Route Agent Training Curve (Reward Convergence)", use_container_width=True)
        else:
            st.info("Route training curve will appear after running training/train_route_agent.py")

    with col_dr2:
        st.markdown("#### 🗓️ Intra-City Itinerary PPO Policy")
        itin_curve_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training", "plots", "itinerary_training_curve.png")
        if os.path.exists(itin_curve_path):
            st.image(itin_curve_path, caption="PPO Itinerary Agent Training Curve (Diversity & Time Optimization)", use_container_width=True)
        else:
            st.info("Itinerary training curve will appear after running training/train_itinerary_agent.py")
