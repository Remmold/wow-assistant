import dlt
from mounts_pipeline import blizzard_api_source as mount_source
from journal_pipeline import journal_api_source
from journal_encounters_pipeline import journal_encounter_source
from items_pipeline import item_api_source  # ✅ ADD THIS

PIPELINES = {
    "mounts": False,
    "journal": False,
    "journal_encounters": False,
    "items": True  # ✅ Enable when needed
}

# ✅ Fixed destination: outputs to your dbt_wow_assistant folder
pipeline = dlt.pipeline(
    pipeline_name="wow_pipeline",
    destination=dlt.destinations.duckdb(
        credentials="dbt_wow_assistant/wow_assistant.duckdb"
    ),
    dataset_name="raw"
)

def run_selected_pipelines():
    sources = []

    if PIPELINES.get("mounts"):
        print("[🐎] Mounts enabled — adding to run list.")
        sources.append(mount_source())

    if PIPELINES.get("journal"):
        print("[📘] Journal Instances enabled — adding to run list.")
        sources.append(journal_api_source(limit=None))  # Limit for testing

    if PIPELINES.get("journal_encounters"):
        print("[⚔️] Journal Encounters enabled.")
        sources.append(journal_encounter_source(limit=None))  # Limit for testing
    if PIPELINES.get("items"):
        print("[🧤] Item API enabled — fetching item data.")
        sources.append(item_api_source(calls_per_hour=25000))  # ✅ Adjust this limit

    if not sources:
        print("⚠️ No pipelines selected to run. Update the PIPELINES dict.")
        return

    load_info = pipeline.run(sources)
    print(load_info)

if __name__ == "__main__":
    run_selected_pipelines()
