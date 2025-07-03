import dlt
from wow_api_dlt import auth_util,db
import json
import pandas as pd

# Fetch and bring all the connected realm IDs, returns a list of IDs
def _fetch_ids():
    """
    Fetches all the connected realm ids and cut out the id from the url. THIS IS ONLY NECESARY LIKE ONES?? 
    """
    endpoint = "/data/wow/connected-realm/index"
    params = {
        "namespace" : "dynamic-eu"
    }
    response = auth_util.get_api_response(endpoint=endpoint, params=params)
    connected_realm_list = response.json()["connected_realms"]
    
    list_of_realm_ids = [x["href"].split("/")[-1].split("?")[0] for x in connected_realm_list]
    return list_of_realm_ids


# Fetch data about connected realms    
@dlt.resource(table_name="realm_data", write_disposition="replace")
def fetch_realm_data():
    for realm_id in _fetch_ids():
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
    counter = 0 #DEBUG
    realm_ids = _fetch_ids() # Fetch all connected realm IDs once
    if test_mode:
        realm_ids = realm_ids[:3]

    for realm_id in realm_ids:
        try:
            endpoint = f"/data/wow/connected-realm/{realm_id}/auctions"                             
            params = {                
                "{{connectedRealmId}}" : realm_id,
                "namespace" : "dynamic-eu",
                }
            response = auth_util.get_api_response(endpoint=endpoint, params=params)
            response.raise_for_status()
            counter += 1 #DEBUG
            data = response.json()
            for auction in data["auctions"]:
                auction["realm_id"] = realm_id
                yield auction # Detta tar rad för rad så i varje connected realm, så yieldar man istället rad för rad istället för alla cirka 30-50 k rader
                #yield data["auctions"] # Detta blir batchar man yieldar med 30 k rader svårt för dlt att behandla
        except Exception as e:
            print(f"DENNA MISSLYCKADES nr{counter} realm id: {realm_id}")
        print(f"\nYIELDAT NR {counter} <-------------------\n") #DEBUG


# Fetch AH commodities
@dlt.resource(table_name="commodities", write_disposition="replace") # merge?
def fetch_ah_commodities():
    endpoint = f"/data/wow/auctions/commodities"                             
    params = {                
        "namespace" : "dynamic-eu",
        }
    response = auth_util.get_api_response(endpoint=endpoint, params=params)
    data = response.json()
    for auction in data["auctions"]:
        yield auction


# Returns a list of indexes for item classes
def fetch_item_classes(): 
    endpoint = "/data/wow/item-class/index"
    params = {
        "namespace": "static-eu"
    }
    item_class_ids = []
    response = auth_util.get_api_response(endpoint=endpoint, params=params)
    data = response.json()
    for id in data.get("item_classes", []):
        item_class_ids.append(id["id"])
    return item_class_ids

# Returns a dictionary of indexes for item subclasses
def fetch_item_subclasses():
    item_class_ids = fetch_item_classes()
    subclass_dict = {}

    for item_class_id in item_class_ids:
        endpoint = f"/data/wow/item-class/{item_class_id}"
        params = {
            "namespace": "static-eu",
            "region": "eu"
        }

        response = auth_util.get_api_response(endpoint=endpoint, params=params)
        data = response.json()

        subclass_ids = [subclass["id"] for subclass in data.get("item_subclasses", [])]
        subclass_dict[item_class_id] = subclass_ids

        print(f"Item class {item_class_id} has subclasses: {subclass_ids}")
    return subclass_dict

@dlt.resource(table_name="item_media", write_disposition="replace")
def fetch_media_hrfs():
    db_path = "wow_api_dbt/wow_api_data.duckdb"
    
    with db.DuckDBConnection(db_path) as db_handler:
        df = db_handler.query("SELECT DISTINCT media_id FROM refined.dim_items WHERE media_id IS NOT NULL")
        # df = df[:100] # For testing purposes, limit to 100 rows
    amount_of_media = len(df)
    current_media = 0
    for _, row in df.iterrows():
        try:
            media_id = int(row["media_id"])
        except (ValueError, TypeError):
            print(f"Skipping invalid media_id: {row['media_id']}")
            continue

        endpoint = f"/data/wow/media/item/{media_id}"
        params = {"namespace": "static-eu"}

        try:
            response = auth_util.get_api_response(endpoint=endpoint, params=params)
            data = response.json()
        except Exception as e:
            print(f"Failed to fetch or parse media {media_id}: {e}")
            continue

        assets = data.get("assets", [])
        if not isinstance(assets, list):
            print(f"Invalid assets format for media {media_id}")
            continue

        for asset in assets:
            if asset.get("key") == "icon":
                url = asset.get("value")
                if isinstance(url, str) and url.startswith("http"):
                    yield {
                        "media_id": media_id,
                        "url": url
                    }
                    current_media += 1
                    if current_media >= amount_of_media:
                        break
                else:
                    print(f"Invalid or missing URL for media {media_id}")
        print(f"Current media count: {current_media}/{amount_of_media}: {url}")


@dlt.resource(table_name="item_details", write_disposition="replace")
def fetch_item_details():
    db_path = "wow_api_dbt/wow_api_data.duckdb"
    subclass_dict = fetch_item_subclasses()
    for item_class_id, subclass_ids in subclass_dict.items():
        for subclass_id in subclass_ids:
            with db.DuckDBConnection(db_path) as db_handler:
                df = db_handler.query(f"SELECT DISTINCT id FROM refined.dim_items where item_class_id = {item_class_id} and item_subclass_id = {subclass_id}")
                df = df[:1] # For testing purposes, limit to 1 row
            amount_of_details = len(df)
            current_details = 0
            for _, row in df.iterrows():
                item_id = int(row["id"])
                endpoint = f"/data/wow/item/{item_id}"
                params = {"namespace": "static-eu"}
                return_frame = pd.DataFrame()

                try:
                    response = auth_util.get_api_response(endpoint=endpoint, params=params)
                    data = response.json()
                    return_frame["id"] = [data.get("id")]
                    if "description" in data:
                        return_frame["description"] = [data.get("description", {}).get("en_US")]
                    if "binding" in data:
                        return_frame["binding_name"] = [data.get("binding", {}).get("name",{})]
                    if "item_preview" in data:
                        return_frame["item_preview"] = [data.get("item_preview", {})]
                except Exception as e:
                    print(f"Failed to fetch or parse item {item_id}: {e}")
                    continue

                if not isinstance(data, dict) or "id" not in data:
                    print(f"Invalid data format for item {item_id}")
                    continue

                #yield return_frame
                yield data
                current_details += 1
                if current_details >= amount_of_details:
                    break
                print(f"Current item details count: {current_details}/{amount_of_details} for item ID: {item_id}")
       

# Return all items, one rarity, class and subclass at a time
@dlt.resource(table_name="items", write_disposition="merge", primary_key="id")
def fetch_items():
    subclass_dict = fetch_item_subclasses()
    all_items = []
    rarities = [
        "Poor",        # Gray
        "Common",      # White
        "Uncommon",    # Green
        "Rare",        # Blue
        "Epic",        # Purple
        "Legendary",   # Orange
        "Artifact",    # Gold
        "Heirloom"     # Light Gold
    ]

    for item_class_id, subclass_ids in subclass_dict.items():
        for subclass_id in subclass_ids:
            for rarity in rarities:
                page = 1
                while True:
                    endpoint = "/data/wow/search/item"
                    params = {
                        "namespace": "static-eu",
                        "orderby": "id",
                        "_page": page,
                        "item_class.id": item_class_id,
                        "item_subclass.id": subclass_id,
                        "quality.name.en_US": rarity,
                    }

                    response = auth_util.get_api_response(endpoint=endpoint, params=params)
                    data = response.json()

                    results = data.get("results", [])
                    if not results:
                        break

                    for result in results:
                        yield result["data"]

                    print(f"Fetched {len(results)} items for class {item_class_id}, subclass {subclass_id}, page {page}")
                    
                    page += 1

                    if page > 10:
                        print(f"⚠️ Stopped after 10 pages for subclass {subclass_id}")
                        break

    print(f"✅ Fetched total {len(all_items)} items.")
    return all_items


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
            method_list.append(fetch_ah_commodities())
        if "items" in optional_source_list:
            method_list.append(fetch_items())
        if "realm_data" in optional_source_list:
            method_list.append(fetch_realm_data())
        return method_list
    else:
        #return [fetch_item_details()] 
        return [fetch_media_hrfs(),fetch_ah_commodities(),fetch_auction_house_items(),fetch_items(),fetch_realm_data(),fetch_item_details()] # # For testing purposes, we only run the media fetch resource

if __name__ == "__main__":
    fetch_item_details()

