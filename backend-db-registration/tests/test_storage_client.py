from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError
from storage.storage_client import StorageClient


class MockBoto3S3Client:
    def __init__(self, test_data=None):
        self.test_data = test_data or {}

    def head_bucket(self, **kwargs):
        """バケットの存在確認をモック（boto3形式）"""
        # boto3では例外が発生しなければバケットが存在
        pass

    def list_buckets(self):
        """バケット一覧をモック（boto3形式）"""
        return {"Buckets": []}  # boto3形式のレスポンス

    def get_object(self, **kwargs):
        """オブジェクト取得をモック（boto3形式）"""
        key = kwargs["Key"]
        if key in self.test_data:
            return MockS3Response(self.test_data[key])
        # boto3形式のNoSuchKey例外を発生
        error_response = {
            "Error": {
                "Code": "NoSuchKey",
                "Message": f"The specified key does not exist. Key: {key}",
            }
        }
        raise ClientError(error_response, "GetObject")

    def get_paginator(self, operation_name):
        """ページネーターをモック"""
        return MockPaginator(self.test_data)


class MockS3Response:
    """boto3 S3レスポンスをモック"""

    def __init__(self, data):
        self.data = data
        # boto3のget_object()レスポンス形式に合わせる
        self.body = Mock()
        self.body.read.return_value = data.encode("utf-8")

    def __getitem__(self, key):
        if key == "Body":
            return self.body
        return None


class MockPaginator:
    """boto3 paginatorをモック"""

    def __init__(self, test_data):
        self.test_data = test_data

    def paginate(self, **kwargs):
        """ページネーション結果をモック"""
        prefix = kwargs.get("Prefix", "")
        # プレフィックスに一致するファイルを抽出
        matching_files = []
        for key in self.test_data:
            if key.startswith(prefix):
                matching_files.append({"Key": key})

        # boto3形式のページレスポンス
        if matching_files:
            yield {"Contents": matching_files}
        else:
            yield {}


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
        """,
    }

    # boto3.clientをモックに置き換え
    monkeypatch.setattr(
        "boto3.client",
        lambda *args, **kwargs: MockBoto3S3Client(test_yaml_data),
    )

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
    yaml_data = mock_storage_client.read_yaml_from_storage("human_test.yaml")

    # 検証
    assert yaml_data is not None
    assert yaml_data["name"] == "テスト太郎"
    assert yaml_data["bio"] == "テスト用の人間メンバーです"


def test_read_virtual_member_yaml(mock_storage_client):
    """仮想メンバーのYAMLファイル読み込みテスト"""
    # YAMLファイルを読み込み
    yaml_data = mock_storage_client.read_yaml_from_storage("virtual_test.yaml")

    # 検証
    assert yaml_data is not None
    assert yaml_data["name"] == "AIアシスタント"
    assert yaml_data["bio"] == "テスト用の仮想メンバーです"


def test_read_nonexistent_yaml(mock_storage_client):
    """存在しないYAMLファイルの読み込みテスト"""
    # 存在しないファイルを読み込もうとする
    with pytest.raises(Exception) as exc_info:
        mock_storage_client.read_yaml_from_storage("nonexistent.yaml")

    # エラーメッセージを検証
    assert "File not found" in str(exc_info.value)
