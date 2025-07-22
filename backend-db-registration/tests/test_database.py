import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.members import HumanMember, VirtualMember
from db.database import save_human_member, save_virtual_member, get_human_member_by_name, get_virtual_member_by_name
import os

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

def test_create_human_member(db_session):
    """人間メンバーの作成テスト"""
    print("\n=== 人間メンバー作成テスト開始 ===")
    
    # テストデータ
    test_name = "テスト太郎"
    print(f"テストメンバー名: {test_name}")
    
    # メンバーを作成
    member = save_human_member(db_session, test_name)
    print(f"メンバー作成完了: UUID={member.member_uuid}")
    
    # 検証
    assert member is not None
    assert member.member_name == test_name
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_human_member_by_name(db_session, test_name)
    assert saved_member is not None
    assert saved_member.member_name == test_name
    assert saved_member.member_uuid == member.member_uuid
    
    print("✅ 人間メンバー作成テスト成功")

def test_create_virtual_member(db_session):
    """仮想メンバーの作成テスト"""
    print("\n=== 仮想メンバー作成テスト開始 ===")
    
    # テストデータ
    test_name = "AIアシスタント"
    print(f"テストメンバー名: {test_name}")
    
    # メンバーを作成
    member = save_virtual_member(db_session, test_name)
    print(f"メンバー作成完了: UUID={member.member_uuid}")
    
    # 検証
    assert member is not None
    assert member.member_name == test_name
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_virtual_member_by_name(db_session, test_name)
    assert saved_member is not None
    assert saved_member.member_name == test_name
    assert saved_member.member_uuid == member.member_uuid
    
    print("✅ 仮想メンバー作成テスト成功")

def test_get_nonexistent_human_member(db_session):
    """存在しない人間メンバーの取得テスト"""
    print("\n=== 存在しない人間メンバー取得テスト開始 ===")
    
    # 存在しないメンバーを取得
    nonexistent_name = "存在しないメンバー"
    print(f"存在しないメンバー名: {nonexistent_name}")
    
    member = get_human_member_by_name(db_session, nonexistent_name)
    
    # 検証
    assert member is None
    print("✅ 存在しない人間メンバー取得テスト成功")

def test_get_nonexistent_virtual_member(db_session):
    """存在しない仮想メンバーの取得テスト"""
    print("\n=== 存在しない仮想メンバー取得テスト開始 ===")
    
    # 存在しないメンバーを取得
    nonexistent_name = "存在しないメンバー"
    print(f"存在しないメンバー名: {nonexistent_name}")
    
    member = get_virtual_member_by_name(db_session, nonexistent_name)
    
    # 検証
    assert member is None
    print("✅ 存在しない仮想メンバー取得テスト成功")

# pytestが直接実行された場合のメイン処理
if __name__ == "__main__":
    print("🚀 pytestテストを開始します...")
    print("注意: このファイルは pytest コマンドで実行してください")
    print("例: pytest tests/test_database.py -v")
    print("または: python -m pytest tests/test_database.py -v") 