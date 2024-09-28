from minio import Minio
from minio.error import S3Error
import io
import os
from flask import current_app

class S3Service:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(S3Service, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.client = Minio(
            os.getenv('S3_ENDPOINT'),
            access_key=os.getenv('S3_ACCESS_KEY'),
            secret_key=os.getenv('S3_SECRET_KEY'),
            secure=True  # Set to True if using HTTPS
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    def ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            current_app.logger.error(f"Error occurred, bucket may not exist: {str(e)}")

    def upload_file(self, file_data, object_name):
        try:
            self.ensure_bucket_exists()
            file_size = len(file_data)
            self.client.put_object(
                self.bucket_name, object_name, io.BytesIO(file_data), file_size
            )
            return True
        except S3Error as e:
            current_app.logger.error(f"Error uploading file to S3: {str(e)}")
            return False

    def get_file(self, object_name):
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except S3Error as e:
            current_app.logger.error(f"Error getting file from S3: {str(e)}")
            return None

    def delete_file(self, object_name):
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            current_app.logger.error(f"Error deleting file from S3: {str(e)}")
            return False


s3_service = S3Service()