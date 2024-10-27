from io import BytesIO
from flask import Response
import functions_framework
from google.cloud import storage

@functions_framework.http
def hello_http(request):
    storage_client = storage.Client()
    bucket_name = 'cis-tachyla-lab-07'
    blob_name = 'xd.png'

    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if blob.exists():
            contents = BytesIO()
            blob.download_to_file(contents)
            contents.seek(0)  # Reset the file pointer to the beginning
            return Response(contents, mimetype='image/png')
        else:
            return f'Blob "{blob_name}" not found in bucket "{bucket_name}".', 404
    except Exception as e:
        return f'An error occurred: {str(e)}', 500