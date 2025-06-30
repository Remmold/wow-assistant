# wow_dagster/assets/dbt_assets.py
from dagster_dbt import dbt_assets, DbtCliResource, DagsterDbtTranslator
from pathlib import Path
from dagster import AssetExecutionContext

WORKING_DIR = Path(__file__).resolve().parents[3]
MAN_PATH = WORKING_DIR / "wow_api_dbt" / "target" / "manifest.json"

# 1. Mini-translator i EN rad
dbt_translator = type(
    "WowTranslator",
    (DagsterDbtTranslator,),
    {"get_group_name": lambda self, _props: "dbt_wow_data"},
)()

# 2. Skicka in som keyword-argument
@dbt_assets(
    manifest=MAN_PATH,
    #dagster_dbt_translator=dbt_translator,   # ← enda nya argumentet
)
def wow_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

