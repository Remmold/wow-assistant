import pandas as pd
import streamlit as st
from wow_api_dlt.db import DuckDBConnection
from pathlib import Path

# Temporary (until database is on a server)
working_directory = Path(__file__).resolve().parent.parent
dbt_folder = "wow_api_dbt"
db_filename = "wow_api_data.duckdb" # Database file name
db_path = working_directory / dbt_folder / db_filename # Full path to the database file

# Function for fetching data from the database
def fetch_data_from_db(query: str, params=None) -> pd.DataFrame:
    with DuckDBConnection(db_path) as conn:
        return conn.query(query, params)

# Function for getting sidebar filters
def get_sidebar_filters():
    filters = {
        "region": st.session_state.get("sidebar_region"),
        "realms": st.session_state.get("sidebar_realms"),
        "search_text": st.session_state.get("sidebar_free_text_search", ""),
        "item_class": st.session_state.get("sidebar_item_class"),
        "item_subclass": st.session_state.get("sidebar_item_subclass"),
        "item_type": st.session_state.get("sidebar_item_type"),
        "item_rarity": st.session_state.get("sidebar_rarity"),
    }

    # Get item level (and sort it)
    item_level = st.session_state.get("sidebar_item_level")
    if item_level:
        filters["start_item_lvl"], filters["end_item_lvl"] = sorted(item_level)
    else:
        filters["start_item_lvl"], filters["end_item_lvl"] = None, None

    # Get req. level (and sort it)
    req_level = st.session_state.get("sidebar_req_level")
    if req_level:
        filters["start_req_lvl"], filters["end_req_lvl"] = sorted(req_level)
    else:
        filters["start_req_lvl"], filters["end_req_lvl"] = None, None

    # Get checkbox values
    filters["include_out_of_stock"] = st.session_state.get("sidebar_out_of_stock")
    filters["only_below_vendor_price"] = st.session_state.get("sidebar_only_below_vendor_price")

    return filters

# Realm(s) filter
def _realms_filter(filters, conditions) -> list:
    if filters["realms"]:
        conditions.append(
            f"realm IN ({filters['realms']})" # Name or ID?
        )
    return conditions

# Search text filter
def _search_text_filter(filters, conditions) -> list:
    """Adds a search text filter to the conditions."""
    search_text = filters.get("search_text", "")
    if search_text:
        # Escape single quotes in search text
        escaped_text = search_text.replace("'", "''")
        conditions.append(
            f"item_name ILIKE '%{escaped_text}%'"
        )
    return conditions

# Item category filter
def _item_class_filter(filters, conditions) -> list:
    # Skip filter if "All" is selected or not set
    if filters["item_class"] and filters["item_class"] != "All":
        conditions.append(
            f"item_class_name = '{filters['item_class']}'"
        )
    return conditions

# Item subcategory filter
def _item_subclass_filter(filters, conditions) -> list:
    # Skip filter if "All" is selected or not set
    if filters["item_subclass"] and filters["item_subclass"] != "All":
        conditions.append(
            f"item_subclass_name = '{filters['item_subclass']}'"
        )
    return conditions

# Item type filter
def _item_type_filter(filters, conditions) -> list:
    # Skip filter if nothing is selected or list is empty
    if filters["item_type"] and filters["item_type"] != "All":
        conditions.append(
            f"item_type = '{filters['item_type']}'"
        )
    return conditions

# Rarity filter - CURRENTLY NOT WORKING, needs fixing!
def _rarity_filter(filters, conditions) -> list:
    # Skip filter if nothing is selected or list is empty
    if filters["item_rarity"] and len(filters["item_rarity"]) > 0:
        # Escape single quotes in rarity names if needed
        selected = [r.replace("'", "''") for r in filters["item_rarity"]]
        rarity_list = "', '".join(selected)
        conditions.append(
            f"rarity_name IN ('{rarity_list}')"
        )
    return conditions

# ilvl filter
def _ilvl_filter(filters, conditions) -> list:
    if filters["start_item_lvl"] and filters["end_item_lvl"]:
        conditions.append(
            f"item_level >= {filters['start_item_lvl']} AND item_level <= {filters['end_item_lvl']}"
        )
    return conditions

# Req. level filter
def _req_lvl_filter(filters, conditions) -> list:
    if filters["start_req_lvl"] and filters["end_req_lvl"]:
        conditions.append(
            f"required_level >= {filters['start_req_lvl']} AND required_level <= {filters['end_req_lvl']}"
        )
    return conditions

# Include out-of-stock filter
def _include_out_of_stock_filter(filters, conditions) -> list:
    if filters["include_out_of_stock"]:
        conditions.append(
            # How to build this..?
        )
    return conditions

# Only below vendor price filter
def _only_below_vendor_price_filter(filters, conditions) -> list:
    if filters["include_out_of_stock"]:
        conditions.append(
            # How to build this..?
        )
    return conditions

# Function for building WHERE clause for ITEMS query
def build_items_query_conditions(filters):
    """Builds a list of SQL conditions for the items query based on filters."""
    conditions = []

    _search_text_filter(filters, conditions)
    _item_class_filter(filters, conditions)
    _item_subclass_filter(filters, conditions)
    _item_type_filter(filters, conditions)
    _rarity_filter(filters, conditions)
    _ilvl_filter(filters, conditions)
    _req_lvl_filter(filters, conditions)

    return conditions

# Function for building WHERE clause for AUCTIONS query
def build_auctions_query_conditions(filters):
    """Builds a list of SQL conditions for the auctions query based on filters."""
    conditions = []

    _search_text_filter(filters, conditions)
    _realms_filter(filters, conditions)
    _item_class_filter(filters, conditions)
    _item_subclass_filter(filters, conditions)
    _item_type_filter(filters, conditions)
    _rarity_filter(filters, conditions)
    _ilvl_filter(filters, conditions)
    _req_lvl_filter(filters, conditions)

    # _include_out_of_stock_filter(filters, conditions)
    # _only_below_vendor_price_filter(filters, conditions)

    return conditions

# Function for displaying active filters in the main section
def render_active_filters(filters):
    filter_labels = {
        "search_text": "Keyword",
        "item_class": "Class",
        "item_subclass": "Subclass",
        "item_type": "Type",
        "item_rarity": "Rarity",
    }
    badges = []
    for key, label in filter_labels.items():
        value = filters.get(key)
        if value and value != "All" and value != []:
            # If value is a list, join it as a comma-separated string
            if isinstance(value, list):
                display_value = ", ".join(str(v) for v in value)
            else:
                display_value = value
            badges.append(
                f"<span class='st-badge'>{label}: <b>{display_value}</b></span>"
            )
    if badges:
        st.markdown(
            """
            <style>
            .st-badge {
                display: inline-block;
                background: var(--secondary-background-color, #f0f2f6);
                color: var(--text-color, #262730);
                border-radius: 0.5em;
                padding: 0.25em 0.75em;
                margin-right: 0.5em;
                margin-bottom: 0.25em;
                border: 1px solid #d3d3d3;
                font-size: 0.95em;
                font-family: inherit;
            }
            </style>
            """
            + " ".join(badges),
            unsafe_allow_html=True,
        )
    else:
        st.info("No filters applied - displaying all results.")
