import logging
import httpx
from typing import List, Dict, Any
from visionspace.backend.config.config import settings

logger = logging.getLogger(__name__)

async def search_serpapi(query: str, preferred_currency: str = "INR") -> List[Dict[str, Any]]:
    """
    Search using SerpAPI's Google Shopping engine.
    Falls back to normal Google search if no shopping results are found.
    """
    api_key = settings.SERPAPI_API_KEY
    if not api_key:
        logger.info("SerpAPI Key is not configured.")
        return []
        
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
        
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "gl": loc["gl"],
        "hl": loc["hl"]
    }
    
    products = []
    
    # 1. Try Google Shopping search engine
    try:
        logger.info(f"Querying SerpAPI Google Shopping ({curr} - gl={loc['gl']}) for: '{query}'")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            shopping_results = data.get("shopping_results", [])
            for item in shopping_results:
                products.append({
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "store": item.get("source"),
                    "url": item.get("link"),
                    "rating": item.get("rating"),
                    "reviews": item.get("reviews"),
                    "image": item.get("thumbnail"),
                    "brand": None
                })
            logger.info(f"SerpAPI Shopping returned {len(products)} products.")
    except Exception as e:
        logger.error(f"Error querying SerpAPI Shopping: {e}")
        
    # 2. Fall back to Organic Google Search
    if not products:
        params["engine"] = "google"
        try:
            logger.info(f"SerpAPI Shopping empty. Querying SerpAPI Google Web Search fallback ({curr} - gl={loc['gl']}) for: '{query}'")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                organic = data.get("organic_results", [])
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
                logger.info(f"SerpAPI Web Search returned {len(products)} products.")
        except Exception as e:
            logger.error(f"Error querying SerpAPI Web Search: {e}")
            
    return products
