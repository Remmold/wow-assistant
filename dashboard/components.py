import streamlit as st
from.utils import fetch_data_from_db

# ---------- Constants ---------
RARITY_LIST = ["Poor", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Artifact", "Heirloom Artifact", "Wow Token"]

# ---------- Functions for filling sidebar component options ----------

# Function for getting realm list
def _get_realm_groups_list():
    query = f"""
        SELECT
            DISTINCT realm somethingsomethingsomething
        FROM refined.mart_filter
    """
    df = fetch_data_from_db(query)
    return df["realm somethingsomethingsomething"].tolist() if not df.empty else []

# Function for item class list
@st.cache_data
def _get_item_class_list():
    query = f"""
        SELECT
            DISTINCT item_class_name
        FROM refined.mart_item_class_subclass
    """
    df = fetch_data_from_db(query)
    return df["item_class_name"].tolist() if not df.empty else []

# Function for item subclass list
def _get_item_subclass_list(current_item_class):
    # Build where clause based on current item_class choice
    if current_item_class == "All":
        where_clause = ""
    else:
        where_clause = f"WHERE item_class_name == '{current_item_class}'"

    query = f"""
        SELECT
            DISTINCT item_subclass_name
        FROM refined.mart_item_class_subclass
        {where_clause}
        ORDER BY item_subclass_name
    """
    df = fetch_data_from_db(query)
    return df["item_subclass_name"].tolist() if not df.empty else []

# Function for item type list
def _get_item_type_list(current_item_subclass):
    # Build where clause based on current item_subclass choice
    if current_item_subclass == "All":
        where_clause = ""
    else:
        where_clause = f"WHERE item_subclass_name == '{current_item_subclass}'"

    query = f"""
        SELECT
            DISTINCT item_type
        FROM refined.mart_item_class_subclass
        {where_clause}
        ORDER BY item_type
    """
    df = fetch_data_from_db(query)
    return df["item_type"].tolist() if not df.empty else []


# ---------- Sidebar components ----------

# Free-text-search - TEXT INPUT
def free_text_search():
    st.text_input(
        label = "🔎 Search by name:",
        placeholder = "Search by item name",
        key = "sidebar_free_text_search"
    )

# Region selection - SELECTBOX
def region_selection():
    st.selectbox(
        label = "🌎 Region:",
        options = ["Europe"],
        key = "sidebar_region"
    )

# Realm Group selection - MULTISELECT
def realm_group_selection():
    st.multiselect(
        label = "Realm Group(s):",
        options = ["Khadgar"],
        # options = _get_realm_groups_list(),
        key = "sidebar_realm_groups"
    )

# Item class (category) selection - SELECTBOX
def item_class_selection():
    options = ["All"] + _get_item_class_list()
    st.selectbox(
        label = "**Item Category** 📦",
        options = options,
        key = "sidebar_item_class"
    )

# Item subclass (subcategory) selection - SELECTBOX
def item_subclass_selection(current_item_class):
    options = ["All"] + _get_item_subclass_list(current_item_class)
    st.selectbox(
        label = "Item Sub-category:",
        options = options,
        key = "sidebar_item_subclass"
    )

# Item subclass (subcategory) selection - MULTISELECT
def item_type_selection(current_item_subclass):
    options = ["All"] + _get_item_type_list(current_item_subclass)
    st.selectbox(
        label = "Item Type:",
        options = options,
        key = "sidebar_item_type"
    )

# Item rarity range - RANGE SLIDER
def item_rarity_range():
    rarity_color_list = [f"⚪", "🟢", "🔵", "🟣", "🟠"] # 'Poor' rarity is missing grey blob
    lowest_rarity, highest_rarity = st.select_slider(
        label = "Rarity:",
        options = RARITY_LIST,
        value = (RARITY_LIST[0], RARITY_LIST[5]),
        help = "Filter items by rarity (from lowest to highest), for example Rare to Epic.",
        key = "sidebar_rarity_old"
    )

# Item rarity selection - MULTISELECT
def item_rarity_selection():
    rarity_color_list = [f"⚪", "🟢", "🔵", "🟣", "🟠"] # 'Poor' rarity is missing grey blob
    st.multiselect(
        label = "Rarity:",
        options = RARITY_LIST,
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
        help = "Only show auctions with buyout price lower than vendor price.",
        key="sidebar_only_below_vendor_price"
    )

# ---------- Main Sidebar ----------
def sidebar():
    with st.sidebar:
        # Dashboard header
        st.markdown(f"<span style='font-size:2em;'>:rainbow[WoW API Dashboard]</span>", unsafe_allow_html=True)

        # Selectbox for page selection
        current_page = st.selectbox(
            label = "Page selection",
            options = ["Items", "Auction House", "Realms"],
            key = "sidebar_page_selection",
            index=1
        )

        if current_page == "Items":
            items_page_filters()
        elif current_page == "Auction House":
            auctions_page_filters()
        else:
            st.write("No filters available for the current page.")

# Filters for page "Items"
def items_page_filters():
    free_text_search()
    item_class_selection()
    current_item_class = st.session_state.get("sidebar_item_class", "All")
    item_subclass_selection(current_item_class)
    current_item_subclass = st.session_state.get("sidebar_item_subclass", [])
    item_type_selection(current_item_subclass)
    # item_rarity_range() # Old slider
    item_rarity_selection()
    item_level_range()
    req_level_range()

# Filters for page "Auction House"
def auctions_page_filters():
    region_selection()
    realm_group_selection()
    free_text_search()
    item_class_selection()
    current_item_class = st.session_state.get("sidebar_item_class", "All")
    item_subclass_selection(current_item_class)
    current_item_subclass = st.session_state.get("sidebar_item_subclass", [])
    item_type_selection(current_item_subclass)
    # item_rarity_range() # Old slider
    item_rarity_selection()
    item_level_range()
    req_level_range()
    out_of_stock_checkbox()
    only_below_vendor_price_checkbox()


# ---------- Main Section with page-based content ----------
def main_section():
    # Checks the current page choice
    current_page = st.session_state.get("sidebar_page_selection")

    # ----- ITEMS page -----
    if current_page == "Items":
        from .items import items_page
        items_page()

    # ----- AUCTION HOUSE page -----
    elif current_page == "Auction House":
        from .auction_house import auction_house_page
        auction_house_page()

    # ----- REALMS page -----
    elif current_page == "Realms":
        st.header("Realms")

    # ----- DEFAULT case -----
    else:
        st.markdown("Select a page in the sidebar.")
