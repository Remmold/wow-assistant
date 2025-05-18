import dlt
from mounts_pipeline import blizzard_api_source
from dlt.destinations import duckdb

if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="wow_pipeline",
        destination=duckdb(credentials="dbt_wow_assistant/wow_assistant.duckdb"),
        dataset_name="raw"
    )

    load_info = pipeline.run(blizzard_api_source())
    print(load_info)
