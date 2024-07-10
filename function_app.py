import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="tradePriceLog")
def tradePriceLog(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    stock_name = req.params.get('stock_name')
    date = req.params.get('date')
    low = req.params.get('low')
    high = req.params.get('high')

    if not stock_name or not date or not low or not high:
            return func.HttpResponse(
                "Please pass stock_name, date, low, and high on the query string or in the request body",
                status_code=400
            )
    
    connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    container_name = os.environ['AZURE_STORAGE_BLOB_CONTAINER_NAME']

    if not connection_string:
            logging.error("AZURE_STORAGE_CONNECTION_STRING environment variable is not set.")
            return func.HttpResponse(
                "Azure Storage connection string is not configured properly",
                status_code=500
            )

    if not container_name:
            logging.error("AZURE_STORAGE_BLOB_CONTAINER_NAME environment variable is not set.")
            return func.HttpResponse(
                "Azure Storage container name is not configured properly",
                status_code=500
            )

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{stock_name}_{date}.json")

    stock_data = {
            "stock_name": stock_name,
            "date": date,
            "low": low,
            "high": high
        }
    
    stock_data_json = json.dumps(stock_data)
    blob_client.upload_blob(stock_data_json, overwrite=True)

    return func.HttpResponse(f"Stock data saved: {stock_data_json}", status_code=200)
    