import pandas as pd
from wow_api_dlt.db import DuckDBConnection
from pathlib import Path

# Temporary (until database is on a server)
working_directory = Path(__file__).resolve().parent.parent
dbt_folder = "wow_api_dbt"
db_filename = "wow_api_data.duckdb"
db_path = working_directory / dbt_folder / db_filename

def fetch_data_from_db(query: str, params=None) -> pd.DataFrame:
    with DuckDBConnection(db_path) as conn:
        return conn.query(query, params)