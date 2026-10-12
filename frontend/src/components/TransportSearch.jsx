import React, { useState, useEffect } from "react";
import { GeoAPI, TransportAPI } from "../services/api";
import GroundedReviewSummary from "./GroundedReviewSummary";
import {
  Plane,
  Train,
  Bus,
  Car,
  Search,
  ArrowRight,
  Clock,
  Sparkles,
  ShieldCheck,
  ChevronDown
} from "./Icons";

export default function TransportSearch({ onSelectForBooking }) {
  // State for geo dropdowns & search inputs
  const [states, setStates] = useState([]);
  const [originState, setOriginState] = useState("");
  const [originCities, setOriginCities] = useState([]);
  const [originCityId, setOriginCityId] = useState("");
  const [originSearch, setOriginSearch] = useState("");

  const [destState, setDestState] = useState("");
  const [destCities, setDestCities] = useState([]);
  const [destCityId, setDestCityId] = useState("");
  const [destSearch, setDestSearch] = useState("");

  // Filters
  const [selectedModes, setSelectedModes] = useState(["flight", "train", "bus", "cab"]);
  const [departureWindow, setDepartureWindow] = useState("all");
  const [sortBy, setSortBy] = useState("recommended");
  const [includeConnecting, setIncludeConnecting] = useState(true);
  const [freeTextQuery, setFreeTextQuery] = useState("");

  // Results & Category Tabs
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeCategoryTab, setActiveCategoryTab] = useState("all"); // 'all', 'direct', 'multihop'

  // Load states on mount
  useEffect(() => {
    GeoAPI.getStates()
      .then((data) => {
        setStates(data);
        if (data.length > 0) {
          const tn = data.find((s) => s.toLowerCase().includes("tamil")) || data[0];
          const ka = data.find((s) => s.toLowerCase().includes("karnataka")) || (data.length > 1 ? data[1] : data[0]);
          setOriginState(ka);
          setDestState(tn);
        }
      })
      .catch((err) => console.error("Error fetching states:", err));
  }, []);

  // Fetch origin cities with search keyword
  useEffect(() => {
    if (!originState) return;
    GeoAPI.getCities(originState, originSearch)
      .then((cities) => {
        setOriginCities(cities);
        if (cities.length > 0 && !cities.some((c) => c.id === originCityId)) {
          setOriginCityId(cities[0].id);
        }
      })
      .catch((err) => console.error("Error fetching origin cities:", err));
  }, [originState, originSearch]);

  // Fetch destination cities with search keyword
  useEffect(() => {
    if (!destState) return;
    GeoAPI.getCities(destState, destSearch)
      .then((cities) => {
        setDestCities(cities);
        if (cities.length > 0 && !cities.some((c) => c.id === destCityId)) {
          setDestCityId(cities[0].id);
        }
      })
      .catch((err) => console.error("Error fetching destination cities:", err));
  }, [destState, destSearch]);

  const toggleMode = (mode) => {
    if (selectedModes.includes(mode)) {
      if (selectedModes.length > 1) {
        setSelectedModes(selectedModes.filter((m) => m !== mode));
      }
    } else {
      setSelectedModes([...selectedModes, mode]);
    }
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!originCityId || !destCityId) {
      setError("Please select both origin and destination cities.");
      return;
    }

    setLoading(true);
    setError(null);

    let depWin = null;
    if (departureWindow === "morning") depWin = ["06:00", "12:00"];
    else if (departureWindow === "afternoon") depWin = ["12:00", "18:00"];
    else if (departureWindow === "evening") depWin = ["18:00", "23:59"];

    try {
      const data = await TransportAPI.searchTransport({
        origin_city_id: originCityId,
        dest_city_id: destCityId,
        selected_modes: selectedModes,
        departure_window: depWin,
        sort_by: sortBy,
        include_connecting: includeConnecting,
        free_text_query: freeTextQuery || undefined,
        limit: 40,
      });

      setResults(data);
      // Auto-switch tab if no direct options exist
      if (data.direct_routes && data.direct_routes.length === 0 && data.multihop_routes && data.multihop_routes.length > 0) {
        setActiveCategoryTab("multihop");
      } else {
        setActiveCategoryTab("all");
      }
    } catch (err) {
      setError(err.message || "Failed to search transport routes.");
    } finally {
      setLoading(false);
    }
  };

  const getModeIcon = (mode) => {
    const m = (mode || "").toLowerCase();
    if (m.includes("flight")) return <Plane style={{ width: "18px", height: "18px" }} />;
    if (m.includes("train")) return <Train style={{ width: "18px", height: "18px" }} />;
    if (m.includes("bus")) return <Bus style={{ width: "18px", height: "18px" }} />;
    if (m.includes("cab") || m.includes("car")) return <Car style={{ width: "18px", height: "18px" }} />;
    return <span>🚀</span>;
  };

  const directList = results?.direct_routes || [];
  const multihopList = results?.multihop_routes || results?.connecting_routes || [];
  const displayedRoutes =
    activeCategoryTab === "direct"
      ? directList
      : activeCategoryTab === "multihop"
      ? multihopList
      : results?.all_routes || results?.results || [];

  return (
    <div>
      {/* Search Header Banner */}
      <div className="search-card">
        <form onSubmit={handleSearch}>
          <div className="search-grid">
            {/* Origin */}
            <div className="form-group">
              <label className="form-label">From (State)</label>
              <select
                className="form-select"
                value={originState}
                onChange={(e) => {
                  setOriginState(e.target.value);
                  setOriginSearch("");
                }}
              >
                {states.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                From (City / District)
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
                  value={originSearch}
                  onChange={(e) => setOriginSearch(e.target.value)}
                />
              </label>
              <select
                className="form-select"
                value={originCityId}
                onChange={(e) => setOriginCityId(e.target.value)}
              >
                {originCities.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} {c.granularity_level === 'district_hq' ? '(District HQ)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Destination */}
            <div className="form-group">
              <label className="form-label">To (State)</label>
              <select
                className="form-select"
                value={destState}
                onChange={(e) => {
                  setDestState(e.target.value);
                  setDestSearch("");
                }}
              >
                {states.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">
                To (City / District)
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

            {/* Submit */}
            <div className="form-group">
              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
                style={{ height: "46px" }}
              >
                <Search style={{ width: "18px", height: "18px" }} />
                <span>{loading ? "Searching Graph..." : "Search Routes"}</span>
              </button>
            </div>
          </div>

          {/* Filters Row */}
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
            {/* Mode Selector */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "#64748b" }}>MODES:</span>
              {[
                { id: "flight", label: "Flight", icon: <Plane style={{ width: "14px", height: "14px" }} /> },
                { id: "train", label: "Train", icon: <Train style={{ width: "14px", height: "14px" }} /> },
                { id: "bus", label: "Bus", icon: <Bus style={{ width: "14px", height: "14px" }} /> },
                { id: "cab", label: "Cab", icon: <Car style={{ width: "14px", height: "14px" }} /> },
              ].map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => toggleMode(m.id)}
                  className={`filter-pill-btn ${selectedModes.includes(m.id) ? "active" : ""}`}
                  style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
                >
                  {m.icon}
                  <span>{m.label}</span>
                </button>
              ))}
            </div>

            {/* Departure Time */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: "700", color: "#64748b" }}>TIME:</span>
              {[
                { id: "all", label: "Anytime" },
                { id: "morning", label: "Morning (06-12)" },
                { id: "afternoon", label: "Afternoon (12-18)" },
                { id: "evening", label: "Night (18-24)" },
              ].map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setDepartureWindow(t.id)}
                  className={`filter-pill-btn ${departureWindow === t.id ? "active" : ""}`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Sort & Multi-Hop */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <select
                className="form-select"
                style={{ padding: "0.35rem 0.65rem", fontSize: "0.85rem" }}
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="recommended">Sort: Recommended</option>
                <option value="cheapest">Price: Low to High</option>
                <option value="fastest">Fastest Duration</option>
                <option value="earliest">Earliest Departure</option>
              </select>

              <label style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.82rem", color: "#475569", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={includeConnecting}
                  onChange={(e) => setIncludeConnecting(e.target.checked)}
                />
                Multi-Hop Search
              </label>
            </div>
          </div>
        </form>
      </div>

      {/* 4-Stage Architectural Pipeline Explanation Banner */}
      <div className="stage-pipeline-banner">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Sparkles style={{ width: "16px", height: "16px", color: "#006ce4" }} />
          <span style={{ fontSize: "0.85rem", fontWeight: "700", color: "#1e293b" }}>
            Graph Router & Multi-Modal Optimization Engine
          </span>
        </div>
        <div className="pipeline-steps">
          <span className="pipeline-step-pill step-1">Stage 1: Strict Mode Filter</span>
          <span style={{ color: "#94a3b8" }}>➔</span>
          <span className="pipeline-step-pill step-2">Stage 2: Graph Path Search (Max 3 Hops)</span>
          <span style={{ color: "#94a3b8" }}>➔</span>
          <span className="pipeline-step-pill step-3">Stage 3: Direct vs Multi-Hop Synthesis</span>
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
          <div style={{ fontSize: "2rem", marginBottom: "0.75rem", animation: "spin 1s infinite linear" }}>⚡</div>
          <h3 style={{ fontSize: "1.1rem", color: "#1e293b", fontWeight: "700" }}>
            Running Graph Multi-Modal Search (Max 3 Hops)...
          </h3>
          <p style={{ color: "#64748b", fontSize: "0.85rem" }}>
            Traversing flight, train, bus, and cab schedules with zero mode leakage
          </p>
        </div>
      )}

      {/* Results Display */}
      {results && !loading && (
        <div>
          {/* Header & Category Tabs */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.75rem" }}>
            <div>
              <h3 style={{ fontSize: "1.2rem", fontWeight: "800", color: "#0f172a" }}>
                Found {results.total_count || 0} Routes
              </h3>
              <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                Direct: <strong>{directList.length}</strong> • Multi-Hop / Combined: <strong>{multihopList.length}</strong>
              </div>
            </div>

            {/* Two Categories Navigation Tabs */}
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                type="button"
                className={`filter-pill-btn ${activeCategoryTab === "all" ? "active" : ""}`}
                onClick={() => setActiveCategoryTab("all")}
              >
                All Options ({results.total_count || 0})
              </button>

              <button
                type="button"
                className={`filter-pill-btn ${activeCategoryTab === "direct" ? "active" : ""}`}
                onClick={() => setActiveCategoryTab("direct")}
              >
                Direct Routes ({directList.length})
              </button>

              <button
                type="button"
                className={`filter-pill-btn ${activeCategoryTab === "multihop" ? "active" : ""}`}
                onClick={() => setActiveCategoryTab("multihop")}
              >
                Multi-Hop Combined ({multihopList.length})
              </button>
            </div>
          </div>

          {/* Banner if Direct is unavailable */}
          {directList.length === 0 && multihopList.length > 0 && (
            <div style={{
              background: "#eff6ff",
              border: "1px solid #bfdbfe",
              borderRadius: "8px",
              padding: "0.75rem 1rem",
              marginBottom: "1rem",
              fontSize: "0.85rem",
              color: "#1e40af",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem"
            }}>
              <span>ℹ️</span>
              <span>
                <strong>No direct single-leg service exists between these points.</strong> Showing verified multi-hop connecting journeys combining train, bus, and cab options.
              </span>
            </div>
          )}

          {/* DRL Policy Best Choice Route Recommendation */}
          {results.recommended_route && (
            <div style={{
              background: "linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%)",
              border: "1.5px solid #86efac",
              borderRadius: "12px",
              padding: "1rem 1.25rem",
              marginBottom: "1.5rem",
              boxShadow: "0 4px 12px rgba(16, 185, 129, 0.08)"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem", flexWrap: "wrap", gap: "0.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <span style={{
                    background: "#059669",
                    color: "#fff",
                    fontSize: "0.72rem",
                    fontWeight: "800",
                    padding: "0.2rem 0.55rem",
                    borderRadius: "9999px",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.3rem",
                    letterSpacing: "0.03em"
                  }}>
                    <Sparkles style={{ width: "12px", height: "12px" }} />
                    DRL POLICY BEST CHOICE
                  </span>
                  <span style={{ fontSize: "0.78rem", color: "#065f46", fontWeight: "600" }}>
                    Utility Score: {results.recommended_route.drl_utility_score}
                  </span>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.85rem", fontWeight: "700" }}>
                  <span style={{ color: "#059669" }}>
                    Total: ₹{Number(results.recommended_route.total_fare_inr).toLocaleString()}
                  </span>
                  <span>•</span>
                  <span style={{ color: "#065f46" }}>
                    {results.recommended_route.duration_hours}h
                  </span>
                  <span>•</span>
                  <span style={{ color: "#475569" }}>
                    {results.recommended_route.is_direct ? "Direct (0 transfers)" : `${results.recommended_route.hop_count - 1} transfer`}
                  </span>
                </div>
              </div>

              <div style={{ fontSize: "0.98rem", fontWeight: "800", color: "#064e3b", marginBottom: "0.35rem" }}>
                Recommended: {results.recommended_route.route_title}
              </div>

              <div style={{ fontSize: "0.85rem", color: "#047857", lineHeight: "1.45" }}>
                <strong>Chosen because: </strong>
                {results.recommended_route.reasoning}
              </div>
            </div>
          )}

          {/* Results Empty State */}
          {displayedRoutes.length === 0 ? (
            <div style={{ padding: "3rem", textAlign: "center", background: "#fff", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
              <p style={{ color: "#64748b", fontSize: "0.95rem" }}>
                {results.empty_reason || "No routes match the selected criteria. Try expanding transport modes or layover filters."}
              </p>
            </div>
          ) : (
            <div className="results-grid">
              {displayedRoutes.map((route, idx) => {
                const isMultiHop = !route.is_direct && route.legs && route.legs.length > 1;

                return (
                  <div key={idx} className="result-card">
                    {/* Top Row: Carrier/Mode summary and Price */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
                      {/* Left: Mode & Carrier Info */}
                      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                        <div style={{
                          width: "48px",
                          height: "48px",
                          borderRadius: "10px",
                          background: isMultiHop ? "#f3e8ff" : "#e0f2fe",
                          color: isMultiHop ? "#7e22ce" : "#0284c7",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center"
                        }}>
                          {getModeIcon(route.mode || route.legs[0]?.mode)}
                        </div>

                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                            <span style={{ fontSize: "1.05rem", fontWeight: "800", color: "#0f172a" }}>
                              {route.carrier_name || route.operator_name}
                            </span>
                            {route.is_direct ? (
                              <span style={{ fontSize: "0.72rem", background: "#dcfce7", color: "#15803d", fontWeight: "800", padding: "0.15rem 0.5rem", borderRadius: "9999px" }}>
                                Direct (1 Leg)
                              </span>
                            ) : (
                              <span style={{ fontSize: "0.72rem", background: "#f3e8ff", color: "#7e22ce", fontWeight: "800", padding: "0.15rem 0.5rem", borderRadius: "9999px" }}>
                                {route.legs?.length || 2} Legs Combined ({route.transfer_city ? `via ${route.transfer_city}` : "Connecting"})
                              </span>
                            )}
                          </div>

                          <div style={{ fontSize: "0.82rem", color: "#64748b", marginTop: "0.2rem", display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
                            <span style={{ fontWeight: "700", color: isMultiHop ? "#7e22ce" : "#0284c7" }}>
                              {route.mode}
                            </span>
                            <span>•</span>
                            <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                              <Clock style={{ width: "13px", height: "13px" }} />
                              {route.duration_formatted || `${route.duration_hours} hrs`}
                            </span>
                            {route.distance_km && (
                              <>
                                <span>•</span>
                                <span>{route.distance_km} km</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Middle: Departure & Arrival summary */}
                      <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontSize: "1.15rem", fontWeight: "800", color: "#1e293b" }}>
                            {route.departure_time || "--:--"}
                          </div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                            {route.origin_city_name}
                          </div>
                        </div>

                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: "90px" }}>
                          <div style={{ fontSize: "0.68rem", color: isMultiHop ? "#7e22ce" : "#0284c7", fontWeight: "700" }}>
                            {isMultiHop ? `${route.legs.length - 1} Layover` : "Direct"}
                          </div>
                          <div style={{ width: "100%", height: "2px", background: isMultiHop ? "#c084fc" : "#006ce4", margin: "4px 0", position: "relative" }}>
                            <div style={{ width: "6px", height: "6px", background: isMultiHop ? "#7e22ce" : "#006ce4", borderRadius: "50%", position: "absolute", right: 0, top: "-2px" }} />
                          </div>
                          <div style={{ fontSize: "0.7rem", color: "#64748b" }}>
                            {route.duration_formatted}
                          </div>
                        </div>

                        <div>
                          <div style={{ fontSize: "1.15rem", fontWeight: "800", color: "#1e293b" }}>
                            {route.arrival_time || "--:--"}
                          </div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                            {route.dest_city_name}
                          </div>
                        </div>
                      </div>

                      {/* Right: Total Fare & Book */}
                      <div style={{ textAlign: "right", minWidth: "140px" }}>
                        <div style={{ fontSize: "1.45rem", fontWeight: "800", color: "#006ce4" }}>
                          ₹{(route.total_fare_inr || route.price || 0).toLocaleString()}
                        </div>
                        <div style={{ fontSize: "0.72rem", color: "#64748b", marginBottom: "0.5rem" }}>
                          Total journey fare
                        </div>
                        <button
                          className="btn-primary"
                          style={{ padding: "0.45rem 1rem", fontSize: "0.85rem", width: "100%" }}
                          onClick={() => onSelectForBooking && onSelectForBooking({
                            type: "transport",
                            route: route,
                            amount: route.total_fare_inr || route.price || 0
                          })}
                        >
                          Book Journey
                        </button>
                      </div>
                    </div>

                    {/* Multi-Hop Itemized Leg Breakdown Card */}
                    {isMultiHop && (
                      <div style={{
                        marginTop: "1rem",
                        padding: "0.85rem",
                        background: "#f8fafc",
                        borderRadius: "8px",
                        border: "1px dashed #cbd5e1"
                      }}>
                        <div style={{ fontSize: "0.78rem", fontWeight: "800", color: "#475569", marginBottom: "0.5rem", textTransform: "uppercase" }}>
                          Itemized Journey Legs ({route.legs.length} segments):
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                          {route.legs.map((leg, lIdx) => (
                            <div key={lIdx} style={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              background: "#fff",
                              padding: "0.5rem 0.75rem",
                              borderRadius: "6px",
                              border: "1px solid #e2e8f0",
                              fontSize: "0.82rem",
                              flexWrap: "wrap",
                              gap: "0.5rem"
                            }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                <span style={{
                                  background: "#e0f2fe",
                                  color: "#0369a1",
                                  fontWeight: "800",
                                  fontSize: "0.7rem",
                                  padding: "0.1rem 0.4rem",
                                  borderRadius: "4px"
                                }}>
                                  Leg {leg.leg_number}
                                </span>
                                <span style={{ fontWeight: "700", color: "#0f172a" }}>
                                  {leg.from_city} ➔ {leg.to_city}
                                </span>
                                <span style={{ color: "#64748b" }}>
                                  ({leg.mode.toUpperCase()}: {leg.carrier_name})
                                </span>
                              </div>

                              <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                                <span>{leg.departure_time} - {leg.arrival_time} ({leg.duration_hours}h)</span>
                                <span style={{ fontWeight: "800", color: "#006ce4" }}>₹{leg.fare_inr}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Stage 4 Grounded Carrier Review Summary */}
                    {isMultiHop ? (
                      <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                        {route.legs.map((leg, lIdx) => leg.review_summary && (
                          <GroundedReviewSummary
                            key={lIdx}
                            reviewSummary={leg.review_summary}
                            title={`Leg ${leg.leg_number} (${leg.carrier_name}) Reviews`}
                          />
                        ))}
                      </div>
                    ) : (
                      route.review_summary && (
                        <GroundedReviewSummary
                          reviewSummary={route.review_summary}
                          title={`${route.carrier_name || "Carrier"} Verified Reviews`}
                        />
                      )
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
