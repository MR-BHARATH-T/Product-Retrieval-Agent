import asyncio
import logging
from sqlalchemy.orm import Session

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_vpia")

from visionspace.backend.utils.parser import parse_dimensions, parse_room_dimensions
from visionspace.backend.utils.normalizer import normalize_price, normalize_rating, normalize_reviews, normalize_product
from visionspace.backend.utils.deduplicator import deduplicate_products, is_similar
from visionspace.backend.database.db import init_db, SessionLocal
from visionspace.backend.database.models import Product, SearchHistory, Recommendation
from visionspace.backend.agents.ranking_agent import rank_and_filter_products
from visionspace.backend.agents.llm_agent import get_llm_recommendation
from visionspace.backend.cache.chroma_store import chroma_store

def run_util_tests():
    logger.info("=== RUNNING UTILITY TESTS ===")
    
    # 1. Dimension parser test
    dim1 = parse_dimensions("90x45x75 cm")
    dim2 = parse_dimensions("3 x 1.5 ft")
    room = parse_room_dimensions("10x12 ft")
    logger.info(f"Dimensions 90x45x75 cm -> {dim1}")
    logger.info(f"Dimensions 3x1.5 ft -> {dim2}")
    logger.info(f"Room 10x12 ft -> {room}")
    assert dim1 == {"length": 90.0, "width": 45.0, "height": 75.0}
    assert dim2 == {"length": 91.44, "width": 45.72, "height": None}
    assert room == (304.8, 365.76)
    
    # 2. Price/rating normalizer test
    p1 = normalize_price("₹ 4,999.00")
    p2 = normalize_price("$120.50")
    r1 = normalize_rating("4.8 out of 5 stars")
    rv1 = normalize_reviews("1.5k reviews")
    logger.info(f"Price ₹ 4,999.00 -> {p1}")
    logger.info(f"Price $120.50 -> {p2}")
    logger.info(f"Rating 4.8 -> {r1}")
    logger.info(f"Reviews 1.5k -> {rv1}")
    assert p1 == 4999.0
    assert p2 == 120.5
    assert r1 == 4.8
    assert rv1 == 1500

    # Currency extraction and conversion tests
    from visionspace.backend.utils.normalizer import extract_currency, convert_currency
    curr1 = extract_currency("$120.50")
    curr2 = extract_currency("€ 99.00")
    curr3 = extract_currency("₹ 4999.00")
    curr4 = extract_currency("4999.00", default_currency="USD")
    conv1 = convert_currency(100.0, "USD", "INR")
    conv2 = convert_currency(8350.0, "INR", "USD")
    logger.info(f"Currency $120.50 -> {curr1}")
    logger.info(f"Currency € 99.00 -> {curr2}")
    logger.info(f"Currency ₹ 4999.00 -> {curr3}")
    logger.info(f"Currency 4999.00 (fallback) -> {curr4}")
    logger.info(f"100.0 USD converted to INR -> {conv1}")
    logger.info(f"8350.0 INR converted to USD -> {conv2}")
    assert curr1 == "USD"
    assert curr2 == "EUR"
    assert curr3 == "INR"
    assert curr4 == "USD"
    assert abs(conv1 - 8350.0) < 1e-5
    assert abs(conv2 - 100.0) < 1e-5

    # 3. Deduplicator similarity tests
    prods = [
        {"title": "Wooden Desk A", "price": 4000.0, "store": "Amazon", "url": "url1"},
        {"title": "Wooden Desk A", "price": 3999.0, "store": "Amazon", "url": "url1"},
        {"title": "wood desk a", "price": 4200.0, "store": "amazon", "url": "url2"},
        {"title": "IKEA Desk B", "price": 8000.0, "store": "IKEA", "url": "url3"}
    ]
    dedup = deduplicate_products(prods)
    logger.info(f"Deduplicated products: {dedup}")
    assert len(dedup) == 2
    logger.info("Utility tests passed!")

async def test_full_pipeline():
    logger.info("\n=== RUNNING FULL PIPELINE TEST (MOCK SEARCH) ===")
    
    # Init database
    init_db()
    db = SessionLocal()
    
    query = "Study desk under ₹5000"
    room_dims = "10x12 ft"
    
    # Setup mock raw products matching various merchants
    mock_raw_products = [
        {
            "title": "Adiko Solid Wood Study Desk",
            "price": "₹ 4,500.00",
            "rating": "4.4 out of 5",
            "reviews": "120 reviews",
            "dimensions": "90 x 45 x 75 cm",
            "store": "Amazon",
            "url": "https://amazon.in/desk-a",
            "availability": "Available"
        },
        {
            "title": "Adiko Solid Wood Study Desk",
            "price": "₹ 4,500.00",
            "rating": "4.4",
            "reviews": "125",
            "dimensions": "90 x 45 x 75 cm",
            "store": "Amazon",
            "url": "https://amazon.in/desk-a",
            "availability": "Available"
        },
        {
            "title": "IKEA MICKE Desk",
            "price": "₹ 8,999.00",
            "rating": "4.6",
            "reviews": "350 reviews",
            "dimensions": "105 x 50 x 75 cm",
            "store": "IKEA",
            "url": "https://ikea.com/micke-desk",
            "availability": "Available"
        },
        {
            "title": "Flipkart SmartBuy Foldable Desk",
            "price": "₹ 1,999.00",
            "rating": "3.8",
            "reviews": "1200",
            "dimensions": "80 x 40 x 70 cm",
            "store": "Flipkart",
            "url": "https://flipkart.com/foldable-desk",
            "availability": "Available"
        },
        {
            "title": "Pepperfry Jumbo Office Desk",
            "price": "₹ 12,000.00",
            "rating": "4.2",
            "reviews": "45",
            "dimensions": "180 x 90 x 80 cm",
            "store": "Pepperfry",
            "url": "https://pepperfry.com/jumbo-desk",
            "availability": "Available"
        }
    ]
    
    # 1. Standardize candidate products
    normalized = [normalize_product(p, query) for p in mock_raw_products]
    
    # 2. Deduplicate matching candidates
    unique = deduplicate_products(normalized)
    logger.info(f"Unique normalized products count: {len(unique)}")
    
    # 3. Persist to database
    for u in unique:
        db_prod = Product(
            title=u["title"],
            brand=u["brand"],
            price=u["price"],
            rating=u["rating"],
            reviews=u["reviews"],
            dimensions=u["dimensions"],
            availability=u["availability"],
            store=u["store"],
            url=u["url"],
            image=u["image"],
            searched_query=u["searched_query"]
        )
        db.add(db_prod)
    
    # Store history
    history = SearchHistory(query=query)
    db.add(history)
    db.commit()
    logger.info("Persisted mock search records to SQLite.")
    
    # 4. Insert into ChromaDB
    chroma_store.add_products(unique)
    
    # 5. Filter products by constraints (max budget: 5000, room size: 10x12 ft)
    filtered = rank_and_filter_products(
        products=unique,
        max_price=5000.0,
        min_rating=3.0,
        room_dimensions=room_dims
    )
    logger.info(f"Filtered products count: {len(filtered)}")
    for f in filtered:
        logger.info(f" - {f['title']} (Price: {f['price']}, Store: {f['store']})")

    # 5b. Test currency match priority sorting
    logger.info("\n=== TESTING CURRENCY MATCH PRIORITY ===")
    mock_mixed_currency_products = [
        {"title": "Cheap INR Desk", "price": 1000.0, "currency": "INR", "availability": "Available", "rating": 4.5, "reviews": 10},
        {"title": "Cheap USD Desk", "price": 12.0, "currency": "USD", "availability": "Available", "rating": 4.0, "reviews": 5},
        {"title": "Medium USD Desk", "price": 50.0, "currency": "USD", "availability": "Available", "rating": 4.8, "reviews": 12},
    ]
    usd_prioritized = rank_and_filter_products(
        products=mock_mixed_currency_products,
        max_price=100.0,
        preferred_currency="USD"
    )
    logger.info("USD search results (should show USD matching products first):")
    for item in usd_prioritized:
        logger.info(f" - {item['title']} ({item['price']} {item['currency']}, Rating: {item['rating']})")
    assert usd_prioritized[0]["title"] == "Medium USD Desk"  # Rated 4.8 USD
    assert usd_prioritized[1]["title"] == "Cheap USD Desk"   # Rated 4.0 USD
    assert usd_prioritized[2]["title"] == "Cheap INR Desk"   # Rated 4.5 INR (converted to ~12 USD)
    logger.info("Currency match priority tests passed!")
         
    # 6. Recommendation analysis (runs LLM context mapping, falls back if offline)
    rec = await get_llm_recommendation(
        query=query,
        products=filtered,
        room_dimensions=room_dims,
        db=db
    )
    
    logger.info("Recommendation System Output:")
    import json
    logger.info(json.dumps(rec, indent=2))
    
    db.close()
    logger.info("Pipeline verification test complete.")

if __name__ == "__main__":
    run_util_tests()
    asyncio.run(test_full_pipeline())
