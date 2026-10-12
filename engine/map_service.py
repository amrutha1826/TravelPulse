"""
Interactive Map Rendering Service for TravelPulse Platform.
Constructs dynamic PyDeck and geographic waypoint layers for day-wise itineraries,
stay locations, and sequence paths with color-coded markers and rich metadata.
"""
import pandas as pd
import pydeck as pdk

def build_interactive_map(active_itinerary, selected_hotel=None, dest_city_info=None):
    """
    Constructs dynamic PyDeck map layer with day-specific colors, POI pins, and route paths.
    Returns: (pdk.Deck object, pd.DataFrame of points)
    """
    map_points = []
    path_data = []

    day_colors = {
        1: [2, 132, 199, 230],    # Royal Blue
        2: [16, 185, 129, 230],   # Emerald Green
        3: [245, 158, 11, 230],   # Amber Orange
        4: [147, 51, 234, 230],   # Purple
        5: [225, 29, 72, 230],    # Rose
        6: [14, 165, 233, 230],   # Cyan
        7: [234, 88, 12, 230]     # Sunset Orange
    }

    # Add Hotel Marker
    hotel_coord = None
    if selected_hotel and "latitude" in selected_hotel and "longitude" in selected_hotel:
        hotel_coord = [float(selected_hotel["longitude"]), float(selected_hotel["latitude"])]
        map_points.append({
            "name": f"🏨 Hotel: {selected_hotel['name']}",
            "details": f"Area: {selected_hotel.get('area', 'Central')} | Rating: ⭐{selected_hotel.get('rating', 4.5)}/5.0",
            "lat": float(selected_hotel["latitude"]),
            "lon": float(selected_hotel["longitude"]),
            "color": [239, 68, 68, 255],  # Vivid Red
            "size": 26,
            "day": 0
        })

    # Add Activity POIs & Day Routes
    for d_num, d_data in (active_itinerary or {}).items():
        day_color = day_colors.get(d_num, [100, 116, 139, 230])
        day_coords = []
        if hotel_coord:
            day_coords.append(hotel_coord)

        for act in d_data.get("activities", []):
            poi = act.get("poi", {})
            if "latitude" in poi and "longitude" in poi:
                lat = float(poi["latitude"])
                lon = float(poi["longitude"])
                map_points.append({
                    "name": f"Day {d_num} [{act.get('time_slot', '')}]: {poi.get('name')}",
                    "details": f"Role: {act.get('activity_role')} | Category: {poi.get('category')} | Entry: ₹{poi.get('entry_fee_inr', 0)}",
                    "lat": lat,
                    "lon": lon,
                    "color": day_color,
                    "size": 18,
                    "day": d_num
                })
                day_coords.append([lon, lat])

        if hotel_coord and len(day_coords) > 1:
            day_coords.append(hotel_coord)

        if len(day_coords) >= 2:
            path_data.append({
                "path": day_coords,
                "color": day_color[:3] + [160],
                "day": d_num
            })

    # Fallback to destination center if no points
    if not map_points and dest_city_info:
        map_points.append({
            "name": f"📍 {dest_city_info.get('name')}",
            "details": f"State: {dest_city_info.get('state')} | Transit Hub",
            "lat": float(dest_city_info.get("latitude", 13.0827)),
            "lon": float(dest_city_info.get("longitude", 80.2707)),
            "color": [2, 132, 199, 240],
            "size": 22,
            "day": 0
        })

    if map_points:
        df_points = pd.DataFrame(map_points)
        center_lat = float(df_points["lat"].mean())
        center_lon = float(df_points["lon"].mean())

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11.8,
            pitch=35,
            bearing=0
        )

        layers = []
        # Path Layer for Itinerary Routes
        if path_data:
            df_paths = pd.DataFrame(path_data)
            layer_paths = pdk.Layer(
                "PathLayer",
                data=df_paths,
                get_path="path",
                get_color="color",
                width_scale=20,
                width_min_pixels=3,
                pickable=False
            )
            layers.append(layer_paths)

        # Scatterplot Layer for POI Pins
        layer_scatter = pdk.Layer(
            "ScatterplotLayer",
            data=df_points,
            get_position="[lon, lat]",
            get_color="color",
            get_radius=320,
            pickable=True,
            auto_highlight=True
        )
        layers.append(layer_scatter)

        deck = pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip={"html": "<b>{name}</b><br/><span>{details}</span>", "style": {"backgroundColor": "#0F172A", "color": "#FFFFFF", "fontSize": "12px", "padding": "8px", "borderRadius": "6px"}},
            map_style="mapbox://styles/mapbox/light-v10"
        )
        return deck, df_points

    return None, None
