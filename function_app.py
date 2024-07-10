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

    connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    container_name = os.environ['AZURE_STORAGE_BLOB_CONTAINER_NAME']

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
    