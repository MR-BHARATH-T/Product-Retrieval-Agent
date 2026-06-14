import re
from typing import Dict, Optional, Tuple

def parse_dimensions(dim_str: Optional[str]) -> Optional[Dict[str, Optional[float]]]:
    """
    Parses a dimensions string into length, width, and height in standard centimeters (cm).
    Handles patterns like:
      - '90 x 45 x 75 cm'
      - '3 x 1.5 ft'
      - 'L 90 * W 45 * H 75'
    Returns dict: {"length": cm, "width": cm, "height": cm} or None.
    """
    if not dim_str:
        return None
    
    # Clean the string
    s = dim_str.lower().strip()
    
    # Extract numbers
    numbers = re.findall(r'(\d+(?:\.\d+)?)', s)
    if not numbers:
        return None
    
    # Check if units are feet (ft, feet, foot, ')
    is_ft = any(unit in s for unit in ["ft", "foot", "feet", "'", "’"])
    is_inch = any(unit in s for unit in ["in", "inch", "inches", '"'])
    
    multiplier = 1.0
    if is_ft:
        multiplier = 30.48
    elif is_inch:
        multiplier = 2.54
        
    values = [float(x) for x in numbers]
    
    result = {
        "length": None,
        "width": None,
        "height": None
    }
    
    if len(values) >= 3:
        result = {
            "length": values[0] * multiplier,
            "width": values[1] * multiplier,
            "height": values[2] * multiplier
        }
    elif len(values) == 2:
        result = {
            "length": values[0] * multiplier,
            "width": values[1] * multiplier,
            "height": None
        }
    elif len(values) == 1:
        result = {
            "length": values[0] * multiplier,
            "width": None,
            "height": None
        }
    else:
        return None
        
    return result

def parse_room_dimensions(room_str: Optional[str]) -> Optional[Tuple[float, float]]:
    """
    Parses room dimensions like "10x12 ft" or "300x360 cm".
    Returns (width_cm, depth_cm) or None.
    """
    if not room_str:
        return None
    s = room_str.lower().strip()
    numbers = re.findall(r'(\d+(?:\.\d+)?)', s)
    if len(numbers) < 2:
        return None
        
    is_ft = any(unit in s for unit in ["ft", "foot", "feet", "'", "’"])
    is_inch = any(unit in s for unit in ["in", "inch", "inches", '"'])
    
    multiplier = 1.0
    if is_ft:
        multiplier = 30.48
    elif is_inch:
        multiplier = 2.54
        
    return (float(numbers[0]) * multiplier, float(numbers[1]) * multiplier)
