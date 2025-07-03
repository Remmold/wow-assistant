# ---------- Rarity-related things (dict, list and formatting) ----------
RARITY_COLORS = {
    "Poor": "#9d9d9d",
    "Common": "#ffffff",
    "Uncommon": "#1eff00",
    "Rare": "#0070dd",
    "Epic": "#a335ee",
    "Legendary": "#ff8000",
    "Artifact": "#e6cc80",
    "Heirloom": "#00ccff",
    "Heirloom Artifact": "#00ccff",
    "Wow Token": "#ffd700"
}

RARITY_LIST = ["Poor", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Artifact", "Heirloom Artifact", "Wow Token"]

def get_rarity_color(rarity_name):
    return RARITY_COLORS.get(rarity_name, "#ffffff")

# ---------- Currency-related formatting ----------
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

# ---------- Time-related formatting ----------
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

def get_time_color(time_left_formatted):
    if "0 - 2h" in time_left_formatted:
        return "#ff4444"  # Red
    elif "2 - 12h" in time_left_formatted:
        return "#ffaa00"  # Orange
    elif "12 - 24h" in time_left_formatted and "Very" not in time_left_formatted:
        return "#44ff44"  # Green
    elif "24 - 48h" in time_left_formatted:
        return "#4444ff"  # Blue
    return "#ffffff"  # Default white

def format_auction_listings(df):
    if df.empty:
        return df
    df = df.copy()
    df["Price_Formatted"] = df["Price"].apply(format_wow_currency)
    df["Time_Left_Formatted"] = df["Time left"].apply(format_time_left)
    df["price_color"] = "#FFD700"
    df["time_color"] = df["Time_Left_Formatted"].apply(get_time_color)
    return df