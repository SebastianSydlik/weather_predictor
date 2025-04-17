from pathlib import Path
import pandas as pd
import pandas_gbq
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from pathlib import Path


@task(retries=3)
def extract_from_gcs(town: str):
    """Download a single trip data file from GCS"""
    file_name = f"{town}_data.parquet"
    gcs_path = f"data/{file_name}"             # Path inside GCS bucket
    local_path = Path("data") / file_name      # Local destination

    gcs_block = GcsBucket.load("gcs-connector")

    # Ensure local folder exists
    local_path.parent.mkdir(parents=True, exist_ok=True)

    gcs_block.download_object_to_path(
        from_path=gcs_path,
        to_path=local_path
    )

    return local_path

@task()
def transform(path):
    """Data cleaning"""
    df = pd.read_parquet(path)
    print('placeholder for data transformation')
    return df

@task()
def write_BigQuery(df, town: str):
    """Write Dataframe"""
    gcp_credentials_block = GcpCredentials.load("gcp-creds")

    pandas_gbq.to_gbq(
        df, 
        destination_table = f"weather_dataset_0.{town}",
        project_id = "dataengineering-455510",
        credentials = gcp_credentials_block.get_credentials_from_service_account(),
        if_exists="append", 

    )
    
@flow()
def gcs_to_BigQuery(town:str):
    """Main ETL flow to load data into BigQuery"""
    path = extract_from_gcs(town)
    df = transform(path)
    write_BigQuery(df, town)

@flow()
def gcs_to_BigQuery_parent_flow():
         
    locations = {
        "Wuppertal": {"latitude": 51.26, "longitude": 7.15,},
        "Bruegge": {"latitude": 51.22, "longitude": 3.22,},
        "Groningen": {"latitude": 53.22, "longitude": 6.57,},
        "Erfurt": {"latitude": 50.98, "longitude": 11.03,},
        "Saarbruecken": {"latitude": 49.23, "longitude": 7.00,},
	}

    for town, location in locations.items():
        gcs_to_BigQuery(town)
    return
          
if __name__ == "__main__":
    gcs_to_BigQuery_parent_flow()