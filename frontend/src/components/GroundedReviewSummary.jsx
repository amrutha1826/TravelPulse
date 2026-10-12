import React, { useState } from "react";
import { ThumbsUp, ThumbsDown, ShieldCheck, ChevronDown } from "./Icons";

export default function GroundedReviewSummary({ reviewSummary, title = "Traveler Reviews" }) {
  const [expanded, setExpanded] = useState(false);

  if (!reviewSummary) {
    return (
      <div style={{ marginTop: "0.5rem", fontSize: "0.8rem", color: "#64748b", fontStyle: "italic" }}>
        No reviews available
      </div>
    );
  }

  const effectiveReviewsCount = reviewSummary.num_reviews ?? reviewSummary.total_reviews_analyzed ?? 0;
  const hasReviews = Boolean(reviewSummary.has_reviews) && effectiveReviewsCount > 0;
  const {
    sentiment_score = 0,
    pros = [],
    cons = [],
    summary = ""
  } = reviewSummary;

  if (!hasReviews) {
    return (
      <div style={{
        marginTop: "0.5rem",
        padding: "0.4rem 0.75rem",
        borderRadius: "6px",
        background: "#f1f5f9",
        border: "1px solid #e2e8f0",
        color: "#64748b",
        fontSize: "0.8rem",
        display: "inline-flex",
        alignItems: "center",
        gap: "0.4rem"
      }}>
        <span>💬</span>
        <span>No reviews available</span>
      </div>
    );
  }

  return (
    <div className="grounded-review-box">
      <div
        className="grounded-header"
        style={{ cursor: "pointer", userSelect: "none" }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span className="grounded-badge">
            <ShieldCheck style={{ width: "13px", height: "13px" }} />
            Stage 4 Grounded RAG
          </span>
          <span style={{ fontSize: "0.82rem", fontWeight: "700", color: "#334155" }}>
            {title} ({effectiveReviewsCount} real {effectiveReviewsCount === 1 ? "review" : "reviews"})
          </span>
          {sentiment_score !== 0 && (
            <span style={{
              fontSize: "0.72rem",
              fontWeight: "700",
              padding: "0.1rem 0.4rem",
              borderRadius: "4px",
              background: sentiment_score >= 0.5 ? "#dcfce7" : "#fee2e2",
              color: sentiment_score >= 0.5 ? "#15803d" : "#b91c1c"
            }}>
              {sentiment_score >= 0.5 ? "Positive Sentiment" : "Mixed Sentiment"}
            </span>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.3rem", color: "#006ce4", fontSize: "0.8rem", fontWeight: "600" }}>
          <span>{expanded ? "Hide details" : "View pros & cons"}</span>
          <ChevronDown style={{ width: "14px", height: "14px", transform: expanded ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: "0.75rem", animation: "modalIn 0.15s ease-out" }}>
          {summary && (
            <p style={{ fontSize: "0.82rem", color: "#475569", marginBottom: "0.6rem", lineHeight: 1.45 }}>
              {summary}
            </p>
          )}

          <div className="pros-cons-grid">
            <div className="pros-column">
              <div className="pros-title">
                <ThumbsUp style={{ width: "13px", height: "13px" }} />
                <span>Pros ({pros.length})</span>
              </div>
              {pros.length > 0 ? (
                <ul className="review-list">
                  {pros.map((p, idx) => (
                    <li key={idx} style={{ color: "#166534" }}>
                      {typeof p === "string" ? p : p.text || p.quote || JSON.stringify(p)}
                    </li>
                  ))}
                </ul>
              ) : (
                <div style={{ fontSize: "0.78rem", color: "#65a30d" }}>No specific positives cited</div>
              )}
            </div>

            <div className="cons-column">
              <div className="cons-title">
                <ThumbsDown style={{ width: "13px", height: "13px" }} />
                <span>Cons ({cons.length})</span>
              </div>
              {cons.length > 0 ? (
                <ul className="review-list">
                  {cons.map((c, idx) => (
                    <li key={idx} style={{ color: "#9f1239" }}>
                      {typeof c === "string" ? c : c.text || c.quote || JSON.stringify(c)}
                    </li>
                  ))}
                </ul>
              ) : (
                <div style={{ fontSize: "0.78rem", color: "#059669" }}>No major negatives reported</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
