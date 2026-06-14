import re
from typing import Optional, Dict, Any

def normalize_price(price_input: Any) -> Optional[float]:
    """
    Parses a price input (string, int, or float) to a standard float.
    Cleans currency symbols like ₹, $, Rs., commas, and trailing whitespace.
    """
    if price_input is None:
        return None
    if isinstance(price_input, (int, float)):
        return float(price_input)
        
    s = str(price_input).strip()
    if not s:
        return None
        
    # Remove commas
    s = s.replace(",", "")
    
    # Try finding numerical components
    # Matches patterns like 4999.00 or 4999
    match = re.search(r'(\d+(?:\.\d+)?)', s)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

def normalize_rating(rating_input: Any) -> Optional[float]:
    """
    Parses a rating string/float to a clean float (e.g. 4.5).
    Bounds between 0.0 and 5.0.
    """
    if rating_input is None:
        return None
    if isinstance(rating_input, (int, float)):
        val = float(rating_input)
        return max(0.0, min(5.0, val))
        
    s = str(rating_input).strip()
    if not s:
        return None
        
    # E.g. "4.5 out of 5 stars"
    match = re.search(r'(\d+(?:\.\d+)?)', s)
    if match:
        try:
            val = float(match.group(1))
            # If scale is out of 10, normalize to out of 5
            if val > 5.0 and val <= 10.0:
                val = val / 2.0
            return max(0.0, min(5.0, val))
        except ValueError:
            return None
    return None

def normalize_reviews(reviews_input: Any) -> int:
    """
    Normalizes review count strings/integers to standard integers.
    Converts '1.2k' -> 1200, handles commas, parentheses.
    """
    if reviews_input is None:
        return 0
    if isinstance(reviews_input, int):
        return reviews_input
    if isinstance(reviews_input, float):
        return int(reviews_input)
        
    s = str(reviews_input).strip().lower()
    if not s:
        return 0
        
    # Handle 'k' / 'm' multipliers (e.g., 1.2k)
    k_match = re.search(r'(\d+(?:\.\d+)?)\s*k', s)
    if k_match:
        try:
            return int(float(k_match.group(1)) * 1000)
        except ValueError:
            pass

    m_match = re.search(r'(\d+(?:\.\d+)?)\s*m', s)
    if m_match:
        try:
            return int(float(m_match.group(1)) * 1000000)
        except ValueError:
            pass
            
    # Clean characters
    s = s.replace(",", "").replace("(", "").replace(")", "")
    match = re.search(r'(\d+)', s)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return 0
    return 0

RATES = {
    "INR": 1.0,
    "USD": 83.5,
    "EUR": 90.0,
    "GBP": 106.0,
    "CAD": 61.0,
    "AUD": 55.5,
    "JPY": 0.53,
    "SGD": 62.0,
    "AED": 22.7,
    "CNY": 11.5
}

def extract_currency(price_input: Any, default_currency: str = "INR") -> str:
    """
    Parses currency symbol from price string.
    Supports INR, USD, EUR, GBP, CAD, AUD, JPY, SGD, AED, CNY.
    """
    if price_input is None:
        return default_currency
    s = str(price_input).strip().lower()
    
    # Check currency-specific codes and formats first
    if "cad" in s or "c$" in s:
        return "CAD"
    if "aud" in s or "a$" in s:
        return "AUD"
    if "sgd" in s or "s$" in s:
        return "SGD"
    if "aed" in s or "dirham" in s:
        return "AED"
    if "cny" in s or "rmb" in s:
        return "CNY"
    if "jpy" in s or "yen" in s:
        return "JPY"
        
    # Check general symbols
    if "$" in s or "usd" in s:
        return "USD"
    if "€" in s or "eur" in s:
        return "EUR"
    if "£" in s or "gbp" in s:
        return "GBP"
    if "¥" in s:
        # Default ¥ symbol fallback (could be JPY or CNY, default to JPY)
        return "JPY"
    if "₹" in s or "rs" in s or "inr" in s:
        return "INR"
    return default_currency

def convert_currency(amount: float, from_curr: str, to_curr: str) -> float:
    """
    Converts amount between USD, EUR, GBP, and INR using simple lookup rates.
    """
    if not amount:
        return 0.0
    from_curr = (from_curr or "INR").upper().strip()
    to_curr = (to_curr or "INR").upper().strip()
    if from_curr == to_curr:
        return amount
    # Convert to base (INR)
    inr_val = amount * RATES.get(from_curr, 1.0)
    # Convert from INR to target
    target_val = inr_val / RATES.get(to_curr, 1.0)
    return target_val

def normalize_product(raw: Dict[str, Any], query: str = "", default_currency: str = "INR") -> Dict[str, Any]:
    """
    Standardizes a raw product dictionary to match the database schema format.
    Determines actual product currency based on the scraped content and shop source.
    """
    store_name = str(raw.get("store", "")).lower()
    inferred_default = default_currency
    if "ebay" in store_name:
        inferred_default = "USD"
    elif any(kw in store_name for kw in ["amazon", "flipkart", "ikea"]):
        inferred_default = "INR"

    currency = extract_currency(raw.get("price"), inferred_default)

    return {
        "title": str(raw.get("title", "")).strip(),
        "brand": str(raw.get("brand", "")).strip() if raw.get("brand") else None,
        "price": normalize_price(raw.get("price")),
        "currency": currency,
        "rating": normalize_rating(raw.get("rating")),
        "reviews": normalize_reviews(raw.get("reviews")),
        "dimensions": str(raw.get("dimensions", "")).strip() if raw.get("dimensions") else None,
        "availability": str(raw.get("availability", "Available")).strip(),
        "store": str(raw.get("store", "")).strip() or "Unknown",
        "url": str(raw.get("url", "")).strip() or None,
        "image": str(raw.get("image", "")).strip() or None,
        "searched_query": query.strip()
    }
