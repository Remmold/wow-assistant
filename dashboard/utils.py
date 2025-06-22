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
        "item_class": st.session_state.get("sidebar_item_class"),
        "item_subclass": st.session_state.get("sidebar_item_subclass"),
    }

    # Get rarity range (and sort it)
    rarity_range = st.session_state.get("sidebar_rarity")
    if rarity_range:
        filters["lowest_rarity"], filters["highest_rarity"] = sorted(rarity_range)
    else:
        filters["lowest_rarity"], filters["highest_rarity"] = None, None

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

# Item category filter
def _item_class_filter(filters, conditions) -> list:
    if filters["item_class"]:
        conditions.append(
            f"item_class_name == {filters['item_class']}"
        )
    return conditions

# Item subcategory filter
def _item_subclass_filter(filters, conditions) -> list:
    if filters["item_subclass"]:
        conditions.append(
            f"item_class_name IN ({filters['item_subclass']})"
        )
    return conditions

# Rarity filter - CURRENTLY NOT WORKING, needs fixing!
def rarity_filter(filters, conditions) -> list:
    RARITY_LIST = ["Poor", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
    if filters["lowest_rarity"] and filters["highest_rarity"]:
        lowest_idx = RARITY_LIST.index(filters["lowest_rarity"])
        highest_idx = RARITY_LIST.index(filters["highest_rarity"])
        selected_rarities = RARITY_LIST[lowest_idx:highest_idx+1]
        selected_rarities_sql = "', '".join(selected_rarities)
        conditions.append(
            f"quality__name__en_us IN ('{selected_rarities_sql}')"
        )
    return conditions

# ilvl filter
def _ilvl_filter(filters, conditions) -> list:
    if filters["start_item_lvl"] and filters["end_item_lvl"]:
        conditions.append(
            f"level >= {filters['start_item_lvl']} AND level <= {filters['end_item_lvl']}"
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

    _item_class_filter(filters, conditions)
    _item_subclass_filter(filters, conditions)
    # _rarity_filter(filters, conditions)
    _ilvl_filter(filters, conditions)
    _req_lvl_filter(filters, conditions)

    return conditions

# Function for building WHERE clause for AUCTIONS query
def build_auctions_query_conditions(filters):
    """Builds a list of SQL conditions for the auctions query based on filters."""
    conditions = []

    _realms_filter(filters, conditions)
    _item_class_filter(filters, conditions)
    _item_subclass_filter(filters, conditions)
    # _rarity_filter(filters, conditions)
    _ilvl_filter(filters, conditions)
    _req_lvl_filter(filters, conditions)

    # _include_out_of_stock_filter(filters, conditions)
    # _only_below_vendor_price_filter(filters, conditions)

    return conditions