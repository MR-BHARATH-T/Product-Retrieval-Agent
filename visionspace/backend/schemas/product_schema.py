from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductSchema(BaseModel):
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "INR"
    rating: Optional[float] = None
    reviews: Optional[int] = 0
    dimensions: Optional[str] = None
    availability: Optional[str] = "Available"
    store: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None
    searched_query: Optional[str] = None

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str
    max_price: Optional[float] = None
    room_dimensions: Optional[str] = None  # e.g. "10x12 ft"
    min_rating: Optional[float] = 0.0
    llm_provider: Optional[str] = "lm-studio"
    llm_model: Optional[str] = None
    currency: Optional[str] = "INR"
    openrouter_key: Optional[str] = None
    gemini_key: Optional[str] = None
    grok_key: Optional[str] = None
    groq_key: Optional[str] = None
    page: Optional[int] = 1
    limit: Optional[int] = 6

class PaginatedSearchResponse(BaseModel):
    items: List[ProductSchema]
    total_items: int
    page: int
    limit: int
    total_pages: int

class RecommendationItemSchema(BaseModel):
    title: str
    price: str
    rating: str
    store: str
    url: str
    reason: str
    image: Optional[str] = None

class BestChoiceSchema(BaseModel):
    title: str
    reason: str
    image: Optional[str] = None

class RecommendationResponse(BaseModel):
    recommended_products: List[RecommendationItemSchema]
    best_choice: BestChoiceSchema
    summary: str

class SearchHistorySchema(BaseModel):
    id: int
    query: str
    created_at: datetime

    class Config:
        from_attributes = True
