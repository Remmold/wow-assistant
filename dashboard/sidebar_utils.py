"""
Helper functions for sidebar logic, e.g.:
- Fetching options for selectboxes.
- Any sidebar-specific state logic.

No Streamlit UI code here—just logic/data helpers.
"""

import streamlit as st
from dashboard.db_utils import fetch_data_from_db

# Function for getting all realms and realm group id's
@st.cache_data
def _get_all_realms():
    query = """
        SELECT DISTINCT realm_name
        FROM refined.dim_realms
        ORDER BY realm_name ASC
    """
    df = fetch_data_from_db(query)
    return df["realm_name"].tolist() if not df.empty else []

@st.cache_data
def _get_realm_group_ids_for_realms(selected_realms):
    if not selected_realms:
        return []
    # Prepare for SQL IN clause
    realms_str = "', '".join([r.replace("'", "''") for r in selected_realms])
    query = f"""
        SELECT DISTINCT realm_group_id
        FROM refined.dim_realms
        WHERE realm_name IN ('{realms_str}')
    """
    df = fetch_data_from_db(query)
    return df["realm_group_id"].tolist() if not df.empty else []

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
@st.cache_data
def _get_item_subclass_list(current_item_class):
    # Build where clause based on current item_class choice
    if current_item_class == "All":
        where_clause = ""
    else:
        where_clause = f"WHERE item_class_name = '{current_item_class}'"

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
@st.cache_data
def _get_item_type_list(current_item_subclass):
    # Build where clause based on current item_subclass choice
    if current_item_subclass == "All":
        where_clause = ""
    else:
        where_clause = f"WHERE item_subclass_name = '{current_item_subclass}'"

    query = f"""
        SELECT
            DISTINCT item_type
        FROM refined.mart_item_class_subclass
        {where_clause}
        ORDER BY item_type
    """
    df = fetch_data_from_db(query)
    return df["item_type"].tolist() if not df.empty else []