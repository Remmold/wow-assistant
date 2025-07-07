from wow_api_dlt import auth_util

# Fetch and bring all the connected realm IDs, returns a list of IDs
def fetch_realm_ids():
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