import streamlit as st
from dashboard.sidebar_components import items_page_filters, auctions_page_filters
from dashboard.items import items_page
from dashboard.auction_house import auction_house_page

st.set_page_config(layout="wide", page_title="The Murloc Oracle - WoW Auctions, Item database (and more to come..)")

# ---------- Main Sidebar ----------
def sidebar():
    with st.sidebar:
        st.markdown(f"<span style='font-size:2em;'>The Murloc Oracle</span>", unsafe_allow_html=True)

        # --- PAGE SELECTION BUTTONS ---
        if "sidebar_page_selection" not in st.session_state:
            st.session_state["sidebar_page_selection"] = "Auction House"  # Default

        if st.button("Item Database", use_container_width=True):
            st.session_state["sidebar_page_selection"] = "Item Database"

        if st.button("Auction House", use_container_width=True):
            st.session_state["sidebar_page_selection"] = "Auction House"

        if st.button("Realms", use_container_width=True):
            st.session_state["sidebar_page_selection"] = "Realms"

        current_page = st.session_state["sidebar_page_selection"]

        if current_page == "Item Database":
            items_page_filters()
        elif current_page == "Auction House":
            auctions_page_filters()
        else:
            st.write("No filters available for the current page.")

# ---------- Main Section with page-based content ----------
def main_section():
    current_page = st.session_state.get("sidebar_page_selection")

    if current_page == "Item Database":
        items_page()
    elif current_page == "Auction House":
        auction_house_page()
    elif current_page == "Realms":
        st.header("Realms")
    else:
        st.markdown("Select a page in the sidebar.")

# ---------- Content ----------
sidebar()
main_section()
