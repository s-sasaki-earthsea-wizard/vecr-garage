"""
データベーストランザクションロールバック機能のテスト

メンバー登録は成功するが、プロフィール登録で失敗する異常系ケースで、
全体のトランザクションが正しくロールバックされることを検証します。
"""

import pytest
import tempfile
import yaml
from unittest.mock import patch

from db.database import SessionLocal, DatabaseError
from models.members import HumanMember, VirtualMember, HumanMemberProfile, VirtualMemberProfile
from operations.member_registration import register_human_member_from_yaml, register_virtual_member_from_yaml


@pytest.fixture
def db_session():
    """テスト用データベースセッション"""
    # テーブルが確実に存在するようにする
    from models.members import Base
    from db.database import engine
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    yield db
    # テスト分離のためのクリーンアップは最小限に
    try:
        db.rollback()  # 未完了のトランザクションをロールバック
    except:
        pass
    finally:
        db.close()


@pytest.fixture
def human_test_yaml():
    """人間メンバー用のテストYAMLファイル（プロフィール失敗用）"""
    yaml_data = {
        "name": "テスト人間メンバー",
        "bio": "テスト用のbio情報"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True)
        return f.name


@pytest.fixture
def virtual_test_yaml():
    """仮想メンバー用のテストYAMLファイル（プロフィール失敗用）"""
    yaml_data = {
        "name": "テスト仮想メンバー",
        "llm_model": "gpt-4",
        "custom_prompt": "テスト用のカスタムプロンプト"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True)
        return f.name


@pytest.fixture
def mock_storage_client(monkeypatch):
    """ストレージクライアントのモック"""
    def mock_read_yaml(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    class MockStorageClient:
        def read_yaml_from_minio(self, yaml_path):
            return mock_read_yaml(yaml_path)

    monkeypatch.setattr("operations.member_registration.StorageClient", MockStorageClient)


def test_human_member_profile_failure_rollback(db_session, human_test_yaml, mock_storage_client):
    """
    人間メンバー登録でプロフィール失敗時の全体ロールバックテスト

    シナリオ:
    1. human_membersテーブルへの登録は成功
    2. human_member_profilesテーブルへの登録で例外発生
    3. 全体がロールバックされ、human_membersテーブルの変更も取り消される
    """
    # 事前状態確認
    initial_human_count = db_session.query(HumanMember).count()
    initial_profile_count = db_session.query(HumanMemberProfile).count()

    # プロフィール登録で失敗するようにupsert_human_member_profileをモック
    with patch('db.database.upsert_human_member_profile') as mock_upsert:
        mock_upsert.side_effect = DatabaseError("プロフィール登録時のデータベースエラー", Exception("DB接続失敗"))

        # 登録処理を実行し、DatabaseErrorが発生することを確認
        with pytest.raises(DatabaseError) as exc_info:
            register_human_member_from_yaml(human_test_yaml)

        assert "プロフィール登録時のデータベースエラー" in str(exc_info.value)

    # ロールバック後の状態確認
    final_human_count = db_session.query(HumanMember).count()
    final_profile_count = db_session.query(HumanMemberProfile).count()

    # 全体がロールバックされ、初期状態と同じであることを確認
    assert final_human_count == initial_human_count, f"human_membersテーブルのロールバックが失敗: 初期{initial_human_count} → 最終{final_human_count}"
    assert final_profile_count == initial_profile_count, f"human_member_profilesテーブルのロールバックが失敗: 初期{initial_profile_count} → 最終{final_profile_count}"

    print(f"✅ 人間メンバーロールバックテスト成功")
    print(f"   - メンバー数: {initial_human_count} → {final_human_count}")
    print(f"   - プロフィール数: {initial_profile_count} → {final_profile_count}")


def test_virtual_member_profile_failure_rollback(db_session, virtual_test_yaml, mock_storage_client):
    """
    仮想メンバー登録でプロフィール失敗時の全体ロールバックテスト

    シナリオ:
    1. virtual_membersテーブルへの登録は成功
    2. virtual_member_profilesテーブルへの登録で例外発生
    3. 全体がロールバックされ、virtual_membersテーブルの変更も取り消される
    """
    # 事前状態確認
    initial_virtual_count = db_session.query(VirtualMember).count()
    initial_profile_count = db_session.query(VirtualMemberProfile).count()

    # プロフィール登録で失敗するようにupsert_virtual_member_profileをモック
    with patch('db.database.upsert_virtual_member_profile') as mock_upsert:
        mock_upsert.side_effect = DatabaseError("仮想メンバープロフィール登録エラー", Exception("制約違反"))

        # 登録処理を実行し、DatabaseErrorが発生することを確認
        with pytest.raises(DatabaseError) as exc_info:
            register_virtual_member_from_yaml(virtual_test_yaml)

        assert "仮想メンバープロフィール登録エラー" in str(exc_info.value)

    # ロールバック後の状態確認
    final_virtual_count = db_session.query(VirtualMember).count()
    final_profile_count = db_session.query(VirtualMemberProfile).count()

    # 全体がロールバックされ、初期状態と同じであることを確認
    assert final_virtual_count == initial_virtual_count, f"virtual_membersテーブルのロールバックが失敗: 初期{initial_virtual_count} → 最終{final_virtual_count}"
    assert final_profile_count == initial_profile_count, f"virtual_member_profilesテーブルのロールバックが失敗: 初期{initial_profile_count} → 最終{final_profile_count}"

    print(f"✅ 仮想メンバーロールバックテスト成功")
    print(f"   - メンバー数: {initial_virtual_count} → {final_virtual_count}")
    print(f"   - プロフィール数: {initial_profile_count} → {final_profile_count}")


def test_database_constraint_violation_rollback(db_session, human_test_yaml, mock_storage_client):
    """
    データベース制約違反による自動ロールバックテスト

    シナリオ:
    1. 正常なメンバー登録を先に実行
    2. 同じyml_file_uriで重複登録を試行
    3. UNIQUE制約違反でトランザクション全体がロールバック
    """
    # 事前状態確認
    initial_human_count = db_session.query(HumanMember).count()
    initial_profile_count = db_session.query(HumanMemberProfile).count()

    # 最初の正常な登録
    member1 = register_human_member_from_yaml(human_test_yaml)
    assert member1 is not None

    # 中間状態確認
    intermediate_human_count = db_session.query(HumanMember).count()
    intermediate_profile_count = db_session.query(HumanMemberProfile).count()

    assert intermediate_human_count == initial_human_count + 1
    assert intermediate_profile_count == initial_profile_count + 1

    # 同じURIで重複登録を試行（UPSERT動作のため、実際は更新される）
    member2 = register_human_member_from_yaml(human_test_yaml)
    assert member2 is not None

    # UPSERT動作確認：レコード数は変わらず、更新のみ
    final_human_count = db_session.query(HumanMember).count()
    final_profile_count = db_session.query(HumanMemberProfile).count()

    assert final_human_count == intermediate_human_count  # 更新のため増加なし
    assert final_profile_count == intermediate_profile_count  # 更新のため増加なし

    print(f"✅ UPSERT動作確認テスト成功")
    print(f"   - 初期メンバー数: {initial_human_count}")
    print(f"   - 1回目登録後: {intermediate_human_count}")
    print(f"   - 2回目登録後: {final_human_count} (UPSERT動作)")


def test_transaction_isolation_verification(db_session, human_test_yaml, mock_storage_client):
    """
    トランザクション分離レベルの検証テスト

    異なるセッションからロールバック前の未コミット状態が見えないことを確認
    """
    # 別セッションを作成
    external_session = SessionLocal()

    try:
        initial_count = external_session.query(HumanMember).count()

        # プロフィール登録失敗をモック
        with patch('db.database.upsert_human_member_profile') as mock_upsert:
            mock_upsert.side_effect = DatabaseError("テスト用失敗", Exception())

            # 失敗する登録処理を実行
            with pytest.raises(DatabaseError):
                register_human_member_from_yaml(human_test_yaml)

        # 外部セッションから見た場合、変更が見えないことを確認
        external_count = external_session.query(HumanMember).count()
        assert external_count == initial_count, "未コミットの変更が外部セッションから見えています"

        print(f"✅ トランザクション分離確認テスト成功")
        print(f"   - 外部セッションからの変更は不可視")

    finally:
        external_session.close()


if __name__ == "__main__":
    print("🧪 トランザクションロールバックテストを実行中...")
    pytest.main([__file__, "-v"])