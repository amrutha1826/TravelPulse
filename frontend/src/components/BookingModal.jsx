import React, { useState } from "react";
import { BookingAPI } from "../services/api";
import { ShieldCheck, Check, X, Plane, Hotel, Calendar } from "./Icons";

export default function BookingModal({ bookingItem, onClose, onBookingSuccess }) {
  const [name, setName] = useState("Vignesh Kumar");
  const [email, setEmail] = useState("vignesh.kumar@travelpulse.ai");
  const [phone, setPhone] = useState("+91 98401 23456");

  const [loading, setLoading] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [error, setError] = useState(null);

  if (!bookingItem) return null;

  const handleConfirm = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const baseAmount = bookingItem.amount || 2000;
    const taxes = Math.round(baseAmount * 0.05);
    const totalAmount = baseAmount + taxes;

    let details = {};
    if (bookingItem.type === "transport") {
      details = {
        carrier: bookingItem.route.carrier_name || bookingItem.route.operator_name,
        mode: bookingItem.route.mode,
        origin: bookingItem.route.origin_city_name,
        dest: bookingItem.route.dest_city_name,
        departure: bookingItem.route.departure_time,
      };
    } else if (bookingItem.type === "hotel") {
      details = {
        hotel: bookingItem.hotel.name,
        category: bookingItem.hotel.category,
        rating: bookingItem.hotel.rating,
      };
    } else if (bookingItem.type === "itinerary") {
      details = {
        days: bookingItem.plan.num_days,
        hotel: bookingItem.plan.selected_hotel?.name,
        dest_city_id: bookingItem.plan.destination_city_id,
      };
    }

    try {
      const res = await BookingAPI.createBooking({
        user_name: name,
        user_email: email,
        user_phone: phone,
        booking_type: bookingItem.type,
        item_details: details,
        total_amount: totalAmount,
      });

      setConfirmation(res);
      if (onBookingSuccess) onBookingSuccess(res);
    } catch (err) {
      setError(err.message || "Failed to confirm booking.");
    } finally {
      setLoading(false);
    }
  };

  const baseAmount = bookingItem.amount || 2000;
  const taxes = Math.round(baseAmount * 0.05);
  const totalAmount = baseAmount + taxes;

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div className="modal-header">
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <ShieldCheck style={{ width: "20px", height: "20px", color: "#60a5fa" }} />
            <span style={{ fontWeight: "800", fontSize: "1.1rem" }}>
              {confirmation ? "Booking Confirmed" : "TravelPulse Express Checkout"}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{ background: "transparent", border: "none", color: "#fff", cursor: "pointer" }}
          >
            <X style={{ width: "20px", height: "20px" }} />
          </button>
        </div>

        {confirmation ? (
          <div className="modal-body" style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{
              width: "64px",
              height: "64px",
              borderRadius: "50%",
              background: "#dcfce7",
              color: "#16a34a",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "1rem"
            }}>
              <Check style={{ width: "32px", height: "32px" }} />
            </div>

            <h3 style={{ fontSize: "1.3rem", fontWeight: "800", color: "#0f172a", marginBottom: "0.25rem" }}>
              Voucher Confirmed!
            </h3>
            <p style={{ color: "#64748b", fontSize: "0.85rem", marginBottom: "1.5rem" }}>
              Your electronic ticket has been recorded in the TravelPulse registry.
            </p>

            <div style={{
              background: "#f8fafc",
              border: "2px dashed #cbd5e1",
              borderRadius: "12px",
              padding: "1.25rem",
              marginBottom: "1.5rem"
            }}>
              <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#64748b", fontWeight: "700", letterSpacing: "1px" }}>
                Confirmed PNR Code
              </div>
              <div style={{ fontSize: "1.8rem", fontWeight: "900", color: "#006ce4", letterSpacing: "2px", margin: "0.25rem 0" }}>
                {confirmation.pnr}
              </div>
              <div style={{ fontSize: "0.82rem", color: "#334155" }}>
                Guest: <strong>{name}</strong> • Amount: <strong>₹{confirmation.total_amount?.toLocaleString()}</strong>
              </div>
            </div>

            <button className="btn-primary" style={{ width: "100%" }} onClick={onClose}>
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleConfirm}>
            <div className="modal-body">
              {/* Item Summary Box */}
              <div style={{
                background: "#f1f5f9",
                borderRadius: "8px",
                padding: "0.85rem 1rem",
                marginBottom: "1.25rem",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}>
                <div>
                  <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#64748b", fontWeight: "700" }}>
                    Selected Item
                  </div>
                  <div style={{ fontWeight: "800", color: "#0f172a", fontSize: "0.95rem" }}>
                    {bookingItem.type === "transport" && (bookingItem.route.carrier_name || bookingItem.route.operator_name || "Transit Route")}
                    {bookingItem.type === "hotel" && (bookingItem.hotel.name)}
                    {bookingItem.type === "itinerary" && (`${bookingItem.plan.num_days}-Day Complete Trip`)}
                  </div>
                </div>

                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "1.1rem", fontWeight: "800", color: "#006ce4" }}>
                    ₹{baseAmount.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Guest Form */}
              <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    required
                    className="form-input"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Mobile Number</label>
                  <input
                    type="tel"
                    required
                    className="form-input"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </div>
              </div>

              {/* Price Breakdown */}
              <div style={{
                marginTop: "1.25rem",
                paddingTop: "1rem",
                borderTop: "1px solid #e2e8f0",
                display: "flex",
                flexDirection: "column",
                gap: "0.4rem",
                fontSize: "0.85rem"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b" }}>
                  <span>Base Price</span>
                  <span>₹{baseAmount.toLocaleString()}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b" }}>
                  <span>Taxes & GST (5%)</span>
                  <span>₹{taxes.toLocaleString()}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontWeight: "800", fontSize: "1.05rem", color: "#0f172a", marginTop: "0.25rem" }}>
                  <span>Total Payable</span>
                  <span style={{ color: "#006ce4" }}>₹{totalAmount.toLocaleString()}</span>
                </div>
              </div>

              {error && (
                <div style={{ marginTop: "1rem", padding: "0.5rem", borderRadius: "6px", background: "#fee2e2", color: "#b91c1c", fontSize: "0.8rem" }}>
                  {error}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                type="button"
                onClick={onClose}
                style={{
                  padding: "0.6rem 1rem",
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

              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
              >
                {loading ? "Issuing PNR..." : `Pay ₹${totalAmount.toLocaleString()} & Confirm`}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
