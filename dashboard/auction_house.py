import streamlit as st
from .utils import fetch_data_from_db, get_sidebar_filters, build_auctions_query_conditions

# ---------- Items Page ----------
def auction_house_page():
    st.header("Auction House - Auctions")

    filters = get_sidebar_filters()
    conditions = build_auctions_query_conditions(filters)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    auctions_query = f"""
        SELECT
            buyout,
            item_name,
            quantity
        FROM mart_market
        {where_clause}
        LIMIT 50
    """

        # Part of query filtering
        # WHERE class = '{filters["item_class"]}'
        #     AND subclass IN ({filters["item_subclass"]})

    auctions_data = fetch_data_from_db(query=auctions_query)

    if auctions_data.empty:
        st.info(f"No data found with the current filters.")

    # Display the dataframe based on the query
    st.dataframe(data=auctions_data, hide_index=True)
