"""
Chennai Hotel Recommender Engine.
Filters, scores, and matches accommodations based on zone, budget tier, and user preferences.
"""
import os
import pandas as pd

class HotelRecommender:
    def __init__(self, data_dir=r"d:\drl_project"):
        self.data_dir = data_dir
        self.hotels_df = None
        self.load_hotels()

    def load_hotels(self):
        path = os.path.join(self.data_dir, "hotels", "chennai_hotels.csv")
        if os.path.exists(path):
            self.hotels_df = pd.read_csv(path)
        else:
            self.hotels_df = pd.DataFrame()

    def get_recommendations(self, max_price=5000, preferred_zone=None, min_rating=3.8, category=None):
        if self.hotels_df.empty:
            return []
            
        df = self.hotels_df.copy()
        
        # Filter price
        if max_price:
            df = df[df["price_per_night_inr"] <= max_price * 1.25]
            
        # Filter zone
        if preferred_zone and preferred_zone != "Any Zone":
            df = df[df["zone"].str.contains(preferred_zone, case=False, na=False) | df["area"].str.contains(preferred_zone, case=False, na=False)]
            
        # Filter category
        if category and category != "Any Category":
            df = df[df["category"].str.lower() == category.lower()]
            
        # Filter rating
        df = df[df["rating"] >= min_rating]
        
        if df.empty:
            # Fallback to top rated within budget
            df = self.hotels_df[self.hotels_df["price_per_night_inr"] <= max_price * 1.5]
            if df.empty:
                df = self.hotels_df.head(10)
                
        # Sort by rating desc, price asc
        df = df.sort_values(by=["rating", "price_per_night_inr"], ascending=[False, True])
        return df.to_dict(orient="records")

if __name__ == "__main__":
    rec = HotelRecommender()
    res = rec.get_recommendations(max_price=3000, preferred_zone="Central")
    print(f"Found {len(res)} matching hotels!")
    if res:
        print("Top recommendation:", res[0])
