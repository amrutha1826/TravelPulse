const API_BASE = "http://localhost:8000/api";

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const GeoAPI = {
  getStates: () => fetchJson("/geo/states"),
  getCities: (state = "", search = "") => {
    const query = new URLSearchParams();
    if (state) query.append("state", state);
    if (search) query.append("search", search);
    return fetchJson(`/geo/cities?${query.toString()}`);
  },
  getCityPlaces: (cityId) => fetchJson(`/geo/cities/${cityId}/places`),
  getPlacePreview: (cityId, limit = 5) => fetchJson(`/geo/cities/${cityId}/places/preview?limit=${limit}`),
  searchPlaces: (q, cityId = "") => {
    const query = new URLSearchParams({ q });
    if (cityId) query.append("city_id", cityId);
    return fetchJson(`/geo/places/search?${query.toString()}`);
  },
};

export const TransportAPI = {
  getOperators: () => fetchJson("/transport/operators"),
  searchTransport: (searchParams) =>
    fetchJson("/transport/search", {
      method: "POST",
      body: JSON.stringify(searchParams),
    }),
};

export const ItineraryAPI = {
  getCategories: () => fetchJson("/itinerary/categories"),
  generateItinerary: (planParams) =>
    fetchJson("/itinerary/generate", {
      method: "POST",
      body: JSON.stringify(planParams),
    }),
  regenerateDay: (regenParams) =>
    fetchJson("/itinerary/regenerate-day", {
      method: "POST",
      body: JSON.stringify(regenParams),
    }),
  swapActivity: (swapParams) =>
    fetchJson("/itinerary/swap-activity", {
      method: "POST",
      body: JSON.stringify(swapParams),
    }),
};

export const HotelAPI = {
  searchHotels: (params) => {
    const query = new URLSearchParams();
    if (params.cityId) query.append("city_id", params.cityId);
    if (params.category && params.category !== "All") query.append("category", params.category);
    if (params.maxPrice) query.append("max_price", params.maxPrice);
    if (params.minRating) query.append("min_rating", params.minRating);
    if (params.sortBy) query.append("sort_by", params.sortBy);
    if (params.limit) query.append("limit", params.limit);
    return fetchJson(`/hotels/search?${query.toString()}`);
  },
};

export const BookingAPI = {
  createBooking: (bookingData) =>
    fetchJson("/bookings/create", {
      method: "POST",
      body: JSON.stringify(bookingData),
    }),
};
