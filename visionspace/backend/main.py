import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from visionspace.backend.config.config import settings
from visionspace.backend.database.db import get_db, init_db
from visionspace.backend.schemas.product_schema import SearchRequest, ProductSchema, RecommendationResponse, PaginatedSearchResponse
from visionspace.backend.agents.product_agent import run_product_agent
from visionspace.backend.agents.ranking_agent import rank_and_filter_products
from visionspace.backend.agents.llm_agent import get_llm_recommendation
from visionspace.backend.cache.chroma_store import chroma_store

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("visionspace_vpia")

app = FastAPI(
    title="VisionSpace Product Intelligence Agent (VPIA)",
    description="Multi-source product search fallback, SQL/Chroma cache, and local Qwen LLM recommendation framework.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing VPIA Services...")
    init_db()
    logger.info("SQLite Database models initialized successfully.")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "VisionSpace Product Intelligence Agent (VPIA)",
        "features": ["Fallback search chain", "SQL database persistence", "ChromaDB vector lookup", "Local Qwen LLM logic"]
    }

@app.post("/api/search", response_model=PaginatedSearchResponse)
async def search_products(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Executes product retrieval, applies normalization, deduplication, DB logging,
    runs rule-based filter constraints, and returns paginated matches.
    """
    logger.info(f"API Request: POST /api/search for query: '{request.query}' (preferred currency: {request.currency}, page: {request.page}, limit: {request.limit})")
    try:
        # Execute search pipeline
        products = await run_product_agent(request.query, db, preferred_currency=request.currency)
        
        # Rank and apply hard filters (price limits, min ratings, room fit constraints)
        filtered = rank_and_filter_products(
            products=products,
            max_price=request.max_price,
            min_rating=request.min_rating,
            room_dimensions=request.room_dimensions,
            preferred_currency=request.currency
        )
        
        # Paginate results
        page = request.page or 1
        limit = request.limit or 6
        total_items = len(filtered)
        total_pages = max(1, (total_items + limit - 1) // limit)
        
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
            
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_items = filtered[start_idx:end_idx]
        
        return {
            "items": paginated_items,
            "total_items": total_items,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Search endpoint failure: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"VPIA Search processing failed: {str(e)}"
        )

@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend_products(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Executes search, filters by user constraints, and runs the Qwen LLM analyzer.
    Enforces structured recommendation reports back to client.
    """
    logger.info(f"API Request: POST /api/recommend for query: '{request.query}' (preferred currency: {request.currency})")
    try:
        # 1. Search products
        products = await run_product_agent(request.query, db, preferred_currency=request.currency)
        
        # 2. Filter matching criteria
        filtered = rank_and_filter_products(
            products=products,
            max_price=request.max_price,
            min_rating=request.min_rating,
            room_dimensions=request.room_dimensions,
            preferred_currency=request.currency
        )
        
        # 3. Call selected LLM or fallback heuristics
        report = await get_llm_recommendation(
            query=request.query,
            products=filtered,
            room_dimensions=request.room_dimensions,
            db=db,
            provider=request.llm_provider,
            model=request.llm_model,
            openrouter_key=request.openrouter_key,
            gemini_key=request.gemini_key,
            grok_key=request.grok_key,
            groq_key=request.groq_key
        )
        return report
    except Exception as e:
        logger.error(f"Recommend endpoint failure: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"VPIA Recommendation report generation failed: {str(e)}"
        )

class SimilarQueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

@app.post("/api/similar", response_model=List[ProductSchema])
async def search_similar_products(request: SimilarQueryRequest):
    """
    Retrieves semantically similar items using the local ChromaDB vector store.
    """
    logger.info(f"API Request: POST /api/similar for query: '{request.query}'")
    try:
        results = chroma_store.search_similar(request.query, limit=request.limit)
        return results
    except Exception as e:
        logger.error(f"Similar vector search endpoint failure: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic matching query failed: {str(e)}"
        )
