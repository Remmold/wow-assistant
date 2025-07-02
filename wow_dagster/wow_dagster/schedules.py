# wow_dagster/schedules.py
from dagster_dbt import build_schedule_from_dbt_selection
from .assets.dlt_asset import wow_api_source
import dagster as dg
from .assets.dbt_assets import wow_dbt_assets




daily_refresh_job = dg.define_asset_job(
    "hourly_refresh", 
    selection=dg.AssetSelection.assets("dlt_wow_api_data_fetch_auction_house_items", "dlt_wow_api_data_fetch_ah_commodities").downstream()
)

daily_schedule = dg.ScheduleDefinition(
    job=daily_refresh_job,
    cron_schedule="0 * * * *", # Every hour  
)
