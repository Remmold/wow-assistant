import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from .utils import fetch_data_from_db, get_sidebar_filters, build_items_query_conditions, render_active_filters

# ---------- Items Page ----------
def items_page():
    st.title("Item Database")

    filters = get_sidebar_filters()
    render_active_filters(filters)
    conditions = build_items_query_conditions(filters)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Fetch ALL filtered data
    items_query = f"""
        SELECT
            id,
            item_name,
            item_level,
            required_level,
            rarity_name,
            media_id
        FROM refined.mart_items
        {where_clause}
        ORDER BY item_name ASC, item_level DESC
    """
    items_data = fetch_data_from_db(query=items_query)

    # Placeholder icon url
    items_data["icon"] = "https://wow.zamimg.com/images/wow/icons/large/inv_potion_51.jpg"

    # Icon url
    # items_data["icon"] = items_data["media_id"].apply(
    #     lambda x: f"https://wow.zamimg.com/images/wow/icons/large/{x}.jpg" if x else "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg"
    # )
    columns_to_show = ["id", "icon", "item_name", "item_level", "required_level", "rarity_name"]
    items_data = items_data[columns_to_show]

    # Rarity color mapping
    rarity_colors = {
        "Poor": "#9d9d9d",
        "Common": "#ffffff",
        "Uncommon": "#1eff00",
        "Rare": "#0070dd",
        "Epic": "#a335ee",
        "Legendary": "#ff8000",
        "Artifact": "#e6cc80",
        "Heirloom": "#00ccff",
        "Heirloom Artifact": "#00ccff",
        "Wow Token": "#ffd700"
    }

    # Add rarity color to dataframe
    items_data["rarity_color"] = items_data["rarity_name"].map(rarity_colors)

    # Results column + details column (50/50%)
    col_results, col_details = st.columns([0.5, 0.5])

    # ---------- Results dataframe column ----------
    with col_results:
        if not items_data.empty:
            gb = GridOptionsBuilder.from_dataframe(items_data)
            gb.configure_selection('single', use_checkbox=False)
            # gb.configure_column('id', hide=False) # Hide item id
            # Change column labels
            gb.configure_column("id", header_name="ID", width=100) # To be removed later
            gb.configure_column("item_name", header_name="Item name", width=280)
            gb.configure_column("item_level", header_name="iLvl", width=100)
            gb.configure_column("required_level", header_name="Req. lvl", width=100)
            gb.configure_column("rarity_name", header_name="Rarity", width=120)
            gb.configure_column(
                "icon",
                header_name="Image",
                cellRenderer="""
                    function(params) {
                        return `<img src="${params.value}" style="height:56px;width:56px;object-fit:contain;" />`
                    }
                """,
                width=60,
                pinned="left"
            )
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
            grid_options = gb.build()
            grid_options["pagination"] = True

            # Build rarity text color style and assign it dynamically
            rarity_color_style = JsCode("""
                function(params) {
                    return {color: params.data.rarity_color || "#fff", fontWeight: "bold"};
                }
            """)

            for col in grid_options["columnDefs"]:
                if col["field"] == "item_name":
                    col["cellStyle"] = rarity_color_style

            grid_response = AgGrid(
                items_data,
                gridOptions=grid_options,
                theme="alpine",
                allow_unsafe_jscode=True,
                update_mode="SELECTION_CHANGED",
                custom_css={
                    "#gridToolBar": {"padding-bottom": "0px !important"},
                    ".ag-paging-panel": {"justify-content": "flex-start !important"},
                }
            )
            selected_rows = grid_response['selected_rows']
        else:
            st.info("No items found with the current filters.")
            selected_rows = []

    # ---------- Item details column ----------
    with col_details:
        with st.container(border=True):
            st.subheader("Item details")
            # Handle if selected_rows is a list of dicts (AgGrid default)
            if isinstance(selected_rows, list) and len(selected_rows) > 0:
                selected_id = selected_rows[0].get("id")
            elif hasattr(selected_rows, "iloc") and len(selected_rows) > 0:
                selected_id = selected_rows.iloc[0].get("id")
            else:
                selected_id = None

            item = None
            
            # Query the database with the selected item (if selected)
            if selected_id is not None:
                details_query = f"""
                    SELECT *
                    FROM refined.mart_items
                    WHERE id = {selected_id}
                    LIMIT 1
                """
                details_df = fetch_data_from_db(details_query)
                if not details_df.empty:
                    item = details_df.iloc[0].to_dict()

            # If an item is selected in the results dataframe
            if item:
                # Rarity color mapping
                rarity_colors = {
                    "Poor": "#9d9d9d",
                    "Common": "#ffffff",
                    "Uncommon": "#1eff00",
                    "Rare": "#0070dd",
                    "Epic": "#a335ee",
                    "Legendary": "#ff8000",
                    "Artifact": "#e6cc80",
                    "Heirloom": "#00ccff",
                    "Heirloom Artifact": "#00ccff",
                    "Wow Token": "#ffd700"
                }
                
                # Item detail variables
                item_name = item.get("item_name")
                item_class = item.get("item_class_name")
                item_subclass = item.get("item_subclass_name")
                item_ilvl = item.get("item_level")
                item_req_lvl = item.get("required_level")

                # Retrieve item rarity and assign color to variable
                rarity = item.get("rarity_name", "Common")
                color = rarity_colors.get(rarity, "#ffffff") # Defaults to white
                
                # ---------- Item details layout ----------
                image_col, name_col = st.columns([0.08, 0.92])

                # Image column (10% width)
                with image_col:
                    image_url = item.get("icon", "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg")
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
                
                stats_col, description_col = st.columns([0.5, 0.5])

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
            else:
                st.info("Select an item in the results to see its details.")
