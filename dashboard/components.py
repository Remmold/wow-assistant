import streamlit as st
from .items import items_page

# ---------- Constants ---------
RARITY_LIST = ["Poor", "Common", "Uncommon", "Rare", "Epic", "Legendary"]

# ---------- Sidebar components ----------

# Era (expansion) selection - SELECTBOX
def era_selection():
    era_list = ["Classic", "TBC", "WotLK", "Cataclysm", "MoP", "WoD", "Legion", "BfA", "SL", "DF", "TWW"]
    era_full_list=[
        "The Burning Crusade (2007)",
        "Wrath of the Lich King (2008)",
        "Cataclysm (2010)",
        "Mists of Pandaria (2012)",
        "Warlods of Draenor (2014)",
        "Legion (2016)",
        "Battle for Azeroth (2018)",
        "Shadowlands (2020)",
        "Dragonflight (2022)",
        "The War Within (2024)"
    ]
    era = st.selectbox(
        label = "Era (expansion):",
        options = era_full_list,
        key = "sidebar_era"
    )

# Region selection - SELECTBOX
def region_selection():
    region = st.selectbox(
        label = "Region:",
        options = ["Europe", "Americas", "Asia"],
        key = "sidebar_region"
    )

# Realm selection - MULTISELECT
def realm_selection():
    realms = st.multiselect(
        label = "Realm(s):",
        options = "",
        key = "sidebar_realms"
    )

# Item class (category) selection - SELECTBOX
def item_class_selection():
    item_class = st.selectbox(
        label = "Item Category:",
        options = ["All", "Consumables", "Weapons", "Armor"],
        key = "sidebar_item_class"
    )

# Item subclass (subcategory) selection - MULTISELECT
def item_subclass_selection():
    item_subclass = st.multiselect(
        label = "Item Sub-category:",
        options = "",
        key = "sidebar_item_subclass"
    )

# Item rarity range - RANGE SLIDER
def item_rarity_range():
    rarity_color_list = [f"⚪", "🟢", "🔵", "🟣", "🟠"] # 'Poor' rarity is missing grey blob
    lowest_rarity, highest_rarity = st.select_slider(
        label = "Rarity:",
        options = RARITY_LIST,
        value = (RARITY_LIST[0], RARITY_LIST[5]),
        help = "Filter items by rarity (from lowest to highest), for example Rare to Epic.",
        key = "sidebar_rarity"
    )

# Item level (ilvl) range - RANGE SLIDER
def item_level_range():
    start_item_lvl, end_item_lvl = st.select_slider(
        "Item level (ilvl):",
        options = [x for x in range(1, 685)],
        value = (1, 684),
        help = "Filter items by item level.",
        key = "sidebar_item_level"
    )

# Req. level range - RANGE SLIDER
def req_level_range():
    start_req_lvl, end_req_lvl = st.select_slider(
        "Required level:",
        options = [x for x in range(1, 81)],
        value = (1, 80),
        help = "Filter items by required player level.",
        key = "sidebar_req_level"
    )

# Include out-of-stock checkbox - CHECKBOX
def out_of_stock_checkbox():
    include_out_of_stock = st.checkbox(
        "Include out-of-stock",
        help = "Include out-of-stock items.",
        key="sidebar_out_of_stock"
    )

# Only below vendor price checkbox - CHECKBOX
def only_below_vendor_price_checkbox():
    only_below_vendor_price = st.checkbox(
        "Only below vendor price",
        help = "Only show auctions with posting price lower than vendor price.",
        key="sidebar_only_below_vendor_price"
    )

# ---------- Main Sidebar ----------
def sidebar():
    with st.sidebar:
        # Selectbox for page selection
        current_page = st.selectbox(
            label = "Page selection",
            options = ["Items", "Auction House", "Realms"],
            key = "sidebar_page_selection"
        )

        if current_page == "Items":
            items_page_filters()
        elif current_page == "Auction House":
            auctions_page_filters()
        else:
            st.write("No filters available for the current page.")

# Filters for page "Items"
def items_page_filters():
    item_class_selection()
    item_subclass_selection()
    item_rarity_range()
    item_level_range()
    req_level_range()

# Filters for page "Auction House"
def auctions_page_filters():
    era_selection()
    region_selection()
    realm_selection()
    item_class_selection()
    item_subclass_selection()
    item_rarity_range()
    item_level_range()
    req_level_range()
    out_of_stock_checkbox()
    only_below_vendor_price_checkbox()


# ---------- Main Section with page-based content ----------
def main_section():
    # Checks the current page choice
    current_page = st.session_state.get("sidebar_page_selection")

    if current_page == "Items":
        items_page()
    elif current_page == "Auction House":
        st.header("Auction House")
    elif current_page == "Realms":
        st.header("Realms")
    else:
        items_page()