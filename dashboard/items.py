import streamlit as st
from .utils import fetch_data_from_db, get_sidebar_filters, build_items_query_conditions

# ---------- Items Page ----------
def items_page():
    st.header("Items")

    filters = get_sidebar_filters()
    conditions = build_items_query_conditions(filters)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    items_query = f"""
        SELECT
            name__en_us AS name,
            item_class__name__en_us AS class,
            item_class__id AS class_id,
            item_subclass__name__en_us AS subclass,
            item_subclass__id AS subclass_id,
            inventory_type__name__en_us AS inventory_type,
            level AS ilvl,
            required_level,
            purchase_price,
            sell_price,
            quality__name__en_us AS rarity,
            is_stackable
        FROM raw.items
        {where_clause}
        LIMIT 50
    """

        # Part of query filtering
        # WHERE class = '{filters["item_class"]}'
        #     AND subclass IN ({filters["item_subclass"]})

    items_data = fetch_data_from_db(query=items_query)

    if items_data.empty:
                st.info(f"No data found with the current filters.")

    # Display the dataframe based on the query
    st.dataframe(data=items_data, hide_index=True)