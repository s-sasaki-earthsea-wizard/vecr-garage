import os

import boto3
import yaml
from botocore.exceptions import ClientError


class StorageClient:
    """S3互換ストレージサービスとの通信を行うクライアントクラス

    メンバー登録システムで使用するYAMLファイルの読み込み、ファイル一覧取得、
    ストレージ接続確認などの機能を提供します。環境変数から認証情報を
    自動的に取得し、安全なストレージ操作を実現します。

    主な機能:
    - ストレージ接続の確認
    - YAMLファイルの一覧取得
    - YAMLファイルの読み込みとパース
    - バケット存在確認

    Attributes:
        client (boto3.client): S3クライアントインスタンス
        bucket_name (str): 使用するバケット名

    Note:
        - 環境変数から認証情報を取得（STORAGE_HOST, STORAGE_PORT, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD）
        - 開発環境ではHTTP接続、本番環境ではHTTPS接続を推奨
        - boto3ライブラリを使用してS3互換APIでアクセス
        - ローカルMinIOと本番S3の両方に対応
    """

    def __init__(self):
        # 環境変数から認証情報を取得
        storage_host = os.environ.get("STORAGE_HOST")
        storage_port = os.environ.get("STORAGE_PORT")

        # S3互換エンドポイントのURL構築
        endpoint_url = f"http://{storage_host}:{storage_port}"  # 開発環境はHTTP

        # boto3 S3クライアントの初期化
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=os.environ.get("MINIO_ROOT_USER"),
            aws_secret_access_key=os.environ.get("MINIO_ROOT_PASSWORD"),
            region_name="ap-northeast-1",  # 東京リージョン（MinIOではリージョンは任意だがboto3には必須）
            aws_session_token=None,
            verify=False,  # 開発環境でSSL証明書検証を無効化
        )
        self.bucket_name = os.environ.get("MINIO_BUCKET_NAME")

    def storage_connection_check(self):
        """ストレージサービスへの接続を確認する

        バケットの存在確認とストレージサービスの応答をチェックし、
        接続が正常に確立されているかを検証します。

        Returns:
            bool: 接続が成功した場合はTrue

        Raises:
            Exception: 接続に失敗した場合、詳細なエラーメッセージと共に例外を発生

        Example:
            >>> client = StorageClient()
            >>> if client.storage_connection_check():
            ...     print("✅ ストレージ接続成功")
            ... else:
            ...     print("❌ ストレージ接続失敗")
        """
        try:
            self._check_bucket_exists()
            self.client.list_buckets()
            return True
        except Exception as e:
            raise Exception(f"❌ Error connecting to storage: {e}") from e

    def _check_bucket_exists(self, bucket_name=None):
        """指定されたバケットが存在するかを確認する（内部メソッド）

        プライベートメソッドとして実装されており、指定されたバケットが
        ストレージサービスに存在するかをチェックします。

        Args:
            bucket_name (str, optional): 確認するバケット名。Noneの場合はself.bucket_nameを使用

        Returns:
            bool: バケットが存在する場合はTrue、存在しない場合はFalse

        Raises:
            Exception: バケット確認時にエラーが発生した場合

        Note:
            このメソッドは内部使用を想定しており、直接呼び出すことは推奨されません。
            代わりにstorage_connection_check()を使用してください。
        """
        if bucket_name is None:
            bucket_name = self.bucket_name

        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return False
            raise Exception(f"❌ Error checking if bucket {bucket_name} exists: {e}") from e
        except Exception as e:
            raise Exception(f"❌ Error checking if bucket {bucket_name} exists: {e}") from e

    def list_yaml_files(self, prefix=""):
        """指定されたプレフィックスに一致するYAMLファイルの一覧を取得する

        ストレージ内の指定されたディレクトリ（プレフィックス）から
        .yml または .yaml 拡張子を持つファイルのパス一覧を取得します。

        Args:
            prefix (str): ファイルをフィルタリングするプレフィックス（例: "data/human_members/"）

        Returns:
            list: YAMLファイルのパスリスト

        Raises:
            Exception: ファイル一覧取得時にエラーが発生した場合

        Example:
            >>> client = StorageClient()
            >>> human_files = client.list_yaml_files("data/human_members/")
            >>> print(f"Found {len(human_files)} human member files")
            >>> for file in human_files:
            ...     print(f"  - {file}")
        """
        try:
            yaml_files = []

            # boto3のlist_objects_v2を使用してオブジェクト一覧を取得
            paginator = self.client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

            for page in page_iterator:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        object_key = obj["Key"]
                        if object_key.endswith(".yml") or object_key.endswith(".yaml"):
                            yaml_files.append(object_key)

            return yaml_files
        except Exception as e:
            raise Exception(f"❌ Error listing YAML files with prefix '{prefix}': {e}") from e

    def read_yaml_from_storage(self, object_name: str) -> dict:
        """ストレージからYAMLファイルを読み込み、パースされた辞書オブジェクトを返す

        指定されたオブジェクト名（ファイルパス）のYAMLファイルを
        ストレージから読み込み、Pythonの辞書オブジェクトとしてパースします。

        Args:
            object_name (str): 読み込むオブジェクトの名前（パスを含む）

        Returns:
            dict: パースされたYAMLデータ（辞書形式）

        Raises:
            Exception: ファイル読み込みやパース時にエラーが発生した場合

        Example:
            >>> client = StorageClient()
            >>> data = client.read_yaml_from_storage("data/human_members/田中太郎.yml")
            >>> print(f"Name: {data.get('name')}")
            >>> print(f"Age: {data.get('age')}")

        Note:
            - ファイルが見つからない場合は専用のエラーメッセージが表示されます
            - YAML形式が不正な場合はパースエラーが発生します
            - boto3では自動的にリソースが管理されます
        """
        try:
            # boto3でオブジェクトを取得
            response = self.client.get_object(Bucket=self.bucket_name, Key=object_name)

            # ストリームからデータを読み込み
            content = response["Body"].read()

            # YAMLとしてパース
            return yaml.safe_load(content)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchKey":
                raise Exception(
                    f"❌ File not found: {object_name} in bucket {self.bucket_name}"
                ) from e
            raise Exception(f"❌ Error reading {object_name} from {self.bucket_name}: {e}") from e
        except Exception as e:
            raise Exception(f"❌ Error reading {object_name} from {self.bucket_name}: {e}") from e


def main():
    """ストレージクライアントのテスト用メイン関数

    ストレージ接続の確認、ファイル一覧の取得、特定ファイルの読み込みを
    実行し、結果を表示します。開発時の動作確認やデバッグに使用されます。

    実行内容:
    1. ストレージ接続の確認
    2. 全YAMLファイルの一覧表示
    3. 人間メンバーファイルの一覧表示
    4. 仮想メンバーファイルの一覧表示
    5. 特定ファイルの読み込みと内容表示

    Usage:
        python storage_client.py

    Note:
        この関数はテスト用であり、本番環境での使用は推奨されません。
        環境変数が正しく設定されていることを確認してから実行してください。
    """
    storage_client = StorageClient()

    if storage_client.storage_connection_check():
        print("✅ Successfully connected to storage!")

    try:
        # List all YAML files
        print("\n=== All YAML files in storage ===")
        all_files = storage_client.list_yaml_files()
        for file in all_files:
            print(f"  {file}")

        # List human member files
        print("\n=== Human member YAML files ===")
        human_files = storage_client.list_yaml_files("data/samples/human_members/")
        for file in human_files:
            print(f"  {file}")

        # List virtual member files
        print("\n=== Virtual member YAML files ===")
        virtual_files = storage_client.list_yaml_files("data/samples/virtual_members/")
        for file in virtual_files:
            print(f"  {file}")

        # Read specific files
        syota_data = storage_client.read_yaml_from_storage("data/samples/human_members/syota.yml")
        kasen_data = storage_client.read_yaml_from_storage("data/samples/virtual_members/kasen.yml")

        print(f"\nSyota data: {syota_data}")
        print(f"Kasen data: {kasen_data}")

    except Exception as e:
        raise Exception(f"❌ Error reading data from storage: {e}") from e


if __name__ == "__main__":
    main()
