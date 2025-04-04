from minio import Minio
import os

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

    def read_yaml_from_minio(self, object_name):
        """
        Read a YAML file from a MinIO bucket
        
        Args:
            bucket_name (str): Bucket name
            object_name (str): Object name (including path)
            
        Returns:
            dict: The YAML data read
        """
        import yaml
        from io import BytesIO
        
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
            print(f"Error reading {object_name} from {self.bucket_name}: {e}")
            return None

def main():
    storage_client = StorageClient()
    # Read specific files
    syota_data = storage_client.read_yaml_from_minio("data/human_members/Syota.yml")
    kasen_data = storage_client.read_yaml_from_minio("data/virtual_members/Kasen.yml")

    print(f"Syota data: {syota_data}")
    print(f"Kasen data: {kasen_data}")

    # Alternatively, enumerate all files in the directory
    objects = storage_client.client.list_objects(
        storage_client.bucket_name, prefix="data/human_members/",
        recursive=True
        )
    for obj in objects:
        print(f"Found object: {obj.object_name}, size: {obj.size}")

if __name__ == "__main__":
    main()
