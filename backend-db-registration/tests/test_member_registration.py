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
        "bio": "テスト用の仮想メンバーです",
        "llm_model": "gpt-4"
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

# 実際のtest_casesファイルを使用した異常系テスト
@pytest.fixture
def mock_storage_with_real_files(monkeypatch, tmp_path):
    """実際のtest_casesと同等の内容でテスト用ファイルを作成するモック"""
    import os
    
    # テスト用の異常系ファイルを作成
    test_files = {
        "data/test_cases/human_members/invalid_missing_bio.yml": {
            "bio": "プロフィールのみが存在しています"
            # nameフィールドが意図的に欠損
        },
        "data/test_cases/human_members/invalid_missing_name.yml": {
            "bio": "名前フィールドが欠損しているテストファイル"
            # nameフィールドが意図的に欠損
        },
        "data/test_cases/virtual_members/invalid_missing_name.yml": {
            "llm_model": "gpt-4o",
            "custom_prompt": "名前フィールドが欠損している仮想メンバー"
            # nameフィールドが意図的に欠損
        },
        "data/test_cases/virtual_members/invalid_missing_model.yml": {
            "name": "テスト仮想メンバー",
            "custom_prompt": "正常なプロンプトです"
            # llm_modelフィールドが意図的に欠損
        },
        "data/test_cases/human_members/invalid_empty_file.yml": None,  # 空ファイル
        "data/samples/human_members/rin.yml": {
            "name": "Rin",
            "bio": "I'm a human member."
        },
        "data/samples/virtual_members/darcy.yml": {
            "name": "Darcy",
            "custom_prompt": "I'm a virtual member.",
            "llm_model": "gpt-4o"
        },
        "data/samples/human_members/syota.yml": {
            "name": "Syota",
            "bio": "I'm a human member."
        },
        "data/samples/virtual_members/kasen.yml": {
            "name": "華扇",
            "custom_prompt": "私は華扇です。",
            "llm_model": "gpt-4o"
        }
    }
    
    class MockStorageClientForRealFiles:
        def read_yaml_from_minio(self, yaml_path):
            if yaml_path in test_files:
                content = test_files[yaml_path]
                if content is None:  # 空ファイルの場合
                    return None
                return content
            else:
                raise FileNotFoundError(f"テストファイルが見つかりません: {yaml_path}")
    
    monkeypatch.setattr("operations.member_registration.StorageClient", MockStorageClientForRealFiles)
    return MockStorageClientForRealFiles()

def test_human_member_missing_name_validation(db_session, mock_storage_with_real_files):
    """実際のテストケース: 人間メンバーのname欠損でバリデーションエラー"""
    from validation.yaml_validator import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        register_human_member_from_yaml("data/test_cases/human_members/invalid_missing_bio.yml")
    
    # 日本語エラーメッセージの検証
    assert "人間メンバーYAMLに必須フィールドが不足しています: name" in str(exc_info.value) or \
           "Required fields missing in human member YAML: name" in str(exc_info.value)
    assert "name" in exc_info.value.missing_fields

def test_human_member_missing_name_original(db_session, mock_storage_with_real_files):
    """実際のテストケース: 人間メンバーのname欠損（元ファイル）でバリデーションエラー"""
    from validation.yaml_validator import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        register_human_member_from_yaml("data/test_cases/human_members/invalid_missing_name.yml")
    
    # 日本語エラーメッセージの検証
    assert "人間メンバーYAMLに必須フィールドが不足しています: name" in str(exc_info.value) or \
           "Required fields missing in human member YAML: name" in str(exc_info.value)
    assert "name" in exc_info.value.missing_fields

def test_virtual_member_missing_name_validation(db_session, mock_storage_with_real_files):
    """実際のテストケース: 仮想メンバーのname欠損でバリデーションエラー"""
    from validation.yaml_validator import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        register_virtual_member_from_yaml("data/test_cases/virtual_members/invalid_missing_name.yml")
    
    # 日本語エラーメッセージの検証
    assert "仮想メンバーYAMLに必須フィールドが不足しています: name" in str(exc_info.value) or \
           "Required fields missing in virtual member YAML: name" in str(exc_info.value)
    assert "name" in exc_info.value.missing_fields

def test_virtual_member_missing_model_validation(db_session, mock_storage_with_real_files):
    """実際のテストケース: 仮想メンバーのllm_model欠損でバリデーションエラー"""
    from validation.yaml_validator import ValidationError
    
    with pytest.raises(ValidationError) as exc_info:
        register_virtual_member_from_yaml("data/test_cases/virtual_members/invalid_missing_model.yml")
    
    # 日本語エラーメッセージの検証
    assert "仮想メンバーYAMLに必須フィールドが不足しています: llm_model" in str(exc_info.value) or \
           "Required fields missing in virtual member YAML: llm_model" in str(exc_info.value)
    assert "llm_model" in exc_info.value.missing_fields

def test_human_member_empty_file_error(db_session, mock_storage_with_real_files):
    """実際のテストケース: 空ファイルでエラー"""
    with pytest.raises(Exception) as exc_info:
        register_human_member_from_yaml("data/test_cases/human_members/invalid_empty_file.yml")
    
    # 'NoneType' object has no attribute 'get' エラーが発生することを確認
    assert "'NoneType' object has no attribute 'get'" in str(exc_info.value) or "ValidationError" in str(exc_info.type)

# 新しいディレクトリ構造（samples/）を使用した正常系テスト
def test_human_member_from_samples_directory(db_session, mock_storage_with_real_files):
    """新しいディレクトリ構造: samplesディレクトリから人間メンバー登録"""
    # Rinファイルが正常に登録されることを確認
    member = register_human_member_from_yaml("data/samples/human_members/rin.yml")
    
    # 検証
    assert member is not None
    assert member.member_name == "Rin"
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_human_member_by_name(db_session, "Rin")
    assert saved_member is not None
    assert saved_member.member_name == "Rin"

def test_virtual_member_from_samples_directory(db_session, mock_storage_with_real_files):
    """新しいディレクトリ構造: samplesディレクトリから仮想メンバー登録"""
    # Darcyファイルが正常に登録されることを確認
    member = register_virtual_member_from_yaml("data/samples/virtual_members/darcy.yml")
    
    # 検証
    assert member is not None
    assert member.member_name == "Darcy"
    assert member.member_uuid is not None
    
    # データベースから取得して検証
    saved_member = get_virtual_member_by_name(db_session, "Darcy")
    assert saved_member is not None
    assert saved_member.member_name == "Darcy"

def test_human_member_syota_from_samples(db_session, mock_storage_with_real_files):
    """新しいディレクトリ構造: Syotaファイルから人間メンバー登録"""
    # Syotaファイルが正常に登録されることを確認
    member = register_human_member_from_yaml("data/samples/human_members/syota.yml")
    
    # 検証
    assert member is not None
    assert member.member_name == "Syota"
    assert member.member_uuid is not None

def test_virtual_member_kasen_from_samples(db_session, mock_storage_with_real_files):
    """新しいディレクトリ構造: 華扇ファイルから仮想メンバー登録"""
    # 華扇ファイルが正常に登録されることを確認
    member = register_virtual_member_from_yaml("data/samples/virtual_members/kasen.yml")
    
    # 検証
    assert member is not None
    assert member.member_name == "華扇"
    assert member.member_uuid is not None

# yml_file_uriベースのUPSERT処理テスト
def test_yml_file_uri_based_upsert_human_member(db_session, monkeypatch):
    """yml_file_uriベースのUPSERT処理: 人間メンバーの新規作成と更新"""
    # 最初の登録
    test_uri = "data/test/human_members/test_user.yml"

    # テストファイル内容
    test_files = {}
    test_files[test_uri] = {
        "name": "テストユーザー",
        "bio": "初回登録のプロフィールです"
    }

    class MockStorageClient:
        def read_yaml_from_minio(self, yaml_path):
            if yaml_path in test_files:
                content = test_files[yaml_path]
                if content is None:
                    return None
                return content
            else:
                raise FileNotFoundError(f"テストファイルが見つかりません: {yaml_path}")

    monkeypatch.setattr("operations.member_registration.StorageClient", MockStorageClient)

    # 1. 新規作成
    member1 = register_human_member_from_yaml(test_uri)
    assert member1 is not None
    assert member1.member_name == "テストユーザー"
    assert member1.yml_file_uri == test_uri

    # プロフィール情報の確認
    from db.database import SessionLocal
    session = SessionLocal()
    try:
        from models.members import HumanMemberProfile
        profile = session.query(HumanMemberProfile).filter(
            HumanMemberProfile.member_uuid == member1.member_uuid
        ).first()
        assert profile is not None
        assert profile.bio == "初回登録のプロフィールです"
    finally:
        session.close()

    # 2. 同じURIで更新（内容変更）
    test_files[test_uri] = {
        "name": "テストユーザー更新",
        "bio": "更新されたプロフィールです"
    }

    member2 = register_human_member_from_yaml(test_uri)
    assert member2 is not None
    assert member2.member_name == "テストユーザー更新"
    assert member2.yml_file_uri == test_uri

    # 同じレコードが更新されることを確認（IDが同じ）
    assert member1.member_id == member2.member_id
    assert member1.member_uuid == member2.member_uuid

    # プロフィール情報が更新されることを確認
    session = SessionLocal()
    try:
        profile = session.query(HumanMemberProfile).filter(
            HumanMemberProfile.member_uuid == member2.member_uuid
        ).first()
        assert profile is not None
        assert profile.bio == "更新されたプロフィールです"
    finally:
        session.close()

def test_yml_file_uri_based_upsert_virtual_member(db_session, monkeypatch):
    """yml_file_uriベースのUPSERT処理: 仮想メンバーの新規作成と更新"""
    # 最初の登録
    test_uri = "data/test/virtual_members/test_ai.yml"

    # テストファイル内容
    test_files = {}
    test_files[test_uri] = {
        "name": "テストAI",
        "llm_model": "gpt-4",
        "custom_prompt": "初回登録のプロンプトです"
    }

    class MockStorageClient:
        def read_yaml_from_minio(self, yaml_path):
            if yaml_path in test_files:
                content = test_files[yaml_path]
                if content is None:
                    return None
                return content
            else:
                raise FileNotFoundError(f"テストファイルが見つかりません: {yaml_path}")

    monkeypatch.setattr("operations.member_registration.StorageClient", MockStorageClient)

    # 1. 新規作成
    member1 = register_virtual_member_from_yaml(test_uri)
    assert member1 is not None
    assert member1.member_name == "テストAI"
    assert member1.yml_file_uri == test_uri

    # プロフィール情報の確認
    from db.database import SessionLocal
    session = SessionLocal()
    try:
        from models.members import VirtualMemberProfile
        profile = session.query(VirtualMemberProfile).filter(
            VirtualMemberProfile.member_uuid == member1.member_uuid
        ).first()
        assert profile is not None
        assert profile.llm_model == "gpt-4"
        assert profile.custom_prompt == "初回登録のプロンプトです"
    finally:
        session.close()

    # 2. 同じURIで更新（内容変更）
    test_files[test_uri] = {
        "name": "テストAI更新版",
        "llm_model": "gpt-4o",
        "custom_prompt": "更新されたプロンプトです"
    }

    member2 = register_virtual_member_from_yaml(test_uri)
    assert member2 is not None
    assert member2.member_name == "テストAI更新版"
    assert member2.yml_file_uri == test_uri

    # 同じレコードが更新されることを確認（IDが同じ）
    assert member1.member_id == member2.member_id
    assert member1.member_uuid == member2.member_uuid

    # プロフィール情報が更新されることを確認
    session = SessionLocal()
    try:
        profile = session.query(VirtualMemberProfile).filter(
            VirtualMemberProfile.member_uuid == member2.member_uuid
        ).first()
        assert profile is not None
        assert profile.llm_model == "gpt-4o"
        assert profile.custom_prompt == "更新されたプロンプトです"
    finally:
        session.close()

def test_profile_information_storage(db_session, monkeypatch):
    """Profile情報（bio, custom_prompt, llm_model）が正しく登録されることを確認"""
    # テスト用URIの設定
    human_uri = "data/test/profile/human_with_bio.yml"
    virtual_uri = "data/test/profile/virtual_with_prompt.yml"

    # テストファイル内容
    test_files = {}
    test_files[human_uri] = {
        "name": "プロフィールテスト人間",
        "bio": "詳細なプロフィール情報です。趣味はプログラミングです。"
    }
    test_files[virtual_uri] = {
        "name": "プロフィールテスト仮想",
        "llm_model": "claude-3-opus",
        "custom_prompt": "私は詳細なプロンプトを持つAIアシスタントです。質問があれば何でも聞いてください。"
    }

    class MockStorageClient:
        def read_yaml_from_minio(self, yaml_path):
            if yaml_path in test_files:
                content = test_files[yaml_path]
                if content is None:
                    return None
                return content
            else:
                raise FileNotFoundError(f"テストファイルが見つかりません: {yaml_path}")

    monkeypatch.setattr("operations.member_registration.StorageClient", MockStorageClient)

    # 人間メンバーの登録とプロフィール確認
    human_member = register_human_member_from_yaml(human_uri)
    assert human_member is not None

    from db.database import SessionLocal
    session = SessionLocal()
    try:
        from models.members import HumanMemberProfile
        human_profile = session.query(HumanMemberProfile).filter(
            HumanMemberProfile.member_uuid == human_member.member_uuid
        ).first()
        assert human_profile is not None
        assert human_profile.bio == "詳細なプロフィール情報です。趣味はプログラミングです。"
        assert human_profile.member_id == human_member.member_id
        assert human_profile.member_uuid == human_member.member_uuid
    finally:
        session.close()

    # 仮想メンバーの登録とプロフィール確認
    virtual_member = register_virtual_member_from_yaml(virtual_uri)
    assert virtual_member is not None

    session = SessionLocal()
    try:
        from models.members import VirtualMemberProfile
        virtual_profile = session.query(VirtualMemberProfile).filter(
            VirtualMemberProfile.member_uuid == virtual_member.member_uuid
        ).first()
        assert virtual_profile is not None
        assert virtual_profile.llm_model == "claude-3-opus"
        assert virtual_profile.custom_prompt == "私は詳細なプロンプトを持つAIアシスタントです。質問があれば何でも聞いてください。"
        assert virtual_profile.member_id == virtual_member.member_id
        assert virtual_profile.member_uuid == virtual_member.member_uuid
    finally:
        session.close() 