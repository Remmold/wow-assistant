# wow_dagster/wow_dagster/definitions.py
from dagster import Definitions

# DLT imports
from .resources.dlt_resource import dlt_resource       
from .assets.dlt_asset import raw_wow_assets     

# DBT imports
from .resources.dbt_resource import dbt_resource     
from .assets.dbt_assets import wow_dbt_assets        

# Define the assets and resources for the Dagster Definitions
# This is where we define the assets and resources that will be used in the Dagster pipeline
defs = Definitions(
    assets=[
        raw_wow_assets,    # DLT assets for data ingestion
        wow_dbt_assets,       # dbt assets for data transformation
    ],
    resources={
        "dlt": dlt_resource,   # DLT resource for data ingestion DagsterDltResource
        "dbt": dbt_resource,   # DBT resource for data transformation
    },
    
)