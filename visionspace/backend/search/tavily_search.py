import logging
import httpx
import re
from typing import List, Dict, Any
from visionspace.backend.config.config import settings

logger = logging.getLogger(__name__)

async def search_tavily(query: str) -> List[Dict[str, Any]]:
    """
    Search using Tavily API and extract products and price details from descriptions.
    """
    api_key = settings.TAVILY_API_KEY
    if not api_key:
        logger.info("Tavily API Key is not configured.")
        return []
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": f"{query} buy online store price",
        "search_depth": "basic",
        "include_answer": False
    }
    
    products = []
    try:
        logger.info(f"Querying Tavily Search for: '{query}'")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            for res in results:
                title = res.get("title", "")
                content = res.get("content", "")
                link = res.get("url", "")
                
                # Attempt to extract price from content using regex (e.g. $99.99, Rs. 4500, ₹1500)
                price_match = re.search(r'(?:[\$\u20B9\xA3\u20AC]|rs\.?)\s*(\d+(?:,\d+)*(?:\.\d+)?)', content, re.IGNORECASE)
                price = price_match.group(0) if price_match else None
                
                # Attempt to extract rating
                rating_match = re.search(r'(\d\.\d|\d)\s*/\s*5', content)
                rating = rating_match.group(1) if rating_match else None
                
                products.append({
                    "title": title,
                    "price": price,
                    "store": None,  # Will fallback to URL domain parsing
                    "url": link,
                    "rating": rating,
                    "reviews": 0,
                    "image": None,
                    "brand": None
                })
            logger.info(f"Tavily Search returned {len(products)} results.")
    except Exception as e:
        logger.error(f"Error querying Tavily Search API: {e}")
        
    return products
