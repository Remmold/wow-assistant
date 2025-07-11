import dlt
from wow_api_dlt.resources.resources_auctions import fetch_auction_house_items, fetch_ah_commodities
from wow_api_dlt.resources.resources_items import fetch_items, fetch_item_details
from wow_api_dlt.resources.resources_misc import fetch_media_hrfs,fetch_realm_data

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

