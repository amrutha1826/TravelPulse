import React, { useState, useEffect } from "react";
import { GeoAPI, ItineraryAPI } from "../services/api";
import GroundedReviewSummary from "./GroundedReviewSummary";
import {
  Calendar,
  Clock,
  MapPin,
  Sparkles,
  RefreshCw,
  Shuffle,
  Star,
  ShieldCheck,
  Search,
  Check,
  X
} from "./Icons";

export default function ItineraryPlanner({ onSelectForBooking }) {
  // Destination Geo
  const [states, setStates] = useState([]);
  const [destState, setDestState] = useState("");
  const [destCities, setDestCities] = useState([]);
  const [destCityId, setDestCityId] = useState("");
  const [destSearch, setDestSearch] = useState("");
  const [landmarksPreview, setLandmarksPreview] = useState([]);
  const [placeSearchQuery, setPlaceSearchQuery] = useState("");
  const [placeSearchResults, setPlaceSearchResults] = useState([]);
  const [searchingPlaces, setSearchingPlaces] = useState(false);

  // Planner parameters
  const [numDays, setNumDays] = useState(3);
  const [pace, setPace] = useState("medium");
  const [budgetPerDay, setBudgetPerDay] = useState(2500);
  const [availableCategories, setAvailableCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [dailyStartTime, setDailyStartTime] = useState("09:00");
  const [dailyEndTime, setDailyEndTime] = useState("19:00");
  const [freeTextQuery, setFreeTextQuery] = useState("");

  // Results
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState(null);
  const [error, setError] = useState(null);
  const [activeDay, setActiveDay] = useState(1);

  // Swap Activity Modal state
  const [swapModalOpen, setSwapModalOpen] = useState(false);
  const [swapTarget, setSwapTarget] = useState(null); // { dayNum, actIdx, oldPlaceName }
  const [cityPlaces, setCityPlaces] = useState([]);
  const [swapSearch, setSwapSearch] = useState("");
  const [swapping, setSwapping] = useState(false);

  // Load states and categories
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

    ItineraryAPI.getCategories()
      .then((cats) => {
        setAvailableCategories(cats);
        setSelectedCategories(cats.slice(0, 3)); // Pre-select first 3
      })
      .catch((err) => console.error("Error fetching categories:", err));
  }, []);

  // Fetch cities when state or destSearch changes
  useEffect(() => {
    if (!destState) return;
    GeoAPI.getCities(destState, destSearch)
      .then((cities) => {
        setDestCities(cities);
        if (cities.length > 0 && !cities.some((c) => c.id === destCityId)) {
          setDestCityId(cities[0].id);
        }
      })
      .catch((err) => console.error("Error fetching cities:", err));
  }, [destState, destSearch]);

  const handleSearchPlaces = async () => {
    if (!placeSearchQuery.trim()) return;
    setSearchingPlaces(true);
    try {
      const places = await GeoAPI.searchPlaces(placeSearchQuery.trim(), destCityId);
      setPlaceSearchResults(places || []);
    } catch (err) {
      console.error("Error searching places:", err);
    } finally {
      setSearchingPlaces(false);
    }
  };

  // Fetch landmark previews when destination city changes
  useEffect(() => {
    if (!destCityId) return;
    GeoAPI.getPlacePreview(destCityId, 6)
      .then((places) => setLandmarksPreview(places || []))
      .catch((err) => console.error("Error fetching landmarks preview:", err));
  }, [destCityId]);

  const toggleCategory = (cat) => {
    if (selectedCategories.includes(cat)) {
      if (selectedCategories.length > 1) {
        setSelectedCategories(selectedCategories.filter((c) => c !== cat));
      }
    } else {
      setSelectedCategories([...selectedCategories, cat]);
    }
  };

  const handleGenerate = async (e) => {
    if (e) e.preventDefault();
    if (!destCityId) {
      setError("Please select a destination city.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await ItineraryAPI.generateItinerary({
        destination_city_id: destCityId,
        num_days: numDays,
        pace: pace,
        categories: selectedCategories,
        budget_per_day: budgetPerDay,
        daily_start_time: dailyStartTime,
        daily_end_time: dailyEndTime,
        free_text_query: freeTextQuery || undefined,
      });

      setItinerary(data);
      setActiveDay(1);
    } catch (err) {
      setError(err.message || "Failed to generate itinerary.");
    } finally {
      setLoading(false);
    }
  };

  // Regenerate single day using DRL policy
  const handleRegenerateDay = async (dayNum) => {
    if (!itinerary || !itinerary.day_plans) return;
    setLoading(true);
    try {
      const res = await ItineraryAPI.regenerateDay({
        current_itinerary: itinerary.day_plans,
        destination_city_id: destCityId,
        day_num: dayNum,
        pace: pace,
        categories: selectedCategories,
        daily_start_time: dailyStartTime,
        daily_end_time: dailyEndTime,
      });
      setItinerary({
        ...itinerary,
        day_plans: res.day_plans,
      });
    } catch (err) {
      setError(`Failed to regenerate Day ${dayNum}: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Open swap activity modal
  const handleOpenSwapModal = async (dayNum, actIdx, oldPlaceName) => {
    setSwapTarget({ dayNum, actIdx, oldPlaceName });
    setSwapModalOpen(true);
    try {
      const places = await GeoAPI.getCityPlaces(destCityId);
      setCityPlaces(places || []);
    } catch (err) {
      console.error("Error loading replacement places:", err);
    }
  };

  // Execute swap activity
  const handleExecuteSwap = async (newPlaceId) => {
    if (!swapTarget || !itinerary) return;
    setSwapping(true);
    try {
      const res = await ItineraryAPI.swapActivity({
        current_itinerary: itinerary.day_plans,
        day_num: swapTarget.dayNum,
        activity_idx: swapTarget.actIdx,
        new_place_id: newPlaceId,
      });
      setItinerary({
        ...itinerary,
        day_plans: res.day_plans,
      });
      setSwapModalOpen(false);
      setSwapTarget(null);
    } catch (err) {
      alert(`Could not swap activity: ${err.message}`);
    } finally {
      setSwapping(false);
    }
  };

  const currentDayData = itinerary?.day_plans?.[activeDay] || itinerary?.day_plans?.[String(activeDay)];

  return (
    <div>
      {/* Search & Configuration Card */}
      <div className="search-card">
        <form onSubmit={handleGenerate}>
          <div className="search-grid">
            {/* Destination State */}
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

            {/* Destination City */}
            <div className="form-group">
              <label className="form-label">
                Destination City
                <input
                  type="text"
                  placeholder="Filter name..."
                  style={{
                    marginLeft: "auto",
                    padding: "0.15rem 0.4rem",
                    fontSize: "0.72rem",
                    border: "1px solid #cbd5e1",
                    borderRadius: "4px",
                    width: "95px"
                  }}
                  value={destSearch}
                  onChange={(e) => setDestSearch(e.target.value)}
                />
              </label>
              <select
                className="form-select"
                value={destCityId}
                onChange={(e) => setDestCityId(e.target.value)}
              >
                {destCities.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} {c.granularity_level === 'district_hq' ? '(District HQ)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Days Duration */}
            <div className="form-group">
              <label className="form-label">Duration (Days)</label>
              <select
                className="form-select"
                value={numDays}
                onChange={(e) => setNumDays(Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5, 6, 7].map((d) => (
                  <option key={d} value={d}>
                    {d} {d === 1 ? "Day" : "Days"}
                  </option>
                ))}
              </select>
            </div>

            {/* Pace */}
            <div className="form-group">
              <label className="form-label">Travel Pace</label>
              <select
                className="form-select"
                value={pace}
                onChange={(e) => setPace(e.target.value)}
              >
                <option value="slow">Relaxed (2-3 places/day)</option>
                <option value="medium">Balanced (4-5 places/day)</option>
                <option value="fast">Intensive (6+ places/day)</option>
              </select>
            </div>

            {/* Submit Button */}
            <div className="form-group">
              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
                style={{ height: "46px" }}
              >
                <Sparkles style={{ width: "18px", height: "18px" }} />
                <span>{loading ? "Optimizing Policy..." : "Generate DRL Itinerary"}</span>
              </button>
            </div>
          </div>

          {/* Places & Attractions Search Bar */}
          <div style={{
            marginTop: "1.25rem",
            paddingTop: "1rem",
            borderTop: "1px solid #e2e8f0",
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            flexWrap: "wrap"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flex: 1, minWidth: "260px" }}>
              <input
                type="text"
                className="form-input"
                style={{ padding: "0.45rem 0.75rem", fontSize: "0.85rem", width: "100%" }}
                placeholder="Search specific tourist places, temples, beaches, forts..."
                value={placeSearchQuery}
                onChange={(e) => setPlaceSearchQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleSearchPlaces(); } }}
              />
              <button
                type="button"
                className="btn-primary"
                style={{ padding: "0.45rem 0.9rem", fontSize: "0.85rem", whiteSpace: "nowrap" }}
                onClick={handleSearchPlaces}
                disabled={searchingPlaces}
              >
                <Search style={{ width: "14px", height: "14px" }} />
                <span>{searchingPlaces ? "Searching..." : "Find Place"}</span>
              </button>
            </div>
          </div>

          {/* Place Search Results */}
          {placeSearchResults.length > 0 && (
            <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
              <span style={{ fontSize: "0.78rem", fontWeight: "700", color: "#006ce4" }}>
                SEARCH RESULTS:
              </span>
              {placeSearchResults.map((p, idx) => (
                <span
                  key={idx}
                  style={{
                    fontSize: "0.75rem",
                    padding: "0.2rem 0.6rem",
                    borderRadius: "9999px",
                    background: "#eff6ff",
                    color: "#1d4ed8",
                    border: "1px solid #bfdbfe",
                    fontWeight: "600"
                  }}
                >
                  ⭐ {p.name} ({p.category}) - {p.rating}★
                </span>
              ))}
            </div>
          )}

          {/* Landmarks Preview */}
          {landmarksPreview.length > 0 && (
            <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
              <span style={{ fontSize: "0.78rem", fontWeight: "700", color: "#64748b" }}>
                DISCOVERED LANDMARKS:
              </span>
              {landmarksPreview.map((lm, idx) => (
                <span
                  key={idx}
                  style={{
                    fontSize: "0.75rem",
                    padding: "0.15rem 0.5rem",
                    borderRadius: "9999px",
                    background: "#f1f5f9",
                    color: "#334155",
                    border: "1px solid #e2e8f0",
                  }}
                >
                  📍 {lm.name} ({lm.category || "Sight"})
                </span>
              ))}
            </div>
          )}

          {/* Categories Filter Chips */}
          <div style={{ marginTop: "1.25rem", paddingTop: "1rem", borderTop: "1px solid #e2e8f0" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "#64748b" }}>
                INTEREST THEMES:
              </span>
            </div>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {availableCategories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => toggleCategory(cat)}
                  className={`filter-pill-btn ${selectedCategories.includes(cat) ? "active" : ""}`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>

      {/* 4-Stage Pipeline Banner */}
      <div className="stage-pipeline-banner">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Sparkles style={{ width: "16px", height: "16px", color: "#006ce4" }} />
          <span style={{ fontSize: "0.85rem", fontWeight: "700", color: "#1e293b" }}>
            PPO Reinforcement Learning Sequential Decision Policy
          </span>
        </div>
        <div className="pipeline-steps">
          <span className="pipeline-step-pill step-1">Stage 1: SQL Filter</span>
          <span style={{ color: "#94a3b8" }}>➔</span>
          <span className="pipeline-step-pill step-2">Stage 2: Semantic TF-IDF</span>
          <span style={{ color: "#94a3b8" }}>➔</span>
          <span className="pipeline-step-pill step-3">Stage 3: DRL PPO Itinerary Agent</span>
          <span style={{ color: "#94a3b8" }}>➔</span>
          <span className="pipeline-step-pill step-4">Stage 4: Grounded Review Traceability</span>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div style={{ padding: "1rem", borderRadius: "8px", background: "#fee2e2", border: "1px solid #fca5a5", color: "#b91c1c", marginBottom: "1.5rem" }}>
          <strong>Error: </strong> {error}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div style={{ padding: "3rem", textAlign: "center", background: "#fff", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>✨</div>
          <h3 style={{ fontSize: "1.1rem", color: "#1e293b", fontWeight: "700" }}>
            Synthesizing Day-Wise Itinerary using PPO Agent...
          </h3>
          <p style={{ color: "#64748b", fontSize: "0.85rem" }}>
            Optimizing sequential travel times, category diversity, and attaching Stage 4 real visitor reviews
          </p>
        </div>
      )}

      {/* Itinerary Results */}
      {itinerary && !loading && (
        <div>
          {/* Top Overview & Selected Hotel Banner */}
          <div style={{
            background: "#fff",
            borderRadius: "12px",
            padding: "1.25rem 1.5rem",
            marginBottom: "1.5rem",
            border: "1px solid #e2e8f0",
            boxShadow: "var(--shadow-sm)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem"
          }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <h3 style={{ fontSize: "1.25rem", fontWeight: "800", color: "#0f172a" }}>
                  {itinerary.num_days}-Day Optimized Plan
                </h3>
                <span style={{ fontSize: "0.75rem", background: "#dcfce7", color: "#15803d", fontWeight: "700", padding: "0.2rem 0.5rem", borderRadius: "9999px" }}>
                  DRL PPO Verified
                </span>
              </div>
              {itinerary.selected_hotel && (
                <div style={{ fontSize: "0.85rem", color: "#64748b", marginTop: "0.25rem" }}>
                  🏨 Base Hotel: <strong>{itinerary.selected_hotel.name}</strong> (₹{itinerary.selected_hotel.price_per_night}/night)
                </div>
              )}
            </div>

            <button
              className="btn-primary"
              style={{ padding: "0.5rem 1.25rem", fontSize: "0.9rem" }}
              onClick={() => onSelectForBooking && onSelectForBooking({
                type: "itinerary",
                plan: itinerary,
                amount: (itinerary.num_days * (itinerary.selected_hotel?.price_per_night || 2000))
              })}
            >
              Book Complete Trip
            </button>
          </div>

          {/* Intercity Transit Recommendation */}
          {(itinerary.recommended_transit || (itinerary.days && itinerary.days[1]?.recommended_transit)) && (
            <div style={{
              background: "#f0fdf4",
              border: "1px solid #86efac",
              borderRadius: "10px",
              padding: "0.85rem 1.25rem",
              marginBottom: "1.25rem",
              fontSize: "0.85rem"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.3rem" }}>
                <span style={{ background: "#059669", color: "#fff", fontSize: "0.7rem", fontWeight: "800", padding: "0.15rem 0.5rem", borderRadius: "9999px" }}>
                  RECOMMENDED INTERCITY TRANSIT
                </span>
                <strong style={{ color: "#064e3b" }}>
                  {(itinerary.recommended_transit || itinerary.days[1].recommended_transit).route_title}
                </strong>
              </div>
              <div style={{ color: "#047857", fontSize: "0.82rem" }}>
                <strong>Why chosen: </strong>
                {(itinerary.recommended_transit || itinerary.days[1].recommended_transit).reasoning}
              </div>
            </div>
          )}

          {/* Day Navigation Tabs */}
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", flexWrap: "wrap", alignItems: "center" }}>
            {Array.from({ length: itinerary.num_days }, (_, i) => i + 1).map((day) => (
              <button
                key={day}
                onClick={() => setActiveDay(day)}
                className={`filter-pill-btn ${activeDay === day ? "active" : ""}`}
                style={{ padding: "0.5rem 1.25rem", fontSize: "0.95rem", fontWeight: "700" }}
              >
                Day {day}
              </button>
            ))}

            <div style={{ marginLeft: "auto" }}>
              <button
                type="button"
                onClick={() => handleRegenerateDay(activeDay)}
                disabled={loading}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.35rem",
                  padding: "0.45rem 0.85rem",
                  borderRadius: "6px",
                  border: "1px solid #cbd5e1",
                  background: "#fff",
                  color: "#006ce4",
                  fontSize: "0.82rem",
                  fontWeight: "600",
                  cursor: "pointer",
                }}
              >
                <RefreshCw style={{ width: "13px", height: "13px" }} />
                <span>Re-roll Day {activeDay} Policy</span>
              </button>
            </div>
          </div>

          {/* Current Day Activities */}
          {currentDayData ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {/* Day theme/header if available */}
              {currentDayData.theme && (
                <div style={{ fontSize: "0.9rem", fontWeight: "700", color: "#334155" }}>
                  🎯 Day Focus: {currentDayData.theme}
                </div>
              )}

              {/* Day-level Plan Review Summary if present */}
              {currentDayData.plan_review_summary && (
                <GroundedReviewSummary
                  reviewSummary={currentDayData.plan_review_summary}
                  title={`Day ${activeDay} Itinerary Traveler Summary`}
                />
              )}

              {/* List of Activities */}
              {currentDayData.activities && currentDayData.activities.map((act, idx) => {
                const placeName = act.place_name || act.name || act.poi?.name || "Landmark";
                const category = act.category || act.poi?.category || "Sightseeing";
                const rating = act.rating || act.poi?.rating;
                const fee = act.entry_fee !== undefined ? act.entry_fee : (act.poi?.entry_fee_inr !== undefined ? act.poi.entry_fee_inr : 0);
                const timeSlot = act.time_slot || `${act.start_time || "09:00"} - ${act.end_time || "11:00"}`;

                return (
                  <div key={idx} className="result-card">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
                      {/* Time slot and Index badge */}
                      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                        <div style={{
                          width: "36px",
                          height: "36px",
                          borderRadius: "50%",
                          background: "#006ce4",
                          color: "#fff",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontWeight: "800",
                          fontSize: "0.95rem"
                        }}>
                          {idx + 1}
                        </div>

                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                            <span style={{ fontSize: "1.1rem", fontWeight: "800", color: "#0f172a" }}>
                              {placeName}
                            </span>
                            <span style={{
                              fontSize: "0.72rem",
                              background: "#e0f2fe",
                              color: "#0369a1",
                              padding: "0.15rem 0.5rem",
                              borderRadius: "9999px",
                              fontWeight: "600"
                            }}>
                              {category}
                            </span>
                          </div>

                          <div style={{ fontSize: "0.82rem", color: "#64748b", marginTop: "0.25rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
                            <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                              <Clock style={{ width: "13px", height: "13px" }} />
                              {timeSlot} ({act.planned_duration_hours || act.duration_hours || 1.5} hrs)
                            </span>
                            {rating && (
                              <>
                                <span>•</span>
                                <span style={{ display: "flex", alignItems: "center", gap: "0.2rem", color: "#d97706", fontWeight: "700" }}>
                                  <Star style={{ width: "13px", height: "13px" }} />
                                  {rating}
                                </span>
                              </>
                            )}
                            <span>•</span>
                            <span>Fee: ₹{fee}</span>
                          </div>
                        </div>
                      </div>

                      {/* Swap button */}
                      <button
                        type="button"
                        onClick={() => handleOpenSwapModal(activeDay, idx, placeName)}
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.35rem",
                          padding: "0.4rem 0.75rem",
                          borderRadius: "6px",
                          border: "1px solid #cbd5e1",
                          background: "#fff",
                          color: "#475569",
                          fontSize: "0.8rem",
                          fontWeight: "600",
                          cursor: "pointer",
                        }}
                      >
                        <Shuffle style={{ width: "13px", height: "13px" }} />
                        <span>Swap Place</span>
                      </button>
                    </div>

                    {/* Stage 4 Grounded Review Summary for this activity */}
                    {act.review_summary && (
                      <GroundedReviewSummary
                        reviewSummary={act.review_summary}
                        title={`${placeName} Verified Reviews`}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ padding: "3rem", textAlign: "center", background: "#fff", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
              <p style={{ color: "#64748b" }}>No activities planned for Day {activeDay}.</p>
            </div>
          )}
        </div>
      )}

      {/* Swap Activity Modal */}
      {swapModalOpen && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Shuffle style={{ width: "18px", height: "18px" }} />
                <span style={{ fontWeight: "700", fontSize: "1rem" }}>
                  Swap: {swapTarget?.oldPlaceName}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setSwapModalOpen(false)}
                style={{ background: "transparent", border: "none", color: "#fff", cursor: "pointer" }}
              >
                <X style={{ width: "20px", height: "20px" }} />
              </button>
            </div>

            <div className="modal-body" style={{ maxHeight: "400px", overflowY: "auto" }}>
              <div style={{ marginBottom: "1rem" }}>
                <input
                  type="text"
                  className="form-input"
                  style={{ width: "100%" }}
                  placeholder="Filter available landmarks..."
                  value={swapSearch}
                  onChange={(e) => setSwapSearch(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {cityPlaces
                  .filter((p) => p.name.toLowerCase().includes(swapSearch.toLowerCase()))
                  .slice(0, 20)
                  .map((p) => (
                    <div
                      key={p.id}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "0.6rem 0.75rem",
                        borderRadius: "8px",
                        border: "1px solid #e2e8f0",
                        background: "#f8fafc",
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: "700", fontSize: "0.88rem", color: "#1e293b" }}>
                          {p.name}
                        </div>
                        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                          {p.category || "Sight"} • Rating: {p.rating || "4.5"}
                        </div>
                      </div>
                      <button
                        type="button"
                        disabled={swapping}
                        className="btn-primary"
                        style={{ padding: "0.3rem 0.75rem", fontSize: "0.78rem" }}
                        onClick={() => handleExecuteSwap(p.id)}
                      >
                        {swapping ? "Swapping..." : "Select"}
                      </button>
                    </div>
                  ))}
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                onClick={() => setSwapModalOpen(false)}
                style={{
                  padding: "0.5rem 1rem",
                  borderRadius: "6px",
                  border: "1px solid #cbd5e1",
                  background: "#fff",
                  color: "#475569",
                  fontWeight: "600",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
