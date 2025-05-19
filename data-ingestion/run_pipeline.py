import dlt
from mounts_pipeline import blizzard_api_source as mount_source
from dungeons_pipeline import dungeon_api_source

# Toggle pipelines here 👇
PIPELINES = {
    "mounts": False,
    "dungeons": True
}

pipeline = dlt.pipeline(
    pipeline_name="wow_pipeline",
    destination="duckdb",
    dataset_name="raw"
)

def run_selected_pipelines():
    sources = []

    if PIPELINES.get("mounts"):
        print("[🐎] Mounts enabled — adding to run list.")
        sources.append(mount_source())

    if PIPELINES.get("dungeons"):
        print("[🏰] Dungeons enabled — adding to run list.")
        sources.append(dungeon_api_source())

    if not sources:
        print("⚠️ No pipelines selected to run. Update the PIPELINES dict.")
        return

    load_info = pipeline.run(sources)
    print(load_info)

if __name__ == "__main__":
    run_selected_pipelines()
