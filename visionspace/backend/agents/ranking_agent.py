import logging
from typing import List, Dict, Any, Optional
from visionspace.backend.utils.parser import parse_dimensions, parse_room_dimensions

logger = logging.getLogger(__name__)

def rank_and_filter_products(
    products: List[Dict[str, Any]],
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    room_dimensions: Optional[str] = None,
    preferred_currency: Optional[str] = "INR"
) -> List[Dict[str, Any]]:
    """
    Ranks and filters a list of products.
    - Filters out items exceeding max_price or falling below min_rating.
    - Filters out items that physically do not fit in the room dimensions (if dimensions are specified).
    - Sorts remaining items by Availability, Rating (descending), Reviews (descending), and Price (ascending).
    """
    filtered = []
    room_parsed = parse_room_dimensions(room_dimensions) if room_dimensions else None
    
    if room_parsed:
        rw, rd = room_parsed
        logger.info(f"Filtering items for room size: {rw:.1f}cm x {rd:.1f}cm")

    for p in products:
        # Price check
        price = p.get("price")
        p_curr = p.get("currency") or "INR"
        if max_price is not None and price is not None:
            from visionspace.backend.utils.normalizer import convert_currency
            price_converted = convert_currency(price, p_curr, preferred_currency)
            if price_converted > max_price:
                logger.debug(f"Filtered out '{p['title']}' due to converted price {price_converted} {preferred_currency} > {max_price}")
                continue
                
        # Rating check
        rating = p.get("rating")
        if min_rating is not None and rating is not None:
            if rating < min_rating:
                logger.debug(f"Filtered out '{p['title']}' due to rating {rating} < {min_rating}")
                continue
                
        # Room dimensions check
        dimensions_str = p.get("dimensions")
        if room_parsed and dimensions_str:
            prod_dims = parse_dimensions(dimensions_str)
            if prod_dims:
                pl = prod_dims.get("length")
                pw = prod_dims.get("width")
                
                if pl and pw:
                    rw, rd = room_parsed
                    # Product can be placed normal or rotated 90 degrees
                    fits_normal = (pl <= rw) and (pw <= rd)
                    fits_rotated = (pw <= rw) and (pl <= rd)
                    
                    if not (fits_normal or fits_rotated):
                        logger.info(
                            f"Filtered out '{p['title']}' because size ({pl:.1f}x{pw:.1f} cm) "
                            f"exceeds room size ({rw:.1f}x{rd:.1f} cm)."
                        )
                        continue
                        
        filtered.append(p)
        
    # Multi-level sorting key helper (lower value is better)
    # Prioritizes exact currency matches first as requested by the user
    pref_curr = (preferred_currency or "INR").upper().strip()
    
    def get_sort_key(item):
        item_curr = (item.get("currency") or "INR").upper().strip()
        currency_mismatch = 0 if item_curr == pref_curr else 1
        
        is_avail = 0 if str(item.get("availability", "")).lower() == "available" else 1
        rating_val = item.get("rating") or 0.0
        reviews_val = item.get("reviews") or 0
        price_val = item.get("price") or float('inf')
        
        return (currency_mismatch, is_avail, -rating_val, -reviews_val, price_val)
        
    filtered.sort(key=get_sort_key)
    return filtered
