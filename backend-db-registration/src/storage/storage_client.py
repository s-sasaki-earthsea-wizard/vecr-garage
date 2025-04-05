import os
import yaml
from io import BytesIO
from minio import Minio

class StorageClient:
    def __init__(self):
        # Get authentication information from environment variables
        self.client = Minio(
            f"{os.environ.get('STORAGE_HOST')}:{os.environ.get('STORAGE_PORT')}",
            access_key=os.environ.get('MINIO_ROOT_USER'),
            secret_key=os.environ.get('MINIO_ROOT_PASSWORD'),
            secure=False  # In development, HTTP is fine. In production, it should be True
        )
        self.bucket_name = os.environ.get('MINIO_BUCKET_NAME')
    
    def storage_connection_check(self):
        """
        Check connection to storage
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            Exception: If connection fails
        """
        try:
            self._check_bucket_exists()
            self.client.list_buckets()
            return True
        except Exception as e:
            raise Exception(f"❌ Error connecting to storage: {e}")

    def _check_bucket_exists(self, bucket_name=None):
        """
        Check if a specific bucket exists
        
        Args:
            bucket_name (str, optional): Name of the bucket to check. If None, uses self.bucket_name
            
        Returns:
            bool: True if the bucket exists, False otherwise
        """
        if bucket_name is None:
            bucket_name = self.bucket_name
            
        try:
            return self.client.bucket_exists(bucket_name)
        except Exception as e:
            raise Exception(f"❌ Error checking if bucket {bucket_name} exists: {e}")

    def read_yaml_from_minio(self, object_name: str) -> dict:
        """
        Read a YAML file from a MinIO bucket
        
        Args:
            object_name (str): Object name (including path)
            
        Returns:
            dict: The YAML data read
            
        Raises:
            Exception: If reading the file fails
        """
        response = None
        try:
            # Get the object
            response = self.client.get_object(self.bucket_name, object_name)
            
            # Read the binary data into memory
            yaml_data = BytesIO(response.read())
            
            # Parse as YAML
            data = yaml.safe_load(yaml_data)
            
            # Close the connection
            response.close()
            response.release_conn()
            
            return data
        except Exception as e:
            raise Exception(f"❌ Error reading {object_name} from {self.bucket_name}: {e}")

def main():
    storage_client = StorageClient()

    if storage_client.storage_connection_check():
        print("✅ Successfully connected to storage!")

    try:
        # Read specific files
        syota_data = storage_client.read_yaml_from_minio("data/human_members/Syota.yml")
        kasen_data = storage_client.read_yaml_from_minio("data/virtual_members/Kasen.yml")

        print(f"Syota data: {syota_data}")
        print(f"Kasen data: {kasen_data}")

    except Exception as e:
        raise Exception(f"❌ Error reading data from storage: {e}")

if __name__ == "__main__":
    main()
