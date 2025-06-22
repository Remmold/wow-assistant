import streamlit as st
from .utils import fetch_data_from_db, get_sidebar_filters, build_auctions_query_conditions

# ---------- Items Page ----------
def auction_house_page():
    st.header("Auction House - Auctions")

    filters = get_sidebar_filters()
    conditions = build_auctions_query_conditions(filters)
    # where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    where_clause = ""

    auctions_query = f"""
        SELECT
            buyout,
            item_name,
            quantity
        FROM refined.mart_market
        {where_clause}
        LIMIT 50
    """

    auctions_data = fetch_data_from_db(query=auctions_query)

    if auctions_data.empty:
        st.info(f"No data found with the current filters.")

    # Display the dataframe based on the query
    st.dataframe(data=auctions_data, hide_index=True)
