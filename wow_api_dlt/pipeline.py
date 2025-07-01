import dlt
from resources import wow_api_source

DB_PATH = "wow_api_dbt/wow_api_data.duckdb"
DB_TEST_PATH = "wow_api_dbt/test_wow_api_data.duckdb"

def run_pipeline(testmode=False):
    if testmode:
        pipeline = dlt.pipeline(
        pipeline_name="wow_api_data_test",  # The name of the pipeline for test mode
        destination=dlt.destinations.duckdb(str(DB_TEST_PATH)),  # The destination where the data will be loaded
        dataset_name="test",  # The name of the dataset for test mode
        progress="log"  # The progress reporting mode, can be "log", "console", or "none"
        )    
        load_info = pipeline.run(wow_api_source(test_mode=True))  # Run the pipeline with test mode enabled
    else:
        pipeline = dlt.pipeline(
        pipeline_name="wow_api_data",  # The name of the pipeline
        destination=dlt.destinations.duckdb(str(DB_PATH)),  # The destination where the data will be loaded
        dataset_name="raw",  # The name of the dataset
        progress="log" # The progress reporting mode, can be "log", "console", or "none"
        )

        load_info = pipeline.run(wow_api_source())
    print(load_info)

if __name__ == "__main__":
    run_pipeline()