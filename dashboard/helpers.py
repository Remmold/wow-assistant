def format_wow_currency(copper_total):
    """Convert total copper to WoW gold/silver/copper format"""
    if copper_total is None or copper_total == 0:
        return "0c"
    
    copper_total = int(copper_total)
    
    # WoW currency: 1 gold = 100 silver = 10000 copper
    gold = copper_total // 10000
    remaining = copper_total % 10000
    silver = remaining // 100
    copper = remaining % 100
    
    parts = []
    if gold > 0:
        parts.append(f"{gold}g")
    if silver > 0:
        parts.append(f"{silver}s")
    if copper > 0 or len(parts) == 0:
        parts.append(f"{copper}c")
    
    return " ".join(parts)

def format_time_left(time_left_raw):
    """Convert WoW time left format to readable format"""
    if not time_left_raw:
        return "Unknown"
    
    time_mapping = {
        "VERY_LONG": "24 - 48h",
        "LONG": "12 - 24h", 
        "MEDIUM": "2 - 12h",
        "SHORT": "0 - 2h"
    }
    
    return time_mapping.get(time_left_raw.upper(), time_left_raw.replace("_", " ").title())