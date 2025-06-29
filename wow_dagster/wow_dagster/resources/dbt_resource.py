# wow_dagster/wow_dagster/resources/dbt_resource.py
from dagster_dbt import DbtCliResource
from pathlib import Path

# --- DEN KORREKTA SÖKVÄGEN ---
# Vi går upp TRE steg från /resources, vilket är rätt härifrån.
DBT_PROJECT_DIR = (
    Path(__file__).resolve().parents[3] / "wow_api_dbt"
)

dbt_resource = DbtCliResource(project_dir=str(DBT_PROJECT_DIR))
