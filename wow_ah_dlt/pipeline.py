import dlt
from resources import wow_ah_source

def run_pipeline():
    pipeline = dlt.pipeline(
    pipeline_name="wow_api_data",  # The name of the pipeline
    destination="duckdb",  # The destination where the data will be loaded
    dataset_name="raw"  # The name of the dataset
    )
    load_info = pipeline.run(wow_ah_source())
    print(load_info)

if __name__ == "__main__":
    run_pipeline()