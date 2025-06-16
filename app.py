import streamlit as st

st.set_page_config(layout="wide", page_title="WoW API Dashboard")
st.title(":rainbow[WoW API Dashboard]")

# --------------- SIDEBAR ---------------
with st.sidebar:
    st.subheader("Filter your search")
    # Era (expansion) selection
    era_list = ["Classic", "TBC", "WotLK", "Cataclysm", "MoP", "WoD", "Legion", "BfA", "SL", "DF", "TWW"]
    era_full_list=["The Burning Crusade (2007)",
                "Wrath of the Lich King (2008)",
                "Cataclysm (2010)",
                "Mists of Pandaria (2012)",
                "Warlods of Draenor (2014)",
                "Legion (2016)",
                "Battle for Azeroth (2018)",
                "Shadowlands (2020)",
                "Dragonflight (2022)",
                "The War Within (2024)"]
    era = st.selectbox(
        label = "Era (expansion):",
        options = era_full_list,
        key = "sidebar_era"
    )

    # Region selection
    region = st.selectbox(
        label = "Region:",
        options = ["Europe", "Americas", "Asia"],
        key = "sidebar_region"
    )

    # Realm selection
    realms = st.multiselect(
        label = "Realm(s):",
        options = "",
        key = "sidebar_realms"
    )

    # Item class (category) selection
    item_class = st.selectbox(
        label = "Item Category:",
        options = ["All", "Consumables", "Weapons", "Armor"],
        key = "sidebar_item_class"
    )

    # Item subclass (subcategory) selection
    item_subclass = st.multiselect(
        label = "Item Sub-category:",
        options = "",
        key = "sidebar_item_subclass"
    )

    # Item rarity range
    rarity_list = [f"Common", "Uncommon", "Rare", "Epic", "Legendary"]
    rarity_color_list = [f"⚪", "🟢", "🔵", "🟣", "🟠"]
    lowest_rarity, highest_rarity = st.select_slider(
        label = "Rarity:",
        options = rarity_list,
        value = (rarity_list[0], rarity_list[4]),
        help = "Filter items by rarity (from lowest to highest), for example Rare to Epic.",
        key = "sidebar_rarity"
    )

    # Item level (ilvl) range
    start_ilvl, end_ilvl = st.select_slider(
        "Item level (ilvl):",
        options = [x for x in range(1, 685)],
        value = (1, 684),
        help = "Filter items by item level.",
        key = "sidebar_item_level"
    )

    # Req. level range
    start_lvl, end_lvl = st.select_slider(
        "Required level:",
        options = [x for x in range(1, 81)],
        value = (1, 80),
        help = "Filter items by required player level.",
        key = "sidebar_req_level"
    )
    
    # Include out-of-stock checkbox
    include_out_of_stock = st.checkbox(
        "Include out-of-stock",
        help = "Include out-of-stock items.",
        key="sidebar_out_of_stock"
    )
    
    # Only below vendor price checkbox
    only_below_vendor_price = st.checkbox(
        "Only below vendor price",
        help = "Only show auctions with posting price lower than vendor price.",
        key="sidebar_only_below_vendor_price"
    )