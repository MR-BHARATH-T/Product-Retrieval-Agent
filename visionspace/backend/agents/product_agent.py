import logging
import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from visionspace.backend.search.serper_search import search_serper
from visionspace.backend.search.tavily_search import search_tavily
from visionspace.backend.search.serpapi_search import search_serpapi
from visionspace.backend.search.playwright_search import search_playwright
from visionspace.backend.utils.normalizer import normalize_product
from visionspace.backend.utils.deduplicator import deduplicate_products
from visionspace.backend.database.models import SearchHistory, Product as DBProduct
from visionspace.backend.cache.chroma_store import chroma_store

logger = logging.getLogger(__name__)

async def run_product_agent(query: str, db: Session, preferred_currency: str = "INR") -> List[Dict[str, Any]]:
    """
    Executes the fallback chain logic:
    Check cache -> Try Serper -> Try Tavily -> Try SerpAPI -> Try Playwright.
    Stores search history and final normalized/deduplicated products in SQLite,
    and indexes them in ChromaDB.
    """
    # 1. Store query in Search History table
    try:
        history = SearchHistory(query=query)
        db.add(history)
        db.commit()
        logger.info(f"Logged query '{query}' to database history.")
    except Exception as e:
        logger.error(f"Failed to save search history: {e}")
        db.rollback()

    # Check cache to avoid hitting external APIs/scraping on pagination clicks
    try:
        time_limit = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        cached_db_products = db.query(DBProduct).filter(
            DBProduct.searched_query == query,
            DBProduct.created_at >= time_limit
        ).all()
        if cached_db_products:
            logger.info(f"Retrieved {len(cached_db_products)} cached products from SQLite for query '{query}'")
            return [
                {
                    "title": p.title,
                    "brand": p.brand,
                    "price": p.price,
                    "currency": p.currency,
                    "rating": p.rating,
                    "reviews": p.reviews,
                    "dimensions": p.dimensions,
                    "availability": p.availability,
                    "store": p.store,
                    "url": p.url,
                    "image": p.image,
                    "searched_query": p.searched_query
                }
                for p in cached_db_products
            ]
    except Exception as cache_err:
        logger.error(f"Failed to query database cache: {cache_err}")

    raw_results = []
    source_used = ""

    # Step 1: Serper API
    try:
        raw_results = await search_serper(query, preferred_currency=preferred_currency)
        if raw_results:
            source_used = "Serper API"
    except Exception as e:
        logger.error(f"Serper API execution failed: {e}")

    # Step 2: Tavily API (Fallback)
    if not raw_results:
        try:
            raw_results = await search_tavily(query)
            if raw_results:
                source_used = "Tavily API"
        except Exception as e:
            logger.error(f"Tavily API execution failed: {e}")

    # Step 3: SerpAPI (Backup Fallback)
    if not raw_results:
        try:
            raw_results = await search_serpapi(query, preferred_currency=preferred_currency)
            if raw_results:
                source_used = "SerpAPI"
        except Exception as e:
            logger.error(f"SerpAPI execution failed: {e}")

    # Step 4: Playwright Scraper (Ultimate Fallback)
    if not raw_results:
        try:
            raw_results = await search_playwright(query, preferred_currency=preferred_currency)
            if raw_results:
                source_used = "Playwright Scraper"
        except Exception as e:
            logger.error(f"Playwright Scraper execution failed: {e}")

    if not raw_results:
        logger.warning(f"No products found for query '{query}' across all sources.")
        return []

    logger.info(f"Retrieved {len(raw_results)} product candidates from {source_used}")

    # Normalize products using the user's preferred currency as a fallback default
    normalized = [normalize_product(p, query, preferred_currency) for p in raw_results]

    # Deduplicate products
    unique_products = deduplicate_products(normalized)
    logger.info(f"Deduplicated results: {len(normalized)} items -> {len(unique_products)} unique items.")

    # Save unique products to SQLite
    try:
        for p in unique_products:
            db_prod = DBProduct(
                title=p["title"],
                brand=p["brand"],
                price=p["price"],
                currency=p["currency"],
                rating=p["rating"],
                reviews=p["reviews"],
                dimensions=p["dimensions"],
                availability=p["availability"],
                store=p["store"],
                url=p["url"],
                image=p["image"],
                searched_query=p["searched_query"]
            )
            db.add(db_prod)
        db.commit()
        logger.info(f"Saved {len(unique_products)} items to SQLite products table.")
    except Exception as e:
        logger.error(f"Failed to persist products to SQLite: {e}")
        db.rollback()

    # Index products in ChromaDB
    try:
        chroma_store.add_products(unique_products)
    except Exception as e:
        logger.error(f"Failed to cache products in ChromaDB: {e}")

    return unique_products
