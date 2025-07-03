import pytest
import yaml
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.base import Base
from operations.member_registration import register_human_member_from_yaml, register_virtual_member_from_yaml
from db.database import get_human_member_by_name, get_virtual_member_by_name

# 環境変数からデータベース接続情報を取得
MEMBER_DB_HOST = os.getenv('MEMBER_DB_HOST', 'db-member')
MEMBER_DB_PORT = os.getenv('MEMBER_DB_PORT', '5432')
MEMBER_DB_USER = os.getenv('MEMBER_DB_USER', 'testuser')
MEMBER_DB_PASSWORD = os.getenv('MEMBER_DB_PASSWORD', 'password')
MEMBER_DB_NAME = os.getenv('MEMBER_DB_NAME', 'test_member_db')

# テスト用のデータベースURL
TEST_DATABASE_URL = f"postgresql://{MEMBER_DB_USER}:{MEMBER_DB_PASSWORD}@{MEMBER_DB_HOST}:{MEMBER_DB_PORT}/{MEMBER_DB_NAME}"

@pytest.fixture(scope="function")
def db_session():
    """テスト用のデータベースセッションを作成するフィクスチャ"""
    print(f"データベース接続URL: {TEST_DATABASE_URL}")
    
    # テスト用のデータベースエンジンを作成
    engine = create_engine(TEST_DATABASE_URL)
    
    # テスト用のテーブルを作成
    Base.metadata.create_all(engine)
    
    # テスト前に全テーブルのデータをクリア
    with engine.connect() as conn:
        # 依存関係を考慮して、子テーブルから親テーブルの順でtruncate
        truncate_sql = text("TRUNCATE TABLE virtual_member_profiles, virtual_members, human_members RESTART IDENTITY CASCADE")
        conn.execute(truncate_sql)
        conn.commit()
    
    # テスト用のセッションを作成
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        # テスト後にセッションをクローズ
        session.close()
        # テーブル削除は依存関係があるため、エラーを無視して削除を試行
        try:
            Base.metadata.drop_all(engine)
        except Exception as e:
            print(f"テーブル削除時の警告: {e}")
            # テーブル削除に失敗してもテストは続行

@pytest.fixture(scope="function")
def test_yaml_files(tmp_path):
    """テスト用のYAMLファイルを作成するフィクスチャ"""
    # 人間メンバー用のYAMLファイル
    human_yaml = {
        "name": "テスト太郎",
        "bio": "テスト用の人間メンバーです"
    }
    human_yaml_path = tmp_path / "human_test.yaml"
    with open(human_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(human_yaml, f, allow_unicode=True)
    
    # 仮想メンバー用のYAMLファイル
    virtual_yaml = {
        "name": "AIアシスタント",
        "bio": "テスト用の仮想メンバーです"
    }
    virtual_yaml_path = tmp_path / "virtual_test.yaml"
    with open(virtual_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(virtual_yaml, f, allow_unicode=True)
    
    return {
        "human": str(human_yaml_path),
        "virtual": str(virtual_yaml_path)
    }

@pytest.fixture
def mock_storage_client(monkeypatch):
    """ストレージクライアントのモックを作成するフィクスチャ"""
    class MockStorageClient:
        def read_yaml_from_minio(self, yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    
    # ストレージクライアントをモックに置き換え
    monkeypatch.setattr("operations.member_registration.StorageClient", MockStorageClient)
    return MockStorageClient()

def test_register_human_member_from_yaml(db_session, test_yaml_files, mock_storage_client):
    """YAMLファイルからの人間メンバー登録テスト"""
    # メンバーを登録
    member = register_human_member_from_yaml(test_yaml_files["human"])
    
    # 検証
    assert member is not None
    assert member.member_name == "テスト太郎"
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_human_member_by_name(db_session, "テスト太郎")
    assert saved_member is not None
    assert saved_member.member_name == "テスト太郎"
    assert saved_member.member_uuid == member.member_uuid

def test_register_virtual_member_from_yaml(db_session, test_yaml_files, mock_storage_client):
    """YAMLファイルからの仮想メンバー登録テスト"""
    # メンバーを登録
    member = register_virtual_member_from_yaml(test_yaml_files["virtual"])
    
    # 検証
    assert member is not None
    assert member.member_name == "AIアシスタント"
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_virtual_member_by_name(db_session, "AIアシスタント")
    assert saved_member is not None
    assert saved_member.member_name == "AIアシスタント"
    assert saved_member.member_uuid == member.member_uuid

def test_register_human_member_invalid_yaml(db_session, tmp_path, mock_storage_client):
    """無効なYAMLファイルからの人間メンバー登録テスト"""
    # 無効なYAMLファイルを作成
    invalid_yaml = {
        "invalid_field": "テスト太郎"
    }
    invalid_yaml_path = tmp_path / "invalid_human.yaml"
    with open(invalid_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(invalid_yaml, f, allow_unicode=True)
    
    # 無効なYAMLファイルで登録を試みる
    with pytest.raises(Exception):
        register_human_member_from_yaml(str(invalid_yaml_path))

def test_register_virtual_member_invalid_yaml(db_session, tmp_path, mock_storage_client):
    """無効なYAMLファイルからの仮想メンバー登録テスト"""
    # 無効なYAMLファイルを作成
    invalid_yaml = {
        "invalid_field": "AIアシスタント"
    }
    invalid_yaml_path = tmp_path / "invalid_virtual.yaml"
    with open(invalid_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(invalid_yaml, f, allow_unicode=True)
    
    # 無効なYAMLファイルで登録を試みる
    with pytest.raises(Exception):
        register_virtual_member_from_yaml(str(invalid_yaml_path)) 