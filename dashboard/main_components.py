"""
All Streamlit UI functions for main content (item/auction details, main tables, etc).
- Anything that is a "main page" or "main section" component.
"""

import streamlit as st
from .helpers import get_rarity_color

# ---------- Items page components ----------
def render_item_details(item: dict):
    # Item detail variables
    item_name = item.get("item_name")
    item_class = item.get("item_class_name")
    item_subclass = item.get("item_subclass_name")
    item_ilvl = item.get("item_level")
    item_req_lvl = item.get("required_level")

    # Retrieve item rarity and assign color to variable
    rarity = item.get("rarity_name", "Common")
    color = get_rarity_color(rarity) # Defaults to white
    
    # ---------- Item details layout ----------
    image_col, name_col = st.columns([0.08, 0.92])

    # Image column (10% width)
    with image_col:
        image_url = item.get("icon_href", "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg")
        st.image(
            image = image_url,
            width = 56
        )

    # Item details column (90% width)
    with name_col:
        # Layout/details
        st.header(f"{item_name}")

    rarity_col, class_col, subclass_col, ilvl_col, reqlvl_col = st.columns([0.2, 0.2, 0.3, 0.15, 0.15])

    # Rarity
    with rarity_col:
        with st.container(border=True):
            st.markdown(
                f"<span style='background:{color};color:#222;padding:6px 18px;border-radius:16px;font-weight:bold;font-size:1em;'>{rarity}</span> ",
                unsafe_allow_html=True
            )

    # Class
    with class_col:
        with st.container(border=True):
            st.markdown(f"<span style='font-size:1em;'>Category: {item_class}</span>", unsafe_allow_html=True)

    # Subclass
    with subclass_col:
        with st.container(border=True):
            st.markdown(f"<span style='font-size:1em;'>Sub-category: {item_subclass}</span>", unsafe_allow_html=True)

    # Item level
    with ilvl_col:
        with st.container(border=True):
            st.markdown(f"<span style='font-size:1em;'>iLevel: {item_ilvl}</span>", unsafe_allow_html=True)

    # Required level
    with reqlvl_col:
        with st.container(border=True):
            st.markdown(f"<span style='font-size:1em;'>Req. level: {item_req_lvl}</span>", unsafe_allow_html=True)
    
    stats_col, description_col = st.columns([0.4, 0.6])

    # Details column (left)
    with stats_col:
        with st.container(border=True):
            st.subheader("Stats:")
            st.markdown("Stats will go here")

    # Description column (right)
    with description_col:
        with st.container(border=True):
            st.subheader("Description:")
            # Placeholder description
            item_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla vitae ipsum pharetra metus mollis gravida. Etiam vestibulum augue egestas aliquet efficitur. Pellentesque placerat odio quis lacinia elementum."
            st.markdown(item_description)

    # Code for later
    # media_id = item.get("media_id")
    # if media_id:
    #     img_url = f"https://wow.zamimg.com/images/wow/icons/large/{media_id}.jpg"
    # else:
    #     img_url = "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg"
    # st.image(img_url, caption="Item image", width=96)
