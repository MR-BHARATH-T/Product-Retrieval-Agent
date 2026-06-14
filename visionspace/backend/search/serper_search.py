import logging
import httpx
from typing import List, Dict, Any
from visionspace.backend.config.config import settings

logger = logging.getLogger(__name__)

async def search_serper(query: str, preferred_currency: str = "INR") -> List[Dict[str, Any]]:
    """
    Search Serper.dev for product information using Google Shopping.
    Falls back to normal web search if Shopping returns no results.
    """
    api_key = settings.SERPER_API_KEY
    if not api_key:
        logger.info("Serper API Key is not configured.")
        return []
        
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Currency to local gl/hl map
    locale_map = {
        "INR": {"gl": "in", "hl": "en"},
        "USD": {"gl": "us", "hl": "en"},
        "EUR": {"gl": "de", "hl": "de"},
        "GBP": {"gl": "uk", "hl": "en"},
        "CAD": {"gl": "ca", "hl": "en"},
        "AUD": {"gl": "au", "hl": "en"},
        "JPY": {"gl": "jp", "hl": "ja"},
        "SGD": {"gl": "sg", "hl": "en"},
        "AED": {"gl": "ae", "hl": "en"},
        "CNY": {"gl": "cn", "hl": "zh-cn"}
    }
    curr = (preferred_currency or "INR").upper().strip()
    loc = locale_map.get(curr, {"gl": "in", "hl": "en"})
    
    payload = {
        "q": query,
        "gl": loc["gl"],
        "hl": loc["hl"]
    }
    
    products = []
    
    # 1. Try Google Shopping endpoint first
    try:
        url_shopping = "https://google.serper.dev/shopping"
        logger.info(f"Querying Serper Shopping ({curr} - gl={loc['gl']}) for: '{query}'")
        async with httpx.AsyncClient() as client:
            response = await client.post(url_shopping, headers=headers, json=payload, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            shopping_results = data.get("shopping", [])
            for item in shopping_results:
                products.append({
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "store": item.get("source"),
                    "url": item.get("link"),
                    "rating": item.get("rating"),
                    "reviews": item.get("ratingCount") or item.get("reviews"),
                    "image": item.get("imageUrl"),
                    "brand": item.get("brand")
                })
            logger.info(f"Serper Shopping returned {len(products)} products.")
    except Exception as e:
        logger.error(f"Error querying Serper Shopping API: {e}")
        
    # 2. Fall back to Organic Web Search if Shopping returned nothing
    if not products:
        try:
            url_search = "https://google.serper.dev/search"
            logger.info(f"Serper Shopping empty. Querying Serper Web Search fallback ({curr} - gl={loc['gl']}) for: '{query}'")
            async with httpx.AsyncClient() as client:
                response = await client.post(url_search, headers=headers, json=payload, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                organic = data.get("organic", [])
                for item in organic:
                    products.append({
                        "title": item.get("title"),
                        "price": None,
                        "store": None,
                        "url": item.get("link"),
                        "rating": None,
                        "reviews": 0,
                        "image": None,
                        "brand": None
                    })
                logger.info(f"Serper Web Search returned {len(products)} products.")
        except Exception as e:
            logger.error(f"Error querying Serper Search API: {e}")
            
    return products
