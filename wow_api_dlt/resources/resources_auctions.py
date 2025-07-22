import dlt
from wow_api_dlt.utilities.dlt_util import fetch_realm_ids, _update_progress_bar
import time
import sys 

from concurrent.futures import ThreadPoolExecutor, as_completed #this is used to multithreading. we use it to perform multiple API calls in parallel, which can significantly speed up the data fetching process.

from wow_api_dlt.utilities import auth_util 


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



