import logging
import urllib.parse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

async def scrape_amazon(page, query: str, preferred_currency: str = "INR") -> List[Dict[str, Any]]:
    products = []
    try:
        curr = (preferred_currency or "INR").upper().strip()
        domain = "amazon.com" if curr == "USD" else "amazon.in"
        url = f"https://www.{domain}/s?k={urllib.parse.quote(query)}"
        logger.info(f"Playwright: Navigating to Amazon ({domain}): {url}")
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        
        # Add quick render timeout
        await page.wait_for_timeout(2000)
        
        cards = await page.query_selector_all('div[data-component-type="s-search-result"]')
        for card in cards[:6]:
            title = ""
            for selector in ['h2 a span', 'h2 a', 'span.a-size-medium', 'span.a-size-base-plus', 'a.a-link-normal span']:
                el = await card.query_selector(selector)
                if el:
                    txt = await el.inner_text()
                    if txt and txt.strip():
                        title = txt.strip()
                        break
            
            link = ""
            for selector in ['h2 a', 'a.a-link-normal', 'a']:
                el = await card.query_selector(selector)
                if el:
                    href = await el.get_attribute('href')
                    if href and href.strip():
                        link = href.strip()
                        break
            
            price = None
            for selector in ['.a-price-whole', '.a-price', 'span.a-color-price', '.a-color-base']:
                el = await card.query_selector(selector)
                if el:
                    txt = await el.inner_text()
                    if txt and txt.strip():
                        price = txt.strip()
                        break
            
            rating = None
            for selector in ['.a-icon-alt', 'span.a-icon-alt']:
                el = await card.query_selector(selector)
                if el:
                    rating = await el.get_attribute('innerHTML') or await el.inner_text()
                    break
                    
            reviews = "0"
            reviews_el = await card.query_selector('span.a-size-base')
            if reviews_el:
                reviews = await reviews_el.inner_text()
            
            # Scrape product image URL
            image = None
            for selector in ['img.s-image', 'img']:
                el = await card.query_selector(selector)
                if el:
                    src = await el.get_attribute('src') or await el.get_attribute('data-src') or await el.get_attribute('srcset')
                    if src:
                        src_strip = src.strip().split(' ')[0]
                        if src_strip.startswith('http'):
                            image = src_strip
                            break
 
            # Exclude non-product text overlays
            if title and title.lower().strip() in ["let us know", "sponsored", "feedback", "ad", "sponsored ad", "close"]:
                title = ""
            
            if title:
                full_link = f"https://www.{domain}{link}" if link.startswith('/') else link
                products.append({
                    "title": title,
                    "price": price,
                    "store": "Amazon",
                    "url": full_link,
                    "rating": rating,
                    "reviews": reviews,
                    "image": image,
                    "brand": "Amazon"
                })
    except Exception as e:
        logger.error(f"Error scraping Amazon via Playwright: {e}")
    return products

async def scrape_ikea(page, query: str, preferred_currency: str = "INR") -> List[Dict[str, Any]]:
    products = []
    try:
        curr = (preferred_currency or "INR").upper().strip()
        domain_path = "us/en" if curr == "USD" else "in/en"
        url = f"https://www.ikea.com/{domain_path}/search/?q={urllib.parse.quote(query)}"
        logger.info(f"Playwright: Navigating to IKEA ({domain_path}): {url}")
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        
        # Wait for dynamic list loading
        await page.wait_for_timeout(4000)
        
        cards = await page.query_selector_all('.plp-fragment-wrapper, .pip-product-compact')
        for card in cards[:6]:
            title = ""
            for selector in ['.plp-price-module__title', '.pip-header-section__title-link', 'h3', 'a']:
                el = await card.query_selector(selector)
                if el:
                    txt = await el.inner_text()
                    if txt and txt.strip():
                        title = txt.strip()
                        break
            
            price = None
            for selector in ['.plp-price__integer', '.pip-price__integer', '.plp-price-module__price', '.pip-price__price']:
                el = await card.query_selector(selector)
                if el:
                    txt = await el.inner_text()
                    if txt and txt.strip():
                        price = txt.strip()
                        break
            
            link = ""
            el = await card.query_selector('a')
            if el:
                href = await el.get_attribute('href')
                if href:
                    link = href.strip()
            
            rating = None
            rating_el = await card.query_selector('.plp-rating-stars, .pip-rating-stars')
            if rating_el:
                rating = await rating_el.get_attribute('aria-label')
            
            # Scrape product image URL
            image = None
            for selector in ['img.pip-image', 'img.plp-image', 'img']:
                el = await card.query_selector(selector)
                if el:
                    src = await el.get_attribute('src') or await el.get_attribute('data-src') or await el.get_attribute('srcset')
                    if src:
                        src_strip = src.strip().split(' ')[0]
                        if src_strip.startswith('http'):
                            image = src_strip
                            break

            if title:
                full_link = f"https://www.ikea.com{link}" if link.startswith('/') else link
                products.append({
                    "title": title,
                    "price": price,
                    "store": "IKEA",
                    "url": full_link,
                    "rating": rating,
                    "reviews": 0,
                    "image": image,
                    "brand": "IKEA"
                })
    except Exception as e:
        logger.error(f"Error scraping IKEA via Playwright: {e}")
    return products

async def scrape_flipkart(page, query: str) -> List[Dict[str, Any]]:
    products = []
    try:
        url = f"https://www.flipkart.com/search?q={urllib.parse.quote(query)}"
        logger.info(f"Playwright: Navigating to Flipkart: {url}")
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Grid/list card wrappers
        cards = await page.query_selector_all('div[data-id]')
        for card in cards[:6]:
            title = ""
            anchors = await card.query_selector_all('a')
            for a in anchors:
                txt = await a.inner_text()
                txt_strip = txt.strip()
                if txt_strip and not any(c in txt_strip for c in ['₹', 'Rs.', '% off', 'Add to Compare', 'Share', 'Login']):
                    if len(txt_strip) > 5:
                        title = txt_strip
                        break
            
            link = ""
            for a in anchors:
                href = await a.get_attribute('href')
                if href and href.strip():
                    link = href.strip()
                    break
            
            price = None
            for selector in ['._30jeq3', '.Nx9bHR', '._1vC4M1', 'div.hlubn', 'div.Nx9bHR']:
                el = await card.query_selector(selector)
                if el:
                    txt = await el.inner_text()
                    if txt and txt.strip():
                        price = txt.strip()
                        break
            if not price:
                # Fallback: search inside spans, divs, anchors for short text containing ₹ or Rs. without newlines
                for el in await card.query_selector_all('span, div, a'):
                    txt = await el.inner_text()
                    if txt:
                        txt_strip = txt.strip()
                        if ('₹' in txt_strip or 'Rs.' in txt_strip) and '\n' not in txt_strip and len(txt_strip) < 30:
                            price = txt_strip
                            break
            
            image = None
            for img in await card.query_selector_all('img'):
                src = await img.get_attribute('src') or await img.get_attribute('data-src') or await img.get_attribute('srcset')
                if src:
                    src_strip = src.strip().split(' ')[0]
                    if src_strip.startswith('http'):
                        image = src_strip
                        break
            
            if title:
                full_link = f"https://www.flipkart.com{link}" if link.startswith('/') else link
                products.append({
                    "title": title,
                    "price": price,
                    "store": "Flipkart",
                    "url": full_link,
                    "rating": None,
                    "reviews": 0,
                    "image": image,
                    "brand": "Flipkart"
                })
    except Exception as e:
        logger.error(f"Error scraping Flipkart via Playwright: {e}")
    return products

async def scrape_ebay(page, query: str) -> List[Dict[str, Any]]:
    products = []
    try:
        logger.info("Playwright: Bypassing eBay bot blocks via home-to-search typing flow...")
        await page.goto("https://www.ebay.com/", timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        search_input = await page.query_selector('input#gh-ac')
        if search_input:
            await search_input.focus()
            await search_input.type(query, delay=100)
            await page.wait_for_timeout(1000)
            
            search_btn = await page.query_selector('input#gh-btn')
            if search_btn:
                await search_btn.click()
            else:
                await page.keyboard.press("Enter")
                
            await page.wait_for_timeout(5000)
            
            cards = await page.query_selector_all('.s-card, .s-item')
            for card in cards[:8]:
                title = ""
                for selector in ['.s-card__title', '.s-item__title', 'h3', 'a']:
                    el = await card.query_selector(selector)
                    if el:
                        txt = await el.inner_text()
                        if txt and txt.strip():
                            title = txt.strip()
                            break
                
                # Exclude ads / templates / navigation helpers
                if not title or "shop on ebay" in title.lower() or title.lower().strip() in ["gallery view", "opens in a new window or tab"]:
                    continue
                    
                price = None
                for selector in ['.s-card__price', '.s-item__price', '.s-item__price span', '.s-card__price span']:
                    el = await card.query_selector(selector)
                    if el:
                        price = await el.inner_text()
                        break
                        
                link = ""
                for selector in ['a.s-card__link', 'a.s-item__link', 'a']:
                    el = await card.query_selector(selector)
                    if el:
                        href = await el.get_attribute('href')
                        if href:
                            link = href.strip()
                            break
                
                image = None
                for selector in ['.s-card__image img', '.s-item__image-img img', 'img']:
                    el = await card.query_selector(selector)
                    if el:
                        src = await el.get_attribute('src') or await el.get_attribute('data-src') or await el.get_attribute('srcset')
                        if src:
                            src_strip = src.strip().split(' ')[0]
                            if src_strip.startswith('http') and "fxxj3ttftm5ltcqnto1o4baovyl" not in src_strip:
                                image = src_strip
                                break
                
                products.append({
                    "title": title,
                    "price": price,
                    "store": "eBay",
                    "url": link,
                    "rating": None,
                    "reviews": 0,
                    "image": image,
                    "brand": "eBay"
                })
        else:
            logger.warning("eBay search input not found on homepage.")
    except Exception as e:
        logger.error(f"Error scraping eBay via Playwright: {e}")
    return products

async def search_playwright(query: str, preferred_currency: str = "INR") -> List[Dict[str, Any]]:
    """
    Spawns headless Chromium via Playwright, executes web scrapers concurrently, and returns product hits.
    """
    try:
        from playwright.async_api import async_playwright
        import asyncio
    except ImportError:
        logger.warning("Playwright is not installed. Scraper fallback skipped.")
        return []
        
    products = []
    try:
        logger.info("Initializing Playwright crawler...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                     "--disable-blink-features=AutomationControlled",
                     "--no-sandbox",
                     "--disable-setuid-sandbox"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            
            # Create a separate page/tab for each merchant to run in parallel
            page_amazon = await context.new_page()
            page_ikea = await context.new_page()
            page_flipkart = await context.new_page()
            page_ebay = await context.new_page()
            
            # Add anti-detection scripts
            for page in [page_amazon, page_ikea, page_flipkart, page_ebay]:
                await page.add_init_script("delete navigator.__proto__.webdriver;")
            
            logger.info("Executing concurrent scraping requests for Amazon, IKEA, Flipkart, and eBay...")
            
            # Gather tasks
            amazon_task = scrape_amazon(page_amazon, query, preferred_currency=preferred_currency)
            ikea_task = scrape_ikea(page_ikea, query, preferred_currency=preferred_currency)
            flipkart_task = scrape_flipkart(page_flipkart, query)
            ebay_task = scrape_ebay(page_ebay, query)
            
            results = await asyncio.gather(
                amazon_task,
                ikea_task,
                flipkart_task,
                ebay_task,
                return_exceptions=True
            )
            
            # Unpack results safely
            amazon_items, ikea_items, flipkart_items, ebay_items = results
            
            if isinstance(amazon_items, list):
                products.extend(amazon_items)
            else:
                logger.error(f"Amazon scraper task encountered an error: {amazon_items}")
                
            if isinstance(ikea_items, list):
                products.extend(ikea_items)
            else:
                logger.error(f"IKEA scraper task encountered an error: {ikea_items}")
                
            if isinstance(flipkart_items, list):
                products.extend(flipkart_items)
            else:
                logger.error(f"Flipkart scraper task encountered an error: {flipkart_items}")
                
            if isinstance(ebay_items, list):
                products.extend(ebay_items)
            else:
                logger.error(f"eBay scraper task encountered an error: {ebay_items}")
            
            await browser.close()
    except Exception as e:
        logger.error(f"Playwright execution encountered an error: {e}")
        
    return products
