import pytest
import yaml
import os
from pathlib import Path
from operations.member_registration import register_human_member_from_yaml, register_virtual_member_from_yaml
from db.database import get_human_member_by_name, get_virtual_member_by_name

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

def test_register_duplicate_human_member(db_session, test_yaml_files, mock_storage_client):
    """重複する人間メンバーの登録テスト"""
    # 最初のメンバーを登録
    first_member = register_human_member_from_yaml(test_yaml_files["human"])
    
    # 同じYAMLファイルで2回目の登録を試みる
    second_member = register_human_member_from_yaml(test_yaml_files["human"])
    
    # 検証（2回目の登録は既存のメンバーを返すはず）
    assert second_member is not None
    assert second_member.member_uuid == first_member.member_uuid

def test_register_duplicate_virtual_member(db_session, test_yaml_files, mock_storage_client):
    """重複する仮想メンバーの登録テスト"""
    # 最初のメンバーを登録
    first_member = register_virtual_member_from_yaml(test_yaml_files["virtual"])
    
    # 同じYAMLファイルで2回目の登録を試みる
    second_member = register_virtual_member_from_yaml(test_yaml_files["virtual"])
    
    # 検証（2回目の登録は既存のメンバーを返すはず）
    assert second_member is not None
    assert second_member.member_uuid == first_member.member_uuid

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