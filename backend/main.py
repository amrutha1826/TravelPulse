import sys
import os

# Ensure root directory is on PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import geo, transport, itinerary, hotels, booking

app = FastAPI(
    title="TravelPulse Enterprise API",
    description="Agoda-Style Travel & Transport Planning Platform powered by DRL (Double-DQN & PPO) and Grounded RAG",
    version="2.0.0"
)

# Enable CORS for React frontend (Vite dev server default: port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(geo.router)
app.include_router(transport.router)
app.include_router(itinerary.router)
app.include_router(hotels.router)
app.include_router(booking.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "service": "TravelPulse Full-Stack API",
        "version": "2.0.0",
        "drl_policy": "PPO & Double-DQN (PyTorch)",
        "rag_retrieval": "Local Dense TF-IDF + SVD (Zero Pretrained Weights)",
        "grounded_reviews": "100% Genuine TripAdvisor, RedBus & IRCTC Dataset"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
