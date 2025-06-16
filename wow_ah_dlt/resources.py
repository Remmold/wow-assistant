import dlt
import auth_util

# Fetch and bring all the connected realm ids cut out the id from url and put into a list
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
REALM_IDS = _fetch_ids()

# Fetch ah
@dlt.resource(table_name="auctions", write_disposition="replace")
def fetch_auction_house_items():
    counter = 0 #DEBUG
    for realm_id in REALM_IDS[:10]: # 92
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
            yield data["auctions"]
        except Exception as e:
            print(f"DENNA MISSLYCKADES nr{counter} realm id: {realm_id}")
        print(f"\nYIELDAT NR {counter} <-------------------\n") #DEBUG
    
@dlt.resource(table_name="realm_data", write_disposition="replace")
def fetch_realm_data():
    for realm_id in REALM_IDS:
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


# Fetch ah commodities
@dlt.resource(table_name="commodities", write_disposition="replace") # merge?
def fetch_ah_commodities():
    pass


@dlt.resource(table_name="test", write_disposition="merge", primary_key="id")
def fetch_items():
    endpoint = "/data/wow/search/item"
    params = {
        ":region": "eu",
        "namespace": "static-eu",
        "orderby": "id",
        "_page": 1,

    }
    page = 1
    while True:
        params["_page"] = page
        print(params["_page"])
        response = auth_util.get_api_response(endpoint=endpoint, params=params)
        print(response.text)
        print("test")
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("⚠️ No more results found. Stopping pagination.")
            break
        for item in results:
            yield item["data"]
        if page == 11:
            print("⚠️ 1000 results fetched - limit reached for this run.")
            break
        print(f"Fetched {len(results)} results...")
        page += 1





# @dlt.source that we use in pipeline.run instead of @dlt.resource we use all the resources we want to run in the pipeline
@dlt.source(name="wow_ah")
def wow_ah_source():
    """
    This is the source function that will be used in the pipeline.
    It returns all the resources that we want to run in the pipeline.
    """
    return [fetch_items()]




