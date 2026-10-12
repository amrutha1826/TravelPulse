import React, { useState, useEffect } from "react";
import { GeoAPI, HotelAPI } from "../services/api";
import GroundedReviewSummary from "./GroundedReviewSummary";
import {
  Hotel,
  Search,
  Star,
  MapPin,
  ShieldCheck,
  Check
} from "./Icons";

export default function HotelSearch({ onSelectForBooking }) {
  const [states, setStates] = useState([]);
  const [destState, setDestState] = useState("");
  const [destCities, setDestCities] = useState([]);
  const [destCityId, setDestCityId] = useState("");
  const [destSearch, setDestSearch] = useState("");

  const [category, setCategory] = useState("All");
  const [maxPrice, setMaxPrice] = useState(10000);
  const [minRating, setMinRating] = useState(3.5);
  const [sortBy, setSortBy] = useState("rating");

  const [loading, setLoading] = useState(false);
  const [hotels, setHotels] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    GeoAPI.getStates()
      .then((data) => {
        setStates(data);
        if (data.length > 0) {
          const tn = data.find((s) => s.toLowerCase().includes("tamil")) || data[0];
          setDestState(tn);
        }
      })
      .catch((err) => console.error("Error fetching states:", err));
  }, []);

  useEffect(() => {
    if (!destState) return;
    GeoAPI.getCities(destState)
      .then((cities) => {
        setDestCities(cities);
        if (cities.length > 0) {
          setDestCityId(cities[0].id);
        }
      })
      .catch((err) => console.error("Error fetching cities:", err));
  }, [destState]);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!destCityId) {
      setError("Please select a city.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await HotelAPI.searchHotels({
        cityId: destCityId,
        category: category !== "All" ? category : undefined,
        maxPrice: maxPrice,
        minRating: minRating,
        sortBy: sortBy,
        limit: 30,
      });
      setHotels(data);
    } catch (err) {
      setError(err.message || "Failed to search hotels.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Search Bar Card */}
      <div className="search-card">
        <form onSubmit={handleSearch}>
          <div className="search-grid">
            {/* State */}
            <div className="form-group">
              <label className="form-label">Destination State</label>
              <select
                className="form-select"
                value={destState}
                onChange={(e) => setDestState(e.target.value)}
              >
                {states.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            {/* City */}
            <div className="form-group">
              <label className="form-label">City</label>
              <input
                type="text"
                className="form-input"
                style={{ padding: "0.25rem 0.5rem", fontSize: "0.8rem", marginBottom: "0.25rem" }}
                placeholder="Type to filter city..."
                value={destSearch}
                onChange={(e) => setDestSearch(e.target.value)}
              />
              <select
                className="form-select"
                value={destCityId}
                onChange={(e) => setDestCityId(e.target.value)}
              >
                {destCities
                  .filter((c) => !destSearch || c.name.toLowerCase().includes(destSearch.toLowerCase()))
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
              </select>
            </div>

            {/* Sort */}
            <div className="form-group">
              <label className="form-label">Sort By</label>
              <select
                className="form-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="rating">Guest Rating (Highest first)</option>
                <option value="price_asc">Price (Lowest first)</option>
                <option value="price_desc">Price (Highest first)</option>
              </select>
            </div>

            {/* Search Button */}
            <div className="form-group">
              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
                style={{ height: "46px" }}
              >
                <Search style={{ width: "18px", height: "18px" }} />
                <span>{loading ? "Searching..." : "Search Stays"}</span>
              </button>
            </div>
          </div>

          {/* Tier & Filter Chips */}
          <div
            style={{
              marginTop: "1.25rem",
              paddingTop: "1rem",
              borderTop: "1px solid #e2e8f0",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "1rem",
            }}
          >
            {/* Hotel Tier */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "#64748b" }}>
                TIER:
              </span>
              {["All", "Luxury", "Standard", "Budget", "Hostel"].map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setCategory(t)}
                  className={`filter-pill-btn ${category === t ? "active" : ""}`}
                >
                  {t}
                </button>
              ))}
            </div>

            {/* Price Slider */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "#64748b" }}>
                MAX PRICE: ₹{maxPrice.toLocaleString()}
              </span>
              <input
                type="range"
                min="500"
                max="25000"
                step="500"
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
                style={{ accentColor: "#006ce4", width: "130px" }}
              />
            </div>

            {/* Min Rating */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "#64748b" }}>
                MIN RATING:
              </span>
              {[3.0, 3.5, 4.0, 4.5].map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setMinRating(r)}
                  className={`filter-pill-btn ${minRating === r ? "active" : ""}`}
                >
                  {r}★
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>

      {/* Error state */}
      {error && (
        <div style={{ padding: "1rem", borderRadius: "8px", background: "#fee2e2", border: "1px solid #fca5a5", color: "#b91c1c", marginBottom: "1.5rem" }}>
          <strong>Error: </strong> {error}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div style={{ padding: "3rem", textAlign: "center", background: "#fff", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>🏨</div>
          <h3 style={{ fontSize: "1.1rem", color: "#1e293b", fontWeight: "700" }}>
            Searching Verified Hotels & Grounded TripAdvisor Reviews...
          </h3>
          <p style={{ color: "#64748b", fontSize: "0.85rem" }}>
            Matching accommodations by star tier and price constraints
          </p>
        </div>
      )}

      {/* Results */}
      {hotels && !loading && (
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ fontSize: "1.15rem", fontWeight: "800", color: "#0f172a" }}>
              {hotels.length} Stays Available
            </h3>
            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
              Grounded TripAdvisor Real-World Traveler Corpus
            </span>
          </div>

          {hotels.length === 0 ? (
            <div style={{ padding: "3rem", textAlign: "center", background: "#fff", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
              <p style={{ color: "#64748b" }}>No hotels found matching these filters. Try increasing max price or lowering minimum rating.</p>
            </div>
          ) : (
            <div className="results-grid">
              {hotels.map((h, idx) => (
                <div key={idx} className="result-card">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
                    {/* Left: Info */}
                    <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                      <div style={{
                        width: "48px",
                        height: "48px",
                        borderRadius: "10px",
                        background: "#fef3c7",
                        color: "#d97706",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center"
                      }}>
                        <Hotel style={{ width: "22px", height: "22px" }} />
                      </div>

                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                          <span style={{ fontSize: "1.1rem", fontWeight: "800", color: "#0f172a" }}>
                            {h.name}
                          </span>
                          <span style={{
                            fontSize: "0.72rem",
                            background: "#e0f2fe",
                            color: "#0369a1",
                            padding: "0.15rem 0.5rem",
                            borderRadius: "9999px",
                            fontWeight: "600",
                            textTransform: "capitalize"
                          }}>
                            {h.category || "Hotel"}
                          </span>
                        </div>

                        <div style={{ fontSize: "0.82rem", color: "#64748b", marginTop: "0.25rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
                          <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                            <MapPin style={{ width: "13px", height: "13px" }} />
                            {h.city_name || destCities.find((c) => c.id === destCityId)?.name || "Central Location"}
                          </span>
                          <span>•</span>
                          <span style={{ display: "flex", alignItems: "center", gap: "0.2rem", color: "#d97706", fontWeight: "700" }}>
                            <Star style={{ width: "13px", height: "13px" }} />
                            {h.rating} / 5.0
                          </span>
                          {h.amenities && (
                            <>
                              <span>•</span>
                              <span style={{ color: "#16a34a" }}>Free WiFi & AC</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Right: Price & Book */}
                    <div style={{ textAlign: "right", minWidth: "140px" }}>
                      <div style={{ fontSize: "1.45rem", fontWeight: "800", color: "#006ce4" }}>
                        ₹{(h.price_per_night || h.price_per_night_inr || 2500).toLocaleString()}
                      </div>
                      <div style={{ fontSize: "0.72rem", color: "#64748b", marginBottom: "0.5rem" }}>
                        per room / night
                      </div>
                      <button
                        className="btn-primary"
                        style={{ padding: "0.45rem 1rem", fontSize: "0.85rem", width: "100%" }}
                        onClick={() => onSelectForBooking && onSelectForBooking({
                          type: "hotel",
                          hotel: h,
                          amount: h.price_per_night || h.price_per_night_inr || 2500
                        })}
                      >
                        Reserve Stay
                      </button>
                    </div>
                  </div>

                  {/* Stage 4 Grounded Review Summary */}
                  {h.review_summary && (
                    <GroundedReviewSummary
                      reviewSummary={h.review_summary}
                      title={`${h.name} TripAdvisor Feedback`}
                    />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
