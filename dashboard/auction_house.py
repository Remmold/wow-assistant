import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from .utils import fetch_data_from_db, get_sidebar_filters, build_auctions_query_conditions, render_active_filters
from .helpers import format_wow_currency, format_time_left

# ---------- Items Page ----------
def auction_house_page():
    st.title("Auction House")

    filters = get_sidebar_filters()
    render_active_filters(filters)
    conditions = build_auctions_query_conditions(filters)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Fetch ALL filtered data - currently limited due to performance reasons
    auctions_query = f"""
        SELECT
            item_id,
            MAX(media_id) AS media_id,
            item_name,
            MAX(item_class_name) AS item_class_name,
            MAX(item_subclass_name) AS item_subclass_name,
            MAX(rarity_name) AS rarity_name,
            MAX(item_level) AS item_level,
            MAX(required_level) AS required_level,
            COUNT(*) AS auction_count,
            MIN(buyout) AS min_buyout,
            MAX(buyout) AS max_buyout
        FROM refined.mart_market
        {where_clause}
        GROUP BY item_id, item_name
        ORDER BY item_id ASC
    """
    auctions_data = fetch_data_from_db(query=auctions_query)

    # Generate icon URLs (using placeholder for now)
    auctions_data["icon"] = "https://wow.zamimg.com/images/wow/icons/large/inv_potion_51.jpg"

    # Icon url
    # auctions_data["icon"] = auctions_data["media_id"].apply(
    #     lambda x: f"https://wow.zamimg.com/images/wow/icons/large/{x}.jpg" if x else "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg"
    # )

    # Ensure icon is str
    #auctions_data["icon"] = auctions_data["icon"].astype(str)

    # Ensure item_id is int
    #auctions_data["item_id"] = auctions_data["item_id"].astype(int)

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
    auctions_data["rarity_color"] = auctions_data["rarity_name"].map(rarity_colors)

    # Results column + details column (50/50%)
    col_results, col_auction_details, col_item_details = st.columns([0.35, 0.25, 0.4])

    # ---------- Results dataframe column ----------
    with col_results:
        with st.container(border=True):
            st.subheader("Auctions")
            if not auctions_data.empty:
                # Use ALL data
                all_display_data = auctions_data[[
                    "icon", "item_name", "min_buyout", "auction_count", 
                    "item_id", "rarity_color", "rarity_name"
                ]].copy()
                
                gb = GridOptionsBuilder.from_dataframe(all_display_data)
                gb.configure_selection('single', use_checkbox=False)

                # Hide unnecessary columns
                for col in ["item_id", "rarity_color", "rarity_name"]:
                    gb.configure_column(col, hide=True)

                # Configure visible columns
                gb.configure_column("icon", header_name="", width=56, pinned="left")
                gb.configure_column("item_name", header_name="Item name", width=280)
                gb.configure_column("min_buyout", header_name="Price", width=120, type=["numericColumn"])
                gb.configure_column("auction_count", header_name="Posted", width=120, type=["numericColumn"])

                # Pagination config
                gb.configure_pagination(
                    paginationAutoPageSize=False,
                    paginationPageSize=20
                )

                # Icon renderer
                icon_renderer = JsCode("""
                class IconCellRenderer {
                    init(params) {
                        this.eGui = document.createElement('div');
                        this.eGui.style.display = 'flex';
                        this.eGui.style.justifyContent = 'center';
                        this.eGui.style.alignItems = 'center';
                        this.eGui.style.height = '100%';
                        
                        const img = document.createElement('img');
                        img.src = params.value || 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg';
                        img.style.height = '32px';
                        img.style.width = '32px';
                        img.style.objectFit = 'contain';
                        img.style.borderRadius = '4px';
                        
                        img.onerror = function() {
                            this.src = 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg';
                        };
                        
                        this.eGui.appendChild(img);
                    }
                    
                    getGui() {
                        return this.eGui;
                    }
                }
                """)

                # Build rarity text color style and assign it dynamically
                rarity_name_style = JsCode("""
                    function(params) {
                        return {color: params.data.rarity_color || "#fff", fontWeight: "bold"};
                    }
                """)

                grid_options = gb.build()
                grid_options["pagination"] = True

                # Apply custom renders
                for col in grid_options["columnDefs"]:
                    if col["field"] == "icon":
                        col["cellRenderer"] = icon_renderer
                        col["sortable"] = False
                    elif col["field"] == "item_name":
                        col["cellStyle"] = rarity_name_style

                # The grid
                grid_response = AgGrid(
                    all_display_data,
                    gridOptions=grid_options,
                    theme="alpine",
                    allow_unsafe_jscode=True,
                    update_mode="SELECTION_CHANGED",
                    height=700,
                    # Custom CSS for grid & toolbar
                    custom_css={
                        "#gridToolBar": {"padding-bottom": "0px !important"},
                        ".ag-row": {"cursor": "pointer"},
                        ".ag-row:hover": {"background-color": "rgba(66, 165, 245, 0.1) !important"},
                        ".ag-header-cell": {"font-size": "12px"},
                        ".ag-paging-panel": {
                            "justify-content": "center !important",
                            "padding": "10px !important",
                        }
                    }
                )
                
                # Get selected rows from AgGrid
                selected_rows = grid_response['selected_rows']
            else:
                st.info("No auctions found with the current filters.")
                selected_rows = []

    # ---------- Auction details column ----------
    with col_auction_details:
        with st.container(border=True):
            st.subheader("Auction listings")
            if selected_rows:
                item_id = selected_rows[0]["item_id"]
                auction_listings_query = f"""
                    SELECT
                        auction_id,
                        MIN(buyout) AS "Price",
                        MIN(realm_name) AS "Realm name",
                        MIN(time_left) AS "Time left"
                    FROM refined.mart_market
                    WHERE item_id = {item_id}
                    GROUP BY auction_id
                    ORDER BY "Price" ASC
                """
                auctions_for_item = fetch_data_from_db(auction_listings_query)
                
                if not auctions_for_item.empty:
                    # Format the data for better display
                    auctions_display = auctions_for_item.copy()
                    
                    # Format currency
                    auctions_display["Price_Formatted"] = auctions_display["Price"].apply(format_wow_currency)
                    
                    # Format time left
                    auctions_display["Time_Left_Formatted"] = auctions_display["Time left"].apply(format_time_left)
                    
                    # Add color data for styling
                    auctions_display["price_color"] = "#FFD700"  # Gold color for all prices
                    
                    # Add time-based colors
                    def get_time_color(time_left_formatted):
                        if "0 - 2h" in time_left_formatted:
                            return "#ff4444"  # Red
                        elif "2 - 12h" in time_left_formatted:
                            return "#ffaa00"  # Orange
                        elif "12 - 24h" in time_left_formatted and "Very" not in time_left_formatted:
                            return "#44ff44"  # Green
                        elif "24 - 48h" in time_left_formatted:
                            return "#4444ff"  # Blue
                        return "#ffffff"  # Default white
                    
                    auctions_display["time_color"] = auctions_display["Time_Left_Formatted"].apply(get_time_color)
                    
                    # Prepare data for AgGrid
                    auction_grid_data = auctions_display[[
                        "Price_Formatted", "Realm name", "Time_Left_Formatted", 
                        "auction_id", "Price", "price_color", "time_color"  # Include color data
                    ]].copy()
                    
                    # Configure AgGrid for auction listings
                    gb_auctions = GridOptionsBuilder.from_dataframe(auction_grid_data)
                    gb_auctions.configure_selection('single', use_checkbox=False)
                    
                    # Hide reference columns
                    for col in ["auction_id", "Price", "price_color", "time_color"]:
                        gb_auctions.configure_column(col, hide=True)
                    
                    # Configure visible columns
                    gb_auctions.configure_column("Price_Formatted", header_name="Price", width=140, pinned="left")
                    gb_auctions.configure_column("Realm name", header_name="Realm", width=130)
                    gb_auctions.configure_column("Time_Left_Formatted", header_name="Time Left", width=150)
                    
                    # Disable pagination for auction listings (usually not many)
                    gb_auctions.configure_pagination(enabled=False)
                    
                    # FIXED: Use cellStyle like your working item names
                    price_style = JsCode("""
                        function(params) {
                            return {color: params.data.price_color || "#FFD700", fontWeight: "bold"};
                        }
                    """)
                    
                    time_style = JsCode("""
                        function(params) {
                            return {color: params.data.time_color || "#ffffff", fontWeight: "bold"};
                        }
                    """)
                    
                    auction_grid_options = gb_auctions.build()
                    
                    # Apply custom styles (using cellStyle, not cellRenderer)
                    for col in auction_grid_options["columnDefs"]:
                        if col["field"] == "Price_Formatted":
                            col["cellStyle"] = price_style
                        elif col["field"] == "Time_Left_Formatted":
                            col["cellStyle"] = time_style
                    
                    # Create the auction listings grid
                    auction_grid_response = AgGrid(
                        auction_grid_data,
                        gridOptions=auction_grid_options,
                        theme="alpine",
                        allow_unsafe_jscode=True,
                        update_mode="SELECTION_CHANGED",
                        height=700,
                        custom_css={
                            "#gridToolBar": {"padding-bottom": "0px !important"},
                            ".ag-row": {"cursor": "pointer"},
                            ".ag-row:hover": {"background-color": "rgba(255, 215, 0, 0.1) !important"},  # Gold hover
                            ".ag-header-cell": {"font-size": "12px"}
                        }
                    )
                    
                    # Show selected auction details if needed
                    selected_auction = auction_grid_response['selected_rows']
                    if selected_auction:
                        auction = selected_auction[0]
                        st.info(f"🎯 Selected auction: {auction['Price_Formatted']} on {auction['Realm name']}")
                    
                else:
                    st.info("No auction listings found for this item.")
            else:
                st.info("Select an item to see its available listings.")

    # ---------- Item details column ----------
    with col_item_details:
        with st.container(border=True):
            st.subheader("Item details")
            # Handle if selected_rows is a list of dicts (AgGrid default)
            if isinstance(selected_rows, list) and len(selected_rows) > 0:
                selected_id = selected_rows[0].get("item_id")
            elif hasattr(selected_rows, "iloc") and len(selected_rows) > 0:
                selected_id = selected_rows.iloc[0].get("item_id")
            else:
                selected_id = None

            auction = None

            # Query the database with the selected auction (if selected)
            if selected_id is not None:
                details_query = f"""
                    SELECT *
                    FROM refined.mart_items
                    WHERE id = {selected_id}
                    LIMIT 1
                """
                details_df = fetch_data_from_db(details_query)
                if not details_df.empty:
                    auction = details_df.iloc[0].to_dict()

            # If an auction is selected in the results dataframe
            if auction:
                # Item detail variables
                item_name = auction.get("item_name")
                item_class = auction.get("item_class_name")
                item_subclass = auction.get("item_subclass_name")
                item_ilvl = auction.get("item_level")
                item_req_lvl = auction.get("required_level")

                # Retrieve item rarity and assign color to variable
                rarity = auction.get("rarity_name", "Common")
                color = rarity_colors.get(rarity, "#ffffff") # Defaults to white
                
                # ---------- Item details layout ----------
                image_col, name_col = st.columns([0.08, 0.92])

                # Image column (10% width)
                with image_col:
                    image_url = auction.get("icon", "https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg")
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
                st.info("Select an item to see item details.")
