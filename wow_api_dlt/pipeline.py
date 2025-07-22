import dlt

from .resources.source import wow_api_source
import os

DB_PATH = os.path.abspath("wow_api_dbt/wow_api_data.duckdb")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def run_pipeline(sources = None, test_mode=False,scheema="raw"):
    pipeline = dlt.pipeline(
    pipeline_name = "wow_api_data",  # The name of the pipeline for test mode
    destination = dlt.destinations.duckdb(str(DB_PATH)),  # The destination where the data will be loaded
    dataset_name = scheema,  # The name of the dataset for test mode
    progress = "log"  # The progress reporting mode, can be "log", "console", or "none"
    )
    if sources is not None:
        # If a specific source list is provided, we use it to run only those resources
        load_info = pipeline.run(wow_api_source(optional_source_list=sources,test_mode=test_mode))
    else:
        load_info = pipeline.run(wow_api_source(test_mode=test_mode))
    if load_info:    
        print(load_info)
    
if __name__ == "__main__":
    run_pipeline()