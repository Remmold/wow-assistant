import dlt
from resources import wow_api_source

def run_pipeline():
    pipeline = dlt.pipeline(
    pipeline_name="wow_api_data",  # The name of the pipeline
    destination="duckdb",  # The destination where the data will be loaded
    dataset_name="raw",  # The name of the dataset
    progress="alive_progress"
    )
    load_info = pipeline.run(wow_api_source())
    print(load_info)

if __name__ == "__main__":
    run_pipeline()