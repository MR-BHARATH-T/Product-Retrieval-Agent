from typing import List, Dict, Any
import difflib

def is_similar(str1: str, str2: str, threshold: float = 0.85) -> bool:
    """Computes title similarity using Python's SequenceMatcher."""
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()
    if s1 == s2:
        return True
    ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
    return ratio >= threshold

def deduplicate_products(products: List[Dict[str, Any]], similarity_threshold: float = 0.85) -> List[Dict[str, Any]]:
    """
    Deduplicates a list of normalized products.
    If a duplicate is found (matching URLs or similar titles from the same store),
    it updates the existing entry if the new one has better review count or rating.
    """
    unique_products: List[Dict[str, Any]] = []
    
    for p in products:
        title = p.get("title", "")
        if not title:
            continue
            
        is_dup = False
        for existing in unique_products:
            # Check URL match
            if p.get("url") and existing.get("url") and p.get("url").strip() == existing.get("url").strip():
                is_dup = True
                # Merge statistics
                if p.get("reviews", 0) > existing.get("reviews", 0):
                    existing["reviews"] = p["reviews"]
                if p.get("rating") is not None and (existing.get("rating") is None or p["rating"] > existing["rating"]):
                    existing["rating"] = p["rating"]
                break
                
            # Check title similarity and store match
            if is_similar(title, existing.get("title", ""), similarity_threshold):
                store_p = str(p.get("store", "")).lower().strip()
                store_e = str(existing.get("store", "")).lower().strip()
                if store_p == store_e or not store_p or not store_e:
                    is_dup = True
                    # Keep the one with more reviews/better rating
                    if p.get("reviews", 0) > existing.get("reviews", 0):
                        existing["reviews"] = p["reviews"]
                        if p.get("price") is not None:
                            existing["price"] = p["price"]
                        if p.get("image") and not existing.get("image"):
                            existing["image"] = p["image"]
                    break
        
        if not is_dup:
            unique_products.append(p)
            
    return unique_products
