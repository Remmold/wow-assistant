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
    response = auth_util.get_auth_token_and_request(endpoint=endpoint, params=params)
    connected_realm_list = response.json()["connected_realms"]
    
    list_of_realm_ids = [x["href"].split("/")[-1].split("?")[0] for x in connected_realm_list]
    return list_of_realm_ids
REALM_IDS = _fetch_ids()

# Fetch ah
@dlt.resource(table_name="weapons_armor", write_disposition="replace")
def retrieve_auction_house_items():
    counter = 0 #DEBUG
    for realm_id in REALM_IDS[:2]:
        try:
            endpoint = f"/data/wow/connected-realm/{realm_id}/auctions"                             
            params = {                
                "{{connectedRealmId}}" : realm_id,
                "namespace" : "dynamic-eu",
                }
            response = auth_util.get_auth_token_and_request(endpoint=endpoint, params=params)
            counter += 1 #DEBUG
            data = response.json()
            for auction in data["auctions"]:
                auction["realm_id"] = realm_id
            yield data["auctions"]
        except Exception as e:
            print(f"DENNA MISSLYCKADES nr{counter}")
        print(f"\nYIELDAT NR {counter} <-------------------\n") #DEBUG
    
# Fetch ah commodities
@dlt.resource(table_name="wow_commodities", write_disposition="replace") # merge?
def fetch_ah_commodities():
    pass


# Fetch items
@dlt.resource(table_name="wow_items",write_disposition="merge",primary_key="id")
def fetch_items():
    pass

# @dlt.source that we use in pipeline.run instead of @dlt.resource we use all the resources we want to run in the pipeline
@dlt.source(name="wow_ah")
def wow_ah_source():
    """
    This is the source function that will be used in the pipeline.
    It returns all the resources that we want to run in the pipeline.
    """
    return [retrieve_auction_house_items()]
    







