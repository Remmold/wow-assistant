from wow_api_dlt.utilities import  auth_util
import sys

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
    item_class_dict = {}
    response = auth_util.get_api_response(endpoint=endpoint, params=params)
    data = response.json()
    
    for item in data.get("item_classes", []):
        item_class_dict[item["id"]] = {"name": item["name"]["en_US"]}
    for key,value in item_class_dict.items():
        print(f"Item class ID: {key}, Name: {value['name']}")
    return item_class_dict

# Returns a dictionary of indexes for item subclasses
def fetch_item_class_and_subclasses():
    item_class_dict = fetch_item_classes()
    

    for item_class_id,value in item_class_dict.items():
        endpoint = f"/data/wow/item-class/{item_class_id}"
        params = {
            "namespace": "static-eu",
            "region": "eu"
        }

        response = auth_util.get_api_response(endpoint=endpoint, params=params)
        data = response.json()

        subclass_ids = [subclass["id"] for subclass in data.get("item_subclasses", [])]
        value["subclass_ids"] = subclass_ids

        print(f"Item class {value['name']} has subclasses: {subclass_ids}")
    return item_class_dict

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

if __name__ == "__main__":
    fetch_item_classes()