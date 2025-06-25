# wow_dagster/wow_dagster/definitions.py
from dagster import Definitions

from .resources.dlt_resource import dlt_resource       
from .assets.dlt_asset import raw_ingest_assets       

defs = Definitions(
    assets=[raw_ingest_assets],
    resources={"dlt": dlt_resource},
)
