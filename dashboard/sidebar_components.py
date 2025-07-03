"""
All Streamlit UI functions for sidebar widgets (selectboxes, sliders, checkboxes, etc).
- Sidebar filter configs.
- filter-related functions (layout/rendering).
"""

import streamlit as st
from .sidebar_utils import _get_item_class_list, _get_item_subclass_list, _get_item_type_list, _get_realm_group_ids_for_realms, _get_all_realms
from .helpers import RARITY_LIST


# ---------- Sidebar UI functions ----------
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

# Realm selection - MULTISELECT
def realm_selection():
    st.multiselect(
        label = "Realm(s):",
        options = _get_all_realms(),
        key = "sidebar_realms"
    )

# Item class (category) selection - SELECTBOX
def item_class_selection():
    options = ["All"] + _get_item_class_list()
    st.selectbox(
        label = "📦 Item Category:",
        options = options,
        key = "sidebar_item_class"
    )

# Item subclass (subcategory) selection - SELECTBOX
def item_subclass_selection():
    current_item_class = st.session_state.get("sidebar_item_class", "All")
    options = ["All"] + _get_item_subclass_list(current_item_class)
    st.selectbox(
        label = "Item Sub-category:",
        options = options,
        key = "sidebar_item_subclass"
    )

# Item subclass (subcategory) selection - MULTISELECT
def item_type_selection():
    current_item_subclass = st.session_state.get("sidebar_item_subclass", [])
    options = ["All"] + _get_item_type_list(current_item_subclass)
    st.selectbox(
        label = "Item Type:",
        options = options,
        key = "sidebar_item_type"
    )

# Item rarity range - RANGE SLIDER
def item_rarity_range():
    st.select_slider(
        label = "⭐ asdasdRarity:",
        options = RARITY_LIST,
        value = (RARITY_LIST[0], RARITY_LIST[5]),
        help = "Filter items by rarity (from lowest to highest), for example Rare to Epic.",
        key = "sidebar_rarity_old"
    )

# Item rarity selection - MULTISELECT
def item_rarity_selection():
    st.multiselect(
        label = "✨ Rarity:",
        options = RARITY_LIST,
        key = "sidebar_rarity"
    )

# Item level (ilvl) range - RANGE SLIDER
def item_level_range():
    st.select_slider(
        "Item level (ilvl):",
        options = [x for x in range(1, 685)],
        value = (1, 684),
        help = "Filter items by item level.",
        key = "sidebar_item_level"
    )

# Req. level range - RANGE SLIDER
def req_level_range():
    st.select_slider(
        "Required level:",
        options = [x for x in range(1, 81)],
        value = (1, 80),
        help = "Filter items by required player level.",
        key = "sidebar_req_level"
    )

# Include out-of-stock checkbox - CHECKBOX
def out_of_stock_checkbox():
    st.checkbox(
        "Include out-of-stock",
        help = "Include out-of-stock items.",
        key="sidebar_out_of_stock"
    )

# Only below vendor price checkbox - CHECKBOX
def only_below_vendor_price_checkbox():
    st.checkbox(
        "Only below vendor price",
        help = "Only show auctions with buyout price lower than vendor price.",
        key="sidebar_only_below_vendor_price"
    )

# ---------- Filter Configs ----------
ITEMS_FILTERS = [
    #free_text_search, # Moved to main section
    item_class_selection,
    item_subclass_selection,
    item_type_selection,
    item_rarity_selection,
    item_level_range,
    req_level_range
]
AUCTIONS_FILTERS = [
    # region_selection, # Commented out for now since only Europe available
    realm_selection,
    #free_text_search, # Moved to main section
    item_class_selection,
    item_subclass_selection,
    item_type_selection,
    item_rarity_selection,
    item_level_range,
    req_level_range,
    # "out_of_stock_checkbox", # Not necessary in the moment due to no auctions history
    # "only_below_vendor_price_checkbox" # Skipped for now - bots are too fast :'(
]

def render_sidebar_filters(filter_list):
    for filter_func in filter_list:
        filter_func()

# Filters for page "Items"
def items_page_filters():
    render_sidebar_filters(ITEMS_FILTERS)
    
# Filters for page "Auction House"
def auctions_page_filters():
    render_sidebar_filters(AUCTIONS_FILTERS)