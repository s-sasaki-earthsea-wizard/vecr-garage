import pytest
import yaml
from io import BytesIO
from storage.storage_client import StorageClient

class MockMinioClient:
    def __init__(self, test_data=None):
        self.test_data = test_data or {}
    
    def bucket_exists(self, bucket_name):
        """バケットの存在確認をモック"""
        return True  # テスト用に常にTrueを返す
    
    def list_buckets(self):
        """バケット一覧をモック"""
        return []  # テスト用に空のリストを返す
    
    def get_object(self, bucket_name, object_name):
        if object_name in self.test_data:
            return MockResponse(self.test_data[object_name])
        raise Exception(f"Object {object_name} not found in bucket {bucket_name}")

class MockResponse:
    def __init__(self, data):
        self.data = data
    
    def read(self):
        return self.data.encode('utf-8')
    
    def close(self):
        pass
    
    def release_conn(self):
        pass

@pytest.fixture
def mock_storage_client(monkeypatch):
    """ストレージクライアントのモックを作成するフィクスチャ"""
    # テスト用のYAMLデータ
    test_yaml_data = {
        "human_test.yaml": """
        name: テスト太郎
        bio: テスト用の人間メンバーです
        """,
        "virtual_test.yaml": """
        name: AIアシスタント
        bio: テスト用の仮想メンバーです
        """
    }
    
    # MinioClientをモックに置き換え
    monkeypatch.setattr("storage.storage_client.Minio", lambda *args, **kwargs: MockMinioClient(test_yaml_data))
    
    # 環境変数を設定
    monkeypatch.setenv("STORAGE_HOST", "localhost")
    monkeypatch.setenv("STORAGE_PORT", "9000")
    monkeypatch.setenv("MINIO_ROOT_USER", "testuser")
    monkeypatch.setenv("MINIO_ROOT_PASSWORD", "testpassword")
    monkeypatch.setenv("MINIO_BUCKET_NAME", "test-bucket")
    
    return StorageClient()

def test_storage_connection_check(mock_storage_client):
    """ストレージ接続チェックのテスト"""
    # 接続チェックを実行
    result = mock_storage_client.storage_connection_check()
    
    # 検証
    assert result is True

def test_read_human_member_yaml(mock_storage_client):
    """人間メンバーのYAMLファイル読み込みテスト"""
    # YAMLファイルを読み込み
    yaml_data = mock_storage_client.read_yaml_from_minio("human_test.yaml")
    
    # 検証
    assert yaml_data is not None
    assert yaml_data["name"] == "テスト太郎"
    assert yaml_data["bio"] == "テスト用の人間メンバーです"

def test_read_virtual_member_yaml(mock_storage_client):
    """仮想メンバーのYAMLファイル読み込みテスト"""
    # YAMLファイルを読み込み
    yaml_data = mock_storage_client.read_yaml_from_minio("virtual_test.yaml")
    
    # 検証
    assert yaml_data is not None
    assert yaml_data["name"] == "AIアシスタント"
    assert yaml_data["bio"] == "テスト用の仮想メンバーです"

def test_read_nonexistent_yaml(mock_storage_client):
    """存在しないYAMLファイルの読み込みテスト"""
    # 存在しないファイルを読み込もうとする
    with pytest.raises(Exception) as exc_info:
        mock_storage_client.read_yaml_from_minio("nonexistent.yaml")
    
    # エラーメッセージを検証
    assert "Object nonexistent.yaml not found" in str(exc_info.value) 