import streamlit as st
from dashboard.components import sidebar, main_content

st.set_page_config(layout="wide", page_title="WoW API Dashboard")
st.title(":rainbow[WoW API Dashboard]")

# --------------- Streamlit components ---------------
sidebar()
main_content()

