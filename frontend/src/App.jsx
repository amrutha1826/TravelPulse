import React, { useState } from "react";
import Navbar from "./components/Navbar";
import TransportSearch from "./components/TransportSearch";
import ItineraryPlanner from "./components/ItineraryPlanner";
import HotelSearch from "./components/HotelSearch";
import BookingModal from "./components/BookingModal";
import { ShieldCheck, Compass } from "./components/Icons";

export default function App() {
  const [activeTab, setActiveTab] = useState("transport");
  const [cartItems, setCartItems] = useState([]);
  const [activeBookingItem, setActiveBookingItem] = useState(null);

  const handleSelectForBooking = (item) => {
    setActiveBookingItem(item);
  };

  const handleBookingSuccess = (confirmation) => {
    setCartItems((prev) => [...prev, confirmation]);
  };

  return (
    <div className="app-container">
      {/* Agoda Brand Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        cartCount={cartItems.length}
        onOpenCart={() => {
          if (cartItems.length > 0) {
            alert(`You have ${cartItems.length} confirmed bookings! Latest PNR: ${cartItems[cartItems.length - 1].pnr}`);
          } else {
            alert("Your booking cart is empty. Search transport, hotels, or generate an itinerary to book.");
          }
        }}
      />

      {/* Hero Header */}
      <header className="hero-banner">
        <h1 className="hero-title">
          {activeTab === "transport" && "Search Flights, Trains, Buses & Cabs"}
          {activeTab === "itinerary" && "AI Trip Planner with Reinforcement Learning"}
          {activeTab === "hotels" && "Book Stays & Verified Accommodations"}
        </h1>
        <p className="hero-subtitle">
          {activeTab === "transport" &&
            "Real multi-modal routes powered by Double-DQN policies and genuine traveler review citations."}
          {activeTab === "itinerary" &&
            "Sequential day-wise itinerary synthesis using PPO reinforcement learning with strict Stage 4 review grounding."}
          {activeTab === "hotels" &&
            "Compare verified hotels across India with genuine TripAdvisor ratings and zero hallucinated reviews."}
        </p>
      </header>

      {/* Main Content Area */}
      <main className="main-wrapper">
        {activeTab === "transport" && (
          <TransportSearch onSelectForBooking={handleSelectForBooking} />
        )}

        {activeTab === "itinerary" && (
          <ItineraryPlanner onSelectForBooking={handleSelectForBooking} />
        )}

        {activeTab === "hotels" && (
          <HotelSearch onSelectForBooking={handleSelectForBooking} />
        )}
      </main>

      {/* Booking Checkout Modal */}
      {activeBookingItem && (
        <BookingModal
          bookingItem={activeBookingItem}
          onClose={() => setActiveBookingItem(null)}
          onBookingSuccess={handleBookingSuccess}
        />
      )}

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-top">
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <div style={{ background: "#006ce4", color: "#fff", padding: "4px", borderRadius: "6px" }}>
                <Compass style={{ width: "20px", height: "20px" }} />
              </div>
              <div>
                <strong style={{ color: "#fff", fontSize: "1.1rem" }}>TravelPulse Enterprise</strong>
                <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>
                  Autonomous Deep Reinforcement Learning & Grounded RAG Platform
                </div>
              </div>
            </div>

            <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.82rem" }}>
              <span>🚀 <strong>Primary ML:</strong> PyTorch Double-DQN & PPO</span>
              <span>🔍 <strong>RAG Engine:</strong> Local Dense TF-IDF + SVD</span>
              <span>🛡️ <strong>Corpus:</strong> 100% Genuine Datasets</span>
            </div>
          </div>

          <div className="footer-divider" />

          <div className="footer-bottom">
            TravelPulse Enterprise • Fully Local Mathematical Algorithms (No Pretrained API Weights) • Agoda Architecture
          </div>
        </div>
      </footer>
    </div>
  );
}
