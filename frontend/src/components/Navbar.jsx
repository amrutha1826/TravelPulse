import React from "react";
import { Compass, Plane, Hotel, Calendar, ShieldCheck } from "./Icons";

export default function Navbar({ activeTab, setActiveTab, cartCount, onOpenCart }) {
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="brand-logo" onClick={() => setActiveTab("transport")}>
          <div style={{ background: "#fff", color: "#006ce4", padding: "6px", borderRadius: "10px", display: "flex", alignItems: "center" }}>
            <Compass className="w-6 h-6" style={{ width: "24px", height: "24px" }} />
          </div>
          <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.1 }}>
            <span style={{ fontSize: "1.25rem", fontWeight: "800", letterSpacing: "-0.5px" }}>
              TravelPulse
            </span>
            <span style={{ fontSize: "0.65rem", color: "#93c5fd", fontWeight: "600", textTransform: "uppercase", letterSpacing: "1px" }}>
              Agoda Enterprise
            </span>
          </div>
          <span className="brand-badge">DRL + RAG</span>
        </div>

        <div className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === "transport" ? "active" : ""}`}
            onClick={() => setActiveTab("transport")}
          >
            <Plane style={{ width: "18px", height: "18px" }} />
            <span>Transport & Flights</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === "itinerary" ? "active" : ""}`}
            onClick={() => setActiveTab("itinerary")}
          >
            <Calendar style={{ width: "18px", height: "18px" }} />
            <span>DRL Itinerary Planner</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === "hotels" ? "active" : ""}`}
            onClick={() => setActiveTab("hotels")}
          >
            <Hotel style={{ width: "18px", height: "18px" }} />
            <span>Hotels & Stays</span>
          </button>
        </div>

        <div>
          <button className="nav-cart-btn" onClick={onOpenCart}>
            <ShieldCheck style={{ width: "16px", height: "16px" }} />
            <span>Bookings & Cart ({cartCount})</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
