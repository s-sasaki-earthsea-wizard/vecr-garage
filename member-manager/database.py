#!/usr/bin/env python3
"""
Database connection and operations for member-manager service
PostgreSQL接続とテーブル操作の実装
"""

import json
import logging
import os

import boto3
import psycopg2
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_secret_from_aws(secret_name, key):
    """AWS Secrets Managerから秘密鍵を取得"""
    try:
        aws_profile = os.getenv("AWS_PROFILE")
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
            client = session.client("secretsmanager")
        else:
            client = boto3.client("secretsmanager")

        response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response["SecretString"])
        return secret_dict.get(key)
    except (ClientError, Exception) as e:
        logger.debug(f"AWS Secrets Manager取得失敗: {e}")
        return None


def get_config_value(key, secret_name="vecr-garage-dev-app-secrets", default=None):
    """設定値を取得: Secrets Manager → 環境変数 → デフォルト値"""
    secret_value = get_secret_from_aws(secret_name, key)
    if secret_value:
        return secret_value

    env_value = os.getenv(key)
    if env_value:
        return env_value

    return default


class DatabaseManager:
    """データベース接続管理クラス"""

    def __init__(self):
        """Secrets Manager → 環境変数 → デフォルト値の順でデータベース接続情報を取得"""
        self.db_host = get_config_value("MEMBER_DB_HOST", default="db-member")
        self.db_port = get_config_value("MEMBER_DB_PORT", default="5432")
        self.db_user = get_config_value("MEMBER_DB_USER", default="testuser")
        self.db_password = get_config_value("MEMBER_DB_PASSWORD", default="password")
        self.db_name = get_config_value("MEMBER_DB_NAME", default="member_db")

        # 接続文字列
        self.connection_string = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        self.engine = None
        self.session = None

    def test_connection(self):
        """データベース接続テスト（psycopg2使用）"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
            )
            logger.info("✅ PostgreSQL接続成功 (psycopg2)")

            # 接続情報を表示
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info(f"PostgreSQL バージョン: {version[0]}")

            cur.close()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"❌ PostgreSQL接続失敗 (psycopg2): {e}")
            return False

    def test_sqlalchemy_connection(self):
        """SQLAlchemy接続テスト"""
        try:
            self.engine = create_engine(self.connection_string)

            # 接続テスト
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("✅ SQLAlchemy接続成功")
                return True

        except SQLAlchemyError as e:
            logger.error(f"❌ SQLAlchemy接続失敗: {e}")
            return False

    def get_table_list(self):
        """利用可能なテーブル一覧を取得"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()

            with self.engine.connect() as conn:
                # テーブル一覧を取得
                query = text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """
                )
                result = conn.execute(query)
                tables = [row[0] for row in result]
                logger.info(f"利用可能なテーブル: {tables}")
                return tables

        except Exception as e:
            logger.error(f"テーブル一覧取得失敗: {e}")
            return []

    def get_table_data(self, table_name, limit=100):
        """指定されたテーブルのデータを取得"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()

            with self.engine.connect() as conn:
                # テーブルの列情報を取得
                columns_query = text(
                    f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """
                )
                columns_result = conn.execute(columns_query)
                columns = [
                    {"name": row[0], "type": row[1], "nullable": row[2]}
                    for row in columns_result
                ]

                # テーブルのデータを取得
                data_query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
                data_result = conn.execute(data_query)
                data = [dict(row._mapping) for row in data_result]

                logger.info(
                    f"テーブル '{table_name}' から {len(data)} 件のデータを取得"
                )

                return {
                    "table_name": table_name,
                    "columns": columns,
                    "data": data,
                    "total_count": len(data),
                }

        except Exception as e:
            logger.error(f"テーブル '{table_name}' のデータ取得失敗: {e}")
            return None

    def get_table_count(self, table_name):
        """指定されたテーブルのレコード数を取得"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()

            with self.engine.connect() as conn:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = conn.execute(count_query)
                count = result.scalar()
                logger.info(f"テーブル '{table_name}' のレコード数: {count}")
                return count

        except Exception as e:
            logger.error(f"テーブル '{table_name}' のレコード数取得失敗: {e}")
            return 0

    def insert_record(self, table_name, data):
        """指定されたテーブルに新規レコードを挿入"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()

            with self.engine.begin() as conn:  # トランザクション開始
                # テーブルの列情報を取得
                columns_query = text(
                    f"""
                    SELECT column_name, data_type, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """
                )
                columns_result = conn.execute(columns_query)
                table_columns = {
                    row[0]: {"type": row[1], "default": row[2]}
                    for row in columns_result
                }

                # 自動生成される列（ID、UUID、タイムスタンプ）を除外
                filtered_data = {}
                for key, value in data.items():
                    if key in table_columns and not self._is_auto_generated_column(
                        key, table_columns[key]
                    ):
                        filtered_data[key] = value

                if not filtered_data:
                    raise ValueError("挿入可能なデータがありません")

                # SQL文を動的に生成
                columns = list(filtered_data.keys())
                placeholders = [f":{col}" for col in columns]

                insert_query = text(
                    f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                    RETURNING *
                """
                )

                result = conn.execute(insert_query, filtered_data)
                inserted_record = result.fetchone()

                logger.info(
                    f"テーブル '{table_name}' にレコードを挿入: {filtered_data}"
                )

                return dict(inserted_record._mapping) if inserted_record else None

        except Exception as e:
            logger.error(f"テーブル '{table_name}' へのレコード挿入失敗: {e}")
            raise e

    def _is_auto_generated_column(self, column_name, column_info):
        """列が自動生成されるかどうかを判定"""
        # ID列（自動採番）
        if column_name.endswith("_id") and "serial" in column_info["type"].lower():
            return True

        # UUID列（デフォルト値がある場合）
        if column_name.endswith("_uuid") and column_info["default"]:
            return True

        # タイムスタンプ列（デフォルト値がある場合）
        if column_name in ["created_at", "updated_at"] and column_info["default"]:
            return True

        return False

    def update_record(self, table_name, record_id, data):
        """指定されたテーブルのレコードを更新"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()

            with self.engine.begin() as conn:  # トランザクション開始
                # テーブルの列情報を取得
                columns_query = text(
                    f"""
                    SELECT column_name, data_type, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """
                )
                columns_result = conn.execute(columns_query)
                table_columns = {
                    row[0]: {"type": row[1], "default": row[2]}
                    for row in columns_result
                }

                # 主キー列を特定
                primary_key = self._get_primary_key_column(table_name, conn)

                # 更新可能な列のみフィルタリング
                filtered_data = {}
                for key, value in data.items():
                    if (
                        key in table_columns
                        and key != primary_key
                        and not self._is_auto_generated_column(  # 主キーは更新しない
                            key, table_columns[key]
                        )
                    ):
                        filtered_data[key] = value

                if not filtered_data:
                    raise ValueError("更新可能なデータがありません")

                # updated_atフィールドがある場合は現在時刻を設定
                if "updated_at" in table_columns:
                    filtered_data["updated_at"] = "NOW()"

                # SQL文を動的に生成
                set_clauses = []
                for col in filtered_data:
                    if col == "updated_at" and filtered_data[col] == "NOW()":
                        set_clauses.append(f"{col} = NOW()")
                    else:
                        set_clauses.append(f"{col} = :{col}")

                update_query = text(
                    f"""
                    UPDATE {table_name}
                    SET {', '.join(set_clauses)}
                    WHERE {primary_key} = :record_id
                    RETURNING *
                """
                )

                # updated_atはパラメータから除外（NOWを直接使用するため）
                params = {
                    k: v
                    for k, v in filtered_data.items()
                    if not (k == "updated_at" and v == "NOW()")
                }
                params["record_id"] = record_id

                result = conn.execute(update_query, params)
                updated_record = result.fetchone()

                if not updated_record:
                    raise ValueError(f"レコードID {record_id} が見つかりません")

                logger.info(
                    f"テーブル '{table_name}' のレコードID {record_id} を更新: {filtered_data}"
                )

                return dict(updated_record._mapping)

        except Exception as e:
            logger.error(f"テーブル '{table_name}' のレコード更新失敗: {e}")
            raise e

    def delete_record(self, table_name, record_id):
        """指定されたテーブルのレコードを削除"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()

            with self.engine.begin() as conn:  # トランザクション開始
                # 主キー列を特定
                primary_key = self._get_primary_key_column(table_name, conn)

                delete_query = text(
                    f"""
                    DELETE FROM {table_name}
                    WHERE {primary_key} = :record_id
                    RETURNING *
                """
                )

                result = conn.execute(delete_query, {"record_id": record_id})
                deleted_record = result.fetchone()

                if not deleted_record:
                    raise ValueError(f"レコードID {record_id} が見つかりません")

                logger.info(f"テーブル '{table_name}' のレコードID {record_id} を削除")

                return dict(deleted_record._mapping)

        except Exception as e:
            logger.error(f"テーブル '{table_name}' のレコード削除失敗: {e}")
            raise e

    def _get_primary_key_column(self, table_name, conn):
        """テーブルの主キー列名を取得"""
        pk_query = text(
            f"""
            SELECT column_name
            FROM information_schema.key_column_usage
            WHERE table_name = '{table_name}'
            AND constraint_name IN (
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = '{table_name}'
                AND constraint_type = 'PRIMARY KEY'
            )
        """
        )

        result = conn.execute(pk_query)
        pk_row = result.fetchone()

        if pk_row:
            return pk_row[0]

        # 主キーが見つからない場合は、一般的な命名規則で推測
        if table_name.endswith("_members"):
            return "member_id"
        if table_name.endswith("_profiles"):
            return "profile_id"
        if table_name.endswith("_relationships"):
            return "relationship_id"
        return "id"  # デフォルト

    def sync_related_tables(self, table_name, record_id, updated_data):
        """メンバーテーブル更新時に関連するプロファイルテーブルも同期更新"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()

            with self.engine.begin() as conn:
                # メンバーテーブルが更新された場合、関連するプロファイルテーブルも更新
                if table_name in ["human_members", "virtual_members"]:
                    profile_table = (
                        f"{table_name.replace('_members', '_member_profiles')}"
                    )

                    # 対象のmember_uuidを取得
                    member_query = text(
                        f"SELECT member_uuid FROM {table_name} WHERE {self._get_primary_key_column(table_name, conn)} = :record_id"
                    )
                    result = conn.execute(member_query, {"record_id": record_id})
                    member_row = result.fetchone()

                    if member_row:
                        member_uuid = member_row[0]

                        # プロファイルテーブルの更新可能なフィールドを抽出
                        profile_updates = {}
                        if table_name == "human_members" and "bio" in updated_data:
                            profile_updates["bio"] = updated_data["bio"]
                        elif table_name == "virtual_members":
                            if "llm_model" in updated_data:
                                profile_updates["llm_model"] = updated_data["llm_model"]
                            if "custom_prompt" in updated_data:
                                profile_updates["custom_prompt"] = updated_data[
                                    "custom_prompt"
                                ]

                        # プロファイルテーブルを更新
                        if profile_updates:
                            profile_updates["updated_at"] = "NOW()"
                            set_clauses = []
                            for col in profile_updates:
                                if col == "updated_at":
                                    set_clauses.append(f"{col} = NOW()")
                                else:
                                    set_clauses.append(f"{col} = :{col}")

                            profile_update_query = text(
                                f"""
                                UPDATE {profile_table}
                                SET {', '.join(set_clauses)}
                                WHERE member_uuid = :member_uuid
                            """
                            )

                            # updated_atはパラメータから除外
                            params = {
                                k: v
                                for k, v in profile_updates.items()
                                if not (k == "updated_at" and v == "NOW()")
                            }
                            params["member_uuid"] = member_uuid

                            conn.execute(profile_update_query, params)
                            logger.info(
                                f"関連テーブル '{profile_table}' も更新しました (UUID: {member_uuid})"
                            )

                # プロファイルテーブルが更新された場合、関連するメンバーテーブルの更新日時を同期
                elif table_name.endswith("_profiles"):
                    member_table = table_name.replace("_member_profiles", "_members")

                    # 対象のmember_uuidを取得
                    profile_query = text(
                        f"SELECT member_uuid FROM {table_name} WHERE {self._get_primary_key_column(table_name, conn)} = :record_id"
                    )
                    result = conn.execute(profile_query, {"record_id": record_id})
                    profile_row = result.fetchone()

                    if profile_row:
                        member_uuid = profile_row[0]

                        # メンバーテーブルのupdated_atを更新
                        member_update_query = text(
                            f"""
                            UPDATE {member_table}
                            SET updated_at = NOW()
                            WHERE member_uuid = :member_uuid
                        """
                        )

                        conn.execute(member_update_query, {"member_uuid": member_uuid})
                        logger.info(
                            f"関連テーブル '{member_table}' の更新日時を同期しました (UUID: {member_uuid})"
                        )

        except Exception as e:
            logger.error(f"関連テーブル同期処理エラー: {e}")
            # エラーが発生しても主処理は継続


def test_database_connection():
    """データベース接続テストの実行"""
    logger.info("🔍 データベース接続テスト開始")

    db_manager = DatabaseManager()

    # 接続情報を表示
    logger.info(f"接続先: {db_manager.db_host}:{db_manager.db_port}")
    logger.info(f"データベース: {db_manager.db_name}")
    logger.info(f"ユーザー: {db_manager.db_user}")

    # psycopg2接続テスト
    psycopg2_success = db_manager.test_connection()

    # SQLAlchemy接続テスト
    sqlalchemy_success = db_manager.test_sqlalchemy_connection()

    if psycopg2_success and sqlalchemy_success:
        logger.info("🎉 すべての接続テストが成功しました！")

        # テーブル一覧を取得
        tables = db_manager.get_table_list()

        # 各テーブルのレコード数を確認
        for table in tables:
            count = db_manager.get_table_count(table)
            logger.info(f"テーブル '{table}': {count} 件")

        return True
    logger.error("💥 接続テストが失敗しました")
    return False


if __name__ == "__main__":
    test_database_connection()
