import dlt
from wow_api_dlt import db
from wow_api_dlt.utilities.dlt_util import fetch_item_class_and_subclasses, _update_progress_bar
from wow_api_dlt.utilities.auth_util import get_api_response
import time
import sys 
from concurrent.futures import ThreadPoolExecutor, as_completed

from wow_api_dlt.utilities import auth_util #this is used to multithreading. we use it to perform multiple API calls in parallel, which can significantly speed up the data fetching process.
FULL_ITEM_CONFIG = {
    "namespace": "static-eu",
    "orderby": "id",
    "api_results_per_page": 1000, # Max allowed by Blizzard API for search
    "max_concurrent_requests": 10, # Number of concurrent API calls for pagination
}

@dlt.resource(table_name="items", write_disposition="replace", primary_key="id")
def fetch_items():
    """
    Fetches all items from the Blizzard API using pagination and ID range fetching
    to handle large datasets effectively.
    """
    print("Starting full item data extraction...")
    start_time = time.time()

    total_items_fetched = 0
    all_yielded_ids = set() # To ensure unique items are yielded

    current_min_id = 1 

    id_chunk_size = 1000  # Example: Fetch items with ID 1-1000, then 1001-2000, etc.

    highest_id_fetched = 0

    while True:
        sys.stdout.write(f"\nProcessing ID range: [{current_min_id}, {current_min_id + id_chunk_size - 1}]...\n")
        sys.stdout.flush()

        range_start = current_min_id
        range_end = current_min_id + id_chunk_size - 1

        # Inner loop: Paginate within the current ID range
        page_num = 1
        page_futures = []
        paginating_in_range = True

        # Use ThreadPoolExecutor for concurrent page fetching within an ID range
        with ThreadPoolExecutor(max_workers=FULL_ITEM_CONFIG["max_concurrent_requests"]) as executor:
            while paginating_in_range:
                params = {
                    "namespace": FULL_ITEM_CONFIG["namespace"],
                    "orderby": FULL_ITEM_CONFIG["orderby"],
                    "_pageSize": FULL_ITEM_CONFIG["api_results_per_page"],
                    "_page": page_num,
                    "id": f"[{range_start},{range_end}]" # Filter by ID range

                }
                endpoint = "/data/wow/search/item"
                filter_description = f"ID Range [{range_start},{range_end}] Page {page_num}"

                # Submit the API call to the thread pool
                future = executor.submit(get_api_response, endpoint=endpoint, params=params)
                page_futures.append((future, filter_description, page_num))

                if len(page_futures) >= FULL_ITEM_CONFIG["max_concurrent_requests"]:
                    for processed_future, desc, p_num in page_futures:
                        try:
                            response = processed_future.result()
                            data = response.json()
                            results = data.get("results", [])

                            if not results:
                                sys.stdout.write(f"\nNo more results on {desc}. Stopping pagination for this ID range.\n")
                                sys.stdout.flush()
                                paginating_in_range = False # No more results for this range
                                break # Exit inner future processing loop
                            
                            for result in results:
                                if "data" in result:
                                    item_id = result["data"].get("id")
                                    if item_id is not None:
                                        # Update highest ID found
                                        if item_id > highest_id_fetched:
                                            highest_id_fetched = item_id
                                        
                                        if item_id not in all_yielded_ids:
                                            # You can refine the data before yielding here if needed
                                            yield result["data"]
                                            all_yielded_ids.add(item_id)
                                            total_items_fetched += 1
                                else:
                                    sys.stdout.write(f"\nWarning: 'data' field missing in result for {desc}. Result: {result}\n")
                                    sys.stdout.flush()
                            
                            _update_progress_bar(len(all_yielded_ids), total_items_fetched + 1, f"Fetching items in {desc}") # Progress bar logic here might need refinement
                            
                        except Exception as e:
                            sys.stdout.write(f"\nError during fetch for {desc}: {e}\n")
                            sys.stdout.flush()
                            # Continue to next future even if one fails
                    
                    page_futures = [] # Clear futures after processing a batch

                    if not paginating_in_range: # If we stopped in the inner loop, break outer too
                        break
                    
                page_num += 1 # Move to the next page

            # Process any remaining futures if the loop ended early
            for processed_future, desc, p_num in page_futures:
                try:
                    response = processed_future.result()
                    data = response.json()
                    results = data.get("results", [])

                    if not results:
                        sys.stdout.write(f"\nNo more results on {desc}. Stopping pagination for this ID range.\n")
                        sys.stdout.flush()
                        paginating_in_range = False
                        break
                    
                    for result in results:
                        if "data" in result:
                            item_id = result["data"].get("id")
                            if item_id is not None:
                                if item_id > highest_id_fetched:
                                    highest_id_fetched = item_id
                                if item_id not in all_yielded_ids:
                                    yield result["data"]
                                    all_yielded_ids.add(item_id)
                                    total_items_fetched += 1
                        else:
                            sys.stdout.write(f"\nWarning: 'data' field missing in result for {desc}. Result: {result}\n")
                            sys.stdout.flush()
                    
                    _update_progress_bar(len(all_yielded_ids), total_items_fetched + 1, f"Fetching items in {desc}")
                except Exception as e:
                    sys.stdout.write(f"\nError during fetch for {desc}: {e}\n")
                    sys.stdout.flush()

        sys.stdout.write("\n")
        sys.stdout.flush()
        

        
        previous_total_items_fetched = total_items_fetched
        
        # Advance to the next ID range
        current_min_id += id_chunk_size

        if (current_min_id - id_chunk_size) > (highest_id_fetched + id_chunk_size) and (total_items_fetched == previous_total_items_fetched):
             print(f"Stopping fetch: No new items found in range [{current_min_id - id_chunk_size}, {current_min_id - 1}] and past highest ID {highest_id_fetched}.")
             break # Break the outer while True loop

        # To prevent excessively large IDs if there are gaps
        if current_min_id > 1000000: # Arbitrary large number to cap search if no more items are found
            print(f"Stopping fetch: Reached practical ID limit ({current_min_id}).")
            break

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n--- Full Item Data Extraction Summary ---")
    print(f"✅ Fetched total {total_items_fetched} unique items.")
    print(f"✅ Total extraction time: {duration:.2f} seconds.")
    print("------------------------------------")

@dlt.resource(write_disposition="replace" ,table_name="item_details")
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
                    query = f"SELECT DISTINCT id FROM raw_items.items WHERE item_class__id = {item_class_id} AND item_subclass__id = {subclass_id}"
                else:
                    query = f"SELECT DISTINCT id FROM raw_items.items WHERE item_class__id = {item_class_id}"

                df = db_handler.query(query)
                #df = df[:1] # Keep this commented out if you want to fetch all items for actual runs

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

                yield data

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


       
