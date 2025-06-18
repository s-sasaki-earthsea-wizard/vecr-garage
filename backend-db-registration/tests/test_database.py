import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.members import HumanMember, VirtualMember
from db.database import create_human_member, create_virtual_member, get_human_member_by_name, get_virtual_member_by_name
import os

# テスト用のデータベースURL
TEST_DATABASE_URL = "postgresql://testuser:password@member-database:5432/test_member_db"

@pytest.fixture(scope="function")
def db_session():
    """テスト用のデータベースセッションを作成するフィクスチャ"""
    # テスト用のデータベースエンジンを作成
    engine = create_engine(TEST_DATABASE_URL)
    
    # テスト用のテーブルを作成
    Base.metadata.create_all(engine)
    
    # テスト用のセッションを作成
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        # テスト後にテーブルを削除
        session.close()
        Base.metadata.drop_all(engine)

def test_create_human_member(db_session):
    """人間メンバーの作成テスト"""
    # テストデータ
    test_name = "テスト太郎"
    
    # メンバーを作成
    member = create_human_member(db_session, test_name)
    
    # 検証
    assert member is not None
    assert member.member_name == test_name
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_human_member_by_name(db_session, test_name)
    assert saved_member is not None
    assert saved_member.member_name == test_name
    assert saved_member.member_uuid == member.member_uuid

def test_create_virtual_member(db_session):
    """仮想メンバーの作成テスト"""
    # テストデータ
    test_name = "AIアシスタント"
    
    # メンバーを作成
    member = create_virtual_member(db_session, test_name)
    
    # 検証
    assert member is not None
    assert member.member_name == test_name
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_virtual_member_by_name(db_session, test_name)
    assert saved_member is not None
    assert saved_member.member_name == test_name
    assert saved_member.member_uuid == member.member_uuid

def test_duplicate_human_member(db_session):
    """重複する人間メンバーの作成テスト"""
    # テストデータ
    test_name = "テスト太郎"
    
    # 最初のメンバーを作成
    first_member = create_human_member(db_session, test_name)
    
    # 同じ名前で2回目のメンバーを作成
    with pytest.raises(Exception):
        create_human_member(db_session, test_name)

def test_duplicate_virtual_member(db_session):
    """重複する仮想メンバーの作成テスト"""
    # テストデータ
    test_name = "AIアシスタント"
    
    # 最初のメンバーを作成
    first_member = create_virtual_member(db_session, test_name)
    
    # 同じ名前で2回目のメンバーを作成
    with pytest.raises(Exception):
        create_virtual_member(db_session, test_name)

def test_get_nonexistent_human_member(db_session):
    """存在しない人間メンバーの取得テスト"""
    # 存在しないメンバーを取得
    member = get_human_member_by_name(db_session, "存在しないメンバー")
    
    # 検証
    assert member is None

def test_get_nonexistent_virtual_member(db_session):
    """存在しない仮想メンバーの取得テスト"""
    # 存在しないメンバーを取得
    member = get_virtual_member_by_name(db_session, "存在しないメンバー")
    
    # 検証
    assert member is None 