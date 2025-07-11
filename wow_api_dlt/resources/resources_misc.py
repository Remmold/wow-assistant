import dlt
from wow_api_dlt import db
from wow_api_dlt.utilities.dlt_util import fetch_realm_ids, _update_progress_bar
import sys 


from concurrent.futures import ThreadPoolExecutor, as_completed

from wow_api_dlt.utilities import auth_util #this is used to multithreading. we use it to perform multiple API calls in parallel, which can significantly speed up the data fetching process.

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
