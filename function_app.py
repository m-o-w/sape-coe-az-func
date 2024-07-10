import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobServiceException
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="tradePriceLog")
def tradePriceLog(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        stock_name = req.params.get('stock_name')
        date = req.params.get('date')
        low = req.params.get('low')
        high = req.params.get('high')

        if not stock_name or not date or not low or not high:
            try:
                req_body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    "Invalid request body",
                    status_code=400
                )
            else:
                stock_name = req_body.get('stock_name')
                date = req_body.get('date')
                low = req_body.get('low')
                high = req_body.get('high')

        if not stock_name or not date or not low or not high:
            return func.HttpResponse(
                "Please pass stock_name, date, low, and high on the query string or in the request body",
                status_code=400
            )

        connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        container_name = os.environ.get('AZURE_STORAGE_BLOB_CONTAINER_NAME')

        if not connection_string or not container_name:
            return func.HttpResponse(
                "Azure Storage connection details are not configured properly",
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
    except BlobServiceException as e:
        logging.error(f"Azure Blob Storage error: {e}")
        return func.HttpResponse(
            "Error occurred while interacting with Azure Blob Storage",
            status_code=500
        )
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        return func.HttpResponse(
            "An unexpected error occurred",
            status_code=500
        )
