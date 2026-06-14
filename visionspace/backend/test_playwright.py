import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_playwright")

from visionspace.backend.search.playwright_search import search_playwright

async def test_playwright_live():
    logger.info("=== TESTING PLAYWRIGHT CRAWLER FALLBACK ===")
    
    query = "study desk"
    logger.info(f"Triggering Playwright search for: '{query}'")
    
    try:
        results = await search_playwright(query)
        logger.info(f"Playwright Scraper Execution Complete. Returned {len(results)} products.")
        
        # Group by merchant source
        amazon_prods = [p for p in results if p.get("store") == "Amazon"]
        ikea_prods = [p for p in results if p.get("store") == "IKEA"]
        
        logger.info(f" - Scraped from Amazon: {len(amazon_prods)} products")
        logger.info(f" - Scraped from IKEA: {len(ikea_prods)} products")
        
        if results:
            logger.info("\nSample Scraped Products:")
            for idx, p in enumerate(results[:5]):
                logger.info(
                    f" #{idx+1}: {p['title']} | Price: {p['price']} | Store: {p['store']} | URL: {p['url'][:60]}..."
                )
        else:
            logger.warning(
                "Scraper executed successfully but returned 0 results. "
                "This can occur if selectors mismatch or pages hit bot-protection walls."
            )
            
    except Exception as e:
        logger.error(f"Playwright verification test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_playwright_live())
