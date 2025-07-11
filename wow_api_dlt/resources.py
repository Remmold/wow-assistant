import dlt
from wow_api_dlt import auth_util,db
from wow_api_dlt.dlt_util import fetch_realm_ids, fetch_item_class_and_subclasses
import pandas as pd
import time
import datetime
import sys 

from concurrent.futures import ThreadPoolExecutor, as_completed #this is used to multithreading. we use it to perform multiple API calls in parallel, which can significantly speed up the data fetching process.

# Fetch data about connected realms    
@dlt.resource(table_name="realm_data", write_disposition="replace")
def fetch_realm_data():
    for realm_id in fetch_realm_ids():
        endpoint = f"/data/wow/connected-realm/{realm_id}"
        params = {                
            "{{connectedRealmId}}" : realm_id,
            "namespace" : "dynamic-eu",
            }
        response = auth_util.get_api_response(endpoint=endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        yield data
        print(f"Yieldat connected realm {realm_id}!")


# Fetch AH items
@dlt.resource(table_name="auctions", write_disposition="replace")
def fetch_auction_house_items(test_mode=False):
    time_of_run = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"run started at : {time_of_run}")
    realm_ids = fetch_realm_ids() # Fetch all connected realm IDs once
    if test_mode:
        realm_ids = realm_ids[:3] # Limit for testing

    amount_of_realms = len(realm_ids)
    print(f"Total realms to fetch auction data for: {amount_of_realms}")

    MAX_WORKERS = 10 # Adjust based on API rate limits and network latency for AH data

    current_processed_realms = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tasks for each realm ID
        future_to_realm_id = {
            executor.submit(
                auth_util.get_api_response,
                endpoint=f"/data/wow/connected-realm/{r_id}/auctions",
                params={"{{connectedRealmId}}": r_id, "namespace": "dynamic-eu"}
            ): r_id
            for r_id in realm_ids
        }

        _update_progress_bar(current_processed_realms, amount_of_realms, "Fetching AH Items")

        for future in as_completed(future_to_realm_id):
            realm_id = future_to_realm_id[future]
            
            try:
                response = future.result()
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = response.json()
                
                if "auctions" not in data:
                    sys.stdout.write(f"\nWarning: 'auctions' key not found for realm ID: {realm_id}. Skipping.\n")
                    sys.stdout.flush()
                    continue

                for auction in data["auctions"]:
                    auction["realm_id"] = realm_id # Add realm_id to each auction item
                    auction["timestamp"] = time_of_run
                    yield auction 
            except Exception as e:
                # Print errors on a new line to not interfere with the progress bar
                sys.stdout.write(f"\nError fetching data for realm ID {realm_id}: {e}\n")
                sys.stdout.flush()
            
            current_processed_realms += 1
            _update_progress_bar(current_processed_realms, amount_of_realms, "Fetching AH Items")

    sys.stdout.write("\n") # Final newline after progress bar completion
    sys.stdout.flush()
    print(f"Finished fetching auction data for {current_processed_realms} realms.")



# Fetch AH commodities
@dlt.resource(table_name="commodities", write_disposition="append")
def fetch_ah_commodities():
    time_of_run = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"run started at : {time_of_run}")
    print("Fetching Auction House Commodities...")
    endpoint = "/data/wow/auctions/commodities"
    params = {
        "namespace": "dynamic-eu",
    }
    try:
        response = auth_util.get_api_response(endpoint=endpoint, params=params)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        if "auctions" not in data:
            print("Warning: 'auctions' key not found in commodities response. No data to yield.")
            return # Exit if no auctions
        for auction in data["auctions"]:
            auction["timestamp"] = time_of_run
            yield auction
        print("Successfully fetched Auction House Commodities.")
    except Exception as e:
        print(f"Error fetching Auction House Commodities: {e}")




# wow_api_dlt/resources.py (updated fetch_media_hrfs function)

# ... (other imports and resources as before) ...

@dlt.resource(table_name="item_media", write_disposition="replace")
def fetch_media_hrfs():
    db_path = "wow_api_dbt/wow_api_data.duckdb"
    
    media_ids_to_fetch = []
    with db.DuckDBConnection(db_path) as db_handler:
        df = db_handler.query("SELECT DISTINCT media_id FROM refined.dim_items WHERE media_id IS NOT NULL")
        # df = df[:100] # For testing purposes, limit to 100 rows
        for _, row in df.iterrows():
            try:
                media_id = int(row["media_id"])
                media_ids_to_fetch.append(media_id)
            except (ValueError, TypeError):
                print(f"Skipping invalid media_id: {row['media_id']}")
                continue

    amount_of_media = len(media_ids_to_fetch)
    print(f"Total unique media IDs to fetch: {amount_of_media}")

    MAX_WORKERS_MEDIA_FETCH = 10 # You can adjust this, similar to other resources

    current_processed_count = 0
    bar_length = 50

    with ThreadPoolExecutor(max_workers=MAX_WORKERS_MEDIA_FETCH) as executor:
        future_to_media_id = {
            executor.submit(auth_util.get_api_response, endpoint=f"/data/wow/media/item/{media_id}", params={"namespace": "static-eu"}): media_id
            for media_id in media_ids_to_fetch
        }

        _update_progress_bar(current_processed_count, amount_of_media, "Fetching Media HRFs")

        for future in as_completed(future_to_media_id):
            media_id = future_to_media_id[future]
            try:
                response = future.result()
                data = response.json()

                assets = data.get("assets", [])
                if not isinstance(assets, list):
                    sys.stdout.write(f"\nWarning: Invalid assets format for media {media_id}. Skipping.\n")
                    sys.stdout.flush()
                    continue

                found_icon = False
                for asset in assets:
                    if asset.get("key") == "icon":
                        url = asset.get("value")
                        if isinstance(url, str) and url.startswith("http"):
                            yield {
                                "media_id": media_id,
                                "url": url
                            }
                            found_icon = True
                            break # Found the icon, no need to check other assets for this media_id
                        else:
                            sys.stdout.write(f"\nWarning: Invalid or missing URL for media {media_id}. Skipping.\n")
                            sys.stdout.flush()
                            break # Invalid URL, break from inner loop
                
                if not found_icon and assets: # If assets exist but no valid icon was found
                     sys.stdout.write(f"\nWarning: No valid icon asset found for media {media_id}.\n")
                     sys.stdout.flush()

            except Exception as e:
                sys.stdout.write(f"\nError fetching media {media_id}: {e}\n")
                sys.stdout.flush()
                continue
            
            current_processed_count += 1
            _update_progress_bar(current_processed_count, amount_of_media, "Fetching Media HRFs")
    
    sys.stdout.write("\n")
    sys.stdout.flush()
    print(f"Finished fetching media HRFs for {current_processed_count} media IDs.")


@dlt.resource()
def fetch_item_details():
    db_path = "wow_api_dbt/wow_api_data.duckdb"

    item_class_dict = fetch_item_class_and_subclasses()
    
    MAX_WORKERS = 10

    all_item_ids_to_fetch = []
    item_id_context = {} 

    print("Collecting item IDs from DuckDB...")
    for item_class_id, value in item_class_dict.items():
        item_class_name_raw = value.get("name", f"Unknown Class {item_class_id}")
        item_class_name_sanitized = item_class_name_raw.lower().replace(" ", "_").replace("-", "_")

        subclass_ids = value.get("subclass_ids", [])
        if not subclass_ids:
            subclass_ids = [None] 

        for subclass_id in subclass_ids:
            with db.DuckDBConnection(db_path) as db_handler:
                if subclass_id is not None:
                    query = f"SELECT DISTINCT id FROM refined.dim_items WHERE item_class_id = {item_class_id} AND item_subclass_id = {subclass_id}"
                else:
                    query = f"SELECT DISTINCT id FROM refined.dim_items WHERE item_class_id = {item_class_id}"
                
                df = db_handler.query(query)
                # df = df[:1] # Keep this commented out if you want to fetch all items for actual runs

            for _, row in df.iterrows():
                item_id = int(row["id"])
                all_item_ids_to_fetch.append(item_id)
                item_id_context[item_id] = { 
                    "item_class_id": item_class_id,
                    "class_name_sanitized": item_class_name_sanitized,
                    "class_name_raw": item_class_name_raw,
                    "subclass_id": subclass_id
                }

    amount_of_details = len(all_item_ids_to_fetch)
    print(f"Total unique items to fetch details for: {amount_of_details}")

    # Manual progress bar variables
    current_processed_count = 0
    bar_length = 50 # Length of the progress bar in characters
    
    # This allows us to use a thread pool to fetch item details concurrently
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_item_id = {
            executor.submit(auth_util.get_api_response, endpoint=f"/data/wow/item/{item_id}", params={"namespace": "static-eu"}): item_id
            for item_id in all_item_ids_to_fetch
        }

        # Initial display of the progress bar
        _update_progress_bar(current_processed_count, amount_of_details, bar_length)

        for future in as_completed(future_to_item_id):
            item_id = future_to_item_id[future]
            context = item_id_context[item_id]
            item_class_id = context["item_class_id"]
            item_class_name_sanitized = context["class_name_sanitized"]
            item_class_name_raw = context["class_name_raw"]
            subclass_id = context["subclass_id"]

            try:
                response = future.result() 
                data = response.json()

                if not isinstance(data, dict) or "id" not in data:
                    # Print full message on a new line for invalid data, then update progress
                    sys.stdout.write(f"\nWarning: Invalid data format for item {item_id}\n")
                    sys.stdout.flush()
                    continue

                item_data_to_yield = {}
                item_data_to_yield["id"] = data.get("id")
                if "description" in data:
                    item_data_to_yield["description"] = data.get("description", {}).get("en_US")
                if "binding" in data:
                    item_data_to_yield["binding_name"] = data.get("binding", {}).get("name")
                if "item_preview" in data:
                    item_data_to_yield["item_preview"] = data.get("item_preview")

                item_data_to_yield["item_class_id"] = item_class_id
                item_data_to_yield["item_subclass_id"] = subclass_id if subclass_id is not None else -1

                yield dlt.mark.with_table_name(item_data_to_yield, table_name=f"item_details_{item_class_name_sanitized}")

            except Exception as e:
                # Print full message on a new line for errors, then update progress
                sys.stdout.write(f"\nError fetching item {item_id}: {e}\n")
                sys.stdout.write(f"  Class: {item_class_name_raw}, Subclass: {subclass_id}\n")
                sys.stdout.flush()
                continue
            
            # Increment and update progress bar
            current_processed_count += 1
            _update_progress_bar(current_processed_count, amount_of_details, bar_length)

    # Final newline to ensure subsequent prints appear on a new line
    sys.stdout.write("\n")
    sys.stdout.flush()
    print(f"Finished fetching details for all items. Total processed: {current_processed_count} successfully.")

def _update_progress_bar(current, total, desc, bar_length=50):
    """
    Manually updates a console progress bar on the same line.
    """
    if total == 0: # Avoid division by zero if no items
        sys.stdout.write(f"\r{desc}: No items to process.")
        sys.stdout.flush()
        return

    progress = current / total
    arrow = '=' * int(round(progress * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    
    sys.stdout.write(f"\r{desc}: [{arrow}{spaces}] {current}/{total} ({progress:.1%})")
    sys.stdout.flush()
       



# wow_api_dlt/resources.py (updated fetch_items function)

# ... (other imports and resources as before) ...

@dlt.resource(table_name="items", write_disposition="merge", primary_key="id")
def fetch_items():
    print("Starting item data extraction with adaptive filtering...")
    start_time = time.time()

    print("Fetching item subclasses...")
    item_class_dict = fetch_item_class_and_subclasses()
    print(f"✅ Item subclasses fetched. Found {len(item_class_dict)} item classes with subclasses.")

    rarities = [
        "Poor", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Artifact", "Heirloom"
    ]
    print(f"Configured with {len(rarities)} rarities: {', '.join(rarities)}")

    min_overall_ilvl = 1
    max_overall_ilvl = 750
    step = 10

    all_level_ranges = [
        (start_ilvl, min(start_ilvl + step - 1, max_overall_ilvl))
        for start_ilvl in range(min_overall_ilvl, max_overall_ilvl + step, step)
    ]
    print(f"Pre-generated {len(all_level_ranges)} item level ranges for adaptive filtering.")

    total_items_fetched = 0
    total_api_calls = 0 # This will now be primarily handled by the _fetch_page_data wrapper
    incomplete_extractions = set()

    ADAPTIVE_THRESHOLD_PAGES = 10
    API_RESULTS_PER_PAGE = 100
    REFINED_QUERY_PAGE_LIMIT = 10
    BROAD_SEARCH_SAFETY_CAP_PAGES = ADAPTIVE_THRESHOLD_PAGES + 10

    # MAX_WORKERS for _fetch_page_data calls
    # You might want to experiment with this value. 
    # It allows you to fire off many page requests concurrently.
    MAX_WORKERS_ITEM_FETCH = 20 # Can be higher than 10, as the rate limiter will govern actual API hits

    # List to store all tasks (endpoint, params, current_page, filter_description)
    all_api_tasks = []
    task_context_map = {} # To store context for each task (e.g., class_id, subclass_id, rarity)

    # First pass: Collect all broad and refined search tasks
    for item_class_id, value in item_class_dict.items():
        subclass_ids = value.get("subclass_ids", [])
        if not subclass_ids:
            subclass_ids = [None]

        for subclass_id in subclass_ids:
            for rarity in rarities:
                base_params = {
                    "namespace": "static-eu",
                    "orderby": "id",
                    "item_class.id": item_class_id,
                    "item_subclass.id": subclass_id,
                    "quality.name.en_US": rarity,
                }
                endpoint = "/data/wow/search/item"
                
                # Broad search
                for page in range(1, BROAD_SEARCH_SAFETY_CAP_PAGES + 1):
                    task_key = (endpoint, tuple(sorted(base_params.items())), page, "broad", item_class_id, subclass_id, rarity)
                    all_api_tasks.append((endpoint, base_params.copy(), page, f"Class {item_class_id}, Subclass {subclass_id}, Rarity '{rarity}' (broad query page {page})"))
                    task_context_map[task_key] = {
                        "type": "broad",
                        "item_class_id": item_class_id,
                        "subclass_id": subclass_id,
                        "rarity": rarity,
                        "page": page
                    }
                    # We can't know yet if we need to refilter by ilvl here,
                    # so we'll just gather all potential broad requests.
                    # The adaptive logic will apply *after* responses are received.

                    # To avoid submitting an insane number of tasks for broad search if it's not needed
                    # We'll rely on the actual results processing to stop generating new tasks if 'results' is empty
                    # Or if a page limit is hit. This means we'll over-submit initial tasks and then filter.
                    # For a truly adaptive pre-submission, this part would be more complex and iterative.
                    # For now, let's keep it simpler: submit all possible *broad* pages, then process results.
                    # The ILVL part will be handled in a second pass/later logic if a broad search hits its limit.

    print(f"Collected {len(all_api_tasks)} potential broad search API tasks.")

    # Execute all broad search tasks
    processed_broad_tasks = {} # (item_class_id, subclass_id, rarity) -> { 'hit_threshold': bool, 'pages_fetched': int }
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_ITEM_FETCH) as executor:
        future_to_task_key = {}
        for task in all_api_tasks:
            # Create a unique key for each task to retrieve its context later
            endpoint, params, page, desc = task
            task_key = (endpoint, tuple(sorted(params.items())), page, desc)
            future_to_task_key[executor.submit(auth_util.get_api_response, endpoint=endpoint, params=params)] = task_key

        print(f"Submitting {len(future_to_task_key)} broad search API requests...")
        
        # Manual progress bar
        current_processed_count = 0
        total_tasks = len(future_to_task_key)
        bar_length = 50
        _update_progress_bar(current_processed_count, total_tasks, "Fetching Broad Item Data")

        for future in as_completed(future_to_task_key):
            task_key = future_to_task_key[future]
            # Reconstruct original task details
            original_endpoint, original_params_tuple, original_page, original_desc = task_key 
            # We need to map this back to the (class, subclass, rarity) for the adaptive logic
            # This is where the 'task_context_map' would come in, but we discarded it for simplicity
            # Let's re-extract from original_desc for this example, but it's not ideal.
            # A better way is to attach the context to the future itself or pass it through.
            
            # Simple parsing of description to get context
            # Example: "Class 0, Subclass 0, Rarity 'Common' (broad query page 1)"
            # This is fragile, a dedicated task_context_map is better
            # For a quick fix, let's just use the `original_params_tuple` and convert back to dict
            context_params = dict(original_params_tuple)
            item_class_id = context_params.get("item_class.id")
            subclass_id = context_params.get("item_subclass.id")
            rarity = context_params.get("quality.name.en_US")

            composite_key = (item_class_id, subclass_id, rarity)
            if composite_key not in processed_broad_tasks:
                processed_broad_tasks[composite_key] = {'hit_threshold': False, 'pages_fetched': 0}

            try:
                response = future.result()
                data = response.json()
                results = data.get("results", [])

                if results:
                    for result in results:
                        yield result["data"]
                        total_items_fetched += 1
                    
                    processed_broad_tasks[composite_key]['pages_fetched'] += 1

                    # Check for adaptive filtering condition
                    if len(results) == API_RESULTS_PER_PAGE and processed_broad_tasks[composite_key]['pages_fetched'] >= ADAPTIVE_THRESHOLD_PAGES:
                        processed_broad_tasks[composite_key]['hit_threshold'] = True
                        sys.stdout.write(f"\n            Reached {processed_broad_tasks[composite_key]['pages_fetched']} full pages for {composite_key}. Will trigger refined search.\n")
                        sys.stdout.flush()

                elif processed_broad_tasks[composite_key]['pages_fetched'] < original_page: # Only if we haven't already hit a limit and stopped for this filter
                    # If results are empty, it means this broad path is exhausted for this filter.
                    # We only mark it as 'not hitting threshold' if we truly got less than threshold pages.
                    if processed_broad_tasks[composite_key]['pages_fetched'] < ADAPTIVE_THRESHOLD_PAGES:
                        processed_broad_tasks[composite_key]['hit_threshold'] = False
                    # Stop processing further pages for this specific (class, subclass, rarity) combo
                    # This requires more complex management of which futures to cancel or not submit if earlier pages were empty.
                    # For simplicity, we process all submitted, and handle the logic here.
                    sys.stdout.write(f"\n            No more results for {composite_key} broad filter on page {original_page}. Breaking.\n")
                    sys.stdout.flush()

            except Exception as e:
                sys.stdout.write(f"\nError fetching broad data for {composite_key} page {original_page}: {e}\n")
                sys.stdout.flush()
                # If an error occurs, consider this combination as potentially incomplete
                incomplete_extractions.add((item_class_id, subclass_id))
            
            current_processed_count += 1
            _update_progress_bar(current_processed_count, total_tasks, "Fetching Broad Item Data")
            
    sys.stdout.write("\n")
    sys.stdout.flush()
    print("Finished broad search requests. Now processing refined searches if needed.")

    # Second pass: Collect and execute refined search tasks if a broad search hit its threshold
    refined_api_tasks = []
    for item_class_id, value in item_class_dict.items():
        subclass_ids = value.get("subclass_ids", [])
        if not subclass_ids:
            subclass_ids = [None]
        for subclass_id in subclass_ids:
            for rarity in rarities:
                composite_key = (item_class_id, subclass_id, rarity)
                if processed_broad_tasks.get(composite_key, {}).get('hit_threshold'):
                    for min_level, max_level in all_level_ranges:
                        ilvl_params = {
                            "namespace": "static-eu",
                            "orderby": "id",
                            "item_class.id": item_class_id,
                            "item_subclass.id": subclass_id,
                            "quality.name.en_US": rarity,
                            "min_level": min_level,
                            "max_level": max_level,
                        }
                        endpoint = "/data/wow/search/item"
                        for page in range(1, REFINED_QUERY_PAGE_LIMIT + 1):
                            refined_api_tasks.append((endpoint, ilvl_params.copy(), page, 
                                                      f"Class {item_class_id}, Subclass {subclass_id}, Rarity '{rarity}', ILvl {min_level}-{max_level} page {page}"))
                            # Also add to incomplete_extractions if any refined query hits its limit
                            # This needs to be handled AFTER future.result() and page checking.

    print(f"Collected {len(refined_api_tasks)} potential refined search API tasks.")

    if refined_api_tasks:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_ITEM_FETCH) as executor:
            future_to_task_key = {}
            for task in refined_api_tasks:
                endpoint, params, page, desc = task
                task_key = (endpoint, tuple(sorted(params.items())), page, desc)
                future_to_task_key[executor.submit(auth_util.get_api_response, endpoint=endpoint, params=params)] = task_key

            print(f"Submitting {len(future_to_task_key)} refined search API requests...")

            current_processed_count = 0
            total_tasks = len(future_to_task_key)
            _update_progress_bar(current_processed_count, total_tasks, "Fetching Refined Item Data")

            for future in as_completed(future_to_task_key):
                task_key = future_to_task_key[future]
                original_endpoint, original_params_tuple, original_page, original_desc = task_key
                context_params = dict(original_params_tuple)
                item_class_id = context_params.get("item_class.id")
                subclass_id = context_params.get("item_subclass.id")

                try:
                    response = future.result()
                    data = response.json()
                    results = data.get("results", [])

                    if results:
                        for result in results:
                            yield result["data"]
                            total_items_fetched += 1
                        
                        # If a refined query hits its limit (i.e., we get full pages up to REFINED_QUERY_PAGE_LIMIT)
                        # and there might be more, mark it as incomplete.
                        if len(results) == API_RESULTS_PER_PAGE and original_page >= REFINED_QUERY_PAGE_LIMIT:
                            incomplete_extractions.add((item_class_id, subclass_id))
                            sys.stdout.write(f"\n            ⚠️ Refined query for {item_class_id}, {subclass_id} page {original_page} hit limit. Potentially incomplete.\n")
                            sys.stdout.flush()

                except Exception as e:
                    sys.stdout.write(f"\nError fetching refined data for {item_class_id}, {subclass_id} page {original_page}: {e}\n")
                    sys.stdout.flush()
                    incomplete_extractions.add((item_class_id, subclass_id)) # Mark as incomplete on error too
                
                current_processed_count += 1
                _update_progress_bar(current_processed_count, total_tasks, "Fetching Refined Item Data")
        
        sys.stdout.write("\n")
        sys.stdout.flush()
        print("Finished refined search requests.")

    # Your original summary print statements remain unchanged
    end_time = time.time()
    duration = end_time - start_time

    print(f"\n--- Item Data Extraction Summary ---")
    print(f"✅ Fetched total {total_items_fetched} items.")
    # total_api_calls count will be tricky here, as we submit tasks not individual calls.
    # The actual API call count is now within auth_util.get_api_response and might be useful to track there,
    # or you can just count the number of futures submitted.
    print(f"✅ Total extraction time: {duration:.2f} seconds.")

    print(f"\n--- Incomplete Extractions Summary ---")
    if incomplete_extractions:
        print(f"❌ Found {len(incomplete_extractions)} item class/subclass combinations that were not fully extracted (hit page limits):")
        for class_id, sub_id in sorted(list(incomplete_extractions)):
            print(f"  - Item Class: {class_id}, Subclass: {sub_id}")
        print("\nConsider increasing page limits (REFINED_QUERY_PAGE_LIMIT, BROAD_SEARCH_SAFETY_CAP_PAGES) or further refining filters for these combinations.")
    else:
        print("✅ All item class/subclass combinations appear to have been fully extracted within defined page limits.")
    print(f"------------------------------------")


# @dlt.source that we use in pipeline.run instead of @dlt.resource we use all the resources we want to run in the pipeline
"""If you want to use a source specific override for the pipeline you can add a list of resources to pick specific runs.
accepted values are "auctions", "items" and "realm_data". If no list is provided, it will run all resources."""
@dlt.source(name="wow_api_data")
def wow_api_source(optional_source_list=None,test_mode=False):
    """
    This is the source function that will be used in the pipeline.
    It returns all the resources that we want to run in the pipeline.
    """
    if optional_source_list is not None:
        # If an optional source dictionary is provided, we use it to pick resources
        method_list = []
        if "auctions" in optional_source_list:
            method_list.append(fetch_auction_house_items(test_mode=test_mode))
        if "commodities" in optional_source_list:
            method_list.append(fetch_ah_commodities())
        if "items" in optional_source_list:
            method_list.append(fetch_items())
        if "realm_data" in optional_source_list:
            method_list.append(fetch_realm_data())
        if "item_details" in optional_source_list:
            method_list.append(fetch_item_details())
        if "media" in optional_source_list:
            method_list.append(fetch_media_hrfs())
        return method_list
    else:
        #return [fetch_item_details()] 
        return [fetch_media_hrfs(),fetch_ah_commodities(),fetch_auction_house_items(),fetch_items(),fetch_realm_data(),fetch_item_details()] # # For testing purposes, we only run the media fetch resource

if __name__ == "__main__":
    fetch_item_details()

